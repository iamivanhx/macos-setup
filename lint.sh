#!/bin/bash
# The lint command: checks the Wrapper, config.toml and the zsh Dotfiles. GitHub runs it on every push.
set -euo pipefail
cd "$(dirname "$0")"

bash -n bootstrap.sh
shellcheck bootstrap.sh

# tomllib needs Python 3.11. The Mac's python3 is older, so the Mac parses with uv's Python.
# The runner has no uv, and its python3 is new enough.
parse_toml='import sys, tomllib; tomllib.load(open(sys.argv[1], "rb"))'
if command -v uv >/dev/null; then
  uv run --no-project --python '>=3.11' python -c "$parse_toml" config.toml
else
  python3 -c "$parse_toml" config.toml
fi

zsh -n dotfiles/zsh/zshrc
zsh -n dotfiles/zsh/zprofile

# Ghostty checks only the named file, not its default files. The runner has no Ghostty.
if command -v ghostty >/dev/null; then
  ghostty +validate-config --config-file=dotfiles/ghostty/config
fi
