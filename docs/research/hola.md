# Is hola safe to depend on?

Research for the ticket [Is hola safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/6) on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Researched 2026-09-27 by reading source only. hola was not installed or run.

**Sources read.** Unless a link says otherwise, every code citation points at hola commit [`8b1cea3`](https://github.com/ratazzi/hola/tree/8b1cea3bc9a4fe79459da2a749d259cf19591c8c). That commit is the `master` HEAD and is also what the `v0.4.0` tag points to (`git rev-list -n1 v0.4.0`).
Terms (**Bootstrap**, **Fresh Mac**, **Package**, **Dotfile**, **macOS setting**) mean what the map's Notes define them to mean.

## Verdict

**hola is safe to depend on only as a thin, pinned, throwaway layer. The exit is cheap because hola adds very little on top of standard pieces.**

- **Most of what hola runs is already standard.** Packages go through `brew bundle` and `mise install`, and Dotfiles are plain files. The parts that are hola's own are:
  - a top-level symlink loop;
  - `provision.rb`, which for a Mac setup comes down to `defaults write`, Dock layout, and guarded shell commands.

  Leaving hola means rewriting about one shell line per `provision.rb` resource, plus a short bootstrap script.
- **The project is risky as a long-term dependency.** Six facts point that way:
  1. **One maintainer, almost no Mac users.** One person made every commit. The macOS binaries of all stable releases together show 33 downloads.
  2. **The project is moving away from Mac setup.** Recent releases added server and CI provisioning.
  3. **Renames broke users silently.** Two renames shipped without aliases and without being mentioned in the release notes.
  4. **A data-loss fix sits unmerged.** The maintainer's own fix for a silent recursive-delete bug has been open since July.
  5. **`hola apply` can report success after failing.** It turns Homebrew and mise failures into warnings.
  6. **`--dry-run` is not a dry run.** It still installs Homebrew and every Package.
- **Conditions if hola is chosen:**
  - Pin the version by sha256.
  - Keep `provision.rb` to `macos_defaults`, `macos_dock`, and guarded `execute`.
  - Never use `directory … action :delete`.
  - Check `brew bundle` separately.
  - Trial it only in the VM.

Whether hola beats "standard pieces with thin glue" is the tooling ticket's call ([Which tooling approach does the setup use?](https://github.com/iamivanhx/macos-setup/issues/15)). On the map's own measure ("how little the owner maintains"), hola removes about 20 lines of glue. In exchange the owner depends on a single-maintainer binary.

## Facts at charting, re-verified

| Claim in ticket | Finding | Source |
|---|---|---|
| Written in Zig with embedded mruby | True. Zig ≥ 0.16.0, mruby **4.0.0** built from a separate repo, `ratazzi/hola-deps` | [`build.zig.zon` L27, L35-47](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/build.zig.zon); [hola-deps `build_config/hola.rb`](https://github.com/ratazzi/hola-deps/blob/79323f5f98a73b204d0d5b6f7dd8f31d9916e196/build_config/hola.rb); [mruby `version.h` at pinned submodule `831da26`](https://github.com/mruby/mruby/blob/831da26b9021de0369d17b71b5667e2941a1a32d/include/mruby/version.h) |
| Created 2025-11-23 | GitHub repo created 2025-11-23. The first commit is dated earlier, 2025-11-17 | `gh api repos/ratazzi/hola` (`created_at`); `git log --reverse` |
| Latest release v0.4.0 on 2026-09-21 | True. A `nightly` pre-release was rebuilt 2026-09-22 from the same commit | [Releases](https://github.com/ratazzi/hola/releases) |
| One contributor, all 242 commits | True. 242 commits, all from one email under two name spellings (`ratazzi`/`Ratazzi`) | `gh api repos/ratazzi/hola/contributors`; `git log` |
| 25 stars | True; also 0 forks | `gh api repos/ratazzi/hola` |
| MIT licence | True. Bundled third-party code is listed separately | [`LICENSE`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/LICENSE), [`THIRD-PARTY-LICENSES.md`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/THIRD-PARTY-LICENSES.md) |
| Config is a `Brewfile`, `mise.toml`, `~/.dotfiles/`, optional `provision.rb` | True, with one caveat. hola does **not** read a Brewfile from the Dotfiles directory. It runs `brew bundle --global`, which reads `~/.Brewfile` (or `$HOMEBREW_BUNDLE_FILE_GLOBAL`, or the XDG paths) | [`src/apply.zig` L326-361](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L326-L361) |
| Scope widening (signing, notarization, remote SSH) | True. v0.4.0 added a `Holafile` task runner, remote SSH provisioning, and Xcode/codesign/DMG/notarize resources. v0.3.0 had already added an "agent mode" (WebSocket), AWS KMS, mount, and data/secrets bags | [v0.4.0 notes](https://github.com/ratazzi/hola/releases/tag/v0.4.0); [v0.3.0 notes](https://github.com/ratazzi/hola/releases/tag/v0.3.0); [`README.md` L180-478](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L180-L478) |

## What `hola apply` does

The steps run in this order ([`src/apply.zig` L129-206](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L129-L206); the help text in [`src/commands/apply.zig` L201-211](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/apply.zig#L201-L211)):

1. **Optional clone.**
   - `--github user/repo` always clones over SSH, as `git@github.com:user/repo.git`. `--repo <url>` accepts any URL.
   - The clone destination is the Dotfiles root, and it must be empty.
   - Cloning uses the embedded libgit2, so no system `git` is needed.
   - Sources: [`src/commands/apply.zig` L140-174](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/apply.zig#L140-L174), [L11-24](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/apply.zig#L11-L24).
2. **Link Dotfiles** from the Dotfiles root into `$HOME` (details below).
3. **Install Homebrew if missing.** hola runs the official `curl …/Homebrew/install/HEAD/install.sh` with inherited stdout and stderr ([`src/apply.zig` L255-296](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L255-L296)).
4. **Install Packages and mise tools in parallel:**
   - `brew bundle --global --no-upgrade --force`;
   - mise, installed with `curl https://mise.run | sh` if missing;
   - `mise trust`, then `mise install`, in the directory that holds `mise.toml`.

   Sources: [L303-475](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L303-L475), [L518-537](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L518-L537).
5. **Run `provision.rb`** if one exists. hola uses the first match of `<root>/.config/hola/provision.rb`, `~/.dotfiles/.config/hola/provision.rb`, or `~/.config/hola/provision.rb` ([L160-196](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L160-L196)).

## To answer

### What `provision.rb` can express, and what the mruby limits rule out

**Resources available** ([`src/ruby_prelude/resources.rb` L3-9](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/ruby_prelude/resources.rb#L3-L9)):

- files and paths: `file`, `directory`, `link`, `template`, `file_edit`, `remote_file`, `extract`;
- commands and code: `execute`, `ruby_block`;
- packages: `package`, `homebrew_package`;
- Git: `git`;
- macOS: `macos_defaults`, `macos_dock`;
- macOS release resources: `xcode_build`, `macos_signing_certificate`, `macos_codesign`, `macos_dmg`, `macos_notarize`;
- Linux and server resources: `apt_*`, `systemd_unit`, `mount`, `route`, `user`, `group`, `aws_kms`.

Every resource takes `only_if`/`not_if` (a shell string or a Ruby block), `ignore_failure`, and Chef-style `notifies`/`subscribes`.

**macOS settings.**
- `macos_defaults` takes `domain` or `global true`, a `key`, and a `value`. The value's type is inferred as string, integer, boolean, float, array, or dict. `current_host true` writes to the per-host domain. Sources: [`src/resources/macos_defaults_resource.rb` L47-64, L84-88](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_defaults_resource.rb#L47-L88).
- It writes through CFPreferences for the current user only, not through `defaults` ([`src/cfprefs_wrapper.c` L9-32](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/cfprefs_wrapper.c#L9-L32)). So it cannot write system-wide (`/Library/Preferences`) or root-owned settings. Those need `execute` with `sudo`.
- It compares the current value before writing, and after a change it runs `killall` on Finder, Dock, or SystemUIServer as the domain requires ([`src/resources/macos_defaults.zig` L175, L184-238](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_defaults.zig#L175-L238)).
- `macos_dock` sets `apps`, `orientation`, `autohide`, `magnification`, `tilesize`, and `largesize`, and nothing else ([`src/resources/macos_dock_resource.rb` L34-56](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_dock_resource.rb#L34-L56)).

**Files.**
- `file` sets content, mode, and owner, and skips the write when the content already matches ([`src/resources/file.zig` L131-146](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/file.zig#L131-L146)).
- `link`, `directory`, and `template` (ERB with `variables`) are also available ([`provision.example.rb`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/provision.example.rb)).

**Commands.**
- `execute` sets `command`, `cwd`, `user`, `group`, `environment`, `creates`, and `timeout`. The default timeout is 3600 s ([`src/resources/execute_resource.rb` L4-18](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/execute_resource.rb#L4-L18)).
- `execute` runs on every run unless `creates`, `not_if`, or `only_if` guards it ([`src/resources/execute.zig` L107-132](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/execute.zig#L107-L132)).
- `execute` also has a `returns` setter, but the value is never passed to the backend ([`execute_resource.rb` L73-75](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/execute_resource.rb#L73-L75) versus [L34](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/execute_resource.rb#L34)). Exit-code allow-lists therefore do not work.

**What mruby rules out.**
- The README states it plainly: "Regular expressions, native gems, backticks, `exit`, and the block form of `sh` are unavailable" ([`README.md` L394-398](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L394-L398)).
- The embedded mruby uses the `default` gembox plus `mruby-strftime` ([hola-deps `build_config/hola.rb`](https://github.com/ratazzi/hola-deps/blob/79323f5f98a73b204d0d5b6f7dd8f31d9916e196/build_config/hola.rb)). That gembox gives File, IO, and Dir, but no Regexp class ([mruby `default.gembox`](https://github.com/mruby/mruby/blob/831da26b9021de0369d17b71b5667e2941a1a32d/mrbgems/default.gembox), [`stdlib-io.gembox`](https://github.com/mruby/mruby/blob/831da26b9021de0369d17b71b5667e2941a1a32d/mrbgems/stdlib-io.gembox)).
- `require` loads only local files plus a fixed list of shims: `fileutils json time base64 set ostruct` ([`src/ruby_prelude/loader.rb` L31-45](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/ruby_prelude/loader.rb#L31-L45)).
- In practice, Ruby code cannot capture a command's output. The value of a setting cannot be computed from `scutil`, `sw_vers`, or similar tools. Shell logic has to live inside `execute` commands or string guards. A `node` object provides basic facts such as hostname, platform, and architecture ([`src/ruby_prelude/node_info.rb`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/ruby_prelude/node_info.rb)).
- `file_edit` does pattern edits through an embedded PCRE2 ([`src/resources/file_edit_resource.rb` L41-67](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/file_edit_resource.rb#L41-L67)).

### How much of a typical setup must live in `provision.rb`

`provision.rb` is the one part that does not survive leaving hola. hola has no other path for macOS settings, so these must live in it:

- every macOS setting;
- the Dock;
- any file that must be a real copy or a template rather than a symlink;
- every one-off command, for example `chsh`, `ssh-keygen`, or `duti`.

These do **not** need to live in it:

- Packages: native Brewfile, including `mas` lines;
- tool versions: native `mise.toml`;
- Dotfiles: plain files.

For the owner's setup, `provision.rb` is therefore essentially "the macOS settings list plus a few guarded commands". Each `macos_defaults` block is about five lines of DSL for one `defaults write` line.

### Can Dotfiles stay in this repo rather than `~/.dotfiles/`?

**Yes, with these rules.**

**Pointing hola at the repo.**
- `hola apply --dotfiles <path>` accepts any path. hola remembers it as a symlink at `~/.local/state/hola/dotfiles`, so later runs need no flag ([`src/commands/apply.zig` L176-184](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/apply.zig#L176-L184); [`src/dotfiles_paths.zig` L22-55](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/dotfiles_paths.zig#L22-L55)).
- Point it at a subdirectory such as `dotfiles/`, not the repo root, because of how the linker walks the tree (next group).

**How linking works.**
- **Only the top level is linked.** The linker iterates the root's entries without recursing. Each top-level file, directory, or symlink becomes one symlink `$HOME/<name>` → `<root>/<name>` ([`src/dotfiles.zig` L162-190](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/dotfiles.zig#L162-L190)). A `.config/` directory in the repo is linked as the whole `~/.config`. If `~/.config` already exists, it is reported as a conflict and skipped.
- **Default ignores** cover only `.git`, `.github`, `.gitmodules`, `.gitignore`, `.DS_Store`, `README*`, and `LICENSE*` ([L115-125](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/dotfiles.zig#L115-L125)). You can add extra glob ignores in `<root>/.hola.toml` or `~/.config/hola/hola.toml`, under `[dotfiles] ignore` ([`src/apply.zig` L540-617](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L540-L617)).
- **Existing files are never overwritten.** An existing file, directory, or different symlink is skipped and shown as a conflict ([`src/dotfiles.zig` L210-235, L418-470](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/dotfiles.zig#L210-L470)).

**Placement consequences.**
- The Brewfile has to reach `~/.Brewfile`. Either put it in the Dotfiles root as `.Brewfile` so it is linked, or set `HOMEBREW_BUNDLE_FILE_GLOBAL`.
- `mise.toml` is read from the Dotfiles root, so it also gets linked into `$HOME` unless it is ignored ([`src/apply.zig` L393-458](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L393-L458)).
- A `provision.rb` at `<root>/.config/hola/provision.rb` drags the whole `.config` along. Alternatively, run it with `hola provision <path>`.

**Cloning on a Fresh Mac.**
- `--github` needs an SSH key, and the target Mac has none.
- `--repo https://…` clones into the Dotfiles root itself, which conflicts with keeping Dotfiles in a subdirectory.
- The workable sequence is `hola git-clone https://github.com/iamivanhx/macos-setup <dir>`, then `hola apply --dotfiles <dir>/dotfiles` ([`src/commands/git_clone.zig` L7-15](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/git_clone.zig#L7-L15)).

### What the install script does on a Fresh Mac, and what it needs first

The script is [`install.sh`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/install.sh), 56 lines of POSIX `sh`. The hosted copy at `https://hola.ac/install` (the README's recommended `curl -fsSL https://hola.ac/install | bash`, [`README.md` L52](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L52)) was fetched as text on 2026-09-27. It differs from the repo copy only in its usage comments.

**What it does:**
1. It maps `uname -s`/`uname -m` to `hola-macos-aarch64`. There is no Intel macOS build.
2. It picks the URL: `releases/latest`, `nightly`, or a given tag (from `$VERSION` or `$1`) ([L12-46](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/install.sh#L12-L46)).
3. It downloads the binary with `curl -fsSL -o hola` into **the current directory** and runs `chmod +x` ([L50-51](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/install.sh#L50-L51)).
4. It removes the `com.apple.quarantine` xattr ([L54](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/install.sh#L54)).

**What it does not do:**
- It uses no sudo and does not touch `PATH`.
- It installs nothing else.
- **It verifies no checksum or signature.** The CI release job uploads raw binaries, with no signing, notarization, or checksum files ([`.github/workflows/build.yml`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/.github/workflows/build.yml)).

**Where checksums can come from:**
- GitHub's release API reports a sha256 digest per asset. For v0.4.0 `hola-macos-aarch64` it is `dc3e2cd2…e61c`.
- The Homebrew tap formula pins that same sha256 ([`ratazzi/homebrew-hola` `Formula/hola.rb`](https://github.com/ratazzi/homebrew-hola/blob/master/Formula/hola.rb)). The tap, however, requires Homebrew first.

**What it needs first:** only base macOS (`sh`, `curl`, `uname`, `xattr`).
- The binary is statically linked with libcurl, OpenSSL, libgit2, libssh2, and mruby ([`build.zig.zon` L36-47](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/build.zig.zon#L36-L47); [hola-deps `.gitmodules`](https://github.com/ratazzi/hola-deps/blob/79323f5f98a73b204d0d5b6f7dd8f31d9916e196/.gitmodules)). It therefore needs neither Xcode Command Line Tools nor git.
- The v0.4.0 macOS binary is 11.2 MB. The README says "~6 MB" ([`README.md` L484](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L484)).
- `hola apply` itself then runs Homebrew's installer. That installer needs an admin password and installs the Command Line Tools, but that is Homebrew's requirement, not hola's.

### How it behaves on failure and on a second run

**Failure.**
- **`provision.rb` fails fast.** The first failing resource stops the run unless it has `ignore_failure true` ([`src/provision.zig` L333-363](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/provision.zig#L333-L363)). A failed resource is marked converged and is not retried within that run ([L477-480](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/provision.zig#L477-L480)). `hola provision` exits 1 on failure ([`src/commands/provision.zig` L204-217](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/provision.zig#L204-L217)).
- **`hola apply` swallows Package failures.**
  - A `brew bundle` failure becomes the warning "Some Homebrew packages failed to install … Continuing..." ([`src/apply.zig` L363-372](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L363-L372)).
  - The brew and mise steps run in threads whose errors "can't propagate" ([L313-323](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L313-L323)). Zig's `std.Thread` prints the error of a thread function that returns an error, then discards it ([Zig `lib/std/Thread.zig` L575-585](https://github.com/ziglang/zig/blob/738d2be9d6b6ef3ff3559130c05159ef53336224/lib/std/Thread.zig#L575-L585); this is the GitHub mirror, last pushed 2025-11-27, while hola builds with Zig 0.16).
  - So the run goes on to `provision.rb`. It can print "All done!" and exit 0 with Packages missing.
- **Homebrew install failure is fatal.** It aborts `apply` ([L273-281](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L273-L281)).
- **Bad command-line arguments exit 0.** They print a diagnostic and return ([`src/main.zig` L40-43](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/main.zig#L40-L43); [`src/commands/apply.zig` L120-123](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/commands/apply.zig#L120-L123)).
- **`--dry-run` is not dry.** `dry_run` reaches only Dotfile linking and the provision skip. Homebrew installation, `brew bundle`, and `mise install` run for real ([`src/apply.zig` L151-158, L186-192](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L151-L192)).
- **Known data-loss bug, unfixed in v0.4.0.** `directory "x" do action :delete end` without `recursive` can recursively delete the tree, because an uninitialised `mrb_value` is read as the flag ([`src/resources/directory.zig` L228, L237, L267](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/directory.zig#L228-L267)). The maintainer's own fix, [PR #30](https://github.com/ratazzi/hola/pull/30), has been open since 2026-07-16.

**Second run.**
- Dotfile links that already exist are reported "already linked" and skipped ([`src/dotfiles.zig` L229-231](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/dotfiles.zig#L229-L231)).
- `brew bundle` runs with `--no-upgrade` unless `HOMEBREW_BUNDLE_NO_UPGRADE=0` ([`src/apply.zig` L340-358](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/apply.zig#L340-L358)).
- `mise install` skips installed tools. That is mise's behaviour, not hola's.
- `file`, `macos_defaults`, and `macos_dock` compare state before writing and report "up to date".
- `execute` re-runs unless guarded.

So re-runs are safe as long as every `execute` is guarded, which is the property the map asks for.

### How the maintainer handles issues, pull requests, and breaking changes

**Issues.**
- Only three issues have ever come from outside: [#3](https://github.com/ratazzi/hola/issues/3), [#5](https://github.com/ratazzi/hola/issues/5), and [#12](https://github.com/ratazzi/hola/issues/12). All three came from one user and concerned the Dock.
- Each was closed within one to three days. #12 was closed by a fix PR ([#13](https://github.com/ratazzi/hola/pull/13)), and #5 got a courteous, detailed reply that promised and explained a behaviour change.

**Pull requests.**
- All 49 issue and PR numbers belong to the owner except those three issues. There are no outside contributors and no forks.
- The owner works through self-merged PRs with conventional-commit titles.
- The repo's 6 open items are all owner PRs from July 2026: [#25](https://github.com/ratazzi/hola/pull/25) and [#29–#33](https://github.com/ratazzi/hola/pull/33). Among them are the recursive-delete fix (#30), a shell-injection hardening (#31), and a thread-lifetime fix (#32). These fixes were written but not merged, while v0.4.0 shipped new features on top.

**Breaking changes.**
- There is no changelog file and no deprecation policy. Release notes range from none (v0.2.1 is empty) to a highlights list (v0.4.0).
- Two renames removed old names with no alias, and no release note called them out:
  - `remote_file`'s `aws_access_key`/`aws_secret_key` became `aws_access_key_id`/`aws_secret_access_key` ([`4a70944`](https://github.com/ratazzi/hola/commit/4a70944), shipped in v0.2.x);
  - `hola provision --params/--secrets` became `--data-bag/--secrets-bag` ([`471d54c`](https://github.com/ratazzi/hola/commit/471d54c), shipped in v0.3.0).
- By contrast, v0.4.0 kept legacy Rakefile names with a migration warning, and it kept un-phased recipes working ([`README.md` L182-186, L302-306](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L182-L306)). Compatibility care is therefore present but inconsistent. The project is pre-1.0, and semver allows breaks between minor releases.

**Activity.**
- Commits per month (from `git log`): 52 in 2025-11, 33 in 2025-12, 1 in 2026-01, 0 in 2026-02, and 11–37 each month from 2026-03 to 2026-09.
- Six tagged releases in ten months. The `v0.2.0` tag has no GitHub release.

**Who uses it.**
- Download counts from the release API: the macOS binaries of all stable releases total 33 (v0.4.0: 2).
- The Linux x86_64 `nightly` shows 14,580 downloads. The README says remote provisioning falls back to the nightly build and revalidates it every run ([`README.md` L446-450](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md#L446-L450)). This suggests the maintainer's heaviest use is now Linux server provisioning. That is an inference, not a stated fact.

### What still works if hola is abandoned tomorrow

**Keeps working with no change:**
- the Brewfile: `brew bundle --file <path>` or `--global`;
- `mise.toml`: `mise install`;
- every Dotfile, since they are plain files in this repo;
- everything already applied to the Mac.

The last downloaded hola binary also keeps running until a macOS change breaks it. It is ad-hoc built and not notarized, but a `curl` download carries no quarantine flag. Release assets stay on GitHub unless the repo is deleted.

**Has to be rewritten:**
1. **The entry point.** A `bootstrap.sh` of roughly 20 lines (estimate) must:
   - install Homebrew with its official one-liner;
   - run `brew bundle --file Brewfile`;
   - install mise and run `mise install`;
   - link Dotfiles;
   - run the settings script.
2. **Dotfile linking.** hola's convention (link each top-level entry of a directory into `$HOME`, skip anything that already exists) is a shell loop of about ten lines. GNU Stow is another option, but its tree folding differs, so check it before switching.
3. **Every `provision.rb` resource**, which translates line for line:

   | hola resource | Shell replacement |
   |---|---|
   | `macos_defaults` | `defaults write [-currentHost] <domain> <key> -<type> <value>`, followed by `killall Finder/Dock/SystemUIServer` |
   | `macos_dock` | `dockutil` or `defaults write com.apple.dock persistent-apps …` |
   | `file`, `link` | heredoc or `ln -sf` |
   | `execute` with `creates`/`not_if` | `[ -e … ] \|\| cmd` |

   Neither format uses much logic, because mruby cannot capture command output or use regular expressions. The DSL looks like Chef, but no compatibility with Chef or Cinc was checked or is claimed. Do not count on it as an exit.

The exit cost therefore grows with the size of `provision.rb`, about one shell line per resource. For a one-shot Bootstrap that is small.

## Not verifiable without running hola

- Whether v0.4.0 works on **macOS 27**. The newest user report found is on macOS 26.4.1 ([#5](https://github.com/ratazzi/hola/issues/5)).
- The actual exit status of `hola apply` when `brew bundle` fails. The source reading says 0.
- Whether the Homebrew installer launched by hola gets a working TTY for its `sudo` prompt when hola itself is started from a `curl | bash` pipeline. hola passes stdout and stderr through, but the source does not show stdin being set.
- Whether CFPreferences writes (as opposed to `defaults`) take effect on macOS 27 for every setting the owner wants. This includes sandboxed apps' container domains.
- How the linker treats `.hola.toml` itself, and a pre-existing `~/.config` on the target Mac. From the code: `.hola.toml` would be linked, and an existing `~/.config` is a skipped conflict.
- Gatekeeper behaviour of the unsigned binary if it were downloaded through a browser rather than `curl`.
- Whether the directory-delete bug (PR #30) triggers in practice on arm64. The PR reports a reproduction.

These belong in the trial VM ([Set up the trial VM](https://github.com/iamivanhx/macos-setup/issues/12)), never on the target Mac.
