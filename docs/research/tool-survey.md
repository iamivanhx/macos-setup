# Tool survey: what can Bootstrap a Fresh Mac, and how do the options compare?

Research note for the ticket [Which tools can set up a fresh Mac, and how do they compare?](https://github.com/iamivanhx/macos-setup/issues/5), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Written 2026-09-27. Vocabulary (Bootstrap, Fresh Mac, Package, Dotfile, macOS setting) is the map's.

Repository figures (created, last push, stars, licence, latest release, commits on the default branch since 2025-09-27) come from the GitHub API, queried on 2026-09-27. Documentation is quoted from each project's own docs or repository. Nothing here was run on a Mac. Everything is read from sources, and the trial VM ([Set up the trial VM](https://github.com/iamivanhx/macos-setup/issues/12)) is where the claims get tested.

## Answer in brief

Three approaches are worth a hands-on trial:

1. **Plain pieces with thin glue.** A `Brewfile` run by `brew bundle`, Dotfiles kept as plain files in this repo and linked by a short loop (or GNU stow), a file of `defaults write` lines, and one `bootstrap.sh` to run them. Every piece is mature and standard. If the glue is abandoned, the files still work by hand. Homebrew states support for macOS 27 on Apple Silicon. The cost is that the owner maintains the glue.
2. **mise bootstrap.** One `mise.toml` declares Packages (Homebrew formulae and casks, App Store apps), Dotfiles, macOS settings (including Dock apps), language tools and npm globals, with `--dry-run` and `status`. It covers more of the Bootstrap in one file than any other candidate. The catch: the feature first shipped on 2026-06-12, so it is about 3.5 months old, and most of its changes are by one author. The trial has to test whether it is stable.
3. **chezmoi over a Brewfile.** chezmoi handles Dotfiles and hosts the package and settings scripts, re-running each script only when its input changes. It is a single binary with built-in git, so it needs nothing on a Fresh Mac, and it is mature. The cost: Dotfiles are stored under chezmoi's renamed source names (`dot_zshrc`), and it is a second tool with its own concepts.

hola and OpenBoot are not shortlisted at survey depth. Their deep-dive tickets can still change that. Every other candidate is dropped, with reasons, in [Rejected candidates](#rejected-candidates).

## What a Bootstrap has to cover

The Ansible version at `4b8f39e` is the benchmark, but the standing preferences say parity is not a goal. It covers:

- **Prerequisites:** Xcode Command Line Tools, Homebrew, git, Ansible, and the hostname (`bootstrap.sh`).
- **Packages:** 16 formulae and 6 casks, a Nerd Font cask, full Xcode via `mas`, pnpm, Node LTS via pnpm, npm globals via pnpm, and Claude Code via its own installer (`group_vars/all.yml`, `roles/*`).
- **Dotfiles:** Starship config and a line in `~/.zshrc` (`roles/terminal`).
- **macOS settings:** 27 `defaults` tasks for Finder, Dock, keyboard, input, screenshots, Xcode and Time Machine (`roles/macos_defaults`).
- **Identity and access:** git name and email, an ed25519 SSH key with Keychain, `gh` auth and key upload, with human-in-the-loop pauses (`roles/git_setup`).
- **Verify:** a pass/fail report (`roles/verify`).

## Comparison

"Glue" means what is left for the owner to script around the tool. "Exit" means what still works if the tool is abandoned.

| Candidate | Packages | Dotfiles | macOS settings | Config as plain files in repo | Needs on a Fresh Mac | Maturity | Exit cost | Apple Silicon / macOS 27 |
|---|---|---|---|---|---|---|---|---|
| **brew bundle** (Brewfile) | Native: formulae, casks, taps, `mas`, VS Code, npm, uv, go, cargo [B1] | None [B1] | None [B1] | Yes, `Brewfile` | Homebrew. Its installer installs the CLT itself [B3] | Homebrew/brew since 2016; 7.0.6 on 2026-09-21; 6,257 commits in 12 months. bundle was merged into core [B4] | Near zero: a Brewfile is Homebrew's own format | macOS 15 to 27 on Apple Silicon "best and supported" [B2] |
| **Plain script** (donnybrilliant-style) | Glue calls brew | Glue | Glue (`defaults write`) | Yes | bash and curl (built in) | n/a (owner-owned) | Zero | Whatever the called tools support |
| **mise bootstrap** | Native `brew:`/`brew-cask:` without Homebrew installed, `mas:` (needs the mas CLI), `macos-app:` [M2][M3][M4] | Native: symlink, copy, template [M5] | Native: friendly Dock/Finder/keyboard/trackpad keys, raw `defaults`, Dock apps, current-host [M6] | Yes, one `mise.toml` plus plain source files | `curl https://mise.run \| sh` [M7]. `[bootstrap.repos]` needs git [M8] | mise since 2023-01, 34k stars, 639 releases. bootstrap first released 2026-06-12 [M9]; 173 of 204 bootstrap changelog entries are by jdx | Low to moderate: declarations map line-for-line onto Brewfile lines, file paths and `defaults` keys; mise-poured kegs look like Homebrew's own [M3] | brew manager: macOS arm64 only [M3]. macOS 27 not stated |
| **mise `[tools]`** (runtimes only) | Language runtimes and CLIs; npm/pipx/cargo/go backends; no Homebrew backend [M10] | No | No | Yes | as above | as above | Low | macOS arm64 binaries [M7] |
| **chezmoi** | Via `run_onchange_` script calling `brew bundle`, per its own macOS guide [C1] | Native | Via scripts [C2] | Yes, but under source names: `dot_zshrc` becomes `~/.zshrc` [C3]. `.chezmoiroot` can confine it to a subdirectory [C4] | Nothing: single binary, built-in git when `git` is absent [C5][C6] | Since 2018; 258 releases; v2.72.2 on 2026-09-13; twpayne is credited with 5,181 contributions against 5,877 commits on the default branch | Low: default mode writes real files, not symlinks [C6], so the home directory keeps working. Leaving means renaming `dot_*` sources back | darwin_arm64 builds [C5]. macOS 27 not stated |
| **dotbot** | Only via `shell` or plugin (dotbot-brew) [D1] | Native (symlinks, YAML) | Only via `shell` | Yes, `install.conf.yaml` plus a submodule | python3 (its launcher looks for python3/python) [D2] | Since 2014; v1.24.0 on 2025-11-29; 27 commits in 12 months | Low | Not stated |
| **GNU stow** | No | Native (symlink farm) | No | Yes, plain files | Perl; Homebrew's formula uses macOS's Perl [S2] | 2.4.1 released 2024-09-08, the latest [S1] | Near zero | Not stated |
| **mackup** | No | App settings backup/restore via a sync folder | Partial, through app plists | Files live in a storage folder (Dropbox, iCloud, Git…) [K1] | Python (Homebrew formula depends on python@3.14) | Since 2013; 0.11.2 on 2026-09-09 | Low | Link mode "will BREAK YOUR PREFERENCES" on macOS 14 and later [K1] |
| **hola** (survey depth; see [Is hola safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/6)) | Via real Homebrew from `~/.Brewfile` [H1] | Symlinks from a dotfiles dir [H1] | Hola-specific Ruby DSL (`macos_defaults`, `macos_dock`) in `provision.rb` [H1] | Brewfile + mise.toml + dotfiles plain; settings in hola DSL | Single binary [H1] | Created 2025-11-23; v0.4.0; 25 stars; 1 contributor (242/242 commits) | Brewfile, mise.toml and dotfiles survive; the settings DSL does not | arm64 binary [H1]. macOS 27 not stated |
| **OpenBoot** (survey depth; see [Is OpenBoot safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/7)) | Native (brew, casks, taps, npm) [O1][O2] | Clones a separate dotfiles repo and links with GNU stow [O1] | JSON `macos_prefs` list, Dock apps, login items [O2] | JSON config or snapshot (`--from FILE`), or a URL on openboot.dev [O1] | Installer "installs Homebrew, Xcode CLI tools" [O1] | Created 2026-02-01; v1.0.2; 274 stars; 3 contributors, 595 of 600 commits by fullstackjam. v1.0 removed eight commands [O1] | Moderate: the config is OpenBoot's JSON schema | Not stated |

Other candidates surveyed are in [Rejected candidates](#rejected-candidates).

## The shortlist

### 1. Plain pieces with thin glue (Brewfile, plain Dotfiles, a settings file, `bootstrap.sh`)

**Why trial it.** It has the lowest dependency risk and the cheapest exit of anything surveyed:

- Homebrew is the one tool every approach uses anyway. It explicitly supports macOS 15 to 27 on Apple Silicon [B2], and its installer installs the Command Line Tools on its own [B3].
- `brew bundle` is declarative and safe to re-run: "Rather than specifying the `brew` commands you wish to run, you can specify the state you wish to reach" [B1]. It also covers npm and uv entries, which could absorb the Ansible `languages` and `npm_globals` roles [B1].
- Edit cost per concern is one line in one file: a Package is a `Brewfile` line, a macOS setting is one `defaults write` line, and a Dotfile is a file in the repo (plus one entry in a link list, unless the loop or stow links a whole directory).

**What it costs.** The owner writes and maintains the glue: ordering, re-run safety for the non-declarative parts, human-in-the-loop steps (App Store sign-in, `gh auth`), and any verify step.

**Against the reference design** ([donnybrilliant/install.sh](https://github.com/donnybrilliant/install.sh) at `f659cf8`, studied, not copied: it has no licence):

- *What the single config file buys.* One sourced bash file holds arrays for casks, formulae, npm packages, VS Code extensions, App Store IDs, system settings and Dock changes [R1]. That gives one place to edit every kind of thing, which is exactly "one change is one edit in one place".
- *What it costs on a second run.* The README admits error handling "only takes in to account a user who runs it for the first time" [R2]. Reading the script shows why:
  - It re-runs the Homebrew installer every time.
  - It appends the `brew shellenv` line to `~/.zprofile` without checking, so every run adds a duplicate.
  - It stops at interactive `read` prompts partway through.
  - It has no `set -e`, so failures pass silently.
  - It removes Dock items by their localised display names (Norwegian in the shipped config).
  - It runs each settings entry through `eval` as a free-form shell string [R3].
- *Lesson for approach 1.* Keep the single-place-per-concern property, but let the formats do the idempotency. Use a real `Brewfile` rather than loops over `brew install`, because `brew bundle` already converges. Make `defaults write` lines plain data, not `eval`'d strings. Keep the glue non-interactive except for named human-in-the-loop pauses, and make every append guarded.

### 2. mise bootstrap

**Why trial it.** Of every candidate, it comes closest to a Bootstrap in one plain file:

- **Packages.** `[bootstrap.packages]` covers `brew:`, `brew-cask:` and `mas:` [M2]. Applying "installs missing packages; it does not upgrade them on every run" [M2].
- **Dotfiles.** `[dotfiles]` supports symlink, copy and template modes [M5].
- **macOS settings.** `[bootstrap.macos.*]` has friendly Dock, Finder, keyboard and trackpad keys, raw `defaults`, current-host entries, targeted dictionary paths and an ordered Dock app list. Status is strictly typed, and "mise never deletes a default" [M6].
- **Tools.** `[tools]` covers Node, pnpm, uv and npm globals.
- **Custom steps.** Hooks and a `[tasks.bootstrap]` task cover imperative steps such as `gh auth` [M1].
- **Preview and status.** `mise bootstrap --dry-run`, `plan`, and `status --missing` come built in [M1].

Several Ansible-role equivalents (Finder path bar, key repeat, Dock autohide delay) are friendly keys already [M6].

**What the trial must test:**

- **Age.** Declarative system packages arrived in 2026.6.4 on 2026-06-12. Dotfiles and direct casks followed in 2026.6.6 on 2026-06-13 [M9]. That is about 3.5 months before this note, and there have been 204 bootstrap-related changelog entries since. Part names have already been renamed; the old names are kept as aliases [M1].
- **Maintainers.** 173 of those 204 entries are by jdx. mise as a whole has a broad contributor base, but this feature is largely one author's.
- **It is not Homebrew.** mise re-implements bottle pouring, relocation and code-signing itself, and "never shells out to `brew` for homebrew/core formulae" [M3]. A divergence from Homebrew's behaviour would be mise's bug, not Homebrew's.
- **Bootstrap order.** `mas` must be on `PATH` before the packages phase. "Declaring `mas` in `[tools]` alone does not make a fresh full bootstrap install it before the built-in packages phase" [M4]. The `brew` CLI itself is not installed unless declared.
- **Failure mode.** "Bootstrap is a sequence, not a transaction: if a later phase fails, earlier successful changes remain" [M1]. That is acceptable for a one-shot Bootstrap that is safe to re-run.
- **Exit cost.** Exit is cheap only if the declarations stay simple. They map directly onto Brewfile lines, file paths and `defaults` keys. mise also writes Homebrew-compatible install receipts, so `brew list`, `brew upgrade` and `brew uninstall` work on its kegs [M3].

### 3. chezmoi over a Brewfile

**Why trial it.**

- **Maturity.** It is the most mature dedicated Dotfile tool surveyed: 2018, 258 releases, v2.72.2 on 2026-09-13.
- **Nothing to install first.** `sh -c "$(curl -fsLS get.chezmoi.io)" -- init --apply <user>` works on a Fresh Mac with nothing installed. It is a single binary and uses built-in git when `git` is not on `PATH` [C5][C6].
- **Re-run safety comes built in.** A `run_onchange_` script runs "only if their content has changed since the last time they were run successfully" [C2]. Including a file's hash in a script comment makes the script re-run whenever that file changes [C2]. So a `Brewfile` or a settings list stays one edit in one place and re-applies on the next `chezmoi apply`. chezmoi's own macOS guide shows `brew bundle` run this way [C1].
- **Cheap exit.** The default mode writes regular files, not symlinks [C6], so the home directory keeps working if chezmoi is dropped.

**What it costs.**

- **Renamed Dotfiles.** Dotfiles in the repo carry source-state names (`dot_`, `private_`, `executable_`, `.tmpl`) [C3], so they are plain content under non-plain names.
- **Extra concepts.** Templates, encryption and multi-machine features are a learning cost for a one-Mac, one-profile, one-shot setup.
- **Glue still needed.** Packages and macOS settings are still owner-written scripts; chezmoi only hosts and sequences them.

## hola and OpenBoot at survey depth

Their deep-dive tickets own the full assessment. At survey depth neither makes the shortlist.

- **hola.** Its inputs are standard files: `~/.Brewfile`, `mise.toml` and a dotfiles directory [H1]. That makes most of it cheap to leave. But macOS settings and the Dock need its own Ruby DSL in `provision.rb` [H1], so that part is lock-in. It is 10 months old with a single contributor (all 242 commits) and 25 stars. Since June 2026, mise bootstrap covers the same ground (Brewfile-style Packages, mise tools, Dotfiles, typed `defaults`, Dock) inside one larger project. hola's advantage over approach 2 is that it drives real Homebrew rather than a re-implementation. [Is hola safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/6) may promote it.
- **OpenBoot.**
  - Its primary interface is a TUI, a web dashboard and shareable URLs [O1]. A local JSON config via `--from FILE` exists [O1], but its schema is OpenBoot's own [O2].
  - Dotfiles come from a *separate* repo linked with GNU stow [O1], against the preference that Dotfiles live in this repo.
  - It carries an Oh-My-Zsh shell opinion [O1][O2].
  - It is 8 months old. 595 of 600 commits are by one author, who also wrote the comparison article below. v1.0 removed eight commands [O1], a sign of recent interface churn.
  - [Is OpenBoot safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/7) owns the full assessment.

## Rejected candidates

| Candidate | Why dropped |
|---|---|
| dotbot | Dotfiles only. Packages and settings go through `shell` commands or plugins [D1]. It adds a Python dependency [D2] and a git submodule to do what a short link loop or stow does. |
| GNU stow | Dotfiles only, and its last release was 2024-09-08 [S1]. It stays as an optional **component** of approach 1 (the link step), not as an approach of its own. |
| mackup | It backs up app settings through a sync folder rather than bootstrapping from a repo. Its link mode breaks preferences on macOS 14 and later [K1]. Its copy mode overlaps with plain Dotfiles. |
| yadm | Dotfiles via a bare git repo over `$HOME`. Its bootstrap is just a user-written program run after clone [Y1]. The last commit on its default branch was 2025-03-23 (GitHub API). It adds nothing approach 1 or 3 lacks. |
| rcm (thoughtbot) | Dotfiles only. Latest release v1.3.6, 2022-12-30 (GitHub API). |
| dotter | Dotfiles only (Rust, templating). Dropped for the same reasons as dotbot. |
| comtrya | Its README says the maintainer will archive it for lack of new maintainers [CT1]. |
| pyinfra | Ansible-like Python infra-as-code with `brew` and `launchd` operations but no `mas` or `defaults` operation [P1]. It is a lateral move from Ansible, not a simplification. |
| Strap (MikeMcQuaid) | An opinionated bootstrap script that enables FileVault, the firewall and more, then delegates to a user `Brewfile` and a dotfiles `script/setup` [ST1]. Useful as a design precedent for approach 1, not a tool to adopt. |
| thoughtbot/laptop | An opinionated install script rather than a config-driven tool. |
| nix-darwin | Out of scope per the map. |
| Ansible | What the repo is leaving. |

Helpers that any approach may use as glue, not approaches in themselves:

- `mas` (v7.0.0, 2026-05-04). Supports macOS 13+. `get` needs an Apple Account signed in to the App Store, and install commands need root [MS1]. App Store sign-in therefore stays a manual step.
- `dockutil` (3.1.3, 2024-02-09).

## Verifying the OpenBoot author's article

[Mac Setup Automation Guide 2026](https://blog.fullstackjam.com/en/2026/mac-setup-automation-guide-2026/) is dated 2026-02-14 and signed "Jam". The OpenBoot repository's top contributor is `fullstackjam` (595 of 600 commits), which matches the ticket's note that the article is by OpenBoot's author. Its "Covers ~30% / ~70% / ~20% / ~90% / ~85%" column is the author's estimate with no method given. It is not reproduced as fact here. Checking the other claims against primary sources:

| Article claim | Finding |
|---|---|
| Brewfile does not handle shell config, macOS prefs or git identity | Consistent with Homebrew's docs, which list no dotfile or defaults support [B1]. |
| Brewfile "Works offline: Yes" | Not supported by any source. Homebrew installs bottles and casks by download [B1][M3]. Treat as wrong. |
| chezmoi: Packages "No", macOS prefs "No" | Misleading. It is not native, but chezmoi's own macOS guide runs `brew bundle` from a `run_onchange_` script [C1], and scripts can apply settings [C2]. |
| chezmoi: "Rollback: Yes" | Not found. The command reference has no rollback command. Undoing is a git operation in the source directory. |
| dotbot "won't install your apps or touch your macOS preferences" | True natively, but its README lists package-management plugins such as dotbot-brew and a `shell` directive [D1]. |
| mackup backs up "to iCloud or Dropbox" | Incomplete. Supported storages are Dropbox, Google Drive, iCloud and any synced folder such as Git [K1]. The article omits that link mode breaks preferences on macOS 14+ [K1]. |
| OpenBoot handles git identity, "Basic" dotfiles, and is MIT-licensed | Consistent with its README (asks for name and email; clones and stows a dotfiles repo) [O1] and the repo's MIT licence. |
| The table's tool set | It omits mise. mise bootstrap postdates the article: it first shipped 2026-06-12 [M9]. |

## Not verified

- **Nothing was executed.** Every behaviour above is read from docs or source. The trial VM has to confirm each approach end to end on macOS 27.
- **macOS 27 support** is explicitly stated only by Homebrew [B2]. For mise, chezmoi, dotbot, stow, hola and OpenBoot it is not stated. Whether macOS 27 still ships `/usr/bin/perl` (stow) and the `python3` stub (dotbot) was not checked.
- **mise bootstrap stability.** Its docs carry no experimental marker, but its correctness as a Homebrew re-implementation, its behaviour on a truly Fresh Mac, and whether `mise bootstrap --from <url>` needs system git (only `[bootstrap.repos]` states it does [M8]) were not tested.
- **The donnybrilliant second-run failures** come from reading the script at `f659cf8`, not from running it.
- **hola and OpenBoot** were covered from their READMEs and OpenBoot's config types only. Security, licence terms beyond the SPDX field, the openboot.dev service, and release practices belong to their deep-dive tickets.
- **Coverage percentages** in the OpenBoot author's article cannot be verified and are not used.

## Sources

Repository metadata for every candidate: GitHub REST and GraphQL APIs, queried 2026-09-27.

- [B1] Homebrew, "Homebrew Bundle, `brew bundle` and `Brewfile`": https://docs.brew.sh/Brew-Bundle-and-Brewfile
- [B2] Homebrew, `docs/Installation.md` ("macOS requirements" and footnotes 2 and 3) at `ce46735`: https://github.com/Homebrew/brew/blob/ce46735f348df8af3258e854c8a008d272f683b8/docs/Installation.md
- [B3] Homebrew installer `install.sh` at `0a396a4` (`should_install_command_line_tools`, and the step that installs the CLT): https://github.com/Homebrew/install/blob/0a396a4ee5b538f409de666af904fa0570b53949/install.sh
- [B4] Homebrew/homebrew-bundle README ("merged into Homebrew/brew"; repository archived): https://github.com/Homebrew/homebrew-bundle
- [M1] mise, `docs/bootstrap.md` at `dc2b6c3`: https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap.md
- [M2] mise, `docs/bootstrap/packages/index.md`: https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/packages/index.md
- [M3] mise, `docs/bootstrap/packages/brew.md` (no Homebrew required, supported platforms, coexistence): https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/packages/brew.md
- [M4] mise, `docs/bootstrap/packages/mas.md`: https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/packages/mas.md
- [M5] mise, `docs/dotfiles.md` (modes): https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/dotfiles.md
- [M6] mise, `docs/bootstrap/macos-defaults.md`: https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/macos-defaults.md
- [M7] mise, "Installing mise": https://mise.jdx.dev/installing-mise.html
- [M8] mise, `docs/bootstrap/repos.md` ("Git must be installed…"): https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/repos.md
- [M9] mise, `CHANGELOG.md`, entries for 2026.6.4 (2026-06-12, "declarative system packages … brew without brew", #10326) and 2026.6.6 (2026-06-13, "add dotfiles workflow" #10376, "support brew taps and casks directly" #10383): https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/CHANGELOG.md
- [M10] mise, "Backends": https://mise.jdx.dev/dev-tools/backends/
- [C1] chezmoi, "macOS" user guide (brew bundle via `run_onchange_before_…`): https://www.chezmoi.io/user-guide/machines/macos/
- [C2] chezmoi, "Use scripts to perform actions" (`run_`, `run_onchange_`, `run_once_`, re-run on another file's hash): https://www.chezmoi.io/user-guide/use-scripts-to-perform-actions/
- [C3] chezmoi, "Source state attributes": https://www.chezmoi.io/reference/source-state-attributes/
- [C4] chezmoi, `.chezmoiroot`: https://www.chezmoi.io/reference/special-files/chezmoiroot/
- [C5] chezmoi, "Install": https://www.chezmoi.io/install/
- [C6] chezmoi, configuration variables (`useBuiltinGit` default `auto`; `mode` default `file`): https://www.chezmoi.io/reference/configuration-file/variables/
- [D1] dotbot README: https://github.com/anishathalye/dotbot
- [D2] dotbot `bin/dotbot` launcher (finds `python3` or `python`): https://github.com/anishathalye/dotbot/blob/master/bin/dotbot
- [S1] GNU Stow `NEWS` and tag v2.4.1 (commit dated 2024-09-08; ftp.gnu.org tarball Last-Modified 2024-09-08): https://github.com/aspiers/stow/blob/master/NEWS, https://ftp.gnu.org/gnu/stow/
- [S2] Homebrew formula API, `stow` (`uses_from_macos: perl`): https://formulae.brew.sh/api/formula/stow.json
- [K1] mackup README at `9fc1540` (link-mode warning, supported storages): https://github.com/lra/mackup/blob/9fc154052c2b026e4e912ef73fb6d396e4993699/README.md
- [H1] hola README at `8b1cea3`: https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/README.md
- [O1] OpenBoot README at `259b119`: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/README.md
- [O2] OpenBoot `internal/config/types.go` (`RemoteConfig`, `RemoteMacOSPref`): https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/types.go
- [R1] donnybrilliant/install.sh `config` at `f659cf8`: https://github.com/donnybrilliant/install.sh/blob/f659cf869273f39bd839b0ca2ff0ba2a101ebade/config
- [R2] donnybrilliant/install.sh README, "To Do and Feature Ideas": https://github.com/donnybrilliant/install.sh/blob/f659cf869273f39bd839b0ca2ff0ba2a101ebade/README.md
- [R3] donnybrilliant/install.sh `install.sh` at `f659cf8` (Homebrew installer run unconditionally, `.zprofile` append, `read` prompts, `eval` of settings, Dock removal by localised name): https://github.com/donnybrilliant/install.sh/blob/f659cf869273f39bd839b0ca2ff0ba2a101ebade/install.sh
- [Y1] yadm, "Bootstrap": https://yadm.io/docs/bootstrap
- [CT1] comtrya README: https://github.com/comtrya/comtrya
- [P1] pyinfra, "Operations": https://docs.pyinfra.com/en/3.x/operations.html
- [ST1] Strap README: https://github.com/MikeMcQuaid/strap
- [MS1] mas README (supported OS, root privileges, Apple Account requirement): https://github.com/mas-cli/mas
- Article under verification: https://blog.fullstackjam.com/en/2026/mac-setup-automation-guide-2026/
