# Coding standards

The conventions of this repo. Each rule names a file that follows it: read that file for the pattern. Terms in capitals are defined in `CONTEXT.md`, and the decisions behind the rules are in `docs/specs/replace-ansible.md`.

## Shell

- A script starts with `#!/bin/bash` and `set -euo pipefail`, and is clean under `shellcheck`. Follows it: `bootstrap.sh`, `lint.sh`.
- The Wrapper keeps its steps in one function, `main`, below the helpers it calls, such as `step` and `agent_key`. The file ends with one call, `main "$@"`, though `main` reads no arguments. Follows it: `bootstrap.sh`.
- A prompt reads the terminal. Under `curl | bash` stdin is the script, so the Wrapper runs `exec </dev/tty` before it asks anything. Follows it: `bootstrap.sh`.
- The Wrapper reads no arguments. An override is a `BOOTSTRAP_*` environment variable that falls back to the real value when unset, as `BOOTSTRAP_REPO_URL` and `BOOTSTRAP_AGENT_SOCK` do. The Machine values reach mise the same way, as `BOOTSTRAP_HOSTNAME` and `BOOTSTRAP_SSH_PUBLIC_KEY`. Follows it: `bootstrap.sh`, `config.toml`.

## Hook lines

- A hook line that sets a macOS setting reads the state first and acts only when the setting is off: `check || sudo set`, or `check || set` where the command asks for the password itself. Hooks run on every Bootstrap, so a re-run asks for no password when every setting holds. Follows it: the `post-defaults` hooks of `config.toml`.
- A hook line hands a Machine value to a command as a quoted argument, such as `"$BOOTSTRAP_HOSTNAME"`. Nothing builds a command string from `config.toml` or a Machine value and runs it with `eval`: the only `eval` in the repo runs the shell setup that Homebrew, mise, Starship or zoxide prints. Follows it: `config.toml`, `bootstrap.sh`, `dotfiles/zsh/zprofile`, `dotfiles/zsh/zshrc`.

## One change is one edit in one place

- A Package from Homebrew is one line of `Brewfile`. Follows it: `Brewfile`.
- Any other Package, a Dotfile or a macOS setting is one entry in `config.toml`. A Dotfile's file goes under `dotfiles/`. A Package from its own installer is the exception: it takes one line in the task `bootstrap` and, if it has an update command, one in the task `upgrade`, as Claude Code does. Follows it: `config.toml`.
- A Step by hand is one line of `steps-by-hand.md`. Follows it: `steps-by-hand.md`.

## Dotfiles

- A Dotfile is a plain file under its own name, with no hidden or `dot_` name, in one directory per app under `dotfiles/`. Follows it: `dotfiles/`, and the `[dotfiles]` table of `config.toml`.
- The Bootstrap runs no command to write a Dotfile. A template is only for a Local file. Follows it: the template entries of `config.toml`.

## Machine values

- A Machine value is asked for or looked up during the run and never stored in this repo. The Bootstrap writes it into a Local file through a template. Follows it: `bootstrap.sh` (asks for the hostname, reads the key from 1Password's SSH agent), `[bootstrap.secrets]` in `config.toml`, `dotfiles/git/config.local.tera`, `dotfiles/1password/agent.toml.tera`.

## Versions

- No version of mise or of any Package is pinned. A `Brewfile` line names no version, and `config.toml` asks for `lts` or `latest`. Follows it: `Brewfile`, `config.toml`.

## Proof

- The real Bootstrap is the proof. A break is fixed in the checkout and the Wrapper is re-run. The repo holds no test suite, no check script and no Trial harness: Trials were for the refactor only (spec AC-50). Follows it: `README.md`.
- CI runs lint only. The lint command is defined once, in `lint.sh`, and the workflow calls it. Follows it: `lint.sh`, `.github/workflows/lint.yml`.
- Tautological tests considered harmful. Proof observes what a run leaves on the Mac or prints on the terminal, read with the tools' own reports. It never reads how the Wrapper or `config.toml` is written. Follows it: the Testing Decisions of `docs/specs/replace-ansible.md`.

## Docs

- Use the terms of `CONTEXT.md`, capitalised, and none of the synonyms it lists to avoid. Follows it: `README.md`, `docs/specs/replace-ansible.md`.
- Write plain, short sentences, in the voice of the README. Follows it: `README.md`.
- The spec and the research notes are dated records. Each research note says when it was researched. A later finding is added with its date, as a new note that builds on the old one, which stays as it was, or as a dated amendment under the spec's Further Notes. A criterion of the spec is rewritten in place only when its ticket asks for it, and the amendment then records the first wording. A criterion once rewritten is kept current. Otherwise the criterion's old text stays, and the amendment says what changed. Follows it: `docs/research/ghostty-eye-comfort.md`, the Further Notes of `docs/specs/replace-ansible.md`.
