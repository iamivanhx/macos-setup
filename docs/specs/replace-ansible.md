# Replace Ansible with Homebrew, mise bootstrap and a thin Wrapper

This spec is the destination of [the map](https://github.com/iamivanhx/macos-setup/issues/4). It gathers the 19 decisions the map indexes and decides nothing anew, apart from the points listed under [Inferred by this spec](#further-notes). Terms in capitals are defined in `CONTEXT.md`.

## Problem Statement

The owner sets up a Fresh Mac with an Ansible version of this repo that costs more to maintain than the setup it produces: about 800 lines of roles and vars, a 207-line `bootstrap.sh` and about 2,900 lines of tests, for a Bootstrap that runs once per Mac. One change is rarely one edit in one place, some of its lists no longer work as written, and its Packages, Dotfiles and macOS settings no longer match what the owner wants on a Mac.

In detail:

- **The lists have gone stale.** `tldr` is disabled in Homebrew, GitHub Copilot CLI is no longer a formula, `pnpm env` is deprecated, and the list installs iTerm2 where the owner uses Ghostty. Of the 27 macOS settings, one is expected to fail on macOS 27.
- **Config is generated, not stored.** The Ansible version runs `starship preset` and appends to `.zshrc`. The owner has no Dotfiles to read or edit in one place.
- **Git identity and SSH access are not set up.** The target Mac has no git identity, and nothing writes one. Three commits of this repo carry an address git guessed.
- **The tests cannot run on the target Mac**, whose Python has no `yaml` module, and the repo has no CI. So the test suite proves nothing where the Bootstrap runs.
- **The target Mac waits.** It is an M3 Pro on macOS 27.0, installed on 2026-09-26, and it stays minimal until the new setup exists.

## Solution

The owner starts a Bootstrap on a Fresh Mac with one command. It fetches the Wrapper, which runs two standard tools in order:

- **Homebrew** installs every Package that comes from Homebrew, from a `Brewfile`.
- **mise bootstrap** does everything else from one config: the Dotfiles, the Local files, the macOS settings, Node, `sfw`, and the Packages that come from uv or from their own installer.

The Wrapper asks for the hostname, pauses once until this Mac's SSH key is in 1Password's SSH agent, and holds the Mac awake. At the end the Bootstrap prints the Steps by hand. A first run on a Fresh Mac takes about 8 minutes and asks five times. A re-run takes about a second, asks nothing, and sets back what drifted.

Every Mac gets the same 26 Packages, the same Dotfiles and the same 22 macOS settings. Machine values, the hostname and the SSH key, are asked or looked up and never stored in this repo. A new Package, Dotfile, macOS setting or Step by hand is one edit in one place.

The repo moves off Ansible in one merge. The Ansible version is kept under the tag `ansible-final`. The new setup is trialled, then run on the target Mac, and only then merged.

## User Stories

1. As the owner, I want to start a Bootstrap on a Fresh Mac with one command, so that I need nothing installed first.
2. As the owner, I want the Bootstrap to fetch this repo over HTTPS, so that it works before the Mac has SSH access.
3. As the owner, I want the Wrapper to bring Homebrew and the Command Line Tools, so that I install neither by hand.
4. As the owner, I want the checkout at `~/Projects/macos-setup`, so that the README and the docs are not in a hidden directory.
5. As the owner, I want the Wrapper to hold the Mac awake, so that idle sleep does not break a long install.
6. As the owner, I want to be asked for the hostname once, so that a re-run looks it up and asks nothing.
7. As the owner, I want the Wrapper to pause until this Mac's key is in 1Password's SSH agent, so that I start the Wrapper once on a new Mac and not twice.
8. As the owner, I want the pause to name the possible causes, so that I know what to do in 1Password.
9. As the owner, I want one SSH key per Mac, kept in 1Password and never on disk, so that commits and pushes show which Mac made them and a key retires with its Mac.
10. As the owner, I want my commits and tags signed with this Mac's key, so that GitHub shows them as verified.
11. As the owner, I want my git name and email set by a Dotfile, so that git never guesses an address.
12. As the owner, I want 1Password's agent limited to this Mac's key, so that a server does not refuse the connection once the account holds many keys.
13. As the owner, I want a lean list of Packages installed, so that the Mac holds only what I use in the first weeks.
14. As the owner, I want every Package from Homebrew to be one line of a `Brewfile`, so that adding one is one edit and `brew` can upgrade the apps.
15. As the owner, I want Node from mise and Python from uv with no version pinned in this repo, so that each project pins its own.
16. As the owner, I want Claude Code, Codex CLI and pi installed, so that the agents are there after a Bootstrap.
17. As the owner, I want my Dotfiles stored as plain files under their own names, so that I read and edit them as they are.
18. As the owner, I want an edit to a Dotfile in the home directory to land in the checkout, so that I commit it from there.
19. As the owner, I want Machine values written into Local files, so that nothing that names a Mac or a key sits in this public repo.
20. As the owner, I want my own additions to the shell in `~/.zshrc.local`, so that the Bootstrap never touches them.
21. As the owner, I want the prompt, the terminal, bat, delta and fzf to show Catppuccin Latte in light mode and Catppuccin Mocha in dark mode, so that everything follows the macOS appearance.
22. As the owner, I want a lean list of macOS settings applied, so that I change none of them by hand on a Fresh Mac.
23. As the owner, I want the firewall on, stealth mode on and the screen locked within 5 seconds, so that the Mac meets CIS Level 1 where it did not.
24. As the owner, I want Touch ID for `sudo`, so that I type my password less.
25. As the owner, I want the Dock to hold my four apps and nothing else, so that I do not clear Apple's defaults by hand.
26. Dropped by the amendment of 2026-10-03 under Further Notes. As first written: As the owner, I want Spotlight's shortcut turned off, so that Raycast can take Command-Space.
27. As the owner, I want the Steps by hand printed at the end of every run, so that I know what is left for me to do.
28. As the owner, I want a new Step by hand to be one line in one file, so that the checklist is easy to keep.
29. As the owner, I want a re-run to be safe and quick, so that a re-run is how I check and repair a Mac.
30. As the owner, I want a setting changed by hand reported and set back, so that the Mac matches the repo after a re-run.
31. As the owner, I want the tools' own reports to tell me a Mac's state, so that I maintain no check script.
32. As the owner, I want the Wrapper to name the recover command when mise fails, so that an interrupted run does not leave me stuck.
33. As the owner, I want the Bootstrap to stop at a file that is already where a Dotfile goes, so that it never overwrites what it finds.
34. As the owner, I want the README to say how to fix a break during a Bootstrap, so that I fix it on the spot and re-run.
35. As the owner, I want the README to list the checks on a real Mac, so that I check what no tool reports.
36. As the owner, I want lint to run on every push, so that a broken Wrapper does not reach `main` unseen.
37. As the owner, I want the Ansible version kept under a tag, so that I can read it after it leaves `main`.
38. As the owner, I want `main` to change in one merge, so that a Fresh Mac never runs a half state.
39. As the owner, I want the new setup trialled and run on the target Mac before the merge, so that `main` never holds a setup that has not met a real Mac.
40. As the owner, I want the research notes kept in the repo, so that the sources behind the decisions outlast the local branches.
41. As the owner, I want tart, the golden guest and the local branches removed at the end, so that the target Mac holds nothing the refactor left behind.
42. As a reader of this public repo, I want the README to describe the new setup and name the tag of the old one, so that I know what I am looking at.

## Acceptance Criteria

Where a criterion says "in a Trial", it is observed in a clone of the golden guest `fresh-27`. Where it says "on the target Mac", it is observed on the owner's Mac. `<hostname>` is the hostname given to the Wrapper.

### The repo

- [ ] AC-1: On `main` after the merge, the repo root holds `bootstrap.sh`, `Brewfile`, `config.toml`, `steps-by-hand.md`, `dotfiles/`, `README.md`, `CONTEXT.md`, `AGENTS.md`, `LICENSE`, `docs/` and `memory/`, and holds none of `playbook.yml`, `ansible.cfg`, `requirements.yml`, `inventory/`, `group_vars/`, `roles/` and `tests/`
- [ ] AC-2: `dotfiles/` holds one directory per app (`zsh`, `starship`, `ghostty`, `git`, `bat`, `ssh`, `1password`), each file keeps its own name with no hidden or `dot_` name, and each file is named by exactly one entry of `config.toml`
- [ ] AC-3: `docs/research/` on `main` holds the nine notes `appearance.md`, `dev-config.md`, `dev-software.md`, `eye-strain.md`, `hola.md`, `macos-settings.md`, `openboot.md`, `tool-survey.md` and `trial-vm.md`
- [ ] AC-4: `.gitignore` on `main` names `.claude/worktrees/` and holds no line for Ansible (`.ansible/`, `*.retry`)
- [ ] AC-5: `README.md` gives the start command `bash -c "$(curl -fsSL https://raw.githubusercontent.com/iamivanhx/macos-setup/main/bootstrap.sh)"`, names the five prompts of a first run (the hostname, the password and Return at Homebrew's installer, the password at `sudo`, the password at the screen-lock prompt), names the pause at the key check, and says what to click when Homebrew's installer shows the Command Line Tools popup
- [ ] AC-6: `README.md` names the three commands that report a Mac's state (a re-run of the Wrapper, `mise bootstrap status --missing`, `brew bundle check`), says that `mise bootstrap status` run by hand needs `BOOTSTRAP_HOSTNAME` and `BOOTSTRAP_SSH_PUBLIC_KEY` in the environment, and holds one list of checks on a real Mac: the battery percentage, Touch ID for `sudo`, the key step with 1Password, and a push over SSH
- [ ] AC-7: `README.md` says how to fix a break during a Bootstrap (edit the checkout at `~/Projects/macos-setup`, re-run the Wrapper, push once the key step works, and use GitHub's web editor when the break comes before the checkout exists) and names the command `mise dot recover --keep-current --yes` for an interrupted run
- [ ] AC-8: `README.md` points at `steps-by-hand.md` without repeating its lines, and holds one line that names the tag `ansible-final` as where the Ansible version lives
- [ ] AC-9: No file on `main` holds a hostname of a Mac, an SSH public key, or config for Claude Code, Codex CLI or pi, and the tree holds no `statusline-command.sh`

### A first run

- [ ] AC-10: In a Trial, the start command run from a URL ends with exit code 0 and asks exactly five times: the hostname, the password and Return at Homebrew's installer, the password at `sudo`, and the password at the screen-lock prompt
- [ ] AC-11: In a Trial, the output of a first run shows its steps in this order: the hostname, Homebrew's installer with the Command Line Tools, the clone of the repo, `brew bundle`, the key check, `mise bootstrap`
- [ ] AC-12: After a first run in a Trial, `~/Projects/macos-setup` is a git checkout of this repo, `~/.config/mise` is a link to it, and `git -C ~/Projects/macos-setup remote get-url origin` prints `git@github.com:iamivanhx/macos-setup.git`
- [ ] AC-13: While the Wrapper runs, `pmset -g assertions` lists a `caffeinate` assertion that prevents idle sleep, and lists none from the Wrapper after it exits
- [ ] AC-14: In a Trial where the agent does not hold a key titled `SSH Key (<hostname>)`, the Wrapper prints that title, the four causes (1Password not signed in, 1Password locked, the SSH agent off, no key with that title), and that Ctrl-C is safe and a re-run picks up from there, then asks for Return. It asks again after each Return until the key is there, and `mise bootstrap` does not start before it is
- [ ] AC-15: When `~/.config/mise` exists and is not a link, the Wrapper stops with a message that says so, exits non-zero, and leaves `~/.config/mise` as it was
- [ ] AC-16: When `mise bootstrap` fails, the Wrapper prints a message that names `mise dot recover --keep-current --yes`, exits non-zero, and the lines of `steps-by-hand.md` are not printed
- [ ] AC-17: When a real file is already at a path where a Dotfile goes, the Bootstrap stops with mise's error that lists the conflicting path, and the file is unchanged
- [ ] AC-18: The Wrapper clones from the URL in `BOOTSTRAP_REPO_URL` and reads the key from the socket in `BOOTSTRAP_AGENT_SOCK` when they are set, and from GitHub over HTTPS and 1Password's agent socket when they are not
- [ ] AC-19: When a checkout is already at `~/Projects/macos-setup`, the Wrapper uses it as it is, on the branch it is on, and does not clone

### A re-run

- [ ] AC-20: A second run of the Wrapper on a Mac that a first run set up ends with exit code 0 and asks nothing: the hostname is read from `HostName`
- [ ] AC-21: After a run, `brew bundle check --file ~/Projects/macos-setup/Brewfile` reports the dependencies satisfied, and `mise bootstrap status --missing`, run from the home directory with `BOOTSTRAP_HOSTNAME` and `BOOTSTRAP_SSH_PUBLIC_KEY` in the environment, exits 0
- [ ] AC-22: After Dock auto-hide is turned off by hand, `mise bootstrap status` reports that setting as differing, and a re-run sets it back to on
- [ ] AC-23: After the firewall is turned off by hand, a re-run asks for the `sudo` password and turns it on. When the firewall, stealth mode, the lock delay, Touch ID for `sudo` and the three names all hold, a re-run asks for no password
- [ ] AC-24: After `~/.config/git/config.local`, `~/.config/1Password/ssh/agent.toml` or `~/.config/starship-light.toml` is edited by hand, a re-run writes it back to what the Bootstrap produces
- [ ] AC-25: After `~/.zshrc` is edited in the home directory, `git -C ~/Projects/macos-setup status` shows the zsh Dotfile as modified, and a re-run leaves the edit in place

### Packages

- [ ] AC-26: `Brewfile` holds exactly 22 Packages, one per line and none with a version: the formulae `git`, `gh`, `git-delta`, `mise`, `uv`, `pnpm`, `ripgrep`, `fd`, `bat`, `jq`, `fzf`, `starship`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `gitleaks`, and the casks `1password`, `1password-cli`, `ghostty`, `google-chrome`, `visual-studio-code`, `codex`, `font-jetbrains-mono-nerd-font`. It names no tap and no `mas` entry
- [ ] AC-27: After a first run, a new login shell in the home directory runs `node --version`, which prints a current LTS version that mise installed, and `sfw`, which is on `PATH`
- [ ] AC-28: After a first run, `uv python list --only-installed` lists a Python, and a new login shell finds `claude` and `pi` on `PATH`. pi's installer asked for no keypress during the run
- [ ] AC-29: After a first run, `brew list --cask` lists all seven casks of the `Brewfile`, and `brew list node` fails, since Homebrew's `node` is not installed

### Dotfiles and Local files

- [ ] AC-30: After a first run, `~/.zprofile`, `~/.zshrc`, `~/.config/starship.toml`, `~/.config/ghostty/config`, `~/.config/git/config`, `~/.config/git/ignore`, `~/.config/bat/config` and `~/.ssh/config` are links to files under `dotfiles/` of the checkout, and `~/.config/mise/config.toml` is the checkout's `config.toml`
- [ ] AC-31: After a first run, `~/.config/starship-light.toml` differs from `~/.config/starship.toml` in one line, the `palette` line, which names `catppuccin_latte` where the stored file names `catppuccin_mocha`. The light file is not in the repo
- [ ] AC-32: After a first run, `~/.config/git/config.local` sets `user.signingKey` to the public key that the agent holds under the title `SSH Key (<hostname>)`, and `~/.config/1Password/ssh/agent.toml` holds one `[[ssh-keys]]` entry with `item = "SSH Key (<hostname>)"`
- [ ] AC-33: After a first run, a new login shell starts with no warning or error, shows the Starship prompt, has `~/.local/bin` and Homebrew on `PATH` with no duplicate entry, and has sourced `~/.zshrc.local` when that file exists. The Bootstrap never creates `~/.zshrc.local`
- [ ] AC-34: In a shell on a Mac in dark mode, `STARSHIP_CONFIG` is `~/.config/starship.toml` and `DELTA_FEATURES` is `catppuccin-mocha`. In light mode they are `~/.config/starship-light.toml` and `catppuccin-latte`. After the appearance changes, an open shell has the new values at its next prompt
- [ ] AC-35: After a first run, `~/.config/ghostty/config` holds `theme = light:Catppuccin Latte,dark:Catppuccin Mocha` and `font-size = 15` and no font line, `~/.config/bat/config` holds `--theme-light="Catppuccin Latte"` and `--theme-dark="Catppuccin Mocha"`, and `FZF_DEFAULT_OPTS` in a new shell holds `--color=16`
- [ ] AC-36: After a first run, `git config --global --includes --list` shows the name and email that the git Dotfile holds, `user.useconfigonly=true`, `gpg.format=ssh`, `gpg.ssh.program` as 1Password's `op-ssh-sign`, `commit.gpgsign=true`, `tag.gpgsign=true`, `init.defaultbranch=main`, `push.autosetupremote`, `fetch.prune`, `rebase.autostash`, `rebase.autosquash`, `rebase.updaterefs`, `rerere.enabled` and `commit.verbose` as true, `merge.conflictstyle=zdiff3`, `diff.algorithm=histogram`, `diff.colormoved=plain`, `core.pager=delta`, and `core.editor=code --wait`. The git Dotfile sets neither `credential.helper` nor `pull.rebase`
- [ ] AC-37: After a first run, `~/.config/git/ignore` holds GitHub's `Global/macOS.gitignore`, the editor folders and `.env`, and `~/.ssh/config` holds one block, `Host *`, with one line that points `IdentityAgent` at 1Password's agent socket
- [ ] AC-38: On the target Mac after the first real Bootstrap, `ssh -T git@github.com` greets the owner's account, a commit made in the checkout is signed and GitHub shows it as verified, and `git push` over SSH succeeds

### macOS settings

- [ ] AC-39: After a first run, these 18 settings read back with `defaults read` (with `-currentHost` for the battery percentage and AirPlay Receiver): global `AppleInterfaceStyleSwitchesAutomatically` true, `com.apple.swipescrolldirection` false, `AppleShowAllExtensions` true, `ApplePressAndHoldEnabled` false, `KeyRepeat` 2, `InitialKeyRepeat` 15, `NSAutomaticSpellingCorrectionEnabled` false, `NSAutomaticQuoteSubstitutionEnabled` false, `NSAutomaticDashSubstitutionEnabled` false; `com.apple.dock` `autohide` true and `persistent-apps` as Ghostty, Google Chrome, Visual Studio Code, 1Password in that order; `com.apple.finder` `FXEnableExtensionChangeWarning` false, `ShowPathbar` true, `NewWindowTarget` `PfHm`; `com.apple.screencapture` `location` the Downloads folder and `disable-shadow` true; per-host `com.apple.controlcenter` `BatteryShowPercentage` true and `AirplayReceiverEnabled` false
- [ ] AC-40: In a Trial with a window, after a first run and with no step by hand, the Dock shows Ghostty, Google Chrome, Visual Studio Code and 1Password in that order and none of Apple's default apps. After the one logout of the Steps by hand, System Settings shows Appearance as Auto
- [ ] AC-41: After a first run, `socketfilterfw --getglobalstate` reports the firewall enabled, `socketfilterfw --getstealthmode` reports stealth mode on, `sysadminctl -screenLock status` reports 5 seconds, and `/etc/pam.d/sudo_local` holds an active `pam_tid.so` line
- [ ] AC-42: After a first run, `scutil --get ComputerName`, `scutil --get LocalHostName` and `scutil --get HostName` each print `<hostname>`
- [ ] AC-43: In a Trial with a window, a screenshot of a window taken after a first run lands in `~/Downloads` and has no window shadow
- [ ] AC-44: A Bootstrap leaves the sleep timers as they were: `pmset -g custom` prints the same before and after a first run. It sets no Dock icon size, no tap to click and no text size
- [ ] AC-45: On the target Mac after the first real Bootstrap and one logout, the menu bar shows the battery percentage, and `sudo` in a new terminal accepts Touch ID

### Steps by hand

- [ ] AC-46: `steps-by-hand.md` holds five steps and no other, in this order: add this Mac's public key to GitHub as an authentication key and as a signing key unless it is there already, with the address `https://github.com/settings/keys`; sign in to the apps and the AI agents; sign in to VS Code's Settings Sync; make Google Chrome the default browser; log out once, so the keyboard settings load
- [ ] AC-47: Every run that ends with exit code 0, a first run and a re-run alike, prints the lines of `steps-by-hand.md` at its end, whether or not a step was already done

### Lint

- [ ] AC-48: One lint command runs `shellcheck` and `bash -n` on `bootstrap.sh`. It exits 0 on `main` after the merge, and exits non-zero when `bootstrap.sh` holds a syntax error
- [ ] AC-49: A GitHub Actions workflow runs that lint command on every push by calling it, not by repeating its steps, and runs nothing of the Bootstrap. Its run on the pull request of the refactor passed
- [ ] AC-50: `main` after the merge holds no test suite, no check script and no Trial harness: no `tests/`, no `prototypes/`, and no script that prints or checks a Mac's state

### Migration

- [ ] AC-51: The tag `ansible-final` is annotated, is on GitHub, and marks the commit on `main` that adds the status-line work (`roles/npm_globals/files/statusline-command.sh` and the changes to `README.md`, `roles/npm_globals/tasks/main.yml` and `tests/test_npm_globals_role.py`). `git show ansible-final:playbook.yml` prints the playbook
- [ ] AC-52: The new setup reached `main` through one pull request and one merge. Every commit on `main` holds either the Ansible version or the new setup, and none holds a part of each
- [ ] AC-53: Before the first real Bootstrap, a Trial of the branch ended with exit code 0 with both stand-ins (an HTTP server for GitHub, a plain `ssh-agent` for 1Password's agent), and its output is a comment on the pull request
- [ ] AC-54: Before the first real Bootstrap on the target Mac, its `~/.zprofile`, `~/.zshrc` and `~/.ssh/config` were moved by hand to a folder in the home directory. That folder is gone once the checks on a real Mac have passed
- [ ] AC-55: Before the merge, the Wrapper ran on the target Mac from the branch in the checkout at `~/Projects/macos-setup` and ended with exit code 0, the four checks on a real Mac passed, and both results are a comment on the pull request
- [ ] AC-56: On the target Mac, VS Code has the extension `Catppuccin.catppuccin-vsc`, `window.autoDetectColorScheme` is on, and the preferred light and dark themes are Catppuccin Latte and Catppuccin Mocha, set once by hand after the sign-in to Settings Sync
- [ ] AC-57: After the merge, a Trial that runs the start command of AC-5 as written, with the repo fetched from GitHub over HTTPS and only 1Password's agent stood in, ended with exit code 0, and its output is a comment on the pull request
- [ ] AC-58: On the target Mac, `git branch --list 'research/*' 'prototype/*'` prints nothing, and `git worktree list` shows no worktree of such a branch
- [ ] AC-59: On the target Mac, `tart` is not installed, `~/.tart` does not exist, the tap `openai/tools` is gone, and `~/.homebrew/trust.json` holds no entry for `openai/tools/tart` or `openai/tools/softnet`

## Implementation Decisions

Each decision names the ticket that made it. The ticket holds the reasons and what was rejected.

**Tooling** ([#15](https://github.com/iamivanhx/macos-setup/issues/15))

- Two standard tools with a thin Wrapper, split at Homebrew. Homebrew owns every Package that comes from Homebrew, formulae and casks alike. mise bootstrap owns everything else.
- mise installs no cask and no formula. Homebrew cannot see a cask that mise installed, so `brew` could not upgrade the app.
- mise comes from the `Brewfile` and is not pinned. "Not pinned" means Homebrew's current version, which can be a release behind mise's newest.
- The way out is plain pieces with thin glue: a Dotfile entry maps to one link, a settings key to one `defaults write`, and the `Brewfile` is already Homebrew's own format.

**Layout** ([#20](https://github.com/iamivanhx/macos-setup/issues/20))

```
macos-setup/
├── bootstrap.sh        the Wrapper
├── Brewfile            the Packages that come from Homebrew
├── config.toml         everything else: Dotfiles, macOS settings, hook lines, Node, sfw, the task
├── steps-by-hand.md    the checklist, printed at the end of a run
├── dotfiles/           the Dotfile sources, by app
│   ├── zsh/  starship/  ghostty/  git/  bat/  ssh/  1password/
├── README.md  CONTEXT.md  AGENTS.md  LICENSE  docs/  memory/
```

- On a Mac the repo is a checkout at `~/Projects/macos-setup`, and `~/.config/mise` is a link to it. So the repo's `config.toml` is also the global mise config: Node and `mise bootstrap status` work from any directory.
- The link is the directory, not the config file. mise looks for each Dotfile source beside its config.
- The mise config is reached through that link, so it is not one of the linked Dotfiles. Eight Dotfiles are links.

**The order of a run** ([#20](https://github.com/iamivanhx/macos-setup/issues/20), [#11](https://github.com/iamivanhx/macos-setup/issues/11), [#23](https://github.com/iamivanhx/macos-setup/issues/23))

| # | Step | Prompt on a first run |
|---|---|---|
| 1 | Hold the Mac awake with `caffeinate`, for as long as the Wrapper runs | |
| 2 | The hostname: read from `HostName`, asked when it is not set | the hostname |
| 3 | Homebrew's installer, which brings the Command Line Tools | the password, then Return |
| 4 | Clone the repo over HTTPS, with the Command Line Tools' git. A checkout that is there is used as it is | |
| 5 | `brew bundle` | |
| 6 | The key check: `ssh-add -L` against 1Password's socket, with the pause | Return, only while the key is not there |
| 7 | Switch the checkout's remote to SSH | |
| 8 | Link `~/.config/mise` to the checkout | |
| 9 | `mise bootstrap` | the password at `sudo`, the password at the screen-lock prompt |

- mise fixes its own order inside step 9: Dotfiles, macOS settings, the hook lines, tools, the task, the `final` hook.
- `brew bundle` runs before mise because the Dock's apps and 1Password come from it. Any `brew` command ends the `sudo` session, which is why the `sudo` hook lines ask again. The owner accepted three passwords in a first run.
- Nothing calls git before the Command Line Tools exist. On a Fresh Mac `/usr/bin/git` is a stub that opens an install dialog.
- The Command Line Tools popup gets no code. The README names it.
- The Wrapper never passes `--force-dotfiles`, never calls `op`, never makes a key, and leaves `gh`'s sign-in alone.
- The Wrapper keeps two overrides, `BOOTSTRAP_REPO_URL` and `BOOTSTRAP_AGENT_SOCK`, so what was trialled is what ships ([#21](https://github.com/iamivanhx/macos-setup/issues/21)).

**Machine values** ([#13](https://github.com/iamivanhx/macos-setup/issues/13), [#11](https://github.com/iamivanhx/macos-setup/issues/11))

- There are two: the hostname and this Mac's SSH public key. The Wrapper hands both to mise in the environment, as `BOOTSTRAP_HOSTNAME` and `BOOTSTRAP_SSH_PUBLIC_KEY`.
- A Local file that the Bootstrap writes is a template in the repo that mise renders. mise renders every template before it changes anything, so a failed render stops the run with no Dotfile placed.
- mise does not run until the key is in the agent. The templates never handle an empty value.

**The key check** ([#11](https://github.com/iamivanhx/macos-setup/issues/11), [#23](https://github.com/iamivanhx/macos-setup/issues/23))

- The 1Password item is titled `SSH Key (<hostname>)`. The Wrapper takes the line of `ssh-add -L` that carries that title.
- When no such line comes back, the Wrapper cannot tell why. It names the four causes, says that Ctrl-C is safe and a re-run picks up from there, and asks for Return to look again. It does not look again by itself, and it does not open 1Password.
- The owner makes the key and adds it to GitHub by hand, once as an authentication key and once as a signing key.
- GitHub's host key is not pinned. No `allowed_signers` file is kept.

**Packages** ([#10](https://github.com/iamivanhx/macos-setup/issues/10), [#15](https://github.com/iamivanhx/macos-setup/issues/15), [#20](https://github.com/iamivanhx/macos-setup/issues/20))

| Install channel | Packages | Where declared |
|---|---|---|
| Homebrew formula (15) | `git`, `gh`, `git-delta`, `mise`, `uv`, `pnpm`, `ripgrep`, `fd`, `bat`, `jq`, `fzf`, `starship`, `zsh-autosuggestions`, `zsh-syntax-highlighting`, `gitleaks` | `Brewfile` |
| Homebrew cask (7) | `1password`, `1password-cli`, `ghostty`, `google-chrome`, `visual-studio-code`, `codex`, `font-jetbrains-mono-nerd-font` | `Brewfile` |
| mise (1) | Node, current LTS | mise config, as a tool |
| npm global, installed with pnpm (1) | `sfw` | mise config, as the tool `npm:sfw` with pnpm as the npm package manager |
| uv (1) | Python, latest | mise config, in the task |
| The Package's own installer (2) | Claude Code, pi | mise config, in the task |

- The task runs on every Bootstrap, so each installer is skipped when its command is already there.
- pi's installer runs after mise has put Node on `PATH`. A mise task has no terminal, so the installer never waits for its keypress.
- No version is pinned in this repo.

**Dotfiles** ([#13](https://github.com/iamivanhx/macos-setup/issues/13), [#19](https://github.com/iamivanhx/macos-setup/issues/19))

- A Package gets a Dotfile only where the app reads a hand-editable file and has no sync of its own. One place per app, never both.
- Every Dotfile is a plain file stored in this repo. The Bootstrap runs no tool to produce config.
- The Starship Dotfile holds the `catppuccin-powerline` preset as the installed version of Starship prints it, with the Mocha palette. The preset from Starship's main branch made the installed version warn.
- The light Starship file is generated from the stored one by changing the `palette` line. It is an output of the Bootstrap, not a Dotfile.
- A zsh hook that runs before each prompt reads the macOS appearance and exports `STARSHIP_CONFIG` and `DELTA_FEATURES`. Ghostty and bat follow the appearance by their own config. fzf takes the terminal's colours.
- `~/.zshrc.local` is a Local file the owner writes. Git's `config.local` and 1Password's `agent.toml` are Local files the Bootstrap writes.
- VS Code's config travels with Settings Sync. 1Password keeps its own. Config for Claude Code, Codex CLI and pi stays out of this repo.

**macOS settings** ([#14](https://github.com/iamivanhx/macos-setup/issues/14), [#20](https://github.com/iamivanhx/macos-setup/issues/20))

- 22 settings. 18 are entries in the mise config, which mise reports on and sets back. AC-39 lists them with their keys and values.
- 4 need `sudo` and are hook lines: the firewall, stealth mode, the lock delay, and Touch ID for `sudo`. The three names of the Mac are a fifth `sudo` hook line, and one more hook line restarts the Dock and Finder.
- Hooks run on every Bootstrap, so each `sudo` hook line first reads the state and acts only when the setting is off. This form is from the prototype:

  ```sh
  socketfilterfw --getglobalstate | grep -q enabled || sudo socketfilterfw --setglobalstate on
  ```

  The read-back command and the command that sets the setting are in one place. This is why a re-run asks for no password when every setting holds, and why the repo keeps no check script.
- The lock delay is set with `sysadminctl -screenLock 5 -password -`, which asks for the password at its own prompt.
- Touch ID for `sudo` is `/etc/pam.d/sudo_local`, made from Apple's template.
- Not set: the sleep timers, the Dock's icon size, tap to click, text size, and the display settings.

**Steps by hand** ([#23](https://github.com/iamivanhx/macos-setup/issues/23))

- The steps that fall in the middle of a run (sign in to 1Password, turn on its SSH agent, make the key) live in the Wrapper's message only.
- `steps-by-hand.md` holds only the steps that come after a run. The `final` hook prints it, and runs only when mise succeeds.
- A step that asks for itself gets no line: the three passwords, GitHub's host key, and Touch ID for the key.
- The Bootstrap never checks whether a step is done.

**Proof** ([#21](https://github.com/iamivanhx/macos-setup/issues/21))

- The real Bootstrap is the proof. A break is fixed in the checkout and the Wrapper is re-run.
- Trials are for the refactor only, with the prototype's harness as it is. The harness does not enter the repo.
- The repo keeps lint and nothing else. The lint command is defined once, and the workflow calls it.
- A newer mise gets no check and no pin.

**Migration order** ([#22](https://github.com/iamivanhx/macos-setup/issues/22), [#23](https://github.com/iamivanhx/macos-setup/issues/23))

| # | Step | Where |
|---|---|---|
| 1 | Commit the status-line work and push. It goes in unverified | `main` |
| 2 | Tag that commit `ansible-final`, annotated, and push the tag | `main` |
| 3 | Delete `prototype/tooling-approach` and its worktree | target Mac |
| 4 | Build the branch: the Ansible files and the tests out; the Wrapper, `Brewfile`, `config.toml`, `steps-by-hand.md`, `dotfiles/`, the lint workflow, the new README, `CONTEXT.md` and the nine research notes in | branch |
| 5 | Open the pull request. Lint runs | GitHub |
| 6 | The first Trial, with both stand-ins. It also tries the screenshot folder and the pause at the key check | a clone of `fresh-27` |
| 7 | Move `~/.zprofile`, `~/.zshrc` and `~/.ssh/config` aside by hand, to a folder in the home directory | target Mac |
| 8 | The first real Bootstrap, from the branch, then the checks on a real Mac. A break is fixed on the branch. The folder of step 7 is deleted once the checks pass | target Mac |
| 9 | Sign in to VS Code's Settings Sync, then set VS Code's theme by hand | target Mac |
| 10 | Merge | `main` |
| 11 | The second Trial, with the real start command. A break is fixed on `main`, and the Trial repeated | a clone of `fresh-27` |
| 12 | Delete the nine `research/*` branches and their worktrees | target Mac |
| 13 | Remove tart, `fresh-27` and `~/.tart`, from the undo list in [#12](https://github.com/iamivanhx/macos-setup/issues/12#issuecomment-5854372285). Delete `prototype/repo-layout` and its worktree | target Mac |

- The refactor leaves alone: `memory/`, `AGENTS.md`, `docs/agents/` and `LICENSE`.
- `CONTEXT.md` is first committed on the branch. The README is rewritten from zero.
- For the first Trial the harness serves the branch, where the prototype served its own `repo/` directory.
- No ADR: none of these decisions is hard to reverse.

## Testing Decisions

**The agreed seams.** The owner agreed these four on 2026-09-27. They are the only seams the tickets and the implementation test at.

| Seam | What a test there exercises | Criteria |
|---|---|---|
| **The Wrapper, run as a Trial** | A whole Bootstrap in a clone of `fresh-27`, started from a URL and driven by the prototype's harness. Stand-ins enter through `BOOTSTRAP_REPO_URL` and `BOOTSTRAP_AGENT_SOCK` | AC-10 to AC-18, AC-20 to AC-37, AC-39 to AC-44, AC-47, AC-53, AC-57 |
| **The Wrapper, run on the target Mac** | The first real Bootstrap from the branch, a re-run, the tools' own reports, the checks on a real Mac, and the steps of the migration on that Mac | AC-19, AC-20, AC-21, AC-38, AC-45, AC-54 to AC-56, AC-58, AC-59 |
| **The lint command** | `shellcheck` and `bash -n` on the Wrapper, run locally and by the workflow | AC-48, AC-49 |
| **The repo at a ref** | The tree, the tag, the README and the checklist, read with `git` and on GitHub | AC-1 to AC-9, AC-26, AC-46, AC-50 to AC-52 |

The two Wrapper seams are one interface with two adapters at each override: GitHub and 1Password's agent on a real Mac, an HTTP server and a plain `ssh-agent` in a Trial.

**What makes a good test here.**

- It observes what a run leaves on the Mac or prints on the terminal. It never reads how the Wrapper or the mise config is written.
- It reads state with the tools' own reports and the system's own commands: `brew bundle check`, `mise bootstrap status`, `defaults read`, `scutil`, `socketfilterfw`, `sysadminctl`, `git config`.
- A key that reads back is not proof that macOS follows it. The settings of AC-40 and AC-43 are checked by eye in a guest with a window, and those of AC-45 on the target Mac.
- No test stubs commands behind the Wrapper. The stubs would be more code than the Wrapper.

**Prior art.**

- The harness of the layout prototype, on the local branch `prototype/repo-layout`: a driver that clones the guest, serves the repo, starts the stand-in agent and runs the Bootstrap; a script that answers the prompts and counts them; and a script that prints the state. It ran a whole Bootstrap on 2026-09-27: 8 minutes 12 seconds, five prompts, then a re-run of 1 second with no prompt.
- Homebrew's Return prompt has colour codes between its words. The script that answers it matches plain text.
- Nothing of the Ansible version's `tests/` or its `verify` role carries over.

**Direct evidence at a user seam.**

- Every criterion at a Wrapper seam needs a run, not a reading of the config. The output of each Trial and of the first real Bootstrap is posted as a comment on the pull request.
- AC-14 needs a Trial that starts the stand-in agent without the key, then adds it during the pause.
- AC-17 needs a Trial that places a file at a Dotfile's path before the run.
- AC-38, AC-45 and AC-54 to AC-56 need the owner at the target Mac.

**Authorization.**

- This spec authorizes nothing on the target Mac. Each Trial and each step on the target Mac needs the owner's say-so in the session that runs it.
- A session that runs a Trial states the wait before it starts: 15 to 20 minutes, most of it Homebrew's installer and `brew bundle`.
- Every long command runs under `caffeinate`. The golden guest `fresh-27` is never booted: each Trial is a clone.

## Out of Scope

- **nix-darwin, chezmoi, hola, OpenBoot, and plain pieces with thin glue.** Each was weighed and not chosen.
- **Multiple profiles.** Every Mac gets the same Packages, Dotfiles and macOS settings.
- **Intel Macs and Linux.**
- **Continuous sync.** The Bootstrap is one-shot. A re-run is safe, and nothing runs on a schedule.
- **Parity with the Ansible version.** The lists were decided from zero.
- **The Mac App Store, full Xcode, containers and a Ruby toolchain.**
- **Pinned versions,** of mise or of any Package.
- **Agent config.** Settings, status line and skills for Claude Code, Codex CLI and pi belong to the owner's agent setup repos. The Bootstrap does not hand off to them, and the checklist does not name them.
- **VS Code config as a Dotfile.** Settings Sync carries it.
- **A test suite, a check script, and a Trial harness in the repo.** Trials end with the refactor.
- **A workflow that runs the Bootstrap.** CI runs lint only.
- **Making the SSH key, adding it to GitHub, and pinning GitHub's host key.** The first two are Steps by hand.
- **The sleep timers, the display settings, text size, tap to click and the Dock's icon size.**

## Further Notes

**Amended after the first Trial (2026-09-27).** AC-40 as first written had Appearance show Auto with no step by hand. On macOS 27, `AppleInterfaceStyleSwitchesAutomatically` written with `defaults` takes effect only at the next login: the first Trial showed Light until a logout, and `activateSettings -u` did not change that. The owner chose to have Appearance checked after the logout that the Steps by hand already ask for.

**Amended after the audit (2026-10-03).** AC-6 as first written named three commands that report a Mac's state. [#40](https://github.com/iamivanhx/macos-setup/issues/40) adds a fourth: a read-only comparison of `brew leaves --installed-on-request` and `brew list --cask` with the `Brewfile`, which lists the Packages from Homebrew that the `Brewfile` does not declare. On the target Mac it listed `shellcheck`. `brew bundle cleanup` is not that command: it uninstalls what it lists. The README's `brew bundle check` gains `--no-upgrade`, because without it the check also fails when a Package is only outdated. A re-run upgrades the Packages from Homebrew that are outdated, so it takes about a second only when nothing is outdated.

**Amended after the audit (2026-10-03).** AC-48 as first written had the lint command run only `shellcheck` and `bash -n` on `bootstrap.sh`, so a syntax error in `config.toml` or in the zsh Dotfiles was first found by a Bootstrap. [#41](https://github.com/iamivanhx/macos-setup/issues/41) extends it: `lint.sh` also parses `config.toml` with Python's `tomllib`, runs `zsh -n` on `dotfiles/zsh/zshrc` and `dotfiles/zsh/zprofile`, and runs `ghostty +validate-config --config-file=` on the Ghostty Dotfile when Ghostty is installed. The lint command exits non-zero when `config.toml` holds a TOML syntax error or `zshrc` holds a zsh syntax error. `tomllib` needs Python 3.11, and the target Mac's `python3` is Apple's 3.9.6. The owner chose to parse with `uv run --no-project --python '>=3.11'` when `uv` is on `PATH`, as on a Mac after a Bootstrap, and with plain `python3` otherwise, as on the runner, which has Python 3.12 and no uv. With `--config-file=`, `ghostty +validate-config` reads only the named file and not Ghostty's default files. It rejects `--config-default-files=false`. The workflow installs zsh before it calls the lint command, pins `actions/checkout` to a commit SHA and has `permissions: contents: read`. `.github/dependabot.yml` proposes updates to the workflow's actions weekly.

**Amended after the audit (2026-10-03).** User story 26, AC-26, AC-29, AC-39, AC-40 and AC-46 as first written had Raycast installed and given Command-Space, with Spotlight's shortcut turned off. The owner had never used Raycast, and on macOS 27 Spotlight (Command-Space), its clipboard history and the built-in window tiling do the three jobs it was picked for. With [#44](https://github.com/iamivanhx/macos-setup/issues/44) the owner chose to remove it. The `Brewfile` loses the `raycast` cask, so AC-26 holds 22 Packages, AC-29 and the Packages table seven casks, and the Solution 27 Packages. The setting that turned off Spotlight's shortcut, hotkey 64 of `com.apple.symbolichotkeys`, goes too, so AC-39 holds 17 settings, the Solution and the macOS settings 21, and AC-40 no longer has "Show Spotlight search" unticked. The last hook line drops `activateSettings -u` and keeps `killall Dock Finder || true`: hotkey 64 was the only keyboard shortcut the repo set, and `activateSettings -u` does not load Appearance (2026-09-27, above). The Step by hand that set Command-Space inside Raycast goes, so AC-46 holds five steps. The logout stays, because key repeat and Appearance still need it. User story 26 is dropped. mise does not undo a setting removed from its config, so on a Mac that already has Raycast, the owner runs `brew uninstall --cask raycast` and ticks "Show Spotlight search" again by hand.

**Amended after the audit (2026-10-03).** User story 25, AC-39's `persistent-apps` and AC-40's Dock as first written held four apps: Ghostty, Google Chrome, Visual Studio Code and 1Password. [#53](https://github.com/iamivanhx/macos-setup/issues/53) makes it six, in this order: Apps, Ghostty, Google Chrome, Visual Studio Code, 1Password, System Settings. Apps is macOS's app launcher, which replaced Launchpad. Both new apps are under `/System/Applications`, which mise accepts for the Dock. On the target Mac System Settings had been pinned by hand, so `mise bootstrap status` reported `persistent-apps` as differing with 5 items, and a re-run would have removed it. The owner chose to make both apps part of the setup. The Dock still holds none of Apple's other default apps.

**Amended when pi left the Bootstrap (2026-10-03).** User story 16, AC-28 and the Install channel table as first written had the Bootstrap install pi with its own installer. pi moves to a repo of its own ([#62](https://github.com/iamivanhx/macos-setup/issues/62)), the same split this spec makes for agent config, so the Bootstrap no longer installs it. User story 16, AC-28 and the Install channel table no longer cover pi: the row for the Package's own installer holds Claude Code only, and the note on pi's installer and its keypress no longer applies. The Solution's Packages go from 27 (after #44) to 26, and the Solution says so. A Mac that has pi keeps it, because the Bootstrap never removes a Package. The Steps by hand name neither pi nor its repo, as the Bootstrap does not hand off to the agent setup repos.

**Amended after the audit (2026-10-03).** AC-30 and AC-35 as first written named the Ghostty Dotfile `~/.config/ghostty/config`, and its file under `dotfiles/ghostty/` in AC-2 kept the name `config`. Ghostty 1.3 renamed its default file to `config.ghostty` and still reads the old name. [#37](https://github.com/iamivanhx/macos-setup/issues/37) places the Dotfile at `~/.config/ghostty/config.ghostty`, from `dotfiles/ghostty/config.ghostty`, so AC-2, AC-30 and AC-35 now mean that name. The audit also found an empty `config.ghostty` in `~/Library/Application Support/com.mitchellh.ghostty/` on the target Mac, made by Ghostty before the first real Bootstrap. Ghostty reads that file after the Dotfile, so what it holds wins, and Ghostty > Open Configuration opens it whenever it exists. Neither `git status` nor `mise bootstrap status` sees it. A `post-dotfiles` hook line now removes an empty `config.ghostty` or `config` from that folder, and leaves a non-empty one as it is: the run prints its path and says to move its settings into the Dotfile. It is not a macOS setting, so the count of macOS settings does not change. The old link `~/.config/ghostty/config` stays on the target Mac after the rename, and the owner removes it once.

**Amended after the audit (2026-10-03).** AC-39 as first written did not touch AirPlay Receiver, which macOS turns on by default. On the target Mac `lsof -nP -iTCP -sTCP:LISTEN` showed ControlCenter, the process behind AirPlay Receiver, listening on ports 5000 and 7000 on every network interface. Port 5000 is Flask's default, so a dev server there fails with "address already in use". The firewall does not stop it, because "Automatically allow built-in signed software" lets an Apple-signed listener through. Turning AirPlay Receiver off is CIS 2.3.1.2, Level 1, in mSCP's macOS 27 CIS Level 1 baseline as rule `system_settings_airplay_receiver_disable` ([rule](https://github.com/usnistgov/macos_security/blob/c1e6cf9c41d518d0456ab6a7f12a1a4d1f227715/src/mscp/data/rules/system_settings/system_settings_airplay_receiver_disable.yaml), [baseline](https://github.com/usnistgov/macos_security/blob/c1e6cf9c41d518d0456ab6a7f12a1a4d1f227715/src/mscp/data/baselines/macos/cis_lvl1_macos_27.0.yaml)). mSCP enforces it with a configuration profile, `allowAirPlayIncomingRequests` false in `com.apple.applicationaccess`, and the Bootstrap installs no profiles. With [#55](https://github.com/iamivanhx/macos-setup/issues/55) the owner chose to turn it off with the user setting instead: per-host `com.apple.controlcenter` `AirplayReceiverEnabled` false, an entry next to `BatteryShowPercentage`. The key is often written `AirplayRecieverEnabled`, but that spelling is not in macOS 27.0.1's ControlCenter, and `AirplayReceiverEnabled` is, next to `AirplayReceiverAdvertising` and `BatteryShowPercentage`. On the target Mac the key was absent, which means on. So AC-39 holds 18 settings, and the Solution and the macOS settings 22. Setups that write this key restart ControlCenter afterwards. A logout restarts it too, so the logout of the Steps by hand covers it. The key was not checked by toggling the setting in System Settings, and whether the ports close before that logout was not checked.

**Inferred by this spec.** No ticket decided these. Each is open to an amendment.

- The output of each Trial and of the first real Bootstrap is recorded as a comment on the pull request (AC-53, AC-55, AC-57). The tickets say that they run, not where the result is kept.
- The VS Code theme is step 9 of the migration order, after the first real Bootstrap and before the merge. [#23](https://github.com/iamivanhx/macos-setup/issues/23) left the place to this spec. The step does not gate the merge.
- The README says that `mise bootstrap status` run by hand needs the two Machine values (AC-6). The tickets record the fact as a trap.
- The first Trial also reaches the pause at the key check and a file at a Dotfile's path (AC-14, AC-17). [#23](https://github.com/iamivanhx/macos-setup/issues/23) says the first Trial can reach the pause. No ticket planned a Trial against an existing file.
- The prototype's Wrapper has a third override, for the checkout's path. No decision names it, and no criterion asks for it.

**Not verified when this spec was written.** The Trials and the checks on a real Mac cover most of these.

- The key step with 1Password itself, and what `ssh-add -L` returns while 1Password is locked.
- Signing through `op-ssh-sign` on the target Mac, and the form of the `agent.toml` entry, which comes from 1Password's documentation.
- The pause at the key check. The stand-in agent always held the key.
- What mise does at a real file where a Dotfile goes. The refusal is read from mise's docs.
- Whether macOS follows `~/Downloads` as the screenshot folder. The value is stored as that text. If it fails in the first Trial, it is fixed in the repo or joins the README's checks.
- The battery percentage and Touch ID for `sudo`. A guest has neither a battery nor Touch ID.
- A clone from GitHub over HTTPS, and the start command in the `curl … | bash` form.
- The Command Line Tools popup, which did not appear in the whole run.
- An interrupted run under the mise that Homebrew installs.
- A push over SSH after the remote is switched.
- Anything on screen in Ghostty: the prompt's colours, fzf's colours, and whether the `catppuccin-powerline` segments read well on the Latte palette.
- Whether `KeyRepeat = 2` is the fastest value of the slider on macOS 27.
- Whether the status-line work passes its tests. It is committed unverified.

**Traps the implementation meets.**

- An interrupted run leaves mise blocked, with the Dotfiles it placed removed, until `mise dot recover --keep-current --yes` is run. `mise dot recover` alone failed.
- mise needs a terminal for `sudo` and ignores `SUDO_ASKPASS`.
- In a Dotfile template, mise's `config_root` rendered empty. The prototype reads the Starship source by its path under the home directory.
- mise's template for the generated Starship file added one blank line in one trial and none in another.
- Homebrew refuses a formula from a non-official tap until it is trusted. The `Brewfile` names no tap.
- The target Mac is not a Fresh Mac: it has Homebrew and the Command Line Tools. Its first real Bootstrap does not exercise the start of a first run. The Trials do.
- A key pressed in a guest's window may be caught by the host: Command-Space and Shift-Command-3 are.

**Sources.** The decisions: [#10](https://github.com/iamivanhx/macos-setup/issues/10) Packages, [#11](https://github.com/iamivanhx/macos-setup/issues/11) git identity and SSH, [#13](https://github.com/iamivanhx/macos-setup/issues/13) Dotfiles, [#14](https://github.com/iamivanhx/macos-setup/issues/14) macOS settings, [#15](https://github.com/iamivanhx/macos-setup/issues/15) tooling, [#20](https://github.com/iamivanhx/macos-setup/issues/20) layout and start, [#21](https://github.com/iamivanhx/macos-setup/issues/21) proof, [#22](https://github.com/iamivanhx/macos-setup/issues/22) migration order, [#23](https://github.com/iamivanhx/macos-setup/issues/23) Steps by hand. The research behind them is in `docs/research/` once the refactor merges, and on the local `research/*` branches until then.
