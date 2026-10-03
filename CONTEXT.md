# macOS Setup

Automated setup of a fresh Mac: what gets installed, which config files land in the home directory, and which system preferences are applied.

## Language

**Bootstrap**:
The single run that takes a fresh Mac to a fully set-up one. Re-running it is safe, but it is not a continuous sync.
_Avoid_: Provisioning, convergence, sync

**Wrapper**:
The script that starts a bootstrap and runs Homebrew and mise in order. It is not the bootstrap, which is the run, and not `mise bootstrap`, which is a command the wrapper calls.
_Avoid_: Installer, entry point, bootstrap script

**Fresh Mac**:
A Mac with macOS newly installed and nothing set up beyond what the bootstrap itself requires.
_Avoid_: Clean machine, new machine

**Trial**:
A whole bootstrap run in a disposable virtual machine that starts as a fresh Mac. It proves that the bootstrap works before a real Mac meets it.
_Avoid_: Test run, dry run, VM test

**Package**:
Software the bootstrap installs, whether a command-line tool or an app.
_Avoid_: Dependency, tool, formula (when meaning any installed software)

**Install channel**:
The source a package is installed from, such as Homebrew or the package's own installer. A language runtime is a package like any other, whatever its install channel.
_Avoid_: Package manager, install method, source

**Upgrade**:
A deliberate command, `mise run upgrade`, that brings every package on the Mac to its newest version through each install channel, whether this repo declares the package or not. It is never part of the bootstrap, and a re-run of the wrapper upgrades nothing.
_Avoid_: Update, sync, re-run (when meaning an upgrade)

**Dotfile**:
A config file in the home directory that is kept in this repo and put in place by the bootstrap.
_Avoid_: Config, rc file

**Machine value**:
A value that differs from one Mac to the next, such as the hostname. The bootstrap asks for it or looks it up. It is never stored in this repo.
_Avoid_: Variable, host var, secret

**Local file**:
An untracked file in the home directory that a dotfile reads when it exists. It holds machine values or the owner's own additions, and is never kept in this repo.
_Avoid_: Override, private dotfile

**macOS setting**:
A system preference, such as Dock or Finder behaviour, that the bootstrap applies.
_Avoid_: Default, preference, config

**Step by hand**:
Something the owner does to finish setting up a Mac because the bootstrap cannot do it, such as signing in to an app or confirming the default browser. A check that the owner makes after a bootstrap is not a step by hand, and neither is a step done once for the migration.
_Avoid_: Manual step, post-install step, checklist item
