# macos-setup

This repo sets up a Fresh Mac: its Packages, its Dotfiles and its macOS settings. One command starts a Bootstrap. A re-run is safe, and it is how you check and repair a Mac: it installs what is missing, sets back what drifted, and upgrades only what a missing Package needs. Upgrading is a command of its own, `mise run upgrade`.

It is written for the owner's Macs, on Apple Silicon with macOS 27. Every Mac gets the same setup.

A Fresh Mac is installed on APFS (Case-sensitive), one of [Apple's APFS formats](https://support.apple.com/guide/disk-utility/file-system-formats-dsku19ed921c/mac), by choice: it matches Linux, where code and CI run, so a file named with the wrong case fails here as it would in CI. The trade-off is that some apps refuse a case-sensitive volume, and [Adobe's installers](https://helpx.adobe.com/download-install/apps/troubleshoot/error-codes-1-99/error22.html) are the documented case. For such an app, if it can install on another volume, add a separate volume in plain APFS, which is not case-sensitive, to the same container rather than erase the Mac: each volume has its own format and shares the container's space. That does not help an app that checks the startup volume, as Adobe's installers do.

## How it works

The Wrapper, `bootstrap.sh`, runs two standard tools in order:

- **Homebrew** installs the Packages listed in `Brewfile`.
- **mise bootstrap** does everything else from `config.toml`: the Dotfiles, the Local files, the macOS settings, Node, `sfw`, Python and Claude Code.

| Path | What it holds |
|---|---|
| `bootstrap.sh` | The Wrapper |
| `Brewfile` | The Packages that come from Homebrew |
| `config.toml` | Everything else. On a Mac it is also the global mise config |
| `steps-by-hand.md` | The Steps by hand, printed at the end of every run that succeeds |
| `dotfiles/` | The Dotfiles, one directory per app, each file under its own name |
| `docs/research/` | The research notes behind the decisions |

On a Mac the repo is a checkout at `~/Projects/macos-setup`, and `~/.config/mise` is a link to it. The Dotfiles in the home directory are links into the checkout, so an edit to one shows in `git status` there.

The hostname and this Mac's SSH public key are Machine values: a run asks for them or looks them up, and never stores them in this repo. The Bootstrap writes them into two Local files, `~/.config/git/config.local` and `~/.config/1Password/ssh/agent.toml`. Two Local files are yours to write, and the Bootstrap never creates or touches them. Your own additions to the shell go in `~/.zshrc.local`. This Mac's own Ghostty values, such as a different `font-size` on a laptop, go in `~/.config/ghostty/config.local`. Ghostty reads it after the Ghostty Dotfile, so its values win, and a Mac without one runs the Ghostty Dotfile as it is.

## Start a Bootstrap

In Terminal on a Fresh Mac:

```sh
bash -c "$(curl -fsSL https://raw.githubusercontent.com/iamivanhx/macos-setup/main/bootstrap.sh)"
```

A first run takes about 8 minutes and holds the Mac awake while it runs. It asks five times:

1. The hostname, at `Hostname for this Mac:`. A re-run reads it back and does not ask.
2. Your password, at Homebrew's installer.
3. Return, at Homebrew's installer, to go on.
4. Your password at `sudo`, during `mise bootstrap`, for the Mac's names, the firewall, stealth mode and Touch ID for `sudo`.
5. Your password at the screen-lock prompt, which sets the lock delay.

**The Command Line Tools popup.** Homebrew's installer brings the Command Line Tools, and most of the time no window shows. If a popup asks to install the command line developer tools, click **Install** (not Get Xcode), then **Agree**, and **Done** once it has finished. Then press any key in Terminal, where Homebrew's installer waits for you.

**The pause at the key check.** After `brew bundle`, the Wrapper looks in 1Password's SSH agent for a key titled `SSH Key (<hostname>)`. On a Fresh Mac it is not there yet, so the Wrapper pauses, names the four possible causes and waits for Return. Open 1Password, which `brew bundle` has just installed, sign in, turn on the SSH agent, and make an SSH key of type ED25519 with that title. Then press Return. The Wrapper looks again after each Return and goes on once the key is there. Ctrl-C is safe during the pause: a re-run picks up from there.

At the end of the run the Wrapper prints the Steps by hand from [`steps-by-hand.md`](steps-by-hand.md). Every run that succeeds prints them, whether or not you have done them.

## Read a Mac's state

The tools' own reports tell a Mac's state. This repo has no check script.

- **A re-run of the Wrapper**, `~/Projects/macos-setup/bootstrap.sh`. It installs a Package of the `Brewfile` that is missing and upgrades none that is outdated, because the Wrapper runs `brew bundle --no-upgrade`. Installing a missing Package can still upgrade a Package it depends on. A re-run takes about a second when nothing is missing, asks nothing, and sets back what drifted. It asks for the `sudo` password only to set back a setting that needs it.
- **`mise bootstrap status --missing`**. It exits 1 when a Dotfile, a macOS setting or a tool of `config.toml` is out of step. Run by hand, it needs the two Machine values in the environment, `BOOTSTRAP_HOSTNAME` and `BOOTSTRAP_SSH_PUBLIC_KEY`. Without them it reports the two Local files as out of step. The four settings that need `sudo` are not in its report.

  ```sh
  cd ~
  BOOTSTRAP_HOSTNAME="$(scutil --get HostName)" \
  BOOTSTRAP_SSH_PUBLIC_KEY="$(git config --global --includes user.signingKey)" \
  mise bootstrap status --missing
  ```

- **`brew bundle check --no-upgrade --file ~/Projects/macos-setup/Brewfile`**. It exits 1 when a Package of the `Brewfile` is not installed, and `--verbose` names it. When every one is installed it prints `The Brewfile's dependencies are satisfied.` Without `--no-upgrade` it also fails when a Package is only outdated.
- **The Packages from Homebrew that the `Brewfile` does not declare**, such as one installed by hand. This prints one per line, and nothing when there are none. It only reads: it removes nothing. A formula that another installed Package depends on is not listed.

  ```sh
  comm -23 <({ brew leaves --installed-on-request; brew list --cask; } | sort) \
    <(brew bundle list --all --file ~/Projects/macos-setup/Brewfile | sort)
  ```

  `brew bundle cleanup` is not a check: it uninstalls what it lists.

### Checks on a real Mac

No tool reports these. Check them after the first Bootstrap on a real Mac:

- [ ] The menu bar shows the battery percentage, after one logout.
- [ ] `sudo` in a new terminal accepts Touch ID.
- [ ] The key step with 1Password: with 1Password unlocked and its SSH agent on, the key check finds `SSH Key (<hostname>)` with no pause, and `ssh -T git@github.com` greets your GitHub account.
- [ ] A push over SSH: `git push` from the checkout succeeds, and GitHub shows the pushed commit as verified.

## Upgrade a Mac

A re-run upgrades only what a missing Package needs. To bring the Packages to their newest versions, run this from any directory:

```sh
mise run upgrade
```

It covers every Package that Homebrew, uv and pnpm have installed, whether this repo declares it or not, such as one installed by hand, and the tools of `config.toml` and Claude Code. A Package from another installer of its own, such as pi, is not upgraded. It runs these in order and stops at the first that fails:

- **Homebrew**: `brew update`, then `brew upgrade --greedy-auto-updates`. It upgrades every formula and cask, with the casks that update themselves, such as Ghostty, Google Chrome, Visual Studio Code and 1Password. Homebrew may quit an app to upgrade it and opens it again after, but never quits the terminal it runs in.
- **mise**: `mise upgrade`, for the tools of `config.toml`, Node and `sfw`. A tool added with `mise use -g` lands in `config.toml`, so it is covered too. `lts` and `latest` stay as they are written.
- **uv**: `uv python upgrade`, then `uv tool upgrade --all`.
- **pnpm**: `pnpm update -g`, for the global Packages. It needs pnpm's global bin directory on `PATH`, which `~/.zprofile` adds, so run the Upgrade in a new terminal after a Bootstrap.
- **Claude Code**: `claude update`.

A second run straight after the first changes nothing. Nothing runs the Upgrade on a schedule, and a Bootstrap never runs it.

## Fix a break

A break during a Bootstrap is fixed on the spot, and the Wrapper is re-run.

- **Once the checkout exists**, edit the file in `~/Projects/macos-setup` and re-run the Wrapper from there:

  ```sh
  ~/Projects/macos-setup/bootstrap.sh
  ```

  This is the command that the Wrapper's failure message names, with your home folder written out. A re-run uses the checkout as it is, on the branch it is on, and does not clone again. Commit and push the fix from the checkout once the key step works: the push goes over SSH with this Mac's key.

- **Before the checkout exists**, in Homebrew's installer or the clone, fix the file on GitHub with the web editor, commit it to `main`, and run the start command again.

- **An interrupted run** leaves mise blocked. If mise says `interrupted file recovery needs attention`, run this, then re-run the Wrapper:

  ```sh
  mise dot recover --keep-current --yes
  ```

- **A file already where a Dotfile goes** stops the Bootstrap: mise lists the path and leaves the file as it is. Move the file away and re-run. The Wrapper stops the same way when `~/.config/mise` exists and is not a link.

## Change the setup

Each change is one edit in one place, then a re-run:

- A Package from Homebrew is one line of `Brewfile`.
- Any other Package, a Dotfile or a macOS setting is an entry in `config.toml`. A Dotfile's file goes under `dotfiles/`.
- A Step by hand is one line of `steps-by-hand.md`.

## The Ansible version

The Ansible version of this repo lives under the tag `ansible-final`.

## License

MIT. See [`LICENSE`](LICENSE).
