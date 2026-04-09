---
name: GitHub Copilot CLI location
description: Path to the GitHub Copilot CLI binary used for cross-review skill
type: reference
originSessionId: 71a63729-4529-424f-b11d-724b28ede680
---
GitHub Copilot CLI is installed at `/opt/homebrew/bin/copilot` (version 1.0.21).

Use this path when invoking the `cross-review` skill or checking for Copilot availability. The standard `command -v gh && gh copilot` check will NOT find it — use `command -v copilot` or check `/opt/homebrew/bin/copilot` directly.
