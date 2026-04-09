# macos-setup

Automated macOS developer machine setup. One command bootstraps a fresh Mac
with Homebrew, CLI tools, GUI applications, language toolchains, global CLIs,
Git identity + SSH key, a themed terminal, and sensible macOS defaults.

Everything is driven by Ansible roles; everything is idempotent.

## Overview

Run one command on a freshly installed macOS machine and end up with a fully
configured developer environment: Xcode, Homebrew, formulae, casks, pnpm +
Node LTS, uv, Claude Code, Socket CLI, GitHub Copilot CLI, Starship prompt
with Nerd Font, git identity with an ed25519 SSH key auto-uploaded to
GitHub, and ~25 developer-friendly macOS preferences.

The system is a bash bootstrap script that installs Ansible and clones this
repo, then hands off to an Ansible playbook split into focused roles. Each
role can be re-run independently via `--tags`.

## Prerequisites

- **Apple Silicon Mac** (M1/M2/M3/M4). Intel is untested.
- **macOS Tahoe (26.x)** or later. Earlier versions will mostly work but some
  macOS defaults keys differ (notably the battery percentage toggle).
- **Signed into the Mac App Store** with your Apple ID before you run the
  script — the `xcode` role installs Xcode via `mas` and will pause for you
  to sign in if you are not.
- **Admin (sudo) access** on the machine.
- A **GitHub account** (optional but recommended — the `git_setup` role
  uploads your new SSH key via `gh ssh-key add`).

## Quick Start

Run this on the fresh Mac:

```bash
curl -fsSL https://raw.githubusercontent.com/iamivanhx/macos-setup/main/bootstrap.sh | bash
```

The script will prompt for:

1. **Hostname** — the computer name (letters, digits, hyphens).
2. **Git user name** — used for `git config --global user.name`.
3. **Git email** — used for `git config --global user.email`.

Then it will ask for your sudo password once, install Xcode Command Line
Tools, install Homebrew, install Ansible, clone this repo to
`~/macos-setup`, and run the full playbook. Expect ~30–60 minutes on a
fresh machine (most of which is Xcode and GUI app downloads).

## What Gets Installed

| Category | Tool | Installed via |
|---|---|---|
| **CLI** | git, gh, vim, mas, starship, curl, wget, jq, tree, ripgrep, fd, bat, htop, tldr | Homebrew formula |
| **CLI** | uv (Python) | Homebrew formula |
| **CLI** | copilot (GitHub Copilot CLI) | Homebrew formula `copilot-cli` |
| **CLI** | pnpm | Standalone installer (`https://get.pnpm.io/install.sh`) |
| **CLI** | Node LTS | `pnpm env use --global lts` |
| **CLI** | claude (Claude Code) | Official installer (`https://claude.ai/install.sh`) |
| **CLI** | socket (`@socketsecurity/cli`) | `pnpm add -g` |
| **CLI** | sfw (Socket Firewall) | `pnpm add -g` |
| **GUI** | 1Password, Google Chrome, Discord, Obsidian, Visual Studio Code, iTerm2 | Homebrew cask |
| **GUI** | Xcode | Mac App Store via `mas` |
| **Font** | Hack Nerd Font | Homebrew cask (`font-hack-nerd-font`) |
| **Shell** | Starship prompt, gruvbox-rainbow preset, init line in `~/.zshrc` | `starship preset` + `lineinfile` |
| **Git** | Global user.name, user.email, ed25519 SSH key, ssh-agent (Keychain), `gh ssh-key add` | `community.general.git_config` + `ssh-keygen` + `gh` |
| **macOS** | ~25 developer defaults (Finder, Dock, Keyboard, Screenshots, Xcode, Time Machine) | `community.general.osx_defaults` |

### Post-install manual steps

- **Battery percentage in the menu bar**: System Settings → Control Center →
  Battery → Show Percentage. This cannot be scripted on macOS Ventura+ —
  the value lives inside an opaque binary blob under
  `~/Library/Preferences/ByHost/com.apple.controlcenter.bentoboxes.*.plist`
  and `defaults write com.apple.controlcenter BatteryShowPercentage` is
  silently ignored.
- **Log out / reboot** for some keyboard and input settings to apply to
  already-running apps.

## Customization

Tool lists live in `group_vars/all.yml`. Add or remove entries to tailor
the setup to your preferences. Example:

```yaml
homebrew_formulae:
  - git
  - gh
  - starship
  - jq
  - my-extra-tool     # ← added

homebrew_casks:
  - 1password
  - google-chrome
  - my-extra-app      # ← added

npm_global_packages:
  - "@socketsecurity/cli"
  - sfw
  - "@my-org/my-cli"  # ← added
```

Other useful knobs in the same file:

- `nerd_font_cask` — the Homebrew Cask name for your preferred Nerd Font
- `pnpm_install_url` — pnpm standalone installer URL
- `claude_code_install_url` — Claude Code official installer URL
- `xcode_app_store_id` — Mac App Store ID for Xcode (rarely needs changing)

Role-specific knobs live in `roles/<role>/defaults/main.yml`. For example,
the verify role's check lists are in `roles/verify/defaults/main.yml`.

## Running Specific Roles

Each role is tagged with its own name. Run just one role:

```bash
# Re-apply macOS system defaults only
ansible-playbook playbook.yml --tags macos_defaults

# Re-run homebrew formulae install
ansible-playbook playbook.yml --tags homebrew

# Re-run the git identity + SSH key + gh auth flow
ansible-playbook playbook.yml --tags git_setup

# Run the read-only diagnostic report
ansible-playbook playbook.yml --tags verify

# Re-install pnpm globals
ansible-playbook playbook.yml --tags npm_globals
```

Combine tags with a comma:

```bash
ansible-playbook playbook.yml --tags homebrew,cask_apps,terminal
```

The roles are: `homebrew`, `cask_apps`, `xcode`, `languages`, `npm_globals`,
`git_setup`, `terminal`, `macos_defaults`, `verify`.

## Re-running

Re-runs are safe and idempotent:

- **Homebrew formulae / casks / Mac App Store apps** — already-installed
  packages are skipped.
- **pnpm globals** — a pre-check (`pnpm list -g --parseable`) gates the
  install loop; `ignore_errors: true` means a single package failure
  doesn't block the rest.
- **Git identity** — `community.general.git_config` compares before
  writing.
- **SSH key** — if `~/.ssh/id_ed25519` already exists, the role pauses and
  asks whether to **skip** (default, press ENTER) or **overwrite** (type
  `overwrite`). Existing keys are never silently clobbered. `gh ssh-key
  add` tolerates "already exists" responses so a previously-uploaded key
  is a no-op.
- **Starship config** — `~/.config/starship.toml` is generated with a
  `creates:` guard, so if you customize it by hand your edits survive
  re-runs.
- **zshrc Starship init line** — `lineinfile` uses exact-match, no
  duplication.
- **macOS defaults** — `community.general.osx_defaults` compares each key
  before writing; handlers (`killall Finder/Dock/SystemUIServer`) only
  fire when something actually changed.

To see what's currently present vs missing without changing anything, run
the `verify` role:

```bash
ansible-playbook playbook.yml --tags verify
```

## Troubleshooting

### Not signed into the App Store (Xcode fails)

The `xcode` role uses `mas` to install Xcode from the Mac App Store. If you
are not signed in, the role pauses and asks you to sign in via the App
Store app, then press ENTER to continue. If you skip the pause, the role
fails loudly with a clear message telling you to sign in and re-run with
`--tags xcode`.

### pnpm / Node not on PATH

pnpm installs itself at `~/.local/share/pnpm/pnpm` and does **not**
automatically add that directory to your shell PATH. The playbook uses
absolute paths internally so roles always find pnpm, but after the
playbook finishes you will need to open a fresh terminal or source the
pnpm shell init that the pnpm installer wrote to `~/.zshrc`. If `pnpm`
is not on PATH in a new terminal, run `pnpm setup` once and open a new
terminal.

### macOS defaults not taking effect (need logout)

Some macOS preferences — especially keyboard, press-and-hold, and spelling
substitution — only apply to apps started **after** the default was
written. Log out and back in (or restart) to be sure every running app
picks up the new values. Finder/Dock/SystemUIServer are automatically
restarted by role handlers, so those categories take effect immediately.

### Ansible Galaxy collection errors

If `ansible-galaxy collection install -r requirements.yml` fails, it is
almost always a transient network issue. Re-run `bootstrap.sh` or just
that line. The collections resolve from Ansible Galaxy's public index,
which occasionally rate-limits or has regional outages.

### gh is not authenticated

The `git_setup` role runs `gh auth status` first. If `gh` is not
authenticated, the role pauses and asks you to open another terminal and
run `gh auth login` (GitHub.com → HTTPS → authenticate via web browser).
Once `gh auth status` reports success in the other terminal, press ENTER
in the playbook terminal to continue. If you skip the pause, the role
fails clearly and tells you to re-run with `--tags git_setup` after
authenticating.

### Homebrew Cask name changed upstream

macOS Cask names change occasionally (fonts especially). If a cask fails
to install because the name no longer exists, update the relevant entry
in `group_vars/all.yml` — for fonts, `nerd_font_cask` — and re-run with
the role's tag.

## Project Structure

```
.
├── README.md              # you are here
├── LICENSE                # MIT
├── bootstrap.sh           # curl | bash entry point; installs Xcode CLT,
│                          # Homebrew, Ansible, clones this repo, runs
│                          # the playbook with extra-vars
├── ansible.cfg            # Ansible defaults (local connection, inventory
│                          # path, interpreter_python=auto_silent)
├── playbook.yml           # Top-level play; lists every role with its
│                          # matching tag
├── requirements.yml       # Ansible Galaxy collection dependencies
│                          # (community.general)
├── inventory/
│   └── hosts.yml          # localhost with ansible_connection=local
├── group_vars/
│   └── all.yml            # Tool lists: homebrew_formulae,
│                          # homebrew_casks, npm_global_packages,
│                          # nerd_font_cask, xcode_app_store_id,
│                          # pnpm_install_url, claude_code_install_url
├── roles/
│   ├── homebrew/          # brew + formulae
│   ├── cask_apps/         # GUI apps
│   ├── xcode/             # mas + Xcode + license accept
│   ├── languages/         # uv, pnpm, Node LTS
│   ├── npm_globals/       # Claude Code + pnpm globals
│   ├── git_setup/         # git identity, SSH key, gh auth, ssh-key add
│   ├── terminal/          # Nerd Font, Starship preset, zshrc init
│   ├── macos_defaults/    # ~25 defaults + Finder/Dock/SystemUIServer
│   │                      # restart handlers
│   └── verify/            # read-only diagnostic report
└── tests/                 # Python unittest suite that validates the
                           # structure of every role, its tasks, and
                           # the bootstrap script
```

## Adding New Tools

### Adding a new Homebrew formula

1. Edit `group_vars/all.yml` and append the formula name to `homebrew_formulae`.
2. Run `ansible-playbook playbook.yml --tags homebrew` to install it.
3. (Optional) Add the binary name to `roles/verify/defaults/main.yml`
   under `verify_cli_tools` so the verify role confirms it installed.

### Adding a new Homebrew cask

1. Edit `group_vars/all.yml` and append the cask name to `homebrew_casks`.
2. Run `ansible-playbook playbook.yml --tags cask_apps`.
3. (Optional) Add the `.app` name to
   `roles/verify/defaults/main.yml` → `verify_gui_apps`.

### Adding a new pnpm global

1. Edit `group_vars/all.yml` and append the package name to
   `npm_global_packages`.
2. Run `ansible-playbook playbook.yml --tags npm_globals`.
3. (Optional) Add the installed binary name to
   `roles/verify/defaults/main.yml` → `verify_cli_tools`.

### Adding a new macOS default

1. Edit `roles/macos_defaults/tasks/main.yml` and add a new task using
   `community.general.osx_defaults`. Model it after an existing task in
   the same category.
2. If the setting requires a service restart, add `notify: restart Finder`
   (or Dock, or SystemUIServer) to the task.
3. Run `ansible-playbook playbook.yml --tags macos_defaults`.

### Adding a new role

1. Create `roles/<new_role>/tasks/main.yml` with at least one task.
2. Add `roles/<new_role>/defaults/main.yml` if the role has configurable
   data.
3. Add the role to `playbook.yml` with a matching `tags:` entry.
4. Add a test file under `tests/test_<new_role>_role.py` that asserts the
   structural contract of the role's tasks.
