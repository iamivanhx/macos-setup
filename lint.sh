#!/bin/bash
# The lint command: checks the Wrapper. GitHub runs it on every push.
set -euo pipefail
cd "$(dirname "$0")"

bash -n bootstrap.sh
shellcheck bootstrap.sh
