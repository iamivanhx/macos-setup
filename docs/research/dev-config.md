# Config practices for a development Mac

Research note for the ticket [Which config practices are recommended for a development Mac?](https://github.com/iamivanhx/macos-setup/issues/17), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Written 2026-09-27. Vocabulary (Bootstrap, Fresh Mac, Package, Dotfile, macOS setting) is the map's.

**Method.** Behaviour of each setting is taken from the owning project's documentation: git, zsh and OpenSSH from the manual pages installed on the target Mac (git 2.54.0 Apple Git-157, OpenSSH_10.3p1, the system zsh), GitHub, 1Password, Homebrew, Ghostty and VS Code from their own docs, and Apple's own guides. Security baselines come from the NIST macOS Security Compliance Project (mSCP) release 27.0, which publishes the CIS Benchmark mapping for macOS 27 openly. The CIS Benchmark itself is behind a registration wall and was not read directly. Blog posts and popular dotfiles repositories were used only as leads; where a practice rests on them alone, the table says **common practice**.

**The target Mac was read, never changed.** It runs macOS 27.0 (build 26A428) on arm64. What was read is listed in [State of the target Mac](#state-of-the-target-mac).

**macOS 27 caveat.** Apple's support pages cited here are served for "macOS 27 Golden Gate". The CIS mapping for macOS 27 is a **prerelease**: mSCP's release notes say "Added prerelease CIS Benchmark for macOS 27" [N1], and every CIS number below is the same as for macOS 26. Anything drawn from a source written for macOS 26 or earlier says so in the row.

**Legend.** *Rests on*: **Vendor** (the documentation of the tool that owns the setting), **Benchmark** (CIS via mSCP), **Common practice** (leads only). *Public*: whether the file can go in this public repo as written: **Yes**, **Yes, with care** (the note says what to watch), or **No**.

## Answer in brief

- **Shell.** PATH and environment go in `~/.zprofile`, after macOS's `path_helper` has run; interactive setup (options, history, completion, prompt, aliases) goes in `~/.zshrc`; `~/.zshenv` stays absent or holds only `ZDOTDIR`. Raise macOS's small history defaults. Call `compinit` once, after `brew shellenv`. Keep startup fast by not spawning programs per shell, and measure with `zprof`.
- **Git.** A small global config in `~/.config/git/config`, with a global ignore at `~/.config/git/ignore`, which is git's default location, so no setting is needed. It sets: `init.defaultBranch main`, `push.autoSetupRemote`, `fetch.prune`, `rebase.autoStash`/`autoSquash`/`updateRefs`, `rerere.enabled`, `merge.conflictStyle zdiff3`, `diff.algorithm histogram`, `diff.colorMoved`, `commit.verbose`, `branch.sort -committerdate`, and a `pull` policy. Git 2.54 already refuses to merge on a diverged `git pull` (`--ff-only` is the default), so `pull.rebase` is taste, not a fix.
- **Git identity and SSH.** Use an ed25519 key, with a passphrase held by the Keychain or by 1Password. Commit with GitHub's no-reply email so the identity can be public. Load GitHub's published host keys into `known_hosts`. Sign commits with SSH rather than GPG: git has supported it since 2.34 and it needs no extra software. The four options for [How are git identity and SSH access set up?](https://github.com/iamivanhx/macos-setup/issues/11) are compared in [a table below](#options-for-git-identity-and-ssh-access). The main finding: `gh auth login -p ssh` generates **and** uploads an ed25519 key by itself, and on this Mac the 1Password SSH agent is already configured and holds at least one key.
- **Secrets.** Nothing secret is committed. Secrets live in the macOS Keychain (gh's token, git's `osxkeychain` helper, SSH passphrases) or in 1Password (the SSH agent, `op://` references resolved by `op run`/`op inject`). Committed files may *refer* to secrets or *include* untracked local files; git silently skips a missing include, which was tested here. GitHub's push protection for users is on by default for public repos.
- **Security settings.** CIS Level 1 wants FileVault, Firewall with stealth mode, Gatekeeper, SIP, all four automatic-update switches, a screen saver at 15 minutes or less, a password within 5 seconds of it starting, and Remote Login off. This Mac already meets most of them. It has the **Firewall off** and a **300-second screen-lock delay**, which fail CIS 2.2.1, 2.2.2 and 2.11.2. The usual developer loosening is Privacy & Security > **Developer Tools** for the terminal, and Touch ID for `sudo` through Apple's own `/etc/pam.d/sudo_local` hook.
- **macOS settings developers change.** Show filename extensions and hidden files, path and status bars, faster key repeat, press-and-hold off, auto-correct and smart quotes and dashes off, and a screenshot folder. Apple documents the toggles, but choosing them rests on common practice. The owner picks them in [Which macOS settings does the setup apply?](https://github.com/iamivanhx/macos-setup/issues/14), and [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8) covers how each is applied.
- **Editor and terminal.** Keep a Dotfile when the app reads a plain text file and has no sync of its own; Ghostty (`~/.config/ghostty/config`) is the clear case. Leave config to the app's sync when it exists and covers extensions and state, as VS Code's Settings Sync does. Use one or the other per app, never both.
- **Layout.** One folder in the repo mirrors `$HOME`, or one folder per program (stow style). Either way, use the XDG path `~/.config/<tool>/` wherever the tool reads it. Only `~/.zshrc`/`~/.zprofile` (unless `ZDOTDIR` is set) and `~/.ssh/config` must stay at their fixed paths. Link or copy single files, not whole directories, where the app keeps state beside its config (gh).

## 1. Shell (zsh)

zsh reads, in order, `/etc/zshenv`, `~/.zshenv`, then for login shells `/etc/zprofile` and `~/.zprofile`, then for interactive shells `/etc/zshrc` and `~/.zshrc`, then for login shells `/etc/zlogin` and `~/.zlogin`. It reads them from `$ZDOTDIR`, or from `$HOME` if `ZDOTDIR` is unset [Z1]. On macOS, `/etc/zprofile` runs `/usr/libexec/path_helper` [M1]. That rebuilds PATH from `/etc/paths` and `/etc/paths.d/*` [M2] and moves any entries already on PATH **behind** the system directories. This was checked on the target Mac: `PATH=/my/first:/usr/bin path_helper -s` returned the system list first and `/my/first` last. Terminal apps start login shells on macOS: Ghostty launches the shell "via the login command" [G2]. So every new window reads `~/.zprofile` and then `~/.zshrc`.

| Practice | Carried by | Rests on | Public |
|---|---|---|---|
| Put PATH and exported environment in `~/.zprofile`, not `~/.zshenv`. Anything added to PATH in `~/.zshenv` is pushed behind the system paths by `path_helper` in `/etc/zprofile`. | `~/.zprofile` | Vendor: zsh startup order [Z1], `/etc/zprofile` and `path_helper(8)` on the Mac [M1][M2], plus the reordering test above | Yes |
| Load Homebrew with `eval "$(/opt/homebrew/bin/brew shellenv zsh)"` in `~/.zprofile`. Homebrew's installer tells zsh users on macOS to add exactly this line to `~/.zprofile` [H2]. On this Mac its output sets PATH, MANPATH and INFOPATH, and puts `/opt/homebrew/share/zsh/site-functions` at the front of `fpath`. The installer also creates `/etc/paths.d/homebrew` when it has sudo [H2]; that file exists here, but only puts `/opt/homebrew/bin` *after* the system directories. | `~/.zprofile` | Vendor [H1][H2] | Yes |
| Keep `~/.zshenv` absent, or use it only to set `ZDOTDIR`. It runs for every zsh, including scripts; zsh's manual asks that the global one "be kept as small as possible" [Z1]. | `~/.zshenv` | Vendor [Z1] (said of `/etc/zshenv`; applying it to `~/.zshenv` is common practice) | Yes |
| Deduplicate PATH with `typeset -U path PATH`: it keeps "only the first occurrence of each duplicated value" [Z4]. | `~/.zprofile` | Vendor [Z4] | Yes |
| Raise history limits. macOS's `/etc/zshrc` sets `HISTSIZE=2000` and `SAVEHIST=1000` [M1]. Set both much larger (tens of thousands; the exact figure is taste) in `~/.zshrc`. | `~/.zshrc` | Vendor for the defaults [M1][Z5]; the size is common practice | Yes |
| History options: `EXTENDED_HISTORY` (timestamps and durations), `INC_APPEND_HISTORY_TIME` or `SHARE_HISTORY` (write as you go; the second also reads other sessions' commands), `HIST_IGNORE_DUPS`, `HIST_IGNORE_SPACE` (a command typed with a leading space is not kept, which is useful for one-off secrets), `HIST_VERIFY`. | `~/.zshrc` (`setopt …`) | Vendor for behaviour [Z2]; the selection is common practice | Yes |
| Completion: `autoload -Uz compinit && compinit`, once, in `~/.zshrc`, after `brew shellenv` has put Homebrew's completions on `fpath`. If zsh reports insecure directories, run `compaudit` and fix only what it lists, never the whole Homebrew prefix. | `~/.zshrc` | Vendor [Z3][H3] | Yes |
| Startup speed: measure first with `zmodload zsh/zprof` at the top of `~/.zshrc` and `zprof` at the end [Z6]. `compinit -C` skips the check for new completion functions [Z3]. Avoid running programs on every shell start (`$(brew --prefix)`, `eval "$(tool init)"`, plugin managers), or cache their output. | `~/.zshrc` | Vendor for the tools [Z3][Z6]; the advice to avoid per-shell subprocesses is common practice | Yes |
| Machine-only or private additions go in an untracked file sourced if present, such as `[[ -r ~/.zshrc.local ]] && source ~/.zshrc.local`. | `~/.zshrc` + untracked `~/.zshrc.local` | Common practice | Yes (the hook); the local file is **No** |

## 2. Git

Git reads global config from `$XDG_CONFIG_HOME/git/config`, which defaults to `~/.config/git/config`, and from `~/.gitconfig` [GIT1]. The global ignore file defaults to `~/.config/git/ignore`, so `core.excludesFile` need not be set [GIT1]. The Command Line Tools' git on this Mac already ships a system-level file, `/Library/Developer/CommandLineTools/usr/share/git-core/gitconfig`, with `credential.helper = osxkeychain` and `init.defaultBranch = main`. A Homebrew git would not read that file, so set `init.defaultBranch` globally anyway. Upstream git still defaults to `master` and says it "will change to main when Git 3.0 is released" [GIT2].

The keys below are documented in the installed git-config manual [GIT1]; the git-pull manual covers `pull` [GIT3]. The strongest lead for which values to choose is a 2025 survey of what core git developers set [L1]. It is a blog post, so choosing these values is **common practice**; what each key does is **vendor** documentation.

| Setting | What it does (per git's docs) | Recommendation | Public |
|---|---|---|---|
| `init.defaultBranch = main` | Name of the first branch in `git init` | Set | Yes |
| `pull.rebase = true` (or leave unset) | On a diverged pull, rebase instead of merge. Git 2.54's default is `--ff-only`: a diverged `git pull` fails rather than creating a merge [GIT3] | Taste. Unset is safe; `true` suits a linear history | Yes |
| `push.autoSetupRemote = true` | "assume `--set-upstream` on default push when no upstream tracking exists" | Set. `push.default = simple` is already the default "since Git 2.0" | Yes |
| `push.followTags = true` | Push annotated tags that point at pushed commits | Optional | Yes |
| `fetch.prune = true` | Drop remote-tracking branches deleted on the remote | Set | Yes |
| `rebase.autoStash = true` | Stash and re-apply around a rebase ("use with care" if the re-apply conflicts) | Set | Yes |
| `rebase.autoSquash = true` | Apply `fixup!`/`squash!` commits in interactive rebase | Set | Yes |
| `rebase.updateRefs = true` | Move stacked branches along with a rebase | Set | Yes |
| `rerere.enabled = true` | Record conflict resolutions and replay them | Set | Yes |
| `merge.conflictStyle = zdiff3` | Show the base version in conflicts, trimmed of lines common to both sides | Set | Yes |
| `diff.algorithm = histogram` | A diff algorithm other than the default `myers` | Set | Yes |
| `diff.colorMoved = plain` (or `zebra`) | Colour moved lines differently | Set | Yes |
| `commit.verbose = true` | Show the diff in the commit message editor | Set | Yes |
| `branch.sort = -committerdate`, `tag.sort = version:refname`, `column.ui = auto` | Output ordering and layout | Optional (taste) | Yes |
| `help.autocorrect = prompt` | On a typo, "show the suggestion and prompt for confirmation" | Optional | Yes |
| `user.useConfigOnly = true` | Never guess name and email; ask the user to set them | Set if identity comes from a local include (see §3) | Yes |
| `core.fsmonitor = true`, `core.untrackedCache = true` | Built-in file-system monitor daemon ("available … on Windows and MacOS"), which speeds up `git status` in large trees | Per large repository, not global | Yes |
| `transfer.fsckObjects = true` | Abort fetch or receive on malformed objects, including "a malicious .gitmodules file" | Optional hardening | Yes |
| `core.editor`, `diff.tool`, `merge.tool` | Editor and diff/merge tools for commit messages and difftool/mergetool | Set to the chosen editor's wait command once [Which software is recommended for development on a Mac?](https://github.com/iamivanhx/macos-setup/issues/16) settles the editor; no dedicated diff tool is needed | Yes |
| `credential.helper` | How HTTPS credentials are stored | Leave to Apple's `osxkeychain` default, or to `gh auth setup-git` if HTTPS through gh is chosen (§3) | Yes |

**Global ignore** (`~/.config/git/ignore`): GitHub's `Global/macOS.gitignore` template [GH12] is the vendor list for macOS litter (`.DS_Store`, `._*`, `.Spotlight-V100`, `.Trashes`, and more). Add the editor's own folders and local secret files such as `.env` (common practice). **Public: Yes.**

## 3. Git identity, SSH access and signing

### Practices that hold whichever option is chosen

| Practice | Carried by | Rests on | Public |
|---|---|---|---|
| Key type **ed25519**: GitHub's guide uses `ssh-keygen -t ed25519`, and it is `ssh-keygen`'s default on this Mac ("ed25519 (the default)") | key file or 1Password item | Vendor [GH1][S1] | The public key, yes; the private key **never** |
| **Passphrase on the key, held by the Keychain**: `Host github.com` with `AddKeysToAgent yes`, `UseKeychain yes` and `IdentityFile ~/.ssh/id_ed25519`, loaded once with `ssh-add --apple-use-keychain`. Apple's OpenSSH documents both options (`UseKeychain` defaults to "no"). GitHub says to drop `UseKeychain` if the key has no passphrase. The Ansible version created its key with an empty passphrase (`-N ""`), which goes against GitHub's guide. | `~/.ssh/config` | Vendor [GH1][S2][S3] | Yes |
| **Pin GitHub's host keys**: GitHub publishes its `known_hosts` lines "to avoid manually verifying GitHub hosts" | `~/.ssh/known_hosts` (or a `UserKnownHostsFile` in the repo) | Vendor [GH2] | Yes (they are GitHub's public keys) |
| **Commit email is GitHub's no-reply address** (`ID+USERNAME@users.noreply.github.com`), with "Keep my email address private" set on the account [GH3][GH4]. Every pushed commit shows its author email, so a no-reply address makes the identity safe to commit | `user.name`, `user.email` | Vendor [GH3][GH4] | **Yes, with care**: only with the no-reply address. A personal address belongs in an untracked include |
| **Or identity in an untracked include**: `[include] path = ~/.config/git/config.local`, written by a prompt during the Bootstrap. Git skips a missing include without error; tested here with `git config --includes -f <file> --list` (exit 0) | `~/.config/git/config` + untracked local file | Vendor [GIT1]; the missing-file behaviour was tested, not documented | The hook, yes; the local file, **No** |
| **Sign commits with SSH rather than GPG** unless expiring keys are needed. SSH signing needs git 2.34 or later [GH5]; this Mac has 2.54. It takes `gpg.format = ssh`, `user.signingKey`, `commit.gpgSign = true`, and optionally `tag.gpgSign = true` [GIT1]. Local `git verify-commit` needs `gpg.ssh.allowedSignersFile` [GIT1]. GitHub lets the same key be uploaded twice, once as an authentication key and once as a signing key [GH5]. GitHub now keeps "persistent" verification records, so rotating a key does not un-verify old commits [GH5] | `~/.config/git/config`, `~/.ssh/allowed_signers` | Vendor [GH5][GH6][GIT1] | Yes: a public key and a path are not secrets. Point `user.signingKey` at a `.pub` path, or put `key::…` in the local include if the owner prefers the key text out of the repo |

### Options for git identity and SSH access

This table serves [How are git identity and SSH access set up?](https://github.com/iamivanhx/macos-setup/issues/11). "By hand" means the Bootstrap can at best pause for it.

| | A. Key generated on the Mac, uploaded with `gh` | B. 1Password SSH agent | C. HTTPS only through `gh` | D. Commit signing (goes with A, B or C) |
|---|---|---|---|---|
| **Needs on a Fresh Mac** | `ssh-keygen` (built in), `gh` (Homebrew). `gh ssh-key add` calls `POST /user/keys` [GH7], which needs the `write:public_key` scope [GH8]; gh's default scopes are `repo`, `read:org`, `gist` [GH9]. **Shortcut:** `gh auth login -p ssh` finds an existing key or offers to generate `id_ed25519` (optional passphrase), then uploads it, adding `admin:public_key` to the scopes it asks for [GH9][GH10] | 1Password app (cask), signed in; Settings > Developer > "Use the SSH Agent"; an SSH key item (generated in the app, or `op item create --category ssh`, ed25519 by default [OP3]); an `IdentityAgent` line pointing at `~/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock` in `~/.ssh/config`, or `SSH_AUTH_SOCK` [OP1] | `gh` (Homebrew). `gh auth login -p https` (the token goes to "the system credential store") [GH9], then `gh auth setup-git`, which makes gh git's credential helper [GH11] | **SSH:** the settings in the row above. With 1Password, also `gpg.ssh.program = /Applications/1Password.app/Contents/MacOS/op-ssh-sign` [OP2]. The key must be uploaded as a *signing* key: `gh ssh-key add --type signing` calls `POST /user/ssh_signing_keys` [GH7], which needs `write:ssh_signing_key` [GH13], a scope gh does not request by default (`gh auth refresh -s write:ssh_signing_key`; the scope name comes from the REST docs, is missing from GitHub's OAuth scopes page, and was not tested with gh). **GPG:** `gnupg` and `pinentry-mac` from Homebrew, a `pinentry-program` line in `~/.gnupg/gpg-agent.conf` [GH6], a generated GPG key, and `gh gpg-key add` (`write:gpg_key` [GH14]) |
| **Can be scripted** | Key generation; `~/.ssh/config`; `ssh-add --apple-use-keychain`; the upload once gh is signed in | The `~/.ssh/config` line; the key item and public-key export once `op` is signed in | `gh auth setup-git`; `git config` | All the git config. The signing-key upload once the scope is granted |
| **Left by hand** | Browser sign-in for `gh auth login`; typing the passphrase | Signing in to 1Password (account password and Secret Key); turning the agent on (no CLI or settings key for this was found in 1Password's docs); approving each app on first use with Touch ID [OP1]; adding the public key to GitHub, through the browser extension's autofill, by copy and paste [OP1], or with `gh ssh-key add` from an exported `.pub` | Browser sign-in for `gh auth login` | Granting the extra scope in the browser. For GPG: choosing the key's expiry, backing up the secret key, and renewing it |
| **Strengths** | No dependency beyond gh; the Ansible version already does it (`roles/git_setup` at `4b8f39e`); one key per Mac, revoked on GitHub when the Mac is retired | No private key on disk; Touch ID approval "until 1Password locks or quits" [OP1]; the same key works on every device; it also signs commits | Fewest pieces: no SSH key at all; the token sits in the Keychain | SSH signing reuses the key already set up and needs no extra software. GPG signatures carry expiry and revocation, which SSH signatures do not [GH5] |
| **Costs** | The private key lives on disk (encrypted if it has a passphrase); passphrase management | Needs the app running and unlocked, and a subscription. OpenSSH servers allow six authentication attempts by default, so more than about six keys in the agent means `IdentitiesOnly yes` plus `IdentityFile` pointing at a *public* key per host [OP4]. Some SSH clients ignore `IdentityAgent`, so `SSH_AUTH_SOCK` may also be needed [OP1][OP4] | HTTPS git runs on gh's OAuth token (`repo` scope, every repo). No SSH for hosts other than GitHub. Signing still needs a key from A or B | GPG adds two Packages, a config file and yearly upkeep |
| **State on this Mac (2026-09-27)** | No key files in `~/.ssh` | **Already configured:** `~/.ssh/config` has `Host *` with `IdentityAgent` pointing at 1Password's socket, and `ssh-add -l` against that socket exits 0, which means the agent answered and listed at least one identity [S4] | gh installed; login state not read | No global git config; nothing signed yet |

A fifth route exists but was **not** trialled. macOS ships `/usr/lib/ssh-keychain.dylib` and `sc_auth create-ctk-identity`, which can create a non-exportable P-256 key in the Secure Enclave for use by SSH [S5][S6]. GitHub accepts ECDSA P-256 keys (it lists `ssh-keygen -t ecdsa-sk` for hardware keys and publishes its own `ecdsa-sha2-nistp256` host key [GH1][GH2]). Whether git and GitHub accept such a Secure Enclave key end to end was not tested.

## 4. Secrets

| Practice | Carried by | Rests on | Public |
|---|---|---|---|
| Commit nothing secret: no tokens, private keys, `.netrc`, gh's `hosts.yml`, or 1Password's `agent.toml` if it names private vaults | — | Map standing preference; common practice | — |
| gh's token stays in "the system credential store" (the Keychain). Avoid `--insecure-storage`, which writes plain text [GH9] | gh | Vendor [GH9] | n/a |
| Do not export `GH_TOKEN` or `GITHUB_TOKEN` from a Dotfile. When set, it "takes precedence over previously stored credentials" [GH15] | `~/.zshrc` | Vendor [GH15] | — |
| Committed config holds *references* to secrets, and the values are resolved at run time: `op://vault/item/field` read by `op read`, `op run -- <cmd>` (environment) or `op inject` (templates). 1Password: files "that use secret references instead of plaintext secrets can be safely checked into Git" [OP5]. 1Password Shell Plugins authenticate CLIs such as gh with Touch ID instead of a stored token [OP6] | e.g. `.env.tpl`, `~/.config/op/plugins.sh` | Vendor [OP5][OP6] | Yes (the references) |
| Machine-only values go in untracked local files included by tracked ones: `~/.config/git/config.local` (§3), `~/.zshrc.local` (§1), Ghostty's `config-file = ?local` [G1] | local files | Vendor [GIT1][G1]; the pattern is common practice | Hooks yes; local files **No** |
| If chezmoi is chosen, its templates can pull secrets at apply time (`onepasswordRead` and similar) and keep machine data in `~/.config/chezmoi/chezmoi.toml` [C1] | chezmoi | Vendor [C1] | Yes (the templates) |
| Keep one-off secret commands out of history with a leading space (`HIST_IGNORE_SPACE`) | `~/.zshrc` | Vendor [Z2] | Yes |
| Safety net: GitHub's push protection for users is on by default and blocks pushes of supported secrets to public repos [GH16]. Also list `.env` and similar in the global ignore. A pre-commit scanner (gitleaks, trufflehog) is optional | account setting; `~/.config/git/ignore` | Vendor [GH16]; the scanners are common practice | Yes |

## 5. Security settings

The CIS numbers are from the macOS 27 **prerelease** CIS mapping in mSCP release 27.0 [N1][N2], and they match CIS macOS 26 v2.0.0 for every row. How each is applied (`fdesetup`, `socketfilterfw`, `sysadminctl`, profiles, `sudo`) belongs to [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8).

| Setting | Recommendation | Rests on | This Mac | Developer cost | Public |
|---|---|---|---|---|---|
| FileVault | On. On Apple silicon the data volume is always encrypted with a key held by the Secure Enclave; FileVault adds the user's password to protect that key and produces a 24-character recovery key [A1] | Benchmark: CIS 2.6.6 L1 [N3]; Vendor [A1] | **On** | None worth naming | The setting, yes. The recovery key, **No**: keep it in 1Password or iCloud |
| Application Firewall | On, with stealth mode | Benchmark: CIS 2.2.1 and 2.2.2 L1 [N4][N5]; Vendor, for what each option does [A2] | **Off** (stealth off) | Apps that accept incoming connections trigger an allow prompt. Binding dev servers to `127.0.0.1` avoids it (common practice, not checked on 27) | Yes |
| Gatekeeper | On ("App Store and identified developers") | Benchmark: CIS 2.6.5 L1 [N6]; Vendor [A3][A4] | **On** (`assessments enabled`) | Since macOS 15, an unnotarised app can no longer be opened with Control-click; it needs System Settings > Privacy & Security > Open Anyway [A5][A4] | Yes |
| System Integrity Protection | On; never disable | Benchmark: mSCP `os_sip_enable` in the CIS L1 baseline [N2] | **On** | None for normal development | Yes |
| Automatic updates | All on: download, install macOS updates, install App Store updates, install Security Responses and system files | Benchmark: CIS 1.2 to 1.5 L1 [N7][N8][N9][N10]; Vendor [A6] | **All on** (`AutomaticDownload`, `AutomaticallyInstallMacOSUpdates`, `CriticalUpdateInstall`, `ConfigDataInstall`, App Store `AutoUpdate`) | An update can restart the Mac mid-work (common practice) | Yes |
| Screen saver and lock | Screen saver at 15 minutes or less (900 s); password required within 5 s of it starting | Benchmark: CIS 2.11.1 and 2.11.2 L1 [N11][N12] | Screen-lock delay **300 s** (fails 2.11.2); idle time not set in the user domain | None | Yes |
| Automatic login | Off | Benchmark: CIS 2.13.3 L1 [N13] | Not read | None | Yes |
| Remote Login (sshd) | Off unless the owner needs to reach this Mac over SSH | Benchmark: CIS 2.3.3.4 L1 [N14] | Not read | Rules out SSH into this Mac | Yes |
| `sudo` timeout | CIS wants 0 (ask for the password every time) | Benchmark: CIS 5.4 L1 [N15] | Not read | Costly during a Bootstrap: every Homebrew cask step that needs sudo asks again. Owner's call | Yes |
| Touch ID for `sudo` | Uncomment `auth sufficient pam_tid.so` in `/etc/pam.d/sudo_local`. Apple ships a template, `/etc/pam.d/sudo_local.template`, "which survives system update", and `/etc/pam.d/sudo` already includes `sudo_local` | Vendor (files on this Mac) | Not enabled (no `sudo_local`) | Needs sudo once to write | Yes |
| Privacy & Security > Developer Tools | The loosening developers make: listed apps (the terminal) "can run software that doesn't meet the system's security policy" [A7] | Vendor [A7]; turning it on is common practice | Not read | Code launched from that terminal is exempt from that policy. Apple's page does not say which checks are skipped | n/a (a GUI setting) |
| Terminal Secure Keyboard Entry | On in Terminal.app | Benchmark: CIS 6.4.1 L1 [N16] | n/a | Applies to Terminal.app only; whether Ghostty has an equivalent was not checked | Yes |
| Time Machine | Encrypt backups | Benchmark: CIS 2.3.4.2 L1 [N17] | Not read | None | Yes |

CIS Level 1 also covers AirDrop, sharing services, Siri, analytics and Apple Intelligence switches (full list: [N2]). Those are preferences more than development concerns, and [Which macOS settings does the setup apply?](https://github.com/iamivanhx/macos-setup/issues/14) can pick from the baseline.

## 6. macOS settings developers change

Apple documents the user-facing toggle for each of these. Choosing them for a developer rests on **common practice**; the Ansible version's `roles/macos_defaults` at `4b8f39e` and similar dotfiles repos are the leads. This section covers only *what* is changed and *why*. Whether each still works through `defaults write` on macOS 27 is for [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8). This Mac has none of them set (`KeyRepeat`, `InitialKeyRepeat`, `AppleShowAllExtensions`, `AppleShowAllFiles` and the screenshot `location` are all unset); the Dock already auto-hides.

| Setting | Why developers change it | Apple's toggle | Public |
|---|---|---|---|
| Show all filename extensions; do not warn on extension change | See `.ts`, `.env` and other extensions | Finder > Settings > Advanced [A8] | Yes |
| Show hidden files | Dotfiles visible in Finder | Command-Shift-Period in Finder (common practice; not found on an Apple page) | Yes |
| Path bar, status bar, folders first, new window opens home | Orientation in deep trees | Finder View menu and Settings | Yes |
| Fast key repeat, short delay | Moving the cursor in editors | Keyboard > Key repeat rate and Delay until repeat [A9]. Values faster than the slider allows are community practice | Yes |
| Press-and-hold off | Holding a key repeats it instead of showing the accent menu; matters for vim-style navigation. Apple notes that with key repeat Off, "special characters won't appear" [A9] | not a direct toggle | Yes |
| Auto-correct, auto-capitalise, smart quotes, smart dashes, double-space period: off | They corrupt code and shell commands typed in text fields | Keyboard > Text Input | Yes |
| Full keyboard access | Tab moves through all controls | Keyboard > Keyboard navigation | Yes |
| Screenshot folder, no window shadow | Keep the Desktop clean | Screenshot app > Options > Save to [A10] | Yes; write the path as `$HOME/…`, never a literal home path |
| Dock auto-hide and its animation delays | Screen space | Desktop & Dock | Yes |

## 7. Editor and terminal config

| App | Recommendation | Rests on | Public |
|---|---|---|---|
| **Ghostty** (installed) | Keep `~/.config/ghostty/config` as a Dotfile. Ghostty reads `$XDG_CONFIG_HOME/ghostty/config[.ghostty]` first, then `~/Library/Application Support/com.mitchellh.ghostty/config[.ghostty]`, later files overriding earlier ones. It uses a plain `key = value` format and `config-file = ?path` for optional includes. Its docs describe no sync of its own [G1] | Vendor [G1] | Yes |
| **VS Code** (if chosen) | Prefer Settings Sync to a Dotfile. It syncs settings, keybindings, snippets, tasks, MCP servers, UI state, extensions and up to 20 profiles through a GitHub or Microsoft account. `machine`-scoped settings stay local [V1]. A Dotfile of `settings.json` would miss extensions and profiles, and syncing both ways would put one change in two places, against the map's "one edit in one place" preference | Vendor [V1]; the one-place rule is the map's | n/a (sync) or Yes (a settings file) |
| **Prompt, other CLIs** | Dotfile when the tool reads a plain file under `~/.config` | Common practice | Yes, after checking for tokens |
| **Rule of thumb** | Dotfile when the app reads a hand-editable text file and has no sync. App sync when the app rewrites its config from its UI, or the config includes extensions and state. Pick one per app | Common practice | — |

Which editor, prompt and terminal are on the list is for [Which software is recommended for development on a Mac?](https://github.com/iamivanhx/macos-setup/issues/16); font sizes and themes are for [How should a Mac be set up to avoid eye strain?](https://github.com/iamivanhx/macos-setup/issues/18).

## 8. Layout of the Dotfiles folder

| Practice | Rests on | Public |
|---|---|---|
| One of two shapes: **a tree that mirrors `$HOME`** (`home/.zshrc`, `home/.config/git/config`) linked or copied by a short loop, or **one folder per program** (`zsh/.zshrc`, `git/.config/git/config`) as GNU stow expects. The tool survey compares the linking tools [T1] | Common practice; tools per [T1] | Yes |
| Use the XDG path wherever the tool reads it. macOS does not set `XDG_CONFIG_HOME`, and tools fall back to `~/.config`: git [GIT1], gh [GH15], Ghostty [G1], 1Password's `~/.config/1Password/ssh/agent.toml` [OP4]. The spec defines `~/.config`, `~/.local/share`, `~/.local/state` (history and state) and `~/.cache` [X1] | Vendor | Yes |
| Files with fixed homes: `~/.zshrc`, `~/.zprofile` and `~/.zshenv` (zsh looks in `$ZDOTDIR`, else `$HOME` [Z1]; moving them under `~/.config/zsh` needs `ZDOTDIR` set in `~/.zshenv`, one extra file for little gain) and `~/.ssh/config` | Vendor [Z1] | Yes |
| Where an app keeps state or credentials beside its config (gh's `~/.config/gh/hosts.yml`), manage single files, not the directory | Common practice | Directory **No**; `config.yml` yes after checking |
| Local, untracked companions (`*.local`) sit beside tracked files and are ignored by the repo's `.gitignore` | Common practice | The ignore rule, yes |

## Which practices can go into the public repo

- **As written:** every shell file in §1 except `~/.zshrc.local`; all of §2; `~/.ssh/config` with `IdentityAgent`, `UseKeychain`, `AddKeysToAgent` and `IdentityFile` lines (host aliases for private servers are the exception); GitHub's `known_hosts` lines; `allowed_signers` and `user.signingKey` (public keys are not secrets); the security and macOS settings in §5 and §6; Ghostty's config; `op://` references.
- **With care:** `user.name`/`user.email` only with the GitHub no-reply address; paths written with `$HOME` or `~`, never a literal home directory; any config file checked for tokens first.
- **Never:** private keys, the FileVault recovery key, gh's `hosts.yml` or any token, `*.local` files, a personal email address, 1Password vault and item names if the owner treats them as private.

## State of the target Mac

Read on 2026-09-27, without changes.

- macOS 27.0 (26A428), arm64; git 2.54.0 (Apple Git-157); OpenSSH_10.3p1; gh 2.101.0; Homebrew 7.0.6.
- `fdesetup status`: FileVault is On. `socketfilterfw`: firewall disabled, stealth off. `spctl --status`: assessments enabled. `csrutil status`: SIP enabled. `sysadminctl -screenLock status`: delay 300 seconds. Software Update and App Store auto-update preferences all 1.
- `~/.zprofile` holds only the `brew shellenv zsh` line. `~/.zshrc` adds `~/.local/bin` to PATH. There is no `~/.zshenv`. `/etc/paths.d/homebrew` exists.
- There is no `~/.gitconfig` or `~/.config/git`. The CLT system gitconfig sets `osxkeychain` and `main`.
- `~/.ssh` has `config`, `known_hosts` and `known_hosts.old`, and no key files. `config` sets 1Password's `IdentityAgent` for `Host *`. The 1Password agent answered `ssh-add -l` with exit 0.
- `/etc/pam.d/sudo_local.template` is present; `sudo_local` is not.
- gh's config files were not read.

## What could not be verified

- The CIS Benchmark for macOS 27 itself (registration-gated). The CIS numbers come from mSCP's prerelease mapping [N1].
- Turning on the 1Password SSH agent from a script: no documented CLI command or settings key was found.
- The number and type of keys in the 1Password agent. Only the exit status was read, so as not to record key fingerprints or comments.
- Whether a Secure Enclave key from `sc_auth` works for GitHub authentication and git signing.
- Whether Ghostty has a secure-keyboard-entry equivalent, and whether the Application Firewall prompts for dev servers bound to all interfaces on macOS 27.
- What Privacy & Security > Developer Tools exempts in detail; Apple's page does not say.
- That Command-Shift-Period shows hidden files in Finder on macOS 27 (common knowledge, not found on an Apple page).
- Whether the popular `defaults` keys in §6 still take effect on macOS 27; that belongs to [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8).
- That git skips a missing `include.path` silently is **tested** on git 2.54 but not stated in its manual.
- The exact scope string gh accepts for uploading an SSH *signing* key. The REST docs name `write:ssh_signing_key` [GH13], but GitHub's OAuth scopes page does not list it.

## Sources

Manual pages were read on the target Mac (macOS 27.0, 26A428) on 2026-09-27; web pages were fetched on the same day.

**zsh and macOS shell**
- [Z1] `zsh(1)`, STARTUP/SHUTDOWN FILES (installed man page); also https://zsh.sourceforge.io/Doc/Release/Files.html
- [Z2] zsh manual, Options (history, `AUTO_CD`, `INTERACTIVE_COMMENTS`): https://zsh.sourceforge.io/Doc/Release/Options.html
- [Z3] zsh manual, Completion System (`compinit`, `-C`, `-i`/`-u`, `compaudit`): https://zsh.sourceforge.io/Doc/Release/Completion-System.html
- [Z4] `zshbuiltins(1)`, `typeset -U` (installed man page)
- [Z5] `zshparam(1)`, `HISTSIZE`, `SAVEHIST` (installed man page)
- [Z6] `zshmodules(1)`, THE ZSH/ZPROF MODULE (installed man page)
- [M1] `/etc/zprofile` and `/etc/zshrc` as shipped on macOS 27.0 (26A428)
- [M2] `path_helper(8)` (installed man page)
- [H1] Homebrew, Installation: https://docs.brew.sh/Installation
- [H2] Homebrew `install.sh` at commit `0a396a4ee5b538f409de666af904fa0570b53949`, lines 593 to 597 (`/etc/paths.d/homebrew`) and 1141 to 1175 (`~/.zprofile` for zsh on macOS): https://github.com/Homebrew/install/blob/0a396a4ee5b538f409de666af904fa0570b53949/install.sh
- [H3] Homebrew, Shell Completion: https://docs.brew.sh/Shell-Completion

**git**
- [GIT1] `git-config(1)`, git 2.54.0 (Apple Git-157), installed man page; online: https://git-scm.com/docs/git-config
- [GIT2] `git-init(1)`, `--initial-branch` (installed man page)
- [GIT3] `git-pull(1)`, `--ff-only` default (installed man page)
- [L1] Lead only: Scott Chacon, "How Core Git Developers Configure Git", GitButler blog: https://blog.gitbutler.com/how-git-core-devs-configure-git/

**OpenSSH (Apple build)**
- [S1] `ssh-keygen(1)`, `-t` (installed man page)
- [S2] `ssh_config(5)`, `UseKeychain`, `AddKeysToAgent`, `IdentityAgent`, `IdentitiesOnly` (installed man page)
- [S3] `ssh-add(1)`, `--apple-use-keychain`, `--apple-load-keychain` (installed man page)
- [S4] `ssh-add(1)`, EXIT STATUS: "0 on success, 1 if the specified command fails, and 2 if ssh-add is unable to contact the authentication agent" (installed man page). `-l` reports failure when the agent has no identities
- [S5] `ssh-keychain(8)` (installed man page)
- [S6] `sc_auth(8)`, CTK Identity commands (installed man page)

**GitHub**
- [GH1] Generating a new SSH key and adding it to the ssh-agent (Mac): https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent?platform=mac
- [GH2] GitHub's SSH key fingerprints: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/githubs-ssh-key-fingerprints
- [GH3] Setting your commit email address: https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-personal-account-on-github/managing-email-preferences/setting-your-commit-email-address
- [GH4] Email addresses reference (no-reply format): https://docs.github.com/en/account-and-profile/reference/email-addresses-reference
- [GH5] About commit signature verification: https://docs.github.com/en/authentication/managing-commit-signature-verification/about-commit-signature-verification
- [GH6] Telling Git about your signing key (Mac): https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key?platform=mac
- [GH7] GitHub CLI source, `pkg/cmd/ssh-key/add/add.go` and `http.go` (`user/keys` vs `user/ssh_signing_keys`): https://github.com/cli/cli/tree/trunk/pkg/cmd/ssh-key/add
- [GH8] REST API, Git SSH keys (`write:public_key`): https://docs.github.com/en/rest/users/keys?apiVersion=2022-11-28
- [GH9] `gh auth login` manual (and `gh auth login --help`, gh 2.101.0): https://cli.github.com/manual/gh_auth_login
- [GH10] GitHub CLI source, `pkg/cmd/auth/shared/login_flow.go` (generates `id_ed25519`; adds `admin:public_key`): https://github.com/cli/cli/blob/trunk/pkg/cmd/auth/shared/login_flow.go
- [GH11] `gh auth setup-git` manual: https://cli.github.com/manual/gh_auth_setup-git
- [GH12] github/gitignore `Global/macOS.gitignore` at commit `b06d69d5a0b82a187180dac3d46a4ebe1e40bce5`: https://github.com/github/gitignore/blob/b06d69d5a0b82a187180dac3d46a4ebe1e40bce5/Global/macOS.gitignore
- [GH13] REST API, SSH signing keys (`write:ssh_signing_key`): https://docs.github.com/en/rest/users/ssh-signing-keys?apiVersion=2022-11-28
- [GH14] REST API, GPG keys (`write:gpg_key`): https://docs.github.com/en/rest/users/gpg-keys?apiVersion=2022-11-28
- [GH15] `gh help environment` (`GH_TOKEN`, `GH_CONFIG_DIR`): https://cli.github.com/manual/gh_help_environment
- [GH16] Push protection (push protection for users on by default for public repos): https://docs.github.com/en/code-security/concepts/secret-security/push-protection and https://docs.github.com/en/code-security/secret-scanning/working-with-secret-scanning-and-push-protection/push-protection-for-users

**1Password**
- [OP1] Get started with 1Password for SSH: https://www.1password.dev/ssh/get-started (redirected from developer.1password.com/docs/ssh/get-started)
- [OP2] Sign Git commits with SSH: https://www.1password.dev/ssh/git-commit-signing
- [OP3] Manage SSH keys with 1Password CLI: https://www.1password.dev/cli/ssh-keys
- [OP4] Advanced use cases (six-key limit, `IdentitiesOnly`, `agent.toml`): https://www.1password.dev/ssh/agent/advanced
- [OP5] Secret references: https://www.1password.dev/cli/secret-references
- [OP6] Shell plugins: https://www.1password.dev/cli/shell-plugins

**Apple**
- [A1] Apple Platform Security, Volume encryption with FileVault in macOS (guide dated 2026-01-28): https://support.apple.com/guide/security/volume-encryption-with-filevault-sec4c6dc1b6e/web
- [A2] Mac User Guide, Change Firewall settings (served for macOS 27 Golden Gate): https://support.apple.com/guide/mac-help/change-firewall-settings-on-mac-mh11783/mac
- [A3] Apple Platform Security, Gatekeeper and runtime protection in macOS (dated 2024-12-19; written for macOS 15 and earlier): https://support.apple.com/guide/security/gatekeeper-and-runtime-protection-sec5599b66df/web
- [A4] Safely open apps on your Mac (dated 2026-05-27): https://support.apple.com/en-us/102445
- [A5] Apple Developer News, "Updates to runtime protection in macOS Sequoia" (2024-08-06): https://developer.apple.com/news/?id=saqachfa
- [A6] Mac User Guide, Keep your Mac up to date (macOS 27): https://support.apple.com/guide/mac-help/keep-your-mac-up-to-date-mchlpx1065/mac
- [A7] Mac User Guide, Control the ability of apps to run software that doesn't meet the system's security policy (macOS 27, 26, 15): https://support.apple.com/guide/mac-help/mchlc5fb7f9c/mac
- [A8] Mac User Guide, Show or hide filename extensions (macOS 27): https://support.apple.com/guide/mac-help/show-or-hide-filename-extensions-on-mac-mchlp2304/mac
- [A9] Mac User Guide, Set how quickly a key repeats: https://support.apple.com/guide/mac-help/mchl0311bdb4/mac
- [A10] Mac User Guide, Take a screenshot: https://support.apple.com/guide/mac-help/take-a-screenshot-mh26782/mac

**NIST mSCP (CIS mapping), release 27.0, tag `release_27.0` at commit `c1e6cf9c41d518d0456ab6a7f12a1a4d1f227715`**
- [N1] Release notes, "mSCP 2.0, Release 27.0" (2026-09-11): https://github.com/usnistgov/macos_security/releases/tag/release_27.0
- [N2] CIS Level 1 baseline for macOS 27.0: https://github.com/usnistgov/macos_security/blob/c1e6cf9c41d518d0456ab6a7f12a1a4d1f227715/src/mscp/data/baselines/macos/cis_lvl1_macos_27.0.yaml
- Rules under `src/mscp/data/rules/` at the same commit: [N3] `system_settings/system_settings_filevault_enforce.yaml`; [N4] `system_settings/system_settings_firewall_enable.yaml`; [N5] `system_settings/system_settings_firewall_stealth_mode_enable.yaml`; [N6] `os/os_gatekeeper_enable.yaml`; [N7] `system_settings/system_settings_software_update_download_enforce.yaml`; [N8] `system_settings/system_settings_install_macos_updates_enforce.yaml`; [N9] `system_settings/system_settings_software_update_app_update_enforce.yaml`; [N10] `system_settings/system_settings_critical_update_install_enforce.yaml`; [N11] `system_settings/system_settings_screensaver_timeout_enforce.yaml` (CIS L1 value 900 s); [N12] `system_settings/system_settings_screensaver_ask_for_password_delay_enforce.yaml` (CIS L1 value 5 s); [N13] `system_settings/system_settings_automatic_login_disable.yaml`; [N14] `system_settings/system_settings_ssh_disable.yaml`; [N15] `os/os_sudo_timeout_configure.yaml` (CIS L1 value 0); [N16] `os/os_terminal_secure_keyboard_enable.yaml`; [N17] `system_settings/system_settings_time_machine_encrypted_configure.yaml`

**Editors, terminals, layout**
- [G1] Ghostty, Configuration: https://ghostty.org/docs/config
- [G2] Ghostty, Configuration reference (`command`; macOS launches the shell through `login`): https://ghostty.org/docs/config/reference
- [V1] VS Code, Settings Sync: https://code.visualstudio.com/docs/configure/settings-sync
- [X1] XDG Base Directory Specification 0.8: https://specifications.freedesktop.org/basedir/latest/
- [C1] chezmoi, Manage machine-to-machine differences: https://www.chezmoi.io/user-guide/manage-machine-to-machine-differences/
- [T1] Tool survey note for [Which tools can set up a fresh Mac, and how do they compare?](https://github.com/iamivanhx/macos-setup/issues/5), `docs/research/tool-survey.md` on branch `research/tool-survey` at commit `e388dbc88c2f1b5e6648a6c4e28071fb63d36491` (GNU stow, chezmoi, mise Dotfiles)
