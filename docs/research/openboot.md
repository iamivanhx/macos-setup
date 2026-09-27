# Is OpenBoot safe to depend on?

Research for the ticket [Is OpenBoot safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/7) on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Written 2026-09-27 by reading source, docs, the install script's text, releases, issues and pull requests. OpenBoot was not installed or run.

Vocabulary (Bootstrap, Fresh Mac, Package, Dotfile, macOS setting) is as in the map's Notes and `CONTEXT.md`.

## Sources read

| Source | Version read |
|---|---|
| CLI source, [openbootdotdev/openboot][ob] | `main` at `259b119109d3c45fc46b9e8ab3a3bed08c6580a1` (2026-09-24), which is v1.0.2 plus CI and dependency bumps |
| Website and API source, [openbootdotdev/openboot.dev][site] | `main` at `259a0626a92e1a4ad291c180073fefe118513522` (2026-07-18) |
| Homebrew formula, [openbootdotdev/homebrew-tap `Formula/openboot.rb`][tap] | version 1.0.2 |
| Served install script, `https://openboot.dev/install.sh` | fetched as text 2026-09-27 06:31 UTC, not run |
| Repository metadata, releases, contributors, issues, PRs | GitHub API, 2026-09-27 |
| Author's article, [Mac Setup Automation Guide 2026][article] | read 2026-09-27; checked against the code below |

Code links below are pinned to the CLI commit above unless marked otherwise.

## Verdict

**Safe to depend on only in a narrow way: as a one-shot runner of a plain JSON file kept in this repo. It is safe in that mode because leaving is cheap, not because the project is mature.**

- **What makes the narrow mode acceptable.** A Bootstrap can run from a local JSON file with `openboot install --from <file> --silent`. It needs no account and does not fetch its configuration from OpenBoot's servers. The file maps one-to-one onto standard commands (`brew install`, `brew tap`, `npm install -g`, `defaults write`, `git clone` plus `stow`), so leaving means translating one file into a Brewfile and a short script.
- **What counts against it.**
  - One person writes almost all of it: 595 of 600 commits and 143 of 150 PRs.
  - It changes fast: 154 releases between 2026-02-01 and 2026-09-23, with a breaking v1.0 on 2026-08-02 that removed eleven commands.
  - Every `install` run contacts `openboot.dev` for a package catalogue. The contact is harmless: it sends no personal data, and failures fall back silently. It cannot be switched off with a documented setting.
  - The file mode is a side path of a product built around an interactive picker, a web dashboard and URL sharing. That path has gaps (below).
  - Dotfiles cannot live in this repo cleanly: OpenBoot clones a whole git repository into `~/.dotfiles`.

## Answers to the ticket's questions

### 1. Where the configuration lives, and whether a Bootstrap can run from a file in this repo without an account or their servers

**Answer:** it can live in this repo as a plain JSON file. A Bootstrap runs from it with no account and without fetching configuration from openboot.dev. The run still makes two small contacts: a catalogue fetch from openboot.dev and a version check against GitHub (question 5).

- There are three configuration sources:
  - a cloud config on openboot.dev (`user/slug` or an alias);
  - a built-in preset;
  - a local file (`--from <file>`, or any argument that starts with `./` or `/` or ends in `.json`).

  `--from` takes precedence over every other source ([`internal/cli/install.go` L274-L323][install-go]).
- The local file is read with `os.ReadFile`, so it must be a local path, not a URL. It is parsed as a "RemoteConfig" JSON object, or as a snapshot if it has `captured_at` ([`internal/config/remote.go` L123-L153][remote-go]).
- The file schema is the `RemoteConfig` struct ([`internal/config/types.go` L136-L171][types-go]):
  - `packages`, `casks`, `taps`, `npm`
  - `dotfiles_repo`
  - `post_install` (array of shell lines)
  - `shell` (`oh_my_zsh`, `theme`, `plugins`)
  - `macos_prefs` (`domain`, `key`, `type`, `value`, `desc`, `host`)
  - `dock_apps`
  - `login_items`
- An account is only needed to publish configs or to install private cloud configs ([openboot.dev `src/docs/faq.md` "Can I use it without an account?"][faq]). The local-file path never reads the auth token.
- **Docs drift.** The website's config docs describe a different, dashboard-side schema (`base_preset`, `custom_script`, a typed `packages` array, `snapshot.macos_prefs`) and say nothing about a local-file format ([`src/docs/config-options.md`][config-options]). The CLI does accept both shapes: `UnmarshalRemoteConfigFlexible` handles typed package arrays and nested `snapshot.macos_prefs` ([`remote.go` L273-L405][remote-go]). The authoritative local schema is therefore the Go struct, not the docs.

### 2. Whether it can run without the interactive picker

**Answer:** yes, with `--silent`, or when there is no terminal.

- On a terminal without `--silent`, a file source opens the full-screen config wizard ([`install.go` L137-L161][install-go]; `wizardMode` at [L186-L188][install-go]).
- With `--silent`, `planFromRemoteConfig` builds the whole plan from the file with no prompts ([`internal/installer/plan.go` L74-L137][plan-go]).
- `post_install` lines are skipped in silent mode unless `--allow-post-install` is passed ([`internal/installer/step_system.go` L85-L95][step-system]).
- The README's `--silent` example requires `OPENBOOT_GIT_NAME` and `OPENBOOT_GIT_EMAIL`. That rule only applies on the preset or interactive path ([`plan.go` L176-L202][plan-go]).
- Gaps on the file path, found by reading the code (not run):
  - **Git identity is never set from a file.** `RemoteConfig` has no git fields, and `planFromRemoteConfig` leaves the name empty, so the git step prints "Git identity not available in snapshot, skipping" ([`step_git.go` L10-L22][step-git]). Git identity would have to come from a Dotfile or elsewhere.
  - **`--shell`, `--macos` and `--dotfiles skip` are ignored for file and cloud sources.** Only the preset and interactive planners read them ([`plan.go` L223-L280 vs L74-L137][plan-go]). The file itself must leave out what should not run. `--packages-only` is honoured ([`installer.go` L185-L203][installer-go]). The documented `--dotfiles clone|link` modes and `--post-install skip` are not read anywhere in the CLI.
  - **A later bare `openboot install` may try to reach openboot.dev.** After a successful non-dry-run install from a file, `saveSyncSourceIfRemote` saves a "sync source" with an empty slug, because it only checks that a config was loaded ([`internal/cli/helpers.go` L41-L54][helpers-go]). A later bare `openboot install` (no arguments) would try to resume from it and fetch from openboot.dev ([`install.go` L291-L293][install-go]). Re-running with `--from` avoids this, because `--from` takes precedence. This is inferred from the code; no test covers the file case.

### 3. What its Dotfile support covers, and whether Dotfiles can live in this repo

**Answer:** it supports one git repository, cloned whole into `~/.dotfiles` and linked into the home directory. Dotfiles in a subdirectory of this repo are not supported directly.

- `dotfiles_repo` must be an `https://` URL of a git repository ([`validate.go` L27-L64][validate-go]).
- It is cloned to the fixed path `~/.dotfiles` ([`internal/dotfiles/dotfiles.go` L18, L48-L86][dotfiles-go]).
- Linking has three modes, tried in this order ([`dotfiles.go` L231-L252][dotfiles-go]):
  1. `make install`, if the repository has a `Makefile` with an `install:` target;
  2. GNU Stow on each top-level directory that contains dot-entries (Stow is installed with brew if missing);
  3. otherwise, direct symlinks of top-level dot-entries into `~`.

  Files that would be overwritten are backed up to `*.openboot.bak`.
- The only way to keep Dotfiles "in this repo" would be to point `dotfiles_repo` at this whole public repository. OpenBoot would then clone a second copy of it into `~/.dotfiles`, and the repo's top level would have to be shaped for its linker, or carry a `Makefile` `install:` target that does the linking. That means writing the linking logic yourself anyway.
- On a second run with the same URL, it runs `git fetch` and `git reset --hard origin/<branch>`. If `~/.dotfiles` has local changes, it asks on a terminal and skips when there is none. If the URL changed, it renames the old directory to `~/.dotfiles.openboot.bak` and clones again ([`dotfiles.go` L88-L165][dotfiles-go]).
- The author's article calls the Dotfile support "basic compared to chezmoi" ([article][article]). The code agrees: no templating, no secrets handling, no per-file mapping.

### 4. Whether macOS settings are limited to a fixed list, and how a setting outside it is applied

**Answer:** not limited to a list when run from a file. Any scalar `defaults write` is accepted. Anything that is not a scalar `defaults write` has to go through `post_install` or a separate script.

- **The "fixed list".** `DefaultCategories` holds 64 settings in 10 categories ([`internal/macos/categories.go`][categories-go]). They apply only on the preset and interactive paths (`planMacOSDecision`, [`plan.go` L275-L280][plan-go]). The openboot.dev dashboard exposes the same list as a "whitelist" ([`src/docs/config-options.md` "macOS Preferences Whitelist"][config-options]). The article's figure of "23 whitelisted developer settings" is out of date.
- **From a file.** `macos_prefs` entries go straight to `defaults [-currentHost] write <domain> <key> -<type> <value>` ([`internal/macos/macos.go` L88-L123][macos-go]). The only checks are character patterns ([`validate.go` L117-L140][validate-go]):
  - the type is `string`, `int`, `bool` or `float` (or empty, and then it is inferred);
  - the domain matches `[a-zA-Z0-9._-]+`;
  - the key matches `[a-zA-Z0-9 ._-]+`.

  The threat model states there is no domain or key allowlist ([`THREAT_MODEL.md` T7][threat]).
- **What it cannot express:**
  - `-array`, `-dict` and `-data` values, except the Dock's own `dock_apps` handling ([`macos/dock.go`][dock-go]);
  - domains given as file paths;
  - `sudo`: no command runs as root ([`THREAT_MODEL.md` §1][threat]);
  - `pmset`, `systemsetup`, `scutil`, `PlistBuddy`, configuration profiles.

  Login items are set through `osascript` ([`macos/loginitems.go`][loginitems-go]).
- **A setting outside that model** goes in `post_install`. Its lines are joined and run with `/bin/zsh -c` in `$HOME`: on a terminal after a confirmation prompt, or in silent mode only with `--allow-post-install` ([`step_system.go` L85-L136][step-system]). The alternative is a separate script.
- **Fixed side effects.** Whenever any `macos_prefs` are applied, OpenBoot also creates `~/Screenshots` and runs `killall` on Finder, Dock, SystemUIServer and ControlCenter ([`step_system.go` L45-L61][step-system]; [`macos.go` L133-L162][macos-go]).

### 5. What its install script does on a Fresh Mac, and what it sends to its servers

**Answer:** the install script is short. It installs Xcode Command Line Tools and Homebrew if missing, installs OpenBoot through Homebrew, and hands over to `openboot install`. A file-based run sends no personal data to openboot.dev: one catalogue fetch carrying only the CLI version header.

- **Where the script comes from.** `https://openboot.dev/install.sh` answers with HTTP 302 to `https://raw.githubusercontent.com/openbootdotdev/openboot/main/scripts/install.sh`. The served bytes were identical to [`scripts/install.sh`][installsh] (SHA-256 `fba54ecb…0654694`). Because it tracks `main`, it can change at any time without a release.
- **What the script does, in order** ([`scripts/install.sh`][installsh]):
  1. Re-attaches stdin to `/dev/tty`.
  2. If Xcode Command Line Tools are missing, runs `xcode-select --install` and waits in a loop until they appear.
  3. If brew is not on the `PATH`, looks for it in `/opt/homebrew` or `/usr/local`. If it is not there either, runs Homebrew's official installer from `raw.githubusercontent.com/Homebrew/install/HEAD` and appends `eval "$(/opt/homebrew/bin/brew shellenv)"` to `~/.zprofile`.
  4. Runs `brew install openbootdotdev/tap/openboot`, or `brew update` plus `brew upgrade` or `reinstall` if it is already installed.
  5. Prints the version and `exec`s `openboot install "$@"`.

  It does not call `sudo` itself.
- **The Homebrew formula** downloads the prebuilt `openboot-darwin-arm64` binary from the v1.0.2 GitHub release, pinned by SHA-256 ([tap formula][tap]). The binary is not built from source on the Mac.
- **Network contacts of `openboot install --from <file> --silent`**, read from the code:

  | Destination | What is sent | When | Can it be avoided? |
  |---|---|---|---|
  | `GET https://openboot.dev/api/packages` | `X-OpenBoot-Version` header, Go's default User-Agent, the client IP (seen by Cloudflare). No auth token, no package list. | Every `install` run whose 24-hour cache in `~/.openboot/packages-cache.json` is missing or stale. 8-second timeout; failure silently falls back to the embedded catalogue. Sources: [`root.go` L54-L64][root-go], [`packages_remote.go` L53-L114][packages-remote], [`remote.go` L47-L53][remote-go] | No documented switch. `OPENBOOT_API_URL` only accepts https or localhost ([`remote.go` L63-L71][remote-go]). The server side returns a static list and logs nothing ([openboot.dev `src/routes/api/packages/+server.ts`][site-packages]). |
  | `GET https://api.github.com/repos/openbootdotdev/openboot/releases/latest` | Version check. Sends `GITHUB_TOKEN` as a bearer token if that variable is set. | Every `install` run, cached for 24 hours in `~/.openboot/update_state.json`. The default mode only prints a notice; it self-upgrades only if `~/.openboot/config.json` sets `"autoupdate": "true"` ([`updater.go` L111-L182, L805-L830][updater-go]). | Yes: `OPENBOOT_DISABLE_AUTOUPDATE=1`, or `"autoupdate": "false"`. |
  | TCP connect to `github.com:443` and `raw.githubusercontent.com:443`, then `brew update` | Reachability check before installing packages; failure aborts the Packages step ([`brew.go` L222-L325][brew-go]). | When there are packages to install. | No, and Homebrew needs the network anyway. |
  | GitHub (Oh My Zsh installer pinned by commit and SHA-256; external zsh plugin repos; the Dotfiles repo) | Standard git and HTTPS fetches ([`shell.go` L23-L37][shell-go]) | Only if the file has a `shell` block or `dotfiles_repo`. | Yes, by leaving those fields out. |

- **Cloud and publishing paths only** (not used by a file Bootstrap):
  - Fetching a cloud config sends the bearer token if you are logged in, and the server adds one to that config's `install_count` ([openboot.dev `src/lib/server/alias.ts`, `db/configs.ts` L630-L645][site-configs]).
  - `snapshot --publish` uploads the snapshot.

  The FAQ describes install counts as "not telemetry" ([faq][faq]).
- **Logs** are written only to local files in `~/.openboot/logs` ([`internal/logging/logging.go`][logging-go]). A search of all non-test Go code for URLs found no other destinations.

### 6. How it behaves on failure and on a second run

**On failure** ([`installer.go` L118-L159][installer-go]):

- Steps run in this order: Git identity, Packages, npm globals, Shell, Dotfiles, macOS preferences, Post-install.
- A git failure stops the run. Any other failed step is reported, and the run carries on to the next step.
- The errors are joined at the end and the process exits 1 ([`cmd/openboot/main.go`][main-go]).
- Ctrl-C stops between steps; partial changes are logged under `~/.openboot/logs`.
- Packages:
  - Formulae and casks install one at a time, with one retry pass for failures ([`brew_install.go` L91-L186, L280-L307][brew-install]).
  - The article's "4x in parallel" no longer holds: commit `d48b168` (2026-04-18) replaced the "fake-parallel installer" with a serial loop. [`THREAT_MODEL.md`][threat]'s "capped at 4 workers" is stale too.
  - npm installs get three attempts ([`step_packages.go`][step-packages]).
- A failing `defaults write` is collected, and the other settings still apply ([`macos.go` L88-L123][macos-go]).

**On a second run** (inferred from the code, not run):

- Packages already installed are skipped, checked against `brew list` and a state file `~/.openboot/install_state.json` that is reconciled with the system ([`step_packages.go`][step-packages]; [`brew_install.go` L103-L139][brew-install]).
- `defaults write` runs again every time, and Finder and the Dock are restarted again.
- Oh My Zsh is not reinstalled, but its theme and plugins block in `.zshrc` is rewritten in place ([`shell.go` L200-L263][shell-go]).
- Dotfiles are fetched and hard-reset (question 3).
- `post_install` runs again, so its lines must be safe to repeat.
- `install` never uninstalls anything ([`CHANGELOG.md` v1.0.0 "Philosophy"][changelog]).

### 7. What still works if OpenBoot or its service is abandoned tomorrow

- **If openboot.dev goes down:**
  - A file Bootstrap run through `brew install openbootdotdev/tap/openboot` keeps working. The catalogue fetch falls back after up to 8 seconds, and the tap and binaries are on GitHub.
  - The `curl openboot.dev/install.sh | bash` one-liner breaks. Its target, the GitHub raw URL, still works.
  - Cloud configs, aliases, `login`, `snapshot --publish` and the wizard's online search break.
- **If the GitHub organisation or repository disappears:**
  - Installed binaries keep working.
  - A new Fresh Mac cannot install OpenBoot from the tap. The source is MIT-licensed Go ([`LICENSE`][license]) and builds with `go build ./cmd/openboot`, so a fork or a vendored binary would restore it.
  - The Oh My Zsh installer is pinned to an upstream commit, which is not OpenBoot's.
- **If it is left unmaintained:** it slowly drifts from macOS and Homebrew. Examples are menu-bar keys that change per macOS release ([`categories.go` L123-L133][categories-go]) and the pinned Oh My Zsh hash.
- **Exit cost, concretely.** The whole configuration is one JSON file whose fields map one-to-one onto standard commands:

  | JSON field | Standard equivalent |
  |---|---|
  | `packages`, `casks`, `taps` | Brewfile `brew` / `cask` / `tap` lines |
  | `npm` | `npm install -g` |
  | each `macos_prefs` entry | one `defaults [-currentHost] write` line |
  | `dock_apps` | `dockutil`, or `defaults write com.apple.dock persistent-apps` |
  | `login_items` | one `osascript` call |
  | `dotfiles_repo` | `git clone` plus `stow` |
  | `shell` | the Oh My Zsh installer plus a `.zshrc` |
  | `post_install` | already shell |

  OpenBoot keeps no state a later Bootstrap needs; `~/.openboot` holds only caches, logs and markers. Leaving means writing roughly a Brewfile and a short glue script: a small, one-time job.

## Project health (re-verified charting facts)

| Fact at charting | Re-verified 2026-09-27 | Source |
|---|---|---|
| Written in Go | Yes (`go.mod`; Go toolchain 1.26.8 bump in open PR #166) | [repo][ob] |
| Created 2026-02-01 | Yes, `2026-02-01T09:03:10Z` | GitHub API |
| Latest release v1.0.2 on 2026-09-23 | Yes, published `2026-09-23T16:15:57Z`. There are **154 releases** in total; v1.0.0 came out 2026-08-02, a few hours after v0.66.6 | GitHub releases API |
| Three contributors, 595 of 600 commits from the author | Yes: `fullstackjam` 595, `jerryjrxie` 4, `Gingiris` 1. PRs: 143 of 150 by the author. The five open PRs are the author's own dependency and CI work from 2026-09-23. No open issues | GitHub contributors / PR / issue APIs |
| 274 stars | Yes, 274 stars, 13 forks | GitHub API |
| MIT licence | The CLI is MIT. The website and API repo, `openbootdotdev/openboot.dev`, has **no licence file** | GitHub API; repo tree |
| Built around a picker, dashboard, URL sharing | Yes. The README leads with the TUI, the dashboard and share URLs ([README][readme]) | [README][readme] |
| Article: not offline | True in practice: the Packages step aborts if it cannot reach github.com. OpenBoot itself only needs openboot.dev optionally | [`brew.go` L300-L325][brew-go] |
| Article: Dotfile support "basic" | Fair (question 3) | |
| Article: 23 macOS settings in a fixed list | **Stale.** The default list has 64 entries, and file configs accept any scalar `defaults write` (question 4) | [`categories.go`][categories-go] |

Other observations on maturity:

- **Issues.** Issues are few and were answered quickly by the author. Two early "clean OS install" reports ([#5](https://github.com/openbootdotdev/openboot/issues/5), [#9](https://github.com/openbootdotdev/openboot/issues/9), March 2026) were broken `curl | bash` flows on a real Fresh Mac. They were fixed within days, but it shows the Fresh-Mac path has broken before.
- **Breaking changes.** v1.0 removed `pull`, `push`, `diff`, `clean`, `log`, `restore`, `init`, `setup-agent`, `list`, `edit` and `delete` with no aliases. Since then, breaking changes require a major version bump and a migration entry ([`CHANGELOG.md`][changelog]).
- **Business model.** The FAQ says team features "may have paid tiers later" ([faq][faq]).

## What could not be verified without running the tool

- Actual behaviour of `openboot install --from <file> --silent` on a Fresh Mac: sudo prompts for casks, the Xcode Command Line Tools dialog, and exit codes. Everything above is read from code, not observed.
- The real network traffic. It was established by reading every URL in non-test Go code, not by capturing packets.
- Whether the empty sync source saved after a file install really makes a later bare `openboot install` call openboot.dev.
- Whether the released binaries match the source at the tagged commit. The builds were not reproduced.
- What openboot.dev and Cloudflare log per request. The FAQ's "no IP addresses" claim covers install counts only and cannot be checked from outside. The deployed site may also differ from the repo's `main` (HEAD 2026-07-18, last push 2026-09-09).
- Whether each of the 64 default settings still takes effect on macOS 27. That belongs to [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8).

[ob]: https://github.com/openbootdotdev/openboot/tree/259b119109d3c45fc46b9e8ab3a3bed08c6580a1
[readme]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/README.md
[license]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/LICENSE
[changelog]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/CHANGELOG.md
[threat]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/THREAT_MODEL.md
[installsh]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/scripts/install.sh
[main-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/cmd/openboot/main.go
[root-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/cli/root.go
[install-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/cli/install.go
[helpers-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/cli/helpers.go
[remote-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/remote.go
[packages-remote]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/packages_remote.go
[types-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/types.go
[validate-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/validate.go
[installer-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/installer/installer.go
[plan-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/installer/plan.go
[step-git]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/installer/step_git.go
[step-system]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/installer/step_system.go
[step-packages]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/installer/step_packages.go
[brew-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/brew/brew.go
[brew-install]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/brew/brew_install.go
[dotfiles-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/dotfiles/dotfiles.go
[macos-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/macos.go
[categories-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/categories.go
[dock-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/dock.go
[loginitems-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/loginitems.go
[shell-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/shell/shell.go
[updater-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/updater/updater.go
[logging-go]: https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/logging/logging.go
[site]: https://github.com/openbootdotdev/openboot.dev/tree/259a0626a92e1a4ad291c180073fefe118513522
[faq]: https://github.com/openbootdotdev/openboot.dev/blob/259a0626a92e1a4ad291c180073fefe118513522/src/docs/faq.md
[config-options]: https://github.com/openbootdotdev/openboot.dev/blob/259a0626a92e1a4ad291c180073fefe118513522/src/docs/config-options.md
[site-packages]: https://github.com/openbootdotdev/openboot.dev/blob/259a0626a92e1a4ad291c180073fefe118513522/src/routes/api/packages/%2Bserver.ts
[site-configs]: https://github.com/openbootdotdev/openboot.dev/blob/259a0626a92e1a4ad291c180073fefe118513522/src/lib/server/db/configs.ts
[tap]: https://github.com/openbootdotdev/homebrew-tap/blob/main/Formula/openboot.rb
[article]: https://blog.fullstackjam.com/en/2026/mac-setup-automation-guide-2026/
