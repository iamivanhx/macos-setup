#!/usr/bin/env bash
set -euo pipefail

# bootstrap.sh — Set up a fresh macOS machine and hand off to Ansible.
#
# Usage (direct):  ./bootstrap.sh
# Usage (piped):   curl -fsSL <url> | bash
#
# Environment variables:
#   MACOS_SETUP_DIR          Target clone directory (default: ~/macos-setup)
#   MACOS_SETUP_REPO_URL     Git URL of this repo
#   HOMEBREW_INSTALL_URL     Homebrew installer URL (override for testing)
#   XCODE_WAIT_ATTEMPTS      Max 5-second polls for CLT install (default: 120)
#   PROMPT_INPUT_DEVICE      Input device for prompts (default: /dev/tty; override in tests)

readonly LOCK_FILE="/tmp/macos-bootstrap.lock"

# ── Status output ─────────────────────────────────────────────────────────────

info()    { printf '\033[0;34m[INFO]\033[0m  %s\n' "$*"; }
success() { printf '\033[0;32m[✓]\033[0m     %s\n' "$*"; }
warn()    { printf '\033[0;33m[WARN]\033[0m  %s\n' "$*" >&2; }
error()   { printf '\033[0;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

# ── Input validation ──────────────────────────────────────────────────────────

# Returns 0 if the hostname is valid (letters, digits, hyphens; 1-63 chars).
is_valid_hostname() {
    local hostname="$1"
    [[ "$hostname" =~ ^[A-Za-z0-9][A-Za-z0-9-]{0,62}$ ]]
}

# ── Prompt helpers ────────────────────────────────────────────────────────────

# Read a non-empty value, retrying until the user provides one.
# Reads from PROMPT_INPUT_DEVICE (default /dev/tty) so it works when piped from curl.
# Opens the device once so sequential empty-line skips work correctly with files
# (used in tests) as well as with /dev/tty.
prompt_required_tty() {
    local prompt_text="$1"
    local input_device="${PROMPT_INPUT_DEVICE:-/dev/tty}"
    local value=""
    # Use FD 3 (compatible with bash 3.2+) so sequential reads advance through
    # the stream; opening the device once avoids file-rewind on each read call.
    exec 3<"$input_device"
    while [[ -z "$value" ]]; do
        IFS= read -r -p "$prompt_text" value <&3 || break
    done
    exec 3<&-
    printf '%s' "$value"
}

# ── Bootstrap steps ───────────────────────────────────────────────────────────

set_hostname() {
    local hostname="$1"
    if ! is_valid_hostname "$hostname"; then
        error "Invalid hostname '${hostname}'. Use only letters, digits, and hyphens (1-63 chars, must start with alphanumeric)."
    fi
    info "Setting hostname to '${hostname}'..."
    sudo scutil --set ComputerName  "$hostname"
    sudo scutil --set HostName      "$hostname"
    sudo scutil --set LocalHostName "$hostname"
    success "Hostname set to '${hostname}'"
}

install_xcode_clt() {
    if xcode-select -p &>/dev/null; then
        success "Xcode CLT already installed"
        return 0
    fi
    info "Installing Xcode Command Line Tools..."
    xcode-select --install 2>/dev/null || true

    local max_attempts="${XCODE_WAIT_ATTEMPTS:-120}"
    local attempt=0
    while ! xcode-select -p &>/dev/null; do
        if (( attempt >= max_attempts )); then
            warn "Timed out waiting for Xcode CLT — install may still be in progress"
            return 0
        fi
        (( ++attempt ))
        sleep 5
    done
    success "Xcode CLT installed"
}

install_homebrew() {
    if command -v brew &>/dev/null; then
        success "Homebrew already installed"
        return 0
    fi
    info "Installing Homebrew..."
    local installer_url="${HOMEBREW_INSTALL_URL:-https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh}"
    bash -c "$(curl -fsSL "$installer_url")"
    success "Homebrew installed"
}

ensure_homebrew_on_path() {
    if command -v brew &>/dev/null; then
        return 0
    fi
    if [[ -x /opt/homebrew/bin/brew ]]; then
        eval "$(/opt/homebrew/bin/brew shellenv)"
    elif [[ -x /usr/local/bin/brew ]]; then
        eval "$(/usr/local/bin/brew shellenv)"
    fi
}

# install_brew_package <binary-name> <brew-package-name>
install_brew_package() {
    local binary="$1"
    local package="$2"
    if command -v "$binary" &>/dev/null; then
        success "$package already installed"
        return 0
    fi
    info "Installing ${package}..."
    brew install "$package"
    success "$package installed"
}

clone_or_update_repo() {
    local repo_url="$1"
    local target_dir="$2"
    if [[ -d "$target_dir" ]]; then
        info "Repo already cloned — syncing to remote HEAD..."
        git -C "$target_dir" fetch --prune origin
        git -C "$target_dir" reset --hard FETCH_HEAD
        success "Repo updated at ${target_dir}"
    else
        info "Cloning repo to ${target_dir}..."
        git clone -- "$repo_url" "$target_dir"
        success "Repo cloned to ${target_dir}"
    fi
}

run_playbook() {
    local hostname="$1"
    local git_user_name="$2"
    local git_user_email="$3"
    local repo_dir="$4"

    # Build extra-vars as JSON so multi-word values (e.g. full names) are not
    # split by Ansible's space-delimited parser, and shell injection is prevented.
    local extra_vars
    extra_vars="$(printf '{"hostname":"%s","git_user_name":"%s","git_user_email":"%s"}' \
        "$hostname" "$git_user_name" "$git_user_email")"

    info "Installing Ansible Galaxy collections..."
    ansible-galaxy collection install -r "${repo_dir}/requirements.yml"

    info "Running Ansible playbook..."
    ansible-playbook "${repo_dir}/playbook.yml" --extra-vars "$extra_vars"
    success "Ansible playbook complete"
}

# ── Main ──────────────────────────────────────────────────────────────────────

main() {
    local repo_dir="${MACOS_SETUP_DIR:-${HOME}/macos-setup}"
    local repo_url="${MACOS_SETUP_REPO_URL:-https://github.com/iamivanhx/macos-setup.git}"

    # Prevent concurrent runs.
    if [[ -e "$LOCK_FILE" ]]; then
        error "Another bootstrap instance appears to be running (${LOCK_FILE} exists). Remove it if no other run is active."
    fi
    touch "$LOCK_FILE"

    # Request sudo upfront and keep the ticket alive in the background.
    sudo -v
    local sudo_keepalive_pid
    while true; do
        if ! kill -0 "$$" 2>/dev/null; then exit; fi
        sudo -n true
        sleep 60
    done 2>/dev/null &
    sudo_keepalive_pid=$!

    # Clean up lockfile and keepalive on exit, INT, or TERM.
    # shellcheck disable=SC2064
    trap "kill $sudo_keepalive_pid 2>/dev/null; rm -f '$LOCK_FILE'" EXIT INT TERM

    # Collect interactive input — reads from /dev/tty so curl-pipe mode works.
    local hostname git_user_name git_user_email
    hostname="$(prompt_required_tty 'Enter hostname for this machine: ')"
    while ! is_valid_hostname "$hostname"; do
        warn "Invalid hostname. Use only letters, digits, and hyphens (1-63 chars)."
        hostname="$(prompt_required_tty 'Enter hostname for this machine: ')"
    done
    git_user_name="$(prompt_required_tty 'Enter your Git user name: ')"
    git_user_email="$(prompt_required_tty 'Enter your Git email: ')"

    set_hostname        "$hostname"
    install_xcode_clt
    install_homebrew
    ensure_homebrew_on_path
    install_brew_package git     git
    install_brew_package ansible ansible
    clone_or_update_repo "$repo_url" "$repo_dir"
    run_playbook "$hostname" "$git_user_name" "$git_user_email" "$repo_dir"
}

# Run main only when executed directly, not when sourced (enables unit testing).
if [[ "${BASH_SOURCE[0]:-$0}" == "${0}" ]]; then
    main "$@"
fi
