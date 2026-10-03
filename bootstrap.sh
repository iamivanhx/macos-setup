#!/bin/bash
# The Bootstrap: takes a Fresh Mac to a set-up one. Safe to run again.
#
#   bash -c "$(curl -fsSL https://raw.githubusercontent.com/iamivanhx/macos-setup/main/bootstrap.sh)"
set -euo pipefail

REPO_URL="${BOOTSTRAP_REPO_URL:-https://github.com/iamivanhx/macos-setup.git}"
REPO_SSH_URL="git@github.com:iamivanhx/macos-setup.git"
REPO_DIR="$HOME/Projects/macos-setup"
AGENT_SOCK="${BOOTSTRAP_AGENT_SOCK:-$HOME/Library/Group Containers/2BUA8C4S2C.com.1password/t/agent.sock}"

step() { printf '\n==> %s\n' "$1"; }

# The first key in the agent whose comment is exactly $1, so not "$1 old" or "Work $1". A line
# of `ssh-add -L` is `<type> <key> <comment>`: the comment is the line without its first two
# fields. It fails when there is none: the key check pauses on that.
agent_key() {
  local key
  while IFS= read -r key; do
    if [[ "${key#* * }" == "$1" ]]; then echo "$key"; return 0; fi
  done < <(SSH_AUTH_SOCK="$AGENT_SOCK" ssh-add -L 2>/dev/null)
  return 1
}

main() {
  # Under `curl | bash` stdin is the script. Every prompt below needs the terminal.
  [[ -t 0 ]] || exec </dev/tty

  # Hold the Mac awake for as long as this script runs. Idle sleep breaks a long install.
  caffeinate -ims -w $$ &

  step "Hostname"
  if ! BOOTSTRAP_HOSTNAME="$(scutil --get HostName 2>/dev/null)"; then
    # Checked as it is typed: it becomes the LocalHostName, which Apple limits to these
    # characters, and the title of the SSH key, which the owner makes before that is set.
    local allowed='^[A-Za-z0-9]([A-Za-z0-9-]{0,61}[A-Za-z0-9])?$'
    while true; do
      read -r -p "Hostname for this Mac: " BOOTSTRAP_HOSTNAME
      [[ "$BOOTSTRAP_HOSTNAME" =~ $allowed ]] && break
      echo "Use 1 to 63 letters, digits and hyphens, with no hyphen first or last. Example: studio-2"
    done
  fi
  echo "$BOOTSTRAP_HOSTNAME"

  step "Homebrew, with the Command Line Tools"
  if [[ ! -x /opt/homebrew/bin/brew ]]; then
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  fi
  eval "$(/opt/homebrew/bin/brew shellenv)"

  step "This repo, at $REPO_DIR"
  # Over HTTPS: a Fresh Mac has no SSH access yet. git exists now: the Command Line Tools brought it.
  [[ -d "$REPO_DIR/.git" ]] || git clone "$REPO_URL" "$REPO_DIR"

  step "Packages from Homebrew"
  # Installs what is missing and leaves an outdated Package as it is: upgrading is `mise run upgrade`.
  brew bundle --no-upgrade --file "$REPO_DIR/Brewfile"

  step "This Mac's SSH key"
  local title="SSH Key ($BOOTSTRAP_HOSTNAME)" line
  until line="$(agent_key "$title")"; do
    cat <<EOF
1Password's SSH agent does not offer a key titled "$title". One of these is the cause:
  - 1Password is not signed in
  - 1Password is locked
  - the SSH agent is off: 1Password > Settings > Developer > Use the SSH agent
  - no key has that title: make one in 1Password, of type ED25519
Ctrl-C is safe here: a re-run picks up from this point.
EOF
    read -r -p "Press Return to look again. "
  done
  export BOOTSTRAP_HOSTNAME BOOTSTRAP_SSH_PUBLIC_KEY="${line% "$title"}"
  echo "$BOOTSTRAP_SSH_PUBLIC_KEY"
  # Access is by SSH from here on. The first clone was over HTTPS.
  git -C "$REPO_DIR" remote set-url origin "$REPO_SSH_URL"

  step "Dotfiles, macOS settings, and the other Packages"
  # This repo is the global mise config, so `mise bootstrap status` reads from any directory.
  mkdir -p "$HOME/.config"
  if [[ -e "$HOME/.config/mise" && ! -L "$HOME/.config/mise" ]]; then
    echo "$HOME/.config/mise exists and is not a link to this repo. Move it away and run again."; exit 1
  fi
  ln -sfn "$REPO_DIR" "$HOME/.config/mise"
  if ! mise bootstrap --yes; then
    cat <<EOF

The Bootstrap stopped. Fix what it reports and run $REPO_DIR/bootstrap.sh again.
If mise says "interrupted file recovery needs attention", run this first:

  mise dot recover --keep-current --yes
EOF
    exit 1
  fi
}

main "$@"
