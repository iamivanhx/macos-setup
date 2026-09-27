# How can the prompt, terminal, and editor follow light and dark mode?

Research findings for the ticket [How can the prompt, terminal, and editor follow light and dark mode?](https://github.com/iamivanhx/macos-setup/issues/19), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Researched 2026-09-27.

## How to read this note

- **Versions** are the ones Homebrew's API reports on 2026-09-27: `starship` 1.26.0, `ghostty` 1.3.1, `visual-studio-code` 1.139.1, `bat` 0.26.1, `git-delta` 0.19.2, `fzf` 0.74.4 ([formulae.brew.sh](https://formulae.brew.sh/api/formula/starship.json) and the matching `cask/*.json` and `formula/*.json` endpoints). Each tool's source is cited at the commit its release tag points to.
- **Host** means the target Mac, read-only: macOS 27.0, build `26A428` (`sw_vers`). Ghostty 1.3.1 is installed there (`ghostty +version`). Nothing was installed and no setting was changed.
- **Package**, **Dotfile**, **macOS setting**, and **Install channel** are used as the map defines them.
- The note names the Catppuccin Latte and Mocha themes only to say whether each tool ships them, because [Which packages and apps belong on a fresh Mac?](https://github.com/iamivanhx/macos-setup/issues/10#issuecomment-5853874806) named them (decision 22, inferred and open to overturn). Which themes to use stays the owner's choice.

## The answer in brief

| Tool | Follows the appearance natively? | Smallest config | When a switch takes effect | What stays manual |
| --- | --- | --- | --- | --- |
| macOS | It is the source. System Settings > Appearance offers Light, Dark, and Auto. | none | Auto switches on the Night Shift schedule, after a minute of idle | Choosing Auto. Writing it by script is not verified. |
| Ghostty | **Yes.** `theme` takes a light and dark pair. | one line: `theme = light:<name>,dark:<name>` | **Live**, in open windows | nothing; one known bug with the titlebar-tabs style |
| VS Code | **Yes**, once turned on. | `window.autoDetectColorScheme: true`, plus the two preferred-theme settings | **Live** | Catppuccin needs the extension `Catppuccin.catppuccin-vsc` |
| Starship | **No.** One `palette` per config file, no conditionals, no includes. | two config files that differ in the `palette` line, plus a shell hook that points `STARSHIP_CONFIG` at one | at the **next prompt** (hook in `precmd`) or the **next shell** (in `.zshrc`) | the prompt already on screen keeps its colours |
| bat | **Yes, by default** (`--theme=auto` asks the terminal for its background). | none for bat's defaults; two lines to pick the pair | the **next run** | nothing |
| git-delta | **Partly.** Light/dark styling follows the terminal. The syntax theme follows only while none is set (it then uses `GitHub` or `Monokai Extended`). | none for the defaults | the **next run** | a chosen syntax-theme pair needs `DELTA_FEATURES` set by the shell |
| fzf | **No.** It never detects the background and defaults to `dark`. | `--color=16`, which draws with the terminal's ANSI colours, so it follows Ghostty | the **next run** | a non-ANSI light/dark pair needs the shell to choose `--color` |

Two of the seven follow on their own, live: Ghostty and VS Code. bat and delta decide on every run by asking the terminal for its background colour. They therefore follow Ghostty, which already follows macOS. Starship needs the most glue, and a precmd hook costs about 11 ms per prompt for a `defaults read` (host). fzf follows the terminal if told to use ANSI colours.

## macOS 27

**The setting.** System Settings > Appearance offers Light ("a light appearance that doesn't change"), Dark, and Auto. Auto "switches the appearance from light to dark based on the Night Shift schedule you set" and "won't switch the appearance until your Mac has been idle for at least a minute" ([Apple, Mac User Guide for macOS 27](https://support.apple.com/guide/mac-help/mchl52e1c2d2/mac)).

**How a script reads the current appearance.** There are three ways, all run read-only on the host:

1. `defaults read -g AppleInterfaceStyle` prints `Dark` in dark mode. In light mode the key is absent and the command exits 1. On the host, currently Light, it printed "Could not find key 'AppleInterfaceStyle'". bat's own macOS code reads the same key the same way: `Dark` means dark, and "If the key does not exist, then light theme is currently in use" ([bat `src/theme.rs` L287-301](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/src/theme.rs#L287-L301)). Ten reads took 0.11 s on the host, about 11 ms each. Apple does not document this key.
2. JXA through AppKit: `osascript -l JavaScript -e 'ObjC.import("AppKit"); $.NSApplication.sharedApplication.effectiveAppearance.name.js'` printed `NSAppearanceNameAqua` (light) on the host. The dark value is expected to be `NSAppearanceNameDarkAqua` (not observed). It needs no Automation grant because it controls no other app. It is slower: five runs took 0.41 s, about 80 ms each (host).
3. Inside Ghostty only, ask the terminal: send `CSI ? 996 n`; Ghostty answers `CSI ? 997 ; 1 n` for dark or `CSI ? 997 ; 2 n` for light ([`device_status.zig` L66](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/terminal/device_status.zig#L66), [`stream_handler.zig` L870](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/termio/stream_handler.zig#L870), [`Termio.zig` L748-757](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/termio/Termio.zig#L748-L757)). This reports the terminal's theme, not macOS's. Not tried from zsh.

**Whether Auto can be set by script.** [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8#issuecomment-5853562909) does not cover appearance, so this was checked here:

- Both `AppleInterfaceStyle` and `AppleInterfaceStyleSwitchesAutomatically` are present in macOS 27's dyld shared cache (host byte search of `dyld_shared_cache_arm64e*`). The method and its limits are the same as that ticket's: a key that is present is still referenced, which does not prove a write to it is honoured.
- On the host, currently Light, neither key is set in the global domain.
- The scripting dictionary of System Events offers only a boolean `dark mode` ("use dark menu bar and dock") under `appearance preferences`, and no Auto (`/System/Library/CoreServices/System Events.app/Contents/Resources/SystemEvents.sdef` L63-96, host). Driving System Events with `osascript` needs an Automation grant, which a script cannot give itself (issue 8's resolution).
- **Not verified:** whether `defaults write -g AppleInterfaceStyleSwitchesAutomatically -bool true` turns on Auto on 27, and whether it takes effect without a logout. It needs a write, so it belongs in the trial VM.

## Ghostty 1.3.1

**Follows natively: yes.**

- **Config.** `theme` accepts `light:theme-name,dark:theme-name`. "Both light and dark must be specified in this form. In this form, the theme used will be based on the current desktop environment theme." ([`src/config/Config.zig` L580-590](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/config/Config.zig#L580-L590), identical in `ghostty +show-config --default --docs` on the host.) So the smallest config is one line:

  ```
  theme = light:Catppuccin Latte,dark:Catppuccin Mocha
  ```

- **Window chrome.** `window-theme` defaults to `auto`, which "is equivalent to `system`" when `theme` holds a pair ([`Config.zig` L2102-2118](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/config/Config.zig#L2102-L2118)), so it needs no line.
- **Live in open windows: yes.**
  - The macOS app observes `NSApplication.effectiveAppearance` and passes each change to libghostty ([`AppDelegate.swift` L295-310](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/macos/Sources/App/macOS/AppDelegate.swift#L295-L310)). It does the same for every surface in a window ([`BaseTerminalController.swift` L1471-1493](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/macos/Sources/Features/Terminal/BaseTerminalController.swift#L1471-L1493)).
  - Each surface then sets its conditional theme state and triggers a soft config reload ([`Surface.zig` L1679-1687 and L5046-5065](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/Surface.zig#L5046-L5065)).
  - Programs that turned on mode 2031 get the change reported live.
  - The 1.3.0 release notes list "Various fixes around dark/light theme reloading" ([release notes](https://ghostty.org/docs/install/release-notes/1-3-0)).
- **Known bug**, from the option's own docs: "macOS: titlebar tabs style is not updated when switching themes" ([`Config.zig` L589](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/config/Config.zig#L589)).
- **Catppuccin themes ship with it.** `Catppuccin Frappe`, `Catppuccin Latte`, `Catppuccin Macchiato`, and `Catppuccin Mocha` are in `/Applications/Ghostty.app/Contents/Resources/ghostty/themes/` on the host. They come from the bundled theme archive `ghostty-themes-release-20260216-151611-fc73ce3` ([`build.zig.zon` L119-122](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/build.zig.zon#L119-L122)).
- **Where the Dotfile goes.** 1.3 renamed the default file to `config.ghostty`. It reads `~/.config/ghostty/config.ghostty` (or the legacy `config`) when no file exists under `~/Library/Application Support/com.mitchellh.ghostty/` ([`src/config/file_load.zig` L9-121](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/config/file_load.zig#L9-L121)). The Dotfiles decision sets the path.

## VS Code 1.139.1

**Follows natively: yes, once turned on.**

- **Settings** ([`themeConfiguration.ts` L45-89](https://github.com/microsoft/vscode/blob/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/src/vs/workbench/services/themes/common/themeConfiguration.ts#L45-L89); keys and defaults in [`workbenchThemeService.ts` L24-43](https://github.com/microsoft/vscode/blob/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/src/vs/workbench/services/themes/common/workbenchThemeService.ts#L24-L43)):
  - `window.autoDetectColorScheme` (default `false`): "If enabled, will automatically select a color theme based on the system color mode."
  - `workbench.preferredDarkColorTheme` (default `Dark 2026`) and `workbench.preferredLightColorTheme` (default `Light 2026`).
  - The docs page still names the defaults "Dark Modern" and "Light Modern" ([vscode-docs `docs/configure/themes.md`](https://github.com/microsoft/vscode-docs/blob/be599f38eedab8ea204fdc5b9894c16e74b9e3f3/docs/configure/themes.md#automatically-switch-based-on-os-color-scheme)). The 1.139.1 source is taken as correct.
- **Smallest config** in the user `settings.json`:

  ```json
  "window.autoDetectColorScheme": true,
  "workbench.preferredLightColorTheme": "Catppuccin Latte",
  "workbench.preferredDarkColorTheme": "Catppuccin Mocha"
  ```

  Only the first line is needed to follow the appearance with VS Code's own themes.
- **Live: yes.** The theme service listens for the host's colour-scheme change and restores the matching preferred theme ([`browser/workbenchThemeService.ts` L451-460](https://github.com/microsoft/vscode/blob/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/src/vs/workbench/services/themes/browser/workbenchThemeService.ts#L451-L460)). The docs say it will "listen to changes to the OS's color scheme and switch".
- **Catppuccin needs an extension.**
  - VS Code's built-in theme extensions are `theme-abyss`, `theme-defaults`, `theme-kimbie-dark`, `theme-monokai`, `theme-monokai-dimmed`, `theme-quietlight`, `theme-red`, `theme-solarized-dark`, `theme-solarized-light`, and `theme-tomorrow-night-blue` (plus icon themes), with no Catppuccin ([`extensions/` at 1.139.1](https://github.com/microsoft/vscode/tree/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/extensions)).
  - The extension is `Catppuccin.catppuccin-vsc`, version 3.19.0, from a domain-verified publisher (Marketplace API, 2026-09-27). It contributes the themes `Catppuccin Mocha`, `Catppuccin Macchiato`, `Catppuccin Frappé`, and `Catppuccin Latte` ([`packages/catppuccin-vsc/package.json`](https://github.com/catppuccin/vscode/blob/befc9e6fc41980f4241408f7049755d47c06ff45/packages/catppuccin-vsc/package.json)).
  - Two ways to install it by script: the cask links `code` into Homebrew's `bin` (cask API `artifacts`), so `code --install-extension Catppuccin.catppuccin-vsc` works. `brew bundle` also takes VS Code extensions (`man brew`, Homebrew 7.0.6, host).

## Starship 1.26.0

**Follows natively: no.**

- **What the config can express.**
  - The root config has one `palette` string that picks from `palettes`, and nothing conditional ([`docs/config/README.md` L220-221](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/docs/config/README.md#L220-L221); [`src/config.rs` L501-516](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/config.rs#L501-L516)).
  - The docs describe no include or merge of config files.
  - No changelog entry up to 1.26.0 adds anything for light and dark ([`CHANGELOG.md`](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/CHANGELOG.md)).
- **Open feature requests.** [starship#6991 "Use different palettes for dark and light mode"](https://github.com/starship/starship/issues/6991) (opened 2025-09-19) and [starship#5546 "Dinamically pick a palette"](https://github.com/starship/starship/issues/5546) (opened 2023-11-02) are both open. A contributor offered an implementation in #6991 on 2026-02-28. No open pull request implements it (PR search, 2026-09-27).
- **The preset.**
  - `catppuccin-powerline` sets `palette = 'catppuccin_mocha'` and defines four palettes of hex colours ([preset L32, L175-285](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/docs/public/presets/toml/catppuccin-powerline.toml#L32)).
  - Its styles use palette names such as `red` and `peach`.
  - A palette entry is looked up before the ANSI colour of the same name ([`config.rs` L465-468](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/config.rs#L465-L468)), so the prompt draws fixed RGB colours and does not follow Ghostty's theme.
- **How Starship is invoked.**
  - The zsh init sets `promptsubst` and makes `PROMPT` run `starship prompt …` as a new process each time the prompt is drawn ([`src/init/starship.zsh` L98-101](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/init/starship.zsh#L98-L101)).
  - Each run resolves its config from `STARSHIP_CONFIG`, else `~/.config/starship.toml` ([`src/context.rs` L521-526](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/context.rs#L521-L526); [docs L29-32](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/docs/config/README.md#L29-L32)).
  - zsh runs `precmd` hooks "before each prompt" (`man zshmisc`, host).
  - So a value exported in a `precmd` hook applies to the prompt drawn right after it.

**The documented ways, and what each costs:**

1. **Two files, chosen in a `precmd` hook: next prompt.**
   - The files: `starship-light.toml` and `starship-dark.toml`, identical apart from the `palette` line.
   - The hook in `.zshrc`, after `starship init`:

     ```zsh
     _starship_appearance() {
       if [[ "$(defaults read -g AppleInterfaceStyle 2>/dev/null)" == Dark ]]; then
         export STARSHIP_CONFIG=~/.config/starship-dark.toml
       else
         export STARSHIP_CONFIG=~/.config/starship-light.toml
       fi
     }
     add-zsh-hook precmd _starship_appearance
     ```

   - Cost: one `defaults` process per prompt, about 11 ms on the host.
   - The prompt already on screen, and scrollback, keep their old colours until the next prompt is drawn. A prompt sitting idle does not redraw.
   - Two near-identical Dotfiles: a change to the prompt is two edits, unless one file is generated from the other.
2. **Two files, chosen once in `.zshrc`: next shell.** The same files and test, run once at shell start. There is no per-prompt cost. An open shell never switches until it is restarted.
3. **One file, rewritten with `starship config palette <name>`** (suggested by a maintainer in starship#5546):
   - `starship config` writes a temp file beside the config and renames it over the config path ([`src/configure.rs` L241-253](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/configure.rs#L241-L253); [`src/utils/mod.rs` L130-142](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/utils/mod.rs#L130-L142)).
   - A Dotfile symlinked into this repo would therefore be replaced by a plain file, or a copied one would drift from the repo. This is inferred from the source, not tested.
   - It also rewrites the file on every switch.
4. **Terminal colours instead of a hex palette: live, no shell glue.**
   - Proposed in starship#6991: make the prompt use ANSI colour names, so Ghostty's live theme switch recolours it.
   - Palette entries can map names to ANSI names, because a palette value is parsed without the palette ([`config.rs` L465-468](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/config.rs#L465-L468)).
   - Cost: the preset's 26 Catppuccin colours collapse into the terminal's 16, and it is no longer the preset as published. Not tried.

The test in 1 and 2 can use either of the other two ways of reading the appearance in the macOS section. Inside Ghostty, the `CSI ? 996 n` query answers from the terminal's own state; not tried.

## bat 0.26.1

**Follows natively: yes, by default.**

- **Default.** `--theme` defaults to `auto`: "Picks a dark or light theme depending on the terminal's colors (default). Use '--theme-light' and '--theme-dark' to customize the selected theme" ([`doc/long-help.txt` L119-141](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/doc/long-help.txt#L119-L141)). It asks the terminal with OSC 10/11 via `terminal-colorsaurus`, but only when stdout is a terminal ([`src/theme.rs` L234-273](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/src/theme.rs#L234-L273)).
- **Other modes.** `auto:system` reads `AppleInterfaceStyle` instead, on macOS only. `auto:always` detects even when output is redirected.
- **Default themes.** `Monokai Extended` and `Monokai Extended Light` (README).
- **Smallest config.** None, for bat's own default pair. To choose the pair, two lines in the config file (`~/.config/bat/config` on macOS, which follows XDG; `bat --config-file` prints it):

  ```
  --theme-light="Catppuccin Latte"
  --theme-dark="Catppuccin Mocha"
  ```

  The same pair can come from `BAT_THEME_LIGHT` and `BAT_THEME_DARK`. Setting `BAT_THEME` or `--theme` to a single theme name turns auto off.
- **When it takes effect.** Every run.
- **Catppuccin ships with it** since 0.26.0 ("Add Catppuccin, see #3317", [`CHANGELOG.md`](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/CHANGELOG.md)). The bundled theme names include `Catppuccin Latte` and `Catppuccin Mocha` ([`tests/assets.rs` L17-20](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/tests/assets.rs#L17-L20)).

## git-delta 0.19.2

**Follows natively: partly.**

- **Light or dark mode.** This picks the background colours of added and removed lines. Unless `--light` or `--dark` is set, delta asks the terminal each run ([`src/options/theme.rs` L1-14, L83-101](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/options/theme.rs#L1-L14)).
  - `--detect-dark-light` defaults to `auto`: query only when output is not redirected, or when `--color-only` is set, as in `interactive.diffFilter` ([`src/cli.rs` L150-170, L1205-1214](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/cli.rs#L150-L170)).
  - The manual says delta "detects your terminal background color automatically" ([`manual/src/choosing-colors-styles.md`](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/manual/src/choosing-colors-styles.md)).
- **Syntax theme.** One value, from `--syntax-theme` (gitconfig `delta.syntax-theme`), else from `BAT_THEME` ([`cli.rs` L863-869](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/cli.rs#L863-L869); [`src/options/set.rs` L81-83](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/options/set.rs#L81-L83)).
  - With neither set, it follows the detected mode: `GitHub` for light, `Monokai Extended` for dark ([`theme.rs` L62-80](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/options/theme.rs#L62-L80)).
  - It has no light/dark pair and does not read `BAT_THEME_LIGHT` or `BAT_THEME_DARK`.
- **Catppuccin.** It uses the `bat` 0.26 library's themes ([`Cargo.toml` L22](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/Cargo.toml#L22)), so the Catppuccin themes are available. It lists `Catppuccin Latte` among its light themes ([`theme.rs` L52-60](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/options/theme.rs#L52-L60)).
- **Smallest config.** None, if its default pair is acceptable. For a chosen pair:
  - Define two features in the git config, each setting `syntax-theme` (and `light = true` or `dark = true`).
  - Have the shell export `DELTA_FEATURES=+<feature>` from the same appearance test as Starship ([`manual/src/environment-variables.md`](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/manual/src/environment-variables.md); [`features-named-groups-of-settings.md`](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/manual/src/features-named-groups-of-settings.md)).
  - That then switches at the next prompt or the next shell, like Starship.
- **Conflict with bat.** Exporting `BAT_THEME` to steer delta would also turn off bat's auto mode.
- **When it takes effect.** Every run, for what it detects.

## fzf 0.74.4

**Follows natively: no.**

- **Default.** The base scheme defaults to `dark` on a 256-colour terminal, else `base16` ([`man/man1/fzf.1` L250-263](https://github.com/junegunn/fzf/blob/a140afeb4d733cad3c96a56bf6db7e26853b6757/man/man1/fzf.1#L250-L263)). The choice looks only at `TERM` and `tput colors`, never at the background ([`src/tui/light_unix.go` L22-31](https://github.com/junegunn/fzf/blob/a140afeb4d733cad3c96a56bf6db7e26853b6757/src/tui/light_unix.go#L22-L31)). Ghostty is a 256-colour terminal, so fzf there is expected to use `dark` in both modes (inferred, not observed).
- **Smallest config that follows.** `--color=16` (alias of `base16`) in `FZF_DEFAULT_OPTS` or `FZF_DEFAULT_OPTS_FILE`. It draws with the terminal default foreground and background and the ANSI colours ([`src/tui/tui.go` L1111-1133](https://github.com/junegunn/fzf/blob/a140afeb4d733cad3c96a56bf6db7e26853b6757/src/tui/tui.go#L1111-L1133); [`src/options.go` L1424-1433](https://github.com/junegunn/fzf/blob/a140afeb4d733cad3c96a56bf6db7e26853b6757/src/options.go#L1424-L1433)). It therefore takes whatever Ghostty's current theme defines.
- **Alternative.** The shell picks `--color=light` or `--color=dark` (or custom colours) from the appearance test, with the same timing as Starship.
- **When it takes effect.** Every run.
- **Catppuccin.** fzf ships no named themes.

## Could not verify

- How `AppleInterfaceStyle` behaves while Auto is on, on macOS 27. The host is set to Light, and neither appearance key is set.
- Whether `defaults write -g AppleInterfaceStyleSwitchesAutomatically -bool true` turns on Auto on 27, and when it takes effect. The System Events `dark mode` write was not run either: it needs an Automation grant. Both belong in the trial VM.
- How Auto's use of "the Night Shift schedule" works alongside [How should a Mac be set up to avoid eye strain?](https://github.com/iamivanhx/macos-setup/issues/18), which leaves Night Shift unsupported and sets light mode.
- The live switch in Ghostty and VS Code was read from source and docs, not watched on screen. Neither the Starship hook, nor the `CSI ? 996 n` query from zsh, nor bat's and delta's detection inside Ghostty or VS Code's terminal was run: none of these tools is installed on the host, and the ticket forbids installing.
- That `starship config` replaces a symlinked config with a plain file. This is inferred from its rename-based write.
- The default theme names `Dark 2026` and `Light 2026` in VS Code 1.139.1, taken from source; the docs page still says Dark Modern and Light Modern.
- That fzf picks `dark` inside Ghostty, inferred from its `tput colors` check.

## Sources

- Homebrew API, 2026-09-27: `formula/{starship,bat,git-delta,fzf}.json`, `cask/{ghostty,visual-studio-code}.json` at https://formulae.brew.sh/api/.
- Starship `v1.26.0` at [`fca92d8`](https://github.com/starship/starship/tree/fca92d8dcbd5981b0160af2f7ed7a430b6475a72); issues [#6991](https://github.com/starship/starship/issues/6991), [#5546](https://github.com/starship/starship/issues/5546).
- Ghostty `v1.3.1` at [`332b2ae`](https://github.com/ghostty-org/ghostty/tree/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28); [1.3.0 release notes](https://ghostty.org/docs/install/release-notes/1-3-0); the installed app on the host.
- VS Code `1.139.1` at [`04c0d99`](https://github.com/microsoft/vscode/tree/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1); vscode-docs at [`be599f3`](https://github.com/microsoft/vscode-docs/blob/be599f38eedab8ea204fdc5b9894c16e74b9e3f3/docs/configure/themes.md); catppuccin/vscode at [`befc9e6`](https://github.com/catppuccin/vscode/tree/befc9e6fc41980f4241408f7049755d47c06ff45); Visual Studio Marketplace extension query API.
- bat `v0.26.1` at [`979ba22`](https://github.com/sharkdp/bat/tree/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e).
- delta `0.19.2` at [`1502986`](https://github.com/dandavison/delta/tree/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd).
- fzf `v0.74.4` at [`a140afe`](https://github.com/junegunn/fzf/tree/a140afeb4d733cad3c96a56bf6db7e26853b6757).
- Apple: [Use a light or dark appearance on your Mac](https://support.apple.com/guide/mac-help/mchl52e1c2d2/mac) (macOS 27).
- Host, read-only: `sw_vers`; `defaults read -g AppleInterfaceStyle` and `AppleInterfaceStyleSwitchesAutomatically`; the JXA `effectiveAppearance` read; timing of both; `SystemEvents.sdef`; byte search of the dyld shared cache; `ghostty +version` and `+show-config --default --docs`; the Ghostty themes directory; `man zshmisc`; `man brew`.
