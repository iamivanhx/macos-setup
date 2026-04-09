#!/usr/bin/env bats
# Tests for bootstrap.sh
# Run: bats tests/bootstrap.bats

SCRIPT="${BATS_TEST_DIRNAME}/../bootstrap.sh"

# ── helpers ──────────────────────────────────────────────────────────────────

# Create a fake binary at $TEST_BIN/<name> that exits 0 and prints a marker
make_fake() {
    local name="$1"
    local extra="${2:-}"
    mkdir -p "$TEST_BIN"
    printf '#!/usr/bin/env bash\n%s\nexit 0\n' "$extra" > "$TEST_BIN/$name"
    chmod +x "$TEST_BIN/$name"
}

setup() {
    TEST_BIN="$(mktemp -d)"
    # Provide a minimal sudo stub so sudo calls don't prompt
    make_fake sudo 'exec "$@"'
    # Provide stubs that record calls
    export BATS_TMPDIR="${BATS_TMPDIR:-$(mktemp -d)}"
    export PATH="$TEST_BIN:$PATH"
}

teardown() {
    rm -rf "$TEST_BIN"
}

# ── Cycle 1: script skeleton ──────────────────────────────────────────────────

@test "bootstrap.sh exists" {
    [ -f "$SCRIPT" ]
}

@test "bootstrap.sh is executable" {
    [ -x "$SCRIPT" ]
}

@test "bootstrap.sh has bash shebang" {
    head -1 "$SCRIPT" | grep -qE '^#!/usr/bin/env bash'
}

@test "bootstrap.sh enables strict error handling" {
    grep -q 'set -euo pipefail' "$SCRIPT"
}

@test "bootstrap.sh has a main() guard so it can be sourced" {
    grep -q 'BASH_SOURCE\[0\]' "$SCRIPT"
}

# ── Cycle 2: Homebrew idempotency ─────────────────────────────────────────────

@test "install_homebrew skips when brew is already on PATH" {
    make_fake brew
    # Install a sentinel that would fire if the real installer were called
    make_fake curl 'echo CURL_CALLED; exit 1'

    source "$SCRIPT"
    run install_homebrew
    [ "$status" -eq 0 ]
    [[ "$output" == *"already installed"* ]]
    [[ "$output" != *"CURL_CALLED"* ]]
}

@test "install_homebrew prints installing message when brew is absent" {
    # No fake brew → command -v brew fails
    # Fake the installer download so it doesn't actually run
    make_fake curl 'echo INSTALLER_CALLED'
    # Fake bash so the piped installer script doesn't actually run
    make_fake bash 'echo BASH_INSTALLER_CALLED'

    source "$SCRIPT"
    run install_homebrew
    [[ "$output" == *"Installing Homebrew"* ]]
}

# ── Cycle 3: Ansible + Git idempotency ────────────────────────────────────────

@test "install_brew_package skips when package binary is already on PATH" {
    make_fake ansible
    make_fake brew 'echo BREW_CALLED; exit 1'

    source "$SCRIPT"
    run install_brew_package ansible ansible
    [ "$status" -eq 0 ]
    [[ "$output" == *"already installed"* ]]
    [[ "$output" != *"BREW_CALLED"* ]]
}

@test "install_brew_package calls brew install when binary is absent" {
    make_fake brew 'echo "BREW_INSTALL $*"'

    source "$SCRIPT"
    run install_brew_package ansible ansible
    [[ "$output" == *"BREW_INSTALL"* ]]
}

# ── Cycle 4: Xcode CLT idempotency ───────────────────────────────────────────

@test "install_xcode_clt skips when CLT path already exists" {
    # Fake xcode-select -p returning a path → CLT is present
    make_fake xcode-select 'if [[ "$1" == "-p" ]]; then echo "/Library/Developer/CommandLineTools"; exit 0; fi; exit 1'

    source "$SCRIPT"
    run install_xcode_clt
    [ "$status" -eq 0 ]
    [[ "$output" == *"already installed"* ]]
}

@test "install_xcode_clt triggers install when CLT is absent" {
    # Fake xcode-select -p failing → CLT absent; --install just echoes
    make_fake xcode-select 'if [[ "$1" == "-p" ]]; then exit 2; fi; echo "XCODE_INSTALL $*"'

    source "$SCRIPT"
    # XCODE_WAIT_ATTEMPTS=0 → skip the polling loop so the test doesn't hang
    export XCODE_WAIT_ATTEMPTS=0
    run install_xcode_clt
    [[ "$output" == *"Installing Xcode"* ]]
}

# ── Cycle 5: Repo clone vs pull ───────────────────────────────────────────────

@test "clone_or_update_repo runs git clone when target dir is absent" {
    local target
    target="$(mktemp -d)/macos-setup"
    make_fake git 'echo "GIT $*"'

    source "$SCRIPT"
    run clone_or_update_repo "https://example.com/repo.git" "$target"
    [[ "$output" == *"GIT clone"* ]]
}

@test "clone_or_update_repo runs git fetch + reset when target dir already exists" {
    local target
    target="$(mktemp -d)"
    make_fake git 'echo "GIT $*"'

    source "$SCRIPT"
    run clone_or_update_repo "https://example.com/repo.git" "$target"
    [[ "$output" == *"GIT -C"* ]]
    [[ "$output" == *"fetch"* ]]
    [[ "$output" == *"reset"* ]]
}

# ── Cycle 6: Ansible playbook invocation ─────────────────────────────────────

@test "run_playbook passes vars as JSON extra-vars (handles names with spaces)" {
    make_fake ansible-playbook 'echo "ANSIBLE_PLAYBOOK $*"'
    make_fake ansible-galaxy  'echo "GALAXY $*"'

    source "$SCRIPT"
    run run_playbook \
        "myhostname" "Ada Lovelace" "ada@example.com" \
        "$(mktemp -d)"
    [ "$status" -eq 0 ]
    [[ "$output" == *'"hostname":"myhostname"'* ]]
    [[ "$output" == *'"git_user_name":"Ada Lovelace"'* ]]
    [[ "$output" == *'"git_user_email":"ada@example.com"'* ]]
}

@test "run_playbook installs Galaxy collections before running playbook" {
    make_fake ansible-playbook 'echo "ANSIBLE_PLAYBOOK $*"'
    make_fake ansible-galaxy   'echo "GALAXY $*"'

    source "$SCRIPT"
    run run_playbook "h" "n" "e@e.com" "$(mktemp -d)"
    [[ "$output" == *"GALAXY"* ]]
    [[ "$output" == *"collection install"* ]]
}

# ── Cycle 7: /dev/tty for prompt input ───────────────────────────────────────

@test "script reads interactive prompts from /dev/tty" {
    grep -q '/dev/tty' "$SCRIPT"
}

# ── Cycle 8: hostname validation ─────────────────────────────────────────────

@test "is_valid_hostname accepts a simple hostname" {
    source "$SCRIPT"
    run is_valid_hostname "my-mac"
    [ "$status" -eq 0 ]
}

@test "is_valid_hostname accepts alphanumerics and hyphens up to 63 chars" {
    source "$SCRIPT"
    run is_valid_hostname "$(printf 'a%.0s' {1..63})"
    [ "$status" -eq 0 ]
}

@test "is_valid_hostname rejects empty string" {
    source "$SCRIPT"
    run is_valid_hostname ""
    [ "$status" -ne 0 ]
}

@test "is_valid_hostname rejects hostname starting with a dash" {
    source "$SCRIPT"
    run is_valid_hostname "--flag"
    [ "$status" -ne 0 ]
}

@test "is_valid_hostname rejects hostname with spaces" {
    source "$SCRIPT"
    run is_valid_hostname "my host"
    [ "$status" -ne 0 ]
}

@test "is_valid_hostname rejects hostname longer than 63 chars" {
    source "$SCRIPT"
    run is_valid_hostname "$(printf 'a%.0s' {1..64})"
    [ "$status" -ne 0 ]
}

@test "is_valid_hostname rejects shell metacharacters" {
    source "$SCRIPT"
    run is_valid_hostname 'host;rm -rf /'
    [ "$status" -ne 0 ]
}

# ── Cycle 9: required prompt retries on empty input ──────────────────────────

@test "prompt_required_tty returns non-empty value" {
    local input_file result
    input_file="$(mktemp)"
    printf 'Ada Lovelace\n' > "$input_file"

    source "$SCRIPT"
    # Call directly (not via `run`) so the shell function is in scope.
    result="$(PROMPT_INPUT_DEVICE="$input_file" prompt_required_tty "Enter name: ")"
    [[ "$result" == "Ada Lovelace" ]]
    rm -f "$input_file"
}

@test "prompt_required_tty skips empty lines and returns the first non-empty value" {
    local input_file result
    input_file="$(mktemp)"
    printf '\n\nAda Lovelace\n' > "$input_file"

    source "$SCRIPT"
    result="$(PROMPT_INPUT_DEVICE="$input_file" prompt_required_tty "Enter name: ")"
    [[ "$result" == "Ada Lovelace" ]]
    rm -f "$input_file"
}

# ── Cycle 10: concurrent-run lockfile ────────────────────────────────────────

@test "script references a lockfile to prevent concurrent runs" {
    grep -q 'LOCK_FILE\|lock_file\|\.lock' "$SCRIPT"
}
