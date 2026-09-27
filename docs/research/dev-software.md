# Development software: what to install on the Fresh Mac, and on what evidence

Research note for the ticket [Which software is recommended for development on a Mac?](https://github.com/iamivanhx/macos-setup/issues/16), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Written 2026-09-27. Vocabulary (Bootstrap, Fresh Mac, Package, Dotfile, macOS setting) is the map's.

The question is what to install. How to configure it is [Which config practices are recommended for a development Mac?](https://github.com/iamivanhx/macos-setup/issues/17), and fonts and themes seen from eye strain are [How should a Mac be set up to avoid eye strain?](https://github.com/iamivanhx/macos-setup/issues/18). This note is the catalogue that [Which packages and apps belong on a fresh Mac?](https://github.com/iamivanhx/macos-setup/issues/10) chooses from. It recommends; it does not decide the feature list.

Nothing was installed. Every package name was checked against Homebrew's own API index on 2026-09-27 (`formulae.brew.sh/api/formula.json` and `cask.json`) [HB-API].

## How to read the evidence

"Best" is mostly opinion. Each pick below says what it rests on, from this list:

- **Popularity (Homebrew).** Homebrew's public install analytics for 2025-09-27 to 2026-09-27 [HB-A]. Formula figures are *install-on-request* (the user asked for it, not pulled in as a dependency); cask figures are all cask installs. Ranks are within their own list (formulae or casks), so compare a formula with a formula and a cask with a cask. Homebrew's analytics are opt-out and include CI runs [HB-DOC], so the counts measure installs, not people and not satisfaction.
- **Popularity (survey).** The Stack Overflow Developer Survey 2025, the latest published; the 2026 results are not out yet [SO]. Its IDE question and its "AI Agent out-of-the-box tools" question (8,323 respondents) are the only ones that name tools in these groups [SO-T][SO-AI].
- **Maintenance.** GitHub API figures queried 2026-09-27: creation date, stars, licence, latest release and date, and the number of releases in the last 12 months [GH]. A project with no release for a year or more is called *dormant* below. That is a fact about cadence, not proof it is broken.
- **Vendor statement.** What the tool's own docs say, for example a deprecation notice or a supported-OS line. Cited per claim.
- **Fit.** Something about this Mac or this owner: what is already installed (map Notes), the owner's languages (Python, Ruby, Node), or the standing preference that one change is one edit.

No source measured quality head to head (speed, correctness, ergonomics). Where a pick says "faster" or "lighter", that is the vendor's claim, and it is labelled so.

## Answer in brief

One pick per job. "Fit" means the pick rests mainly on this Mac's situation; "popular" on Homebrew analytics or the survey; neither is a measured quality claim.

| Group | Job | Pick | Install | Rests on |
|---|---|---|---|---|
| Terminal | Terminal app | Ghostty (already installed) | cask `ghostty` | fit, popular (#11 cask) |
| | Shell | zsh (built in) | none | vendor: macOS default since 10.15 |
| | Prompt | Starship | formula `starship` | popular (#79), active |
| | Shell add-ons | zsh-autosuggestions, zsh-syntax-highlighting | formulae | popular; common practice |
| | History search | fzf (Ctrl-R) | formula `fzf` | popular (#30) |
| Editors | GUI editor | Visual Studio Code | cask `visual-studio-code` | popular (#5 cask; 75.9% in SO 2025) |
| | Terminal editor | built-in `vim`; Neovim if wanted | none / formula `neovim` | fit (ships with macOS) |
| CLI helpers | search, find, view, list, jump | ripgrep, fd, bat, eza, zoxide | formulae | popular; common practice |
| | JSON / YAML | jq, yq | formulae | popular (#16, #25) |
| | monitoring | htop (btop as alternative) | formula | popular (#80) |
| | cheat sheets | tlrc | formula `tlrc` | vendor: `tldr` is disabled, `tlrc` is its named replacement |
| | misc | tree, wget | formulae | not shipped with macOS |
| Git | VCS | git (Homebrew) | formula `git` | popular (#6) |
| | GitHub | gh (already installed) | formula `gh` | fit, popular (#1) |
| | diff pager / TUI | git-delta, lazygit | formulae | popular (#249, #70) |
| | hooks | pre-commit | formula `pre-commit` | popular (#152), mature |
| Languages | version manager | mise | formula `mise` | popular (#15); fit (one tool for Node and Ruby) |
| | Python | uv | formula `uv` | popular (#4); manages Python itself |
| | Node | Node LTS via mise, pnpm | mise / formula `pnpm` | fit (owner already uses pnpm) |
| | Ruby | Ruby via mise | mise | vendor: precompiled on Apple Silicon |
| Containers & VMs | containers | Docker Desktop | cask `docker-desktop` | popular (#4 cask); vendor's own |
| | Linux/Windows VMs | UTM | cask `utm` | popular (#74 cask), open source |
| | macOS VMs | tart | own tap | already decided on the map |
| API / DB / network | API client | Bruno | cask `bruno` | fit (plain files in git), popular (#62) |
| | DB GUI | DBeaver Community | cask `dbeaver-community` | popular (#31), open source |
| | local HTTPS | mkcert | formula `mkcert` | popular (#40) |
| AI agents | coding agent | Claude Code (already installed) | own installer | fit; SO 2025 40.8% of agent users |
| | second agent | Codex CLI, if wanted | cask `codex` | popular (#2 cask) |
| Supply chain | secret scanning | gitleaks | formula `gitleaks` | popular (#162), mature |
| | install-time firewall | Socket Firewall Free | npm `sfw` | fit (already in the Ansible lists) |
| | dependency audit | osv-scanner | formula `osv-scanner` | vendor (Google, OSV database) |
| | secrets at runtime | 1Password CLI | cask `1password-cli` | fit (1Password installed), popular (#10 cask) |
| Productivity | launcher + clipboard + windows | Raycast | cask `raycast` | popular (#37); one app covers three jobs |
| Fonts | code font | JetBrains Mono | cask `font-jetbrains-mono` | fit (Ghostty's built-in default) |

## What changes from the Ansible lists

The Ansible version's lists are `group_vars/all.yml` at `4b8f39e`. Checked against Homebrew and the vendors today, several entries no longer work as written or are no longer needed:

- **`tldr` is disabled in Homebrew.** Deprecated 2024-10-24 as unmaintained, disabled 2025-10-24, with `tlrc` named as the replacement formula [HB-API]. A Brewfile line `brew "tldr"` fails.
- **`copilot-cli` is no longer a formula.** No formula of that name exists; GitHub Copilot CLI is the cask `copilot-cli` [HB-API]. In a Brewfile it is `cask "copilot-cli"`.
- **`pnpm env` is deprecated.** pnpm's docs: "`pnpm env` is deprecated. Use `pnpm runtime` instead. For example, `pnpm env use --global lts` becomes `pnpm runtime set node lts -g`" [PNPM-ENV]. The Ansible `languages` role installs Node that way.
- **`iterm2` duplicates Ghostty**, which the target Mac already has.
- **`font-hack-nerd-font` is not needed for Starship in Ghostty.** Ghostty "embeds a default font (JetBrains Mono), has built-in nerd fonts" [GT-CFG], and since 1.2.0 there is "no reason to use patched fonts in Ghostty" [GT-120].
- **`vim` and `curl` ship with macOS.** `/usr/bin/vim` and `/usr/bin/curl` are present on the target Mac (checked with `ls` on macOS 27.0). The Homebrew builds are only for newer versions.
- **Full Xcode via `mas` is only needed for Apple-platform work.** Nothing in Python, Ruby, or Node needs it. The Command Line Tools are already on the target Mac (map Notes).
- **`@socketsecurity/cli`** still exists on npm (1.1.180, same version as the package `socket`, which Socket's docs now name) [NPM][SOCK-CLI].

## Catalogue by group

Columns: **Install** is the exact Homebrew name (verified [HB-API]) or the other channel. **Maturity** is from [GH] unless marked. **Rank** is the Homebrew 365-day rank and count [HB-A].

### 1. Terminal, shell, and prompt

| | Install | Adds / replaces | Rank | Maturity, licence, cost | Notes |
|---|---|---|---|---|---|
| **Ghostty** (pick) | cask `ghostty` | replaces Terminal.app | #11 cask, 365,828 | repo since 2022; 1.0.1 on 2024-12-31, 1.3.1 on 2026-03-13 [GT-REL]; MIT; free | Already installed. Embeds JetBrains Mono and Nerd Font symbols [GT-CFG][GT-120], so no font Package is needed for the terminal. |
| iTerm2 | cask `iterm2` | same | #14 cask, 312,403 | since 2011; 3.7.3; GPL-2.0; free | The long-standing default. Duplicates Ghostty. |
| Warp | cask `warp` | same | #27 cask, 143,108 | AGPL-3.0 repo; 55 releases in 12 months | "Rust-based terminal" [HB-API]. Not examined further. |
| kitty | cask `kitty` | same | #88 cask, 53,308 | since 2016; 17 releases in 12 months; GPL-3.0 | |
| WezTerm | cask `wezterm` | same | #109 cask, 44,135 | MIT; last stable release 2024-02-03, since then nightly only | Dormant stable channel. |
| **zsh** (pick) | built in | shell | n/a | "the default login shell and interactive shell" since macOS 10.15 [APPLE-ZSH] | Nothing to install. |
| fish | formula `fish` | replaces zsh | #114, 180,275 | since 2012; 4.9.3; GPL-2.0 | "User-friendly command-line shell" [HB-API]; a different scripting language from zsh and bash. |
| nushell | formula `nushell` | replaces zsh | #360, 47,288 | MIT; 0.116.0, pre-1.0 | |
| **Starship** (pick) | formula `starship` | prompt | #79, 255,577 | since 2019; v1.26.0 on 2026-06-28; ISC; free | Cross-shell. Its docs require "A Nerd Font installed and enabled in your terminal" [STAR]; Ghostty supplies the symbols. |
| Powerlevel10k | formula `powerlevel10k` | prompt | #538, 26,915 | last release 2024-01-26; README: "THE PROJECT HAS VERY LIMITED SUPPORT … MOST BUGS WILL GO UNFIXED" [P10K] | Avoid for a new setup. |
| oh-my-posh | formula `oh-my-posh` | prompt | #284, 63,141 | MIT; 100+ releases in 12 months | |
| **zsh-autosuggestions** (pick) | formula | fish-style suggestions | #259, 69,531 | 0.7.1; MIT; last push 2025-06-24 | Small and stable; slow cadence. |
| **zsh-syntax-highlighting** (pick) | formula | command highlighting | #293, 62,206 | BSD-3-Clause; pushed 2026-09 | |
| Oh My Zsh | own installer | framework of plugins and themes | n/a | since 2009; 190k stars; MIT | Heavier alternative to the two plugins. |
| **fzf** (pick) | formula `fzf` | fuzzy finder, Ctrl-R history | #30, 556,100 | since 2013; 14 releases in 12 months; MIT | Also used by other tools. |
| atuin | formula `atuin` | shell history in SQLite, optional sync | #127, 152,446 | since 2020; 48 releases; MIT | Richer than fzf's Ctrl-R; one more tool. |
| tmux | formula `tmux` | multiplexer | #31, 552,150 | 3.7c on 2026-08-17; ISC | Only if the owner uses one; Ghostty has tabs and splits. |
| zellij | formula `zellij` | multiplexer | #300, 61,396 | MIT; pre-1.0 | |

**Why these picks.** Ghostty is installed, popular, and removes the need for a Nerd Font Package. zsh needs nothing. Starship is the most-installed prompt formula and is actively released, while Powerlevel10k's own README says it is barely supported [P10K]. The two zsh plugins are the lightest way to get suggestions and highlighting without a framework: that is common practice, not a measured result.

### 2. Editors

| | Install | Rank | Maturity, licence, cost | Notes |
|---|---|---|---|---|
| **Visual Studio Code** (pick) | cask `visual-studio-code` | #5 cask, 478,689 | since 2015; 62 releases in 12 months; free. The product is "a distribution of the `Code - OSS` repository … released under a traditional Microsoft product license"; the source is MIT [VSC] | Used by 75.9% of SO 2025 respondents, far ahead of Visual Studio at 29.0% [SO-T]. Claude Code has a VS Code extension [CC]. |
| Cursor | cask `cursor` | #34 cask, 120,276 | proprietary | 17.9% in SO 2025 [SO-T]. "Write, edit, and chat about your code with AI" [HB-API]. |
| Zed | cask `zed` | #42 cask, 110,679 | since 2021; 1.21.0; GPL-3.0-or-later [ZED]; free | Native, fast (vendor claim); smaller extension ecosystem. |
| Antigravity | cask `antigravity` | #82 cask, 58,385 | Google, proprietary | Google's agent IDE; young. Not verified further. |
| JetBrains IDEs | cask `jetbrains-toolbox` (or `pycharm`, `rubymine`) | Toolbox #143 cask; PyCharm #210; RubyMine #1451 | proprietary | Full IDEs per language; PyCharm 15.0% in SO 2025 [SO-T]. |
| Sublime Text | cask `sublime-text` | #75 cask, 61,770 | proprietary | 10.5% in SO 2025 [SO-T]. |
| **built-in vim** (pick for terminal) | none | n/a | ships with macOS (`/usr/bin/vim` on the target Mac) | Enough for commit messages and quick edits. |
| Neovim | formula `neovim` | #37, 496,297 | since 2014; 0.12.5; Apache-2.0 | 14.0% in SO 2025 [SO-T]. Worth it as a main editor; vim covers quick edits. |
| Helix | formula `helix` | #561, 25,389 | last release 2025-07-18; MPL-2.0 | "Post-modern modal text editor" [HB-API]. |
| Xcode | App Store (`mas`) or `xcodes` | xcodes #246 | free | Only for Apple-platform development. |

**Why VS Code.** Popularity is the evidence, and it is overwhelming in both sources. No source measured editor quality. The owner's agent-heavy workflow runs in the terminal, so an AI-first editor (Cursor, Antigravity) is optional, not required.

### 3. Command-line replacements and helpers

All are Homebrew formulae.

| Job | Pick | Rank | Maturity, licence | Alternatives |
|---|---|---|---|---|
| search file contents (grep) | **ripgrep** | #36, 517,295 | since 2016; 15.2.0 on 2026-07-15; Unlicense/MIT | `grep` (built in) |
| find files (find) | **fd** | #95, 216,509 | since 2017; 10.5.0; MIT/Apache | `find` (built in) |
| view files (cat) | **bat** | #101, 203,040 | since 2018; 0.26.1 on 2025-12-02; MIT/Apache | |
| list files (ls) | **eza** | #125, 153,507 | since 2023; "Modern, maintained replacement for ls"; the older `exa` formula no longer exists [HB-API]; EUPL-1.2 | `lsd` (#612) |
| jump to directories (cd) | **zoxide** | #122, 161,064 | since 2020; 0.10.0 on 2026-07-04; MIT | |
| fuzzy finder | **fzf** | #30, 556,100 | see group 1 | |
| JSON | **jq** | #16, 787,726 | since 2012; 1.8.2 on 2026-06-20; MIT | `fx` (#977), `jless` (#1342) for browsing |
| YAML/TOML/XML | **yq** (mikefarah) | #25, 600,017 | since 2015; 13 releases in 12 months; MIT | |
| process monitor (top) | **htop** | #80, 253,523 | 3.5.3 on 2026-08-16; GPL-2.0 | `btop` (#145; prettier, more detail), `bottom` (#401) |
| disk usage (du) | dust (optional) | #490, 30,376 | 1.2.6 on 2026-09-16; Apache-2.0 | `ncdu` (#374) |
| cheat sheets (man) | **tlrc** | #661, 18,995 | official tldr client [HB-API]; 1.13.1; MIT | `tldr` is disabled in Homebrew |
| directory tree | **tree** | #56, 342,553 | GPL-2.0 | `eza --tree` |
| downloads | **wget** | #64, 309,817 | GPL-3.0 | `curl` (built in) |
| task runner | just (optional) | #43, 412,049 | since 2016; CC0 | `make` (built in) |
| file manager TUI | yazi (optional) | #190, 95,194 | since 2023; MIT | `broot` |
| benchmarking | hyperfine (optional) | #735, 16,190 | 1.20.0; MIT/Apache | |

**Why these.** They are the most-installed tool for each job except monitoring and cheat sheets, where htop out-installs btop about two to one and `tlrc` is the only maintained option Homebrew names. The ripgrep/fd/bat/eza/zoxide set is common practice in public dotfiles; that is a lead, not measured evidence. Note that Claude Code usually bundles its own ripgrep [CC], so ripgrep is for the owner, not the agent.

### 4. Git tooling

| | Install | Rank | Maturity, licence | Notes |
|---|---|---|---|---|
| **git** (pick) | formula `git` | #6, 1,401,407 | 2.55.0; GPL-2.0 | Newer than the Command Line Tools' git. Apple's git version on the target Mac was not checked. |
| **gh** (pick) | formula `gh` | #1, 2,934,132 | since 2019; 27 releases in 12 months; MIT | Already installed. |
| **git-delta** (pick) | formula `git-delta` | #249, 74,216 | since 2019; 0.19.2 on 2026-03-28; MIT | "Syntax-highlighting pager for git and diff output" [HB-API]; wiring it in is config. |
| difftastic | formula `difftastic` | #574, 24,506 | MIT; 0.71.0 | Structural diffs; complements or replaces delta. |
| **lazygit** (pick) | formula `lazygit` | #70, 280,106 | since 2018; 17 releases in 12 months; MIT | "Simple terminal UI for git commands" [HB-API]. |
| tig, gitui | formulae | #678, #959 | | Lighter TUIs. |
| git-lfs | formula `git-lfs` | #77, 256,914 | MIT | Only if a repo uses LFS. |
| **pre-commit** (pick) | formula `pre-commit` | #152, 123,411 | since 2014; 4.6.2; MIT | Hook framework used across Python, Ruby, and Node repos. |
| prek | formula `prek` | #536, 27,066 | since 2024-10; 56 releases in 12 months; MIT | "Drop-in alternative to pre-commit" in Rust [HB-API]. Young and fast-moving. |
| lefthook | formula `lefthook` | #428, 37,795 | since 2019; 33 releases in 12 months; MIT | Hook manager "for any type of projects" [HB-API]. |
| jj (Jujutsu) | formula `jj` | #378, 44,125 | since 2020; Apache-2.0; pre-1.0 | Git-compatible alternative VCS. |
| GitHub Desktop | cask `github` | #97 cask, 50,326 | MIT | GUI; Fork (#284) and Sourcetree (#227) also exist. |
| glab | formula `glab` | #57, 338,530 | MIT | Only for GitLab. |

**Why these.** git and gh are the baseline. delta and lazygit are the most-installed tools in their niches. pre-commit is the mature hook runner; prek is the younger drop-in that the owner could switch to later without changing config (vendor claim).

### 5. Language toolchains and version managers

| | Install | Rank | Maturity, licence | Notes |
|---|---|---|---|---|
| **mise** (pick) | formula `mise` | #15, 792,240 | since 2023-01; 100+ releases in 12 months; MIT | One tool for Node, Ruby, Python and more. Downloads precompiled Ruby on Apple Silicon by default, falling back to ruby-build [MISE-RB], and precompiled Python by default [MISE-PY]. Reads `.nvmrc`/`.node-version` once enabled [MISE-NODE]. Also a shortlisted Bootstrap tool on the map; using it as a version manager does not commit the map to `mise bootstrap`. |
| asdf | formula `asdf` | #200, 89,215 | since 2014; MIT | mise began as an asdf clone ("asdf rust clone" [HB-API]). |
| nvm | formula `nvm` (or own script) | #35, 518,364 | since 2010; MIT | Node only. |
| fnm | formula `fnm` | #302, 61,085 | GPL-3.0; 1 release in 12 months | Node only. |
| Volta | formula `volta` | #1320 | README: "Volta is unmaintained … We recommend migrating to mise" [VOLTA] | Avoid. |
| pyenv | formula `pyenv` | #17, 762,630 | since 2012; MIT | Compiles Python; uv or mise make it unnecessary. |
| rbenv + ruby-build | formulae | #150 / #147 | rbenv's last release 2025-01-08; MIT | Compiles Ruby. |
| rv | formula `rv` | #2373 | since 2025-07; Apache-2.0; pre-1.0 | New Ruby manager; too young to rely on. |
| **uv** (pick for Python) | formula `uv` | #4, 1,870,853 | since 2023-10; 99 releases in 12 months; MIT/Apache | Package installer and resolver that also installs Python itself: "you don't need to install Python to get started" [UV]. Makes a separate pyenv unnecessary. |
| pipx, poetry | formulae | #24, #193 | | Older Python tooling. |
| **Node LTS via mise** (pick) | mise | n/a | | Homebrew's `node` (#2) is one global version and tracks the newest release (26.10.0 today) [HB-API]. |
| **pnpm** (pick) | formula `pnpm`, or via mise | #26, 596,420 | MIT; 12.x | Already the owner's choice. Its Node management moved from `pnpm env` to `pnpm runtime` [PNPM-ENV]. |
| bun, deno | formulae | #606, #115 | MIT | Alternative JS runtimes; only if a project uses them. |
| **Ruby via mise** (pick) | mise | n/a | | Precompiled [MISE-RB]. Homebrew `ruby` (#72) is one global version. |
| direnv | formula `direnv` | #153, 123,379 | MIT; last release 2025-07-20 | Per-directory env vars. |
| rustup, go | formulae | #220, #8 | | Only if needed. |

**Why mise and uv.** The owner works in three languages; one manager for all three is one tool to learn and one file per project. mise is the most-installed polyglot manager, and Volta's maintainers now point users to it [VOLTA]. uv is the fourth most-installed formula on Homebrew and manages Python without a separate installer. Which one owns Python (uv alone, or mise installing Python and uv for packages) is a config choice for the config ticket; both work [MISE-PY][UV].

### 6. Containers and virtual machines

| | Install | Rank | Maturity, licence, cost | Notes |
|---|---|---|---|---|
| **Docker Desktop** (pick) | cask `docker-desktop` (old token `docker`) | #4 cask, 524,763 | 4.92.0; proprietary. Free for "fewer than 250 employees AND less than $10 million in annual revenue", personal use, education, and non-commercial open source [DOCKER-LIC] | Docker is used by 71.1% of SO 2025 respondents [SO-T] (the survey does not split Desktop from other runtimes). Docker's own app. |
| OrbStack | cask `orbstack` | #23 cask, 180,238 | closed source. "Always free for personal use"; Pro "$8 per user per month" for commercial use [ORB-PRICE] | "A fast, light, and simple way to run containers and Linux machines" (vendor claim) [ORB]. Also runs Linux VMs. |
| Colima + Docker CLI | formulae `colima`, `docker`, `docker-compose` | #100, #19, #54 | since 2021; MIT; free | Fully open source, CLI only, Brewfile-friendly. |
| Podman / Podman Desktop | formula `podman`, cask `podman-desktop` | #99, #116 cask | Apache-2.0; free | "Tool for managing OCI containers and pods" [HB-API]. |
| Rancher Desktop | cask `rancher` | #137 cask | Apache-2.0; free | Kubernetes-focused. |
| Apple `container` | formula `container` | #478, 31,998 | since 2025-05; 1.4.1; Apache-2.0 | Requires macOS 26 and Apple silicon; "under active development. Its release versions are product versions, not semantic versions"; no mention of Compose [APPLE-CT]. Worth watching, not yet a Docker replacement. |
| **UTM** (pick for general VMs) | cask `utm` | #74 cask, 63,713 | since 2019; Apache-2.0; free | "Virtual machines UI using QEMU" [HB-API], for Linux and other guests. |
| **tart** (pick for macOS VMs) | own tap | not in Homebrew core [HB-API] | the repo `cirruslabs/tart` now redirects to `openai/tart` [GH] | Already chosen by [How can a disposable macOS VM run on this Mac?](https://github.com/iamivanhx/macos-setup/issues/9). The ownership change was noticed here and not investigated. |
| Lima | formula `lima` | #305 | Apache-2.0 | "Linux virtual machines" from the command line [HB-API]. |
| Parallels | cask `parallels` | #465 cask | paid | |

**Why Docker Desktop.** It rests on popularity and on being Docker's own product; its licence is free for the owner if the use is personal or a small business [DOCKER-LIC]. If the owner wants less resource use (vendor claims only; no independent benchmark was found) and the use is personal, OrbStack is the common alternative; if the owner wants only open-source pieces in a Brewfile, Colima with the `docker` formula. The owner's commercial status decides between these and was not known here.

### 7. API, database, and network tools

| | Install | Rank | Maturity, licence, cost | Notes |
|---|---|---|---|---|
| **Bruno** (pick) | cask `bruno` | #62 cask, 76,916 | since 2022; 29 releases in 12 months; MIT; free | Stores collections "directly in a folder on your filesystem" as plain text, for git; "offline-only", "no plans to add cloud-sync … ever" [BRUNO]. Fits a public-repo, files-in-git setup. |
| Postman | cask `postman` | #29 cask, 140,705 | proprietary | The most installed API client; "Collaboration platform for API development" [HB-API]. |
| Insomnia, Yaak | casks | #216, #509 | Apache-2.0 / MIT | |
| curl | built in | n/a | | Enough for one-off requests. |
| xh | formula `xh` | #815, 13,550 | MIT; 0.26.2 on 2026-07-26 | "Friendly and fast tool for sending HTTP requests" [HB-API]; the maintained option in HTTPie's niche. |
| HTTPie | formula `httpie` | #266, 67,639 | BSD-3-Clause; last release 2024-11-01, last push 2024-12 | Dormant. |
| hurl | formula `hurl` | #1344 | Apache-2.0 | HTTP tests in plain text. |
| **DBeaver Community** (pick) | cask `dbeaver-community` | #31 cask, 131,592 | since 2015; 24 releases in 12 months; Apache-2.0; free | Any SQL database. |
| TablePlus | cask `tableplus` | #141 cask, 29,353 | proprietary; free tier (limits not verified) | Native Mac UI. |
| Beekeeper Studio, Postico, Sequel Ace, DataGrip | casks | #334, #568, #170, #300 | mixed | Postico is for PostgreSQL, Sequel Ace for MySQL/MariaDB [HB-API]. |
| psql (without a server) | formula `libpq` | #87, 241,588 | PostgreSQL licence | Only if the owner uses Postgres. `pgcli` (#786) adds completion. |
| sqlite3 | built in | n/a | | Present on the target Mac. |
| **mkcert** (pick) | formula `mkcert` | #40, 468,626 | since 2018; BSD-3-Clause; last release 2022-04-26 | Locally trusted HTTPS certificates. Dormant but widely used. |
| ngrok | cask `ngrok` | #8 cask, 397,016 | proprietary | Tunnels to localhost. |
| cloudflared | formula `cloudflared` | #73, 272,174 | Apache-2.0 | Cloudflare Tunnel client. |
| Tailscale | cask `tailscale-app` | #26 cask, 144,662 | BSD-3-Clause client | Mesh VPN; only if used. |
| mitmproxy | cask `mitmproxy` (moved from formula [HB-TM]) | n/a | MIT | HTTP(S) interception. Proxyman (#262 cask) is the native GUI. |
| nmap | formula `nmap` | #90 | | Port scanning. |

**Why these.** Bruno is picked on fit: the owner keeps everything as files in a public repo, and Bruno is the only popular client that is file-based by design [BRUNO]. DBeaver on popularity and licence. Everything else in this group is on-demand: none of it is needed until a project needs it.

### 8. AI coding agents and assistants

| | Install | Rank | Maturity, licence | Notes |
|---|---|---|---|---|
| **Claude Code** (pick) | own installer `curl -fsSL https://claude.ai/install.sh \| bash` | cask `claude-code` #1 cask, 1,134,756 | since 2025-02; 100+ releases in 12 months; proprietary; needs a Pro, Max, Team, Enterprise, or Console account [CC] | Already installed. The native installer is "Recommended" and auto-updates; Homebrew installs "do not auto-update" unless `CLAUDE_CODE_PACKAGE_MANAGER_AUTO_UPDATE=1`; cask `claude-code` is the stable channel, `claude-code@latest` the latest [CC]. 40.8% of SO 2025 agent users [SO-AI]. |
| Codex CLI | cask `codex` (moved from formula [HB-TM]) | #2 cask, 829,402 | since 2025-04; Apache-2.0 | OpenAI's terminal agent. Its Mac desktop app cask `codex-app` is deprecated as discontinued, pointing to `chatgpt` [HB-API]. |
| GitHub Copilot CLI | cask `copilot-cli` | #17 cask, 226,641 | proprietary | GitHub Copilot is 67.9% of SO 2025 agent users, across all its forms [SO-AI]. |
| OpenCode | formula `opencode` | #49, 372,554 | since 2025-04; MIT | Open source, multi-provider. |
| Gemini CLI | formula `gemini-cli` | #14, 795,249 | **Deprecated in Homebrew 2026-06-18, disabled 2026-12-18**, replacement cask `antigravity-cli` [HB-API] | Google: "On June 18, 2026, Gemini CLI and Gemini Code Assist IDE extensions will stop serving requests for Google AI Pro and Ultra" [GEMINI]. |
| Antigravity CLI | cask `antigravity-cli` | #129 cask, 32,481 | proprietary; young | Google's replacement for Gemini CLI [GEMINI]. |
| Claude desktop app | cask `claude` | #19 cask, 210,638 | proprietary | Chat plus Claude Code in a GUI [CC]. |
| ChatGPT desktop app | cask `chatgpt` | #59 cask | proprietary | |
| Ollama | formula `ollama` / cask `ollama-app` | #23, 616,054 | MIT | Local models. |
| LM Studio | cask `lm-studio` | #87 cask | proprietary, free | Local models with a GUI. |
| Aider | formula `aider` | #905 | Apache-2.0; last release 2025-08-09 | Dormant. |

**Why Claude Code.** It is already installed and the owner's repositories set up AI coding agents; the survey and Homebrew both put it at or near the top. A second agent is a matter of taste and subscriptions, not evidence; Codex CLI is the most installed after it.

### 9. Supply-chain and secret-scanning tools

| | Install | Rank | Maturity, licence | Notes |
|---|---|---|---|---|
| **gitleaks** (pick) | formula `gitleaks` | #162, 113,498 | since 2018; 8.30.1 on 2026-03-21; MIT | "Audit git repos for secrets" [HB-API]; no account. |
| TruffleHog | formula `trufflehog` | #338, 50,754 | AGPL-3.0; 48 releases in 12 months | Verifies whether found credentials are live. |
| detect-secrets, ggshield, talisman, git-secrets | formulae | #1474, #1198, #871, #1427 | | Smaller; ggshield needs a GitGuardian account. |
| **Socket Firewall Free** (pick) | npm `sfw` (`npm i -g sfw`) | not in Homebrew | npm wrapper MIT, binary under PolyForm Shield 1.0.0; no API key [SFW] | Blocks malicious packages at install time for npm, yarn, pnpm, pip, uv, and cargo; Ruby is Enterprise-only [SFW]. Already in the Ansible lists. |
| Socket CLI | npm `socket` (also published as `@socketsecurity/cli`) | not in Homebrew | MIT | Wraps npm/npx with Socket checks; "Most of these commands require an API Token" [SOCK-CLI]. |
| **osv-scanner** (pick) | formula `osv-scanner` | #596, 22,801 | since 2022; 13 releases in 12 months; Apache-2.0 | Google's scanner against the OSV vulnerability database. |
| Trivy, Grype + Syft | formulae | #142, #484 / #457 | Apache-2.0 | Broader: container images and SBOMs. |
| zizmor, actionlint | formulae | #332, #113 | MIT | GitHub Actions security and lint; only if the owner writes workflows. |
| **1Password CLI** (pick) | cask `1password-cli` | #10 cask, 368,074 | proprietary | Command-line access to 1Password [HB-API], so secrets stay in the vault rather than in this public repo. Pairs with the installed app. |

**Why these.** gitleaks is the most-installed secret scanner and needs no account. `sfw` is the owner's existing choice and needs no account; the alternatives either need an account (Socket CLI, ggshield) or scan after the fact. osv-scanner is picked on its vendor and open data source, not popularity (Trivy is more installed but aims at containers). Which of these run as hooks, and how, is the config ticket's.

### 10. Productivity apps used while developing

| | Install | Rank | Maturity, cost | Notes |
|---|---|---|---|---|
| **Raycast** (pick) | cask `raycast` | #37 cask, 115,201 | proprietary. Free plan includes "Clipboard History, Quicklinks, Calculator, Snippets, Window Management"; Pro "$10 / month" [RAYCAST] | One app for launcher, clipboard history, and window snapping. |
| Spotlight | built in | n/a | free | Searches clipboard history since macOS 26 [APPLE-CLIP]. The zero-install option. |
| Alfred | cask `alfred` | #164 cask | paid Powerpack (price not verified) | |
| macOS window tiling | built in | n/a | free | Drag to edges or use Window > Move & Resize, since macOS 15 [APPLE-TILE]. |
| Rectangle | cask `rectangle` | #41 cask, 113,638 | MIT; macOS 14+; Pro version paid [RECT] | Keyboard window snapping. |
| AeroSpace | cask `nikitabobko/tap/aerospace` | #70 cask (tap), 65,015 | MIT; "Public Beta … expect breaking changes until 1.0" [AERO] | i3-style tiling. |
| Amethyst, Loop | casks | #322, #390 | MIT / GPL-3.0 | Tiling / radial snapping. |
| Maccy | cask `maccy` | #43 cask, 110,469 | MIT | Clipboard manager if not using Raycast. |
| AltTab | cask `alt-tab` | #71 cask | GPL-3.0 | Windows-style window switcher. |
| Ice | cask `jordanbaird-ice` | #80 cask | GPL-3.0; last release 2024-10-29 | Menu bar manager; dormant. |

The Ansible lists also had Obsidian and Discord. They are not development tools, so whether they stay is for the feature-list ticket.

**Why Raycast.** It covers three jobs with one Package, which fits the owner's "one change, one place" preference, and it is the most-installed launcher cask. If the owner would rather install nothing, macOS 27's Spotlight clipboard history and built-in tiling cover the basics [APPLE-CLIP][APPLE-TILE].

### 11. Fonts for code

| | Install | Rank | Licence | Notes |
|---|---|---|---|---|
| **JetBrains Mono** (pick) | cask `font-jetbrains-mono` | #113 cask, 43,215 | OFL-1.1; 2.304 (2023) | Ghostty's embedded default [GT-CFG], so the terminal needs nothing; install the cask so VS Code and other apps can use it too. |
| JetBrains Mono Nerd Font | cask `font-jetbrains-mono-nerd-font` | #25 cask, 144,826 | nerd-fonts 3.5.1 | The most-installed font cask. Needed only for Starship icons in a terminal other than Ghostty. |
| Symbols Only Nerd Font | cask `font-symbols-only-nerd-font` | #123 cask | | Just the icons, as a fallback font. |
| Hack Nerd Font | cask `font-hack-nerd-font` | #79 cask | | The Ansible choice; not needed with Ghostty. |
| Fira Code | cask `font-fira-code` | #149 cask | OFL-1.1; last release 2021 | Ligatures. |
| SF Mono | cask `font-sf-mono` | #609 cask | Apple licence | Apple's own. |
| Monaspace, Cascadia Code, Iosevka, Maple Mono, Geist Mono | casks `font-monaspace`, `font-cascadia-code`, `font-iosevka`, `font-maple-mono`, `font-geist-mono` | #356, #477, #398, #378, #831 | OFL-1.1 (most) | |

**Why JetBrains Mono.** Fit: it is already Ghostty's font, so choosing it means one font across terminal and editor with one extra cask. Legibility and eye strain are for the eye-strain ticket, which may pick differently.

## Could not verify

- **Quality head to head.** No primary source measured speed, reliability, or ergonomics across alternatives. Claims such as "lighter" (OrbStack) or "fast" (Zed) are vendors' own.
- **The 2026 Stack Overflow survey.** It is not published yet [SO]; figures are from 2025.
- **Survey coverage.** Stack Overflow does not ask about terminals, prompts, CLI helpers, launchers, window managers, or fonts. Those picks rest on Homebrew analytics and fit only.
- **Apple's bundled git and zsh versions** on the target Mac were not read.
- **Prices** for TablePlus, Alfred, Cursor, and the JetBrains IDEs were not checked.
- **The `openai/tart` redirect**: noticed, not investigated. It concerns the VM ticket, not this one.
- **Homebrew analytics scope**: whether the formula figures include Homebrew on Linux was not checked. They include CI installs [HB-DOC].

## Sources

- [HB-A] Homebrew analytics JSON, 365 days to 2026-09-27: [formula install-on-request](https://formulae.brew.sh/api/analytics/install-on-request/365d.json), [cask install](https://formulae.brew.sh/api/analytics/cask-install/365d.json).
- [HB-API] Homebrew API index, read 2026-09-27: [formula.json](https://formulae.brew.sh/api/formula.json), [cask.json](https://formulae.brew.sh/api/cask.json). Deprecation and disable dates, replacements, versions, licences.
- [HB-DOC] [Homebrew Analytics documentation](https://docs.brew.sh/Analytics).
- [HB-TM] [homebrew-core `tap_migrations.json`](https://github.com/Homebrew/homebrew-core/blob/HEAD/tap_migrations.json): `codex` and `mitmproxy` moved to casks.
- [GH] GitHub REST API (`repos/<owner>/<repo>` and `…/releases`), queried 2026-09-27.
- [SO] [Stack Overflow Developer Survey index](https://survey.stackoverflow.co/): 2025 is the latest published year.
- [SO-T] [Stack Overflow Developer Survey 2025, Technology](https://survey.stackoverflow.co/2025/technology): Dev IDEs; cloud development tools.
- [SO-AI] [Stack Overflow Developer Survey 2025, AI](https://survey.stackoverflow.co/2025/ai): "AI Agent out-of-the-box tools", 8,323 respondents.
- [APPLE-ZSH] [Apple: Use zsh as the default shell on your Mac](https://support.apple.com/en-us/102360).
- [APPLE-CLIP] [Apple: Search your Clipboard history in Spotlight on Mac](https://support.apple.com/en-mt/guide/mac-help/mchl40d5b86b/27/mac/27).
- [APPLE-TILE] [Apple: Tile windows on Mac](https://support.apple.com/guide/mac-help/tile-app-windows-mchlef287e5d/15.0/mac/15.0).
- [APPLE-CT] [apple/container README](https://github.com/apple/container).
- [GT-CFG] [Ghostty: Configuration](https://ghostty.org/docs/config).
- [GT-120] [Ghostty 1.2.0 release notes](https://ghostty.org/docs/install/release-notes/1-2-0).
- [GT-REL] [Ghostty release notes index](https://ghostty.org/docs/install/release-notes).
- [STAR] [Starship guide](https://starship.rs/guide/).
- [P10K] [romkatv/powerlevel10k README](https://github.com/romkatv/powerlevel10k).
- [VSC] [microsoft/vscode README](https://github.com/microsoft/vscode).
- [ZED] [zed-industries/zed README, Licensing](https://github.com/zed-industries/zed#licensing).
- [MISE-RB] [mise: Ruby](https://mise.jdx.dev/lang/ruby.html). [MISE-PY] [mise: Python](https://mise.jdx.dev/lang/python.html). [MISE-NODE] [mise: Node](https://mise.jdx.dev/lang/node.html).
- [UV] [uv: Installing Python](https://docs.astral.sh/uv/guides/install-python/).
- [VOLTA] [volta-cli/volta README](https://github.com/volta-cli/volta).
- [PNPM-ENV] [pnpm: `pnpm env`](https://pnpm.io/cli/env).
- [DOCKER-LIC] [Docker Desktop license agreement](https://docs.docker.com/subscription/desktop-license/).
- [ORB] [OrbStack docs](https://docs.orbstack.dev/). [ORB-PRICE] [OrbStack pricing](https://orbstack.dev/pricing).
- [BRUNO] [usebruno/bruno README](https://github.com/usebruno/bruno).
- [CC] [Claude Code: Advanced setup](https://code.claude.com/docs/en/setup).
- [GEMINI] [Google Developers Blog, 2026-05-19: transitioning Gemini CLI to Antigravity CLI](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/); Homebrew's deprecation PR [Homebrew/homebrew-core#284420](https://github.com/Homebrew/homebrew-core/pull/284420).
- [SFW] [SocketDev/sfw-free README](https://github.com/SocketDev/sfw-free).
- [SOCK-CLI] [Socket CLI docs](https://docs.socket.dev/docs/socket-cli).
- [NPM] npm registry `…/latest` for `sfw`, `socket`, `@socketsecurity/cli`, queried 2026-09-27.
- [RAYCAST] [Raycast pricing](https://www.raycast.com/pricing).
- [RECT] [rxhanson/Rectangle README](https://github.com/rxhanson/Rectangle) and its MIT `LICENSE`.
- [AERO] [nikitabobko/AeroSpace README](https://github.com/nikitabobko/AeroSpace).
