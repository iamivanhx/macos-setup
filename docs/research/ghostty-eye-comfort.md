# Ghostty for eye comfort: which theme pair, font, size and options, on the evidence?

Research note requested on 2026-10-03, following [Turn on Ghostty's SSH, sudo and notification features in the Ghostty Dotfile](https://github.com/iamivanhx/macos-setup/issues/45). Researched 2026-10-03. Vocabulary (Dotfile, Package, Bootstrap, Step by hand, Local file, macOS setting) is [CONTEXT.md](../../CONTEXT.md)'s.

This builds on [eye-strain.md](eye-strain.md) and does not redo it. Its grades are reused as they are:

- **Supported**: clinical or occupational-health guidance, plus at least one controlled study or a systematic review.
- **Guidance only**: consistent guidance, little direct trial evidence.
- **Mixed**: studies disagree, or are small or uncontrolled.
- **Unsupported**: no good evidence that it reduces eye strain.

Every recommendation below says whether it rests on **evidence** (a measurement, a standard, a study) or on **taste**. Contrast ratios are measurements: they are facts about the colours. Whether a higher ratio reduces eye strain is a separate question, and the answer there is "Guidance only".

**Versions and host.** All read-only on the target Mac (Mac15,6, macOS 27.0.1 build 26A434, `sw_vers`):

- Ghostty 1.3.1 (`ghostty +version`), source at tag commit [`332b2ae`](https://github.com/ghostty-org/ghostty/tree/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28).
- Bundled themes come from `ghostty-themes-release-20260216-151611-fc73ce3` ([`build.zig.zon` L119-122](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/build.zig.zon#L119-L122)). They are read from `/Applications/Ghostty.app/Contents/Resources/ghostty/themes/` (463 files).
- bat 0.26.1, git-delta 0.19.2, starship 1.26.0, fzf 0.74.4, zsh-autosuggestions 0.7.1, zsh-syntax-highlighting 0.8.0 (`brew list --versions`); git 2.55.0; VS Code 1.140.0 (`code --version`).
- Display: one Studio Display XDR, "5120 x 2880 Retina", shown as "2560 x 1440 @ 120.00Hz" (`system_profiler SPDisplaysDataType`). `NSScreen` reports 2560 × 1440 points at `backingScaleFactor` 2.

Nothing was installed and no setting was changed. Font and theme files were downloaded only into a scratch folder to be measured. Candidate configs were checked with `ghostty +validate-config --config-file=<scratch file>`.

## Answer in brief

- **Theme pair: Modus Operandi (light) / Modus Vivendi (dark).** It is the only bundled pair where every one of the twelve colour slots that programs use for text is at least 7:1 against the background, in both modes. That is WCAG AAA, as its author designs it to be. The current pair, Catppuccin Latte / Mocha, ranks 20th of 31. In Latte, seven of those twelve slots are below 3:1. The yellow that git uses for commit hashes is 2.3:1.
  - **Runner-up: Modus Operandi Tinted / Modus Vivendi Tinted.** Same design, an off-white and a dark-blue background, worst text slot 6.4:1. The choice between the two is taste.
- **Font: keep JetBrains Mono.** It is embedded in Ghostty, needs no Package, and has the largest x-height per point of the candidates bar one. No font has been shown to reduce eye strain, so the rest is taste.
  - **Runner-up: Atkinson Hyperlegible Mono** (cask `font-atkinson-hyperlegible-mono`). It is designed for character distinction, but no published study backs it. Its x-height is about 10% smaller, so it needs about 1 point more.
- **Size: `font-size = 18`, up from 15.** At 15 points on this display, JetBrains Mono's x-height is 11 minutes of arc at 60 cm. That is below the 12-minute (0.2°) "critical print size" under which reading slows [LB11]. 18 points clears it out to about 66 cm. At 70 cm or more, use 20. The German statutory accident insurer's guide asks for more still: capital height of 22–31 minutes, which is 23–26 points here [DGUV]. Larger is the safe direction.
- **The Ghostty Dotfile block.** It passed `ghostty +validate-config` on Ghostty 1.3.1 (exit 0). It also passed with issue #45's "Recommended" lines appended.

  ```ini
  theme = light:Modus Operandi,dark:Modus Vivendi
  font-size = 18
  minimum-contrast = 1.1
  ```

  `minimum-contrast = 1.1` stops text from vanishing. In Vivendi, zsh-syntax-highlighting draws comments in ANSI black on a black background, at 1.0:1. In Operandi, fzf's selected line is ANSI 15 on ANSI 8, which are both `#595959`, also 1.0:1. Do not use `3`. In Vivendi it would turn zsh-autosuggestions' grey (2.998:1) into white, so suggestions would look like typed text. In Latte it would turn git's green into black.

**Other Dotfile edits the theme choice forces.** Each one moves a tool onto Ghostty's 16 ANSI colours. After that, a future theme change is one line in the Ghostty Dotfile.

1. **Starship** (`dotfiles/starship/starship.toml`): set `palette = 'ansi_dark'`. Replace the four Catppuccin palettes with two palettes that map the preset's names to ANSI names, with `crust = "#000000"` (dark) and `crust = "#ffffff"` (light). The exact text is in [Starship](#starship). Tested: `starship prompt` emits ANSI background codes 41, 103, 43, 42, 46 and 105.
2. **Starship light copy** (`dotfiles/starship/starship-light.toml.tera`): change its `replace` to swap `palette = 'ansi_dark'` for `palette = 'ansi_light'`.
3. **bat** (`dotfiles/bat/config`): replace both lines with `--theme=ansi`.
4. **delta** (`dotfiles/git/config`): replace the two `[delta "catppuccin-…"]` sections with `[delta]` and `syntax-theme = ansi`.
5. **zsh** (`dotfiles/zsh/zshrc`): drop `DELTA_FEATURES=…` from `_follow_appearance`. Keep the `STARSHIP_CONFIG` switch.
6. **fzf**: no change. `--color=16` already uses Ghostty's colours.
7. **VS Code** (not a Dotfile today): the matching extension is `wroyca.modus`. Its settings IDs are `modus-operandi` and `modus-vivendi`, not the labels. The publisher is unverified and has 1,316 installs. The built-in `Default High Contrast Light` / `Default High Contrast` need no install.
8. **Spec**: AC-35 fixes the Ghostty Dotfile's lines. Record the change as a dated amendment, as issue #45 already plans.

**What rests on evidence, and what is taste.**

| Choice | Evidence or taste | Grade for eye strain |
|---|---|---|
| A pair whose text colours are all ≥ 7:1 | Evidence: measured below. Contrast is recommended by AAO, HSE and DGUV | **Guidance only** |
| Light theme by day | Evidence: legibility (lab studies [S1][S2]); DGUV recommends positive polarity | Light mode for strain: not shown. Dark mode for strain: **Unsupported** |
| Dark theme at night (Auto) | Taste | **Unsupported** |
| Pure white vs tinted background | Taste. No study found | **Unsupported** |
| `font-size = 18` or more | Evidence: reading-speed research [LB11]; DGUV's character height [DGUV]; HSE [H2] | **Guidance only** |
| JetBrains Mono vs another font | Taste. Measured x-height is a tie-breaker, not a proven benefit | **Unsupported** |
| `minimum-contrast = 1.1` | Evidence: it fixes measured 1.0:1 cases | **Guidance only** |
| Every other Ghostty option | Taste. Leave the defaults | **Unsupported** |

## 1. Theme

### Method

The contrast measure is WCAG 2's ([WCAG 2.2, "contrast ratio" and "relative luminance"](https://www.w3.org/TR/WCAG22/#dfn-contrast-ratio)). It is the same formula Ghostty uses for `minimum-contrast` ([`shaders.metal` L95-123](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/renderer/shaders/shaders.metal#L95-L123)). The thresholds:

- 4.5:1 is WCAG's minimum for text (SC 1.4.3).
- 7:1 is its enhanced level (SC 1.4.6).
- 3:1 applies to large text and non-text marks (SC 1.4.11).

Terminal text is body text, so 4.5:1 and 7:1 are the relevant ones.

The script reads each bundled theme file and computes the following:

- foreground against background;
- each of the 16 ANSI colours against background;
- selection text against selection background.

It runs on the stock `/usr/bin/python3`:

```python
import os
THEMES = "/Applications/Ghostty.app/Contents/Resources/ghostty/themes"
def rgb(h): h = h.strip().lstrip('#'); return tuple(int(h[i:i+2], 16) / 255 for i in (0, 2, 4))
def lin(c): return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
def lum(c): r, g, b = map(lin, c); return 0.2126 * r + 0.7152 * g + 0.0722 * b
def ratio(a, b): la, lb = lum(a), lum(b); return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)
def load(name):
    t = {"palette": {}}
    for line in open(os.path.join(THEMES, name)):
        if '=' not in line: continue
        k, v = (s.strip() for s in line.split('=', 1))
        if k == "palette": i, c = v.split('='); t["palette"][int(i)] = rgb(c)
        elif v.startswith('#'): t[k] = rgb(v)
    return t
for name in ("Catppuccin Latte", "Catppuccin Mocha", "Modus Operandi", "Modus Vivendi"):
    t = load(name)
    print(name, round(ratio(t["foreground"], t["background"]), 1),
          [round(ratio(t["palette"][i], t["background"]), 1) for i in range(16)])
```

**Which slots count as text colours.** Slots 1–6 (red, green, yellow, blue, magenta, cyan) and 9–14 (their bright forms) are the ones programs use for coloured text. Slot 8 (bright black) is used for deliberately dim text. Slot 0 on a dark theme, and slots 7 and 15 on a light theme, are close to the background by design, so they are not ranked.

**How pairs are ranked.** By the lowest of slots 1–6 across both modes, then by slots 9–14.

### Ranking: 31 light/dark pairs that ship in Ghostty 1.3.1

"L" is the light theme, "D" the dark. Slot lists name the text slots (1–6, 9–14, and 8) below each threshold.

| # | Pair (light / dark) | fg:bg L / D | Worst of 1–6, L / D | Worst of 1–6 and 9–14, L / D | Slots < 4.5, L | < 4.5, D | Slots < 3, L | < 3, D |
|---|---|---|---|---|---|---|---|---|
| 1 | **Modus Operandi / Modus Vivendi** | 21.0 / 21.0 | 7.0 / 7.0 | 7.0 / 7.0 | none | 8 | none | 8 |
| 2 | Xcode Light hc / Xcode Dark hc | 21.0 / 16.4 | 6.9 / 7.2 | 6.9 / 7.2 | 8 | none | 8 | none |
| 3 | **Modus Operandi Tinted / Modus Vivendi Tinted** | 19.7 / 19.1 | 6.6 / 6.4 | 6.6 / 6.4 | none | 8 | none | 8 |
| 4 | GitHub Light Default / GitHub Dark Default | 15.8 / 16.0 | 4.9 / 7.4 | 3.2 / 7.4 | 12, 13, 14 | 8 | none | none |
| 5 | GitHub Light High Contrast / GitHub Dark High Contrast | 18.9 / 17.6 | 4.9 / 9.2 | 3.6 / 9.2 | 14 | none | none | none |
| 6 | GitHub Light Colorblind / GitHub Dark Colorblind | 14.7 / 12.3 | 4.8 / 7.5 | 3.2 / 7.5 | 12, 13, 14 | 8 | none | none |
| 7 | Xcode Light / Xcode Dark | 15.1 / 10.7 | 4.5 / 4.9 | 4.5 / 4.9 | 8 | 8 | 8 | none |
| 8 | Dayfox / Nightfox | 11.1 / 10.1 | 4.6 / 3.6 | 3.4 / 3.6 | 10, 11, 14 | 1, 8 | none | 8 |
| 9 | Gruvbox Material Light / Gruvbox Material Dark | 7.4 / 8.2 | 3.5 / 4.7 | 3.5 / 4.7 | 1, 2, 3, 5, 6, 9, 10, 11, 13, 14, 8 | 8 | 8 | none |
| 10 | Zenbones Light / Zenbones Dark | 10.6 / 9.2 | 3.5 / 5.1 | 3.5 / 5.1 | 6, 8 | 8 | 8 | 8 |
| 11 | Flexoki Light / Flexoki Dark | 18.6 / 12.0 | 3.4 / 4.4 | 2.3 / 2.9 | 2, 3, 6, 9–14, 8 | 1, 9, 10, 12, 13, 14, 8 | 11, 14, 8 | 9, 12, 13, 8 |
| 12 | Bluloco Light / Bluloco Dark | 10.8 / 7.6 | 3.4 / 3.4 | 2.3 / 3.4 | 2, 3, 9–14 | 1, 2, 4, 5, 6 | 9, 10, 11 | none |
| 13 | Kanagawa Lotus / Kanagawa Wave | 6.2 / 11.3 | 3.3 / 3.2 | 2.7 / 3.2 | 1, 2, 3, 5, 6, 9, 10, 11, 12, 14, 8 | 1, 9, 8 | 10, 12, 8 | none |
| 14 | One Half Light / One Half Dark | 10.9 / 10.5 | 3.1 / 4.4 | 1.9 / 4.4 | 1, 2, 3, 4, 6, 9–14 | 1, 9, 8 | 10–14 | 8 |
| 15 | TokyoNight Day / TokyoNight Night | 4.5 / 10.6 | 3.0 / 6.5 | 3.0 / 6.5 | all twelve, 8 | 8 | 8 | 8 |
| 16 | Selenized Light / Selenized Dark | 5.4 / 6.1 | 3.0 / 3.7 | 3.0 / 3.7 | 2, 3, 4, 5, 6, 10, 11, 13, 14, 8 | 1, 4, 9, 8 | 3, 8 | none |
| 17 | Iceberg Light / Iceberg Dark | 9.7 / 10.6 | 2.9 / 6.1 | 2.9 / 6.1 | 1, 2, 3, 5, 6, 9, 10, 11, 14, 8 | 8 | 3, 8 | none |
| 18 | iTerm2 Solarized Light / iTerm2 Solarized Dark | 4.1 / 4.7 | 2.9 / 3.2 | 2.5 / 2.8 | 1–6, 9, 11, 12, 13, 14 | 1, 4, 5, 9, 10, 11, 13, 8 | 2, 3, 6, 12, 14 | 10, 8 |
| 19 | Builtin Tango Light / Builtin Tango Dark | 21.0 / 21.0 | 2.5 / 3.2 | 1.8 / 3.2 | 2, 3, 6, 9–14 | 1, 4, 5, 8 | 3, 10, 11, 12, 14 | 8 |
| 20 | **Catppuccin Latte / Catppuccin Mocha (current)** | 7.1 / 11.3 | 2.3 / 7.1 | 1.9 / 6.2 | 2–6, 9–14, 8 | 8 | 2, 3, 5, 10, 11, 13, 14 | 8 |
| 21 | Gruvbox Light Hard / Gruvbox Dark Hard | 10.5 / 12.0 | 2.3 / 3.0 | 2.3 / 3.0 | 2, 3, 4, 5, 6, 10, 11, 8 | 1, 4, 5, 8 | 2, 3, 6 | 1 |
| 22 | Apple System Colors Light / Apple System Colors | 21.0 / 16.7 | 2.2 / 3.1 | 1.8 / 3.1 | 2, 3, 6, 9–14 | 1, 4, 5, 8 | 3, 10, 11, 14 | 8 |
| 23 | Gruvbox Light / Gruvbox Dark | 10.2 / 10.7 | 2.2 / 2.7 | 2.2 / 2.7 | 2, 3, 4, 5, 6, 10, 11, 14, 8 | 1, 4, 5, 9, 8 | 2, 3, 6 | 1 |
| 24 | Rose Pine Dawn / Rose Pine Moon | 6.7 / 11.9 | 2.1 / 4.3 | 2.1 / 4.3 | 1, 3, 4, 5, 6, 9, 11, 12, 13, 14, 8 | 2, 10, 8 | 3, 6, 11, 14, 8 | none |
| 25 | Light Owl / Night Owl | 9.9 / 13.5 | 2.0 / 5.3 | 2.0 / 5.3 | all twelve, 8 | 8 | 3, 11, 8 | 8 |
| 26 | Ayu Light / Ayu | 5.9 / 10.3 | 1.9 / 6.3 | 1.8 / 6.3 | all twelve | 8 | 1, 2, 3, 4, 6, 9, 10, 11, 12, 14 | none |
| 27 | Nord Light / Nord | 7.5 / 9.2 | 1.9 / 3.1 | 1.9 / 3.1 | all twelve | 1, 5, 9, 13, 8 | 2–6, 10–14 | 8 |
| 28 | Tomorrow / Tomorrow Night | 8.5 / 9.8 | 1.9 / 4.5 | 1.9 / 4.5 | 2, 3, 6, 10, 11, 14 | 1, 9, 8 | 3, 11 | 8 |
| 29 | Atom One Light / Atom One Dark | 13.2 / 7.2 | 1.9 / 4.8 | 1.9 / 4.8 | 1, 2, 3, 6, 9, 10, 11, 14 | 8 | 3, 11 | none |
| 30 | Everforest Light Med / Everforest Dark Hard | 4.7 / 9.4 | 1.8 / 5.8 | 1.8 / 4.7 | all twelve, 8 | none | all twelve, 8 | none |
| 31 | GitHub / GitHub Dark | 9.7 / 6.1 | 1.8 / 3.5 | 1.8 / 3.5 | 2, 3, 5, 6, 10, 11, 13, 14 | 6, 14, 8 | 3, 6, 10, 11, 13, 14 | 8 |

**The pattern.** Nearly every popular pair's dark theme is fine. The light theme is where they fail, usually on yellow, cyan, green and the bright colours. Light themes need dark hues, and many light themes are pale versions of a dark design. Only Modus and Xcode hc keep every hue at or near 7:1 in light mode.

**Why not Xcode hc, despite ranking second.** In Xcode Light hc, slot 0 ("black") is a light grey at 1.5:1, and slot 8 is 2.9:1. Programs that print "black" text, assuming a light background, get near-invisible text. zsh-syntax-highlighting's comments are one example. It also has no matching VS Code theme (see [the chain table](#cost-per-candidate)).

### Per-colour detail for the shortlisted themes

| Theme | bg | fg | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 | selection |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Catppuccin Latte | `#eff1f5` | 7.1 | 5.5 | 4.8 | 3.0 | 2.3 | 4.3 | 2.3 | 3.3 | 1.9 | 4.4 | 4.1 | 2.5 | 1.9 | 3.8 | 1.9 | 2.8 | 1.6 | 3.7 |
| Catppuccin Mocha | `#1e1e2e` | 11.3 | 1.8 | 7.1 | 11.0 | 12.9 | 7.8 | 10.7 | 11.0 | 7.4 | 2.5 | 6.2 | 9.6 | 11.1 | 6.8 | 9.3 | 9.5 | 9.3 | 4.6 |
| Modus Operandi | `#ffffff` | 21.0 | 21.0 | 8.0 | 7.0 | 7.1 | 10.4 | 11.2 | 7.1 | 2.4 | 7.0 | 8.1 | 7.1 | 7.0 | 7.0 | 9.6 | 7.5 | 7.0 | 11.2 |
| Modus Vivendi | `#000000` | 21.0 | 1.0 | 7.0 | 8.5 | 10.9 | 8.7 | 12.0 | 11.2 | 8.6 | 3.0 | 8.8 | 8.8 | 13.2 | 8.9 | 9.5 | 13.4 | 21.0 | 6.9 |
| Modus Operandi Tinted | `#fbf7f0` | 19.7 | 19.7 | 7.5 | 6.6 | 6.6 | 9.8 | 10.5 | 6.6 | 2.3 | 6.6 | 7.6 | 6.6 | 6.6 | 6.6 | 9.0 | 7.0 | 6.6 | 11.2 |
| Modus Vivendi Tinted | `#0d0e1c` | 19.1 | 1.0 | 6.4 | 7.8 | 9.9 | 7.9 | 11.0 | 10.2 | 7.9 | 2.7 | 6.8 | 8.0 | 12.0 | 8.1 | 8.6 | 12.2 | 19.1 | 6.9 |
| Xcode Light hc | `#ffffff` | 21.0 | 1.5 | 7.2 | 7.3 | 7.5 | 7.2 | 6.9 | 7.2 | 21.0 | 2.9 | 7.2 | 11.2 | 7.5 | 10.7 | 6.9 | 10.8 | 21.0 | 14.2 |
| Xcode Dark hc | `#1f1f24` | 16.4 | 1.7 | 7.2 | 8.6 | 9.6 | 8.1 | 7.3 | 7.9 | 16.4 | 4.7 | 7.2 | 13.9 | 8.2 | 10.6 | 7.3 | 11.5 | 16.4 | 9.6 |
| GitHub Light High Contrast | `#ffffff` | 18.9 | 18.9 | 8.1 | 10.2 | 14.6 | 8.0 | 8.1 | 4.9 | 5.0 | 7.8 | 10.2 | 8.1 | 12.5 | 5.1 | 5.1 | 3.6 | 3.2 | 18.9 |
| GitHub Dark High Contrast | `#0a0c10` | 17.6 | 5.0 | 9.2 | 9.2 | 10.7 | 9.2 | 9.2 | 9.4 | 14.5 | 8.0 | 11.3 | 11.4 | 12.4 | 11.4 | 11.4 | 11.1 | 19.6 | 17.6 |

### Which colours the tools on this Mac use

| Tool | Slots used for text | Source |
|---|---|---|
| git (status, branch, log) | green 2 staged and current branch; red 1 unstaged, untracked, remote; yellow 3 commit hashes; cyan 6 hunk headers; bold 1–6 for ref decorations; magenta 5, cyan 6, blue 4, yellow 3 for moved lines (`colorMoved = plain` is set) | git v2.55.0 [`diff.c` L81-103](https://github.com/git/git/blob/e9019fcafe0040228b8631c30f97ae1adb61bcdc/diff.c#L81-L103), [`wt-status.c` L45-55](https://github.com/git/git/blob/e9019fcafe0040228b8631c30f97ae1adb61bcdc/wt-status.c#L45-L55), [`log-tree.c` L41-49](https://github.com/git/git/blob/e9019fcafe0040228b8631c30f97ae1adb61bcdc/log-tree.c#L41-L49), [`builtin/branch.c` L50-58](https://github.com/git/git/blob/e9019fcafe0040228b8631c30f97ae1adb61bcdc/builtin/branch.c#L50-L58) |
| macOS `ls` | blue 4 directories, magenta 5 symlinks, green 2 sockets, yellow 3 pipes, red 1 executables. It colours by default inside Ghostty, because Ghostty sets `COLORTERM=truecolor` and `ls` treats that like `CLICOLOR` | `man ls` on the host: `-G` "is equivalent to defining CLICOLOR or COLORTERM"; default `LSCOLORS` "exfxcxdxbxegedabagacadah"; `echo $COLORTERM` |
| zsh-syntax-highlighting 0.8.0 | green 2 commands; yellow 3 strings, reserved words, redirections; red 1 bold unknown commands; blue 4 globs; magenta 5, cyan 6; **comments `fg=black,bold`** (slot 0) | `/opt/homebrew/share/zsh-syntax-highlighting/highlighters/main/main-highlighter.zsh` L32-65 (host) |
| zsh-autosuggestions 0.7.1 | slot 8 (`fg=8`) | `/opt/homebrew/share/zsh-autosuggestions/zsh-autosuggestions.zsh` L36 (host) |
| fzf `--color=16` | blue 4 prompt; green 2 matches; **bright white 15 on bright black 8 for the current line**; bright green 10 current match; yellow 3, red 1, magenta 5, cyan 6 | fzf v0.74.4 [`src/tui/tui.go` L1111-1133](https://github.com/junegunn/fzf/blob/a140afeb4d733cad3c96a56bf6db7e26853b6757/src/tui/tui.go#L1111-L1133); slot numbers from the `colBlack = iota` enum, L358-373 |
| clang diagnostics | red 1 errors, magenta 5 warnings, cyan 6 notes, green 2 carets and fix-its | LLVM [`TextDiagnostic.cpp` L26-43](https://github.com/llvm/llvm-project/blob/6a61012344ec10ce7ec109d490fc201d1fa56bef/clang/lib/Frontend/TextDiagnostic.cpp#L26-L43) (main at time of reading; Apple's clang not checked) |
| bat and delta with the `ansi` theme | slots 1–6 only | bat [`assets/themes/ansi.tmTheme`](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/assets/themes/ansi.tmTheme), decoded per [`src/terminal.rs` L6-24](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/src/terminal.rs#L6-L24) |

**What this means for Catppuccin Latte today.** The following are below 3:1:

- yellow 3 at 2.3:1: git commit hashes, zsh strings, `ls` pipes;
- magenta 5 at 2.3:1: clang warnings, `ls` symlinks;
- green 2 at 3.0:1: git staged files, zsh commands, fzf matches.

fzf's current line is 15 on 8, at 2.7:1, and its current match is 1.8:1. These are the colours the owner reads all day in light mode.

**What it means for Modus.** Every slot in the table is at least 7:1, with these exceptions:

- **Slot 8 in Vivendi is 3.0:1.** That is zsh-autosuggestions' ghost text. Dim is the intent, and it stays legible.
- **Slot 0 in Vivendi is 1.0:1.** Comments typed at the prompt vanish. They are highlighted only when `INTERACTIVE_COMMENTS` is set, which the zshrc Dotfile does not set. `minimum-contrast = 1.1` turns them white.
- **fzf's current line in Operandi is 1.0:1.** The bundled file sets slot 15 to `#595959`, the same as slot 8. `minimum-contrast = 1.1` turns that text white, at 7.0:1. See the next section for where 15 differs from the author's mapping.

### Is Ghostty's Modus faithful to its author's design?

- **The author's claim.** "The Modus themes are designed for accessible readability. They conform with the highest standard for color contrast between combinations of background and foreground values. For small sized text, this corresponds to the WCAG AAA standard, which specifies a minimum rate of distance in relative luminance of 7:1." ([`doc/modus-themes.org` L71-76](https://github.com/protesilaos/modus-themes/blob/2d044ac89f3bca7011fa2bfda003cf80ce115f70/doc/modus-themes.org#L71-L76), version 5.3.0.) The author adds that the ratio is always "against the background", not between neighbouring colours (L5926-5931).
- **Slots 1–6 and 8–14 of Ghostty's Modus Operandi match the author's palette.**
  - Normal colours: `red`, `green`, `yellow`, `blue`, `magenta`, `cyan`.
  - Bright colours: `red-warmer`, `green-cooler`, `yellow-warmer`, `blue-warmer`, `magenta-cooler`, `cyan-cooler`.
  - Sources: [`modus-themes.el` L686-729](https://github.com/protesilaos/modus-themes/blob/2d044ac89f3bca7011fa2bfda003cf80ce115f70/modus-themes.el#L686-L729) and the terminal mapping, [L614-655](https://github.com/protesilaos/modus-themes/blob/2d044ac89f3bca7011fa2bfda003cf80ce115f70/modus-themes.el#L614-L655).
- **Two slots differ.**
  - **Operandi slot 15** is `#595959` in Ghostty, but `#ffffff` in the author's mapping (`fg-term-white-bright`). That is why fzf's current line is invisible without `minimum-contrast`.
  - **Vivendi slot 9** is `#ff7f9f` in Ghostty, but `#ff6b55` (`red-warmer`) in 5.3.0. Ghostty's value is 8.8:1.
- **The figures above are the bundled files.** They are not the author's own numbers.

### What `minimum-contrast` does

**How it works.** It is a floor, not a gentle shift. Any glyph below the floor against its cell background is redrawn in pure white or pure black, whichever contrasts more ([`shaders.metal` L105-123, applied at L650-656](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/renderer/shaders/shaders.metal#L105-L123)). The hue is lost.

- The docs say: "If you want to avoid invisible text (same color as background), a value of 1.1 is a good value. If you want to avoid text that is difficult to read, a value of 3 or higher is a good value. The higher the value, the more likely that text will become black or white." It "does not apply to Emoji or images." (`ghostty +show-config --default --docs`, host.)
- Ghostty measures in linear Display P3 with sRGB weights ([`load_color`, L126-175](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/renderer/shaders/shaders.metal#L126-L175)). That is close to WCAG, but not identical. Re-running all 62 themes in Ghostty's space moved only 12 slots across a threshold. All of them were within 0.15 of the line, and none was in the recommended pairs.
- It applies to cells with an explicit background too: Starship's segments, delta's diff lines, fzf's current line.

Slots that each floor would replace:

| Theme | at 1.1 | at 3 | at 4.5 |
|---|---|---|---|
| Catppuccin Latte | none | 2, 3, 5, 7, 10, 11, 13, 14, 15 | 2–15 |
| Catppuccin Mocha | none | 0, 8 | 0, 8 |
| Modus Operandi | none | 7 | 7 |
| Modus Vivendi | 0 | 0, **8** (2.998) | 0, 8 |
| Modus Operandi Tinted / Vivendi Tinted | none / 0 | 7 / 0, 8 | 7 / 0, 8 |
| GitHub Light / Dark High Contrast | none / none | none / none | 14, 15 / none |
| Xcode Light hc / Dark hc | none / none | 0, 8 / 0 | 0, 8 / 0 |

**Recommendation: `1.1`. Grade: Guidance only.**

- With Modus, 1.1 is enough. The theme already does the work, and 1.1 only catches the 1.0:1 cases.
- With Latte, issue #45's alternative of `3` would blacken green, yellow and magenta. git status would lose its red/green meaning for staged files.
- With Vivendi, `3` would whiten autosuggestions, so they would look like typed text.

### APCA

No primary source supports using it here. The current W3C draft of WCAG 3 (Working Draft, 10 September 2026) says: "The contrast algorithm used in WCAG 3 is yet to be determined" ([WCAG 3.0 WD, "Text contrast sufficient (minimum)"](https://www.w3.org/TR/wcag-3.0/)). The draft text does not mention APCA. This note uses WCAG 2 only.

### Background luminance and pure white on a bright 5K display

- **Positive polarity.** DGUV's guide recommends dark text on a light background. With "flimmerfreie Positivdarstellung", reflections are less disturbing, and the constant switching between light and dark adaptation is reduced [DGUV p. 33]. This agrees with eye-strain.md's polarity row, and adds a statutory occupational-health source to it.
- **Brightness.** The same page asks for at least 100 cd/m² and a luminance ratio of at least 4:1 between character and background [DGUV p. 33]. Eye-strain.md already covers brightness matched to the room (row 7, **Guidance only**). On the XDR that is a slider, not a theme.
- **Off-white versus white.** No study was found that an off-white background reduces strain. Grade: **Unsupported**.
  - In arithmetic: Latte's background has 88% of white's relative luminance, and Modus Operandi Tinted's has 93%. Choosing a tinted theme is about the same as lowering brightness by 7–12%, which the brightness slider does for every app.
  - So choose Tinted over plain for taste, not for eye comfort.
- **Pure black in Vivendi on a mini-LED panel.** Local-dimming blooming around bright text was not measured and no source was found (see Could not verify).

## 2. The cost of switching theme across the chain

**The idea.** Point every tool at Ghostty's 16 ANSI colours. Then the Ghostty `theme` line is the only place a theme is named, and contrast for every tool traces back to the table above. Today, four tools carry their own Catppuccin copies.

### Starship

- **Today.** `palette = 'catppuccin_mocha'`, with four hard-coded hex palettes. The light copy is generated by swapping the palette line (`dotfiles/starship/starship-light.toml.tera`). Palette entries are looked up before ANSI names, so the prompt ignores Ghostty's theme ([appearance.md](appearance.md#starship-1260)). Starship still has no light/dark palette ([starship#6991](https://github.com/starship/starship/issues/6991), open).
- **A finding about today's light prompt.** Segment text is `crust` (`#dce0e8` in Latte) on saturated segment colours. Measured:

  | Segment | red | peach | yellow | green | sapphire | lavender |
  |---|---|---|---|---|---|---|
  | Latte copy (light), `crust` on colour | 4.1 | 2.3 | **2.0** | 2.5 | 2.4 | 2.4 |
  | Mocha (dark), `crust` on colour | 8.1 | 10.6 | 14.8 | 12.6 | 9.9 | 10.5 |

  The light prompt's directory, git and language segments are all near 2:1.
- **The edit.** A palette value may be an ANSI name, because palette values are parsed without the palette ([`config.rs` L465-468](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/src/config.rs#L465-L468)). Starship's names are `black`, `red`, `green`, `blue`, `yellow`, `purple`, `cyan`, `white`, with an optional `bright-` prefix ([advanced-config "Style Strings"](https://github.com/starship/starship/blob/fca92d8dcbd5981b0160af2f7ed7a430b6475a72/docs/advanced-config/README.md#style-strings)). Note `purple`, not `magenta`.
  - In `dotfiles/starship/starship.toml`, set `palette = 'ansi_dark'`.
  - Replace everything from `[palettes.catppuccin_mocha]` to the end with:

    ```toml
    [palettes.ansi_dark]
    red = "red"
    peach = "bright-yellow"
    yellow = "yellow"
    green = "green"
    sapphire = "cyan"
    lavender = "bright-purple"
    crust = "#000000"

    [palettes.ansi_light]
    red = "red"
    peach = "bright-yellow"
    yellow = "yellow"
    green = "green"
    sapphire = "cyan"
    lavender = "bright-purple"
    crust = "#ffffff"
    ```

  - In `starship-light.toml.tera`, change the `replace` to `from="palette = 'ansi_dark'", to="palette = 'ansi_light'"`.
- **Why `crust` is per mode.** It is the text colour on the coloured segments, so it must be the opposite of the hues. Setting it to the theme's background makes each segment's contrast equal to that hue's ANSI-vs-background ratio. With Modus, that is 7.0–13.2:1:

  | Segment | red 1 | peach → 11 | yellow 3 | green 2 | sapphire → 6 | lavender → 13 |
  |---|---|---|---|---|---|---|
  | Operandi, white text | 8.0 | 7.0 | 7.1 | 7.0 | 7.1 | 9.6 |
  | Vivendi, black text | 7.0 | 13.2 | 10.9 | 8.5 | 11.2 | 9.5 |

- **Tested.** The ANSI mapping was tested in a scratch copy of the Dotfile with `starship prompt`. The output used ANSI backgrounds 41, 103, 43, 42, 46 and 105, and text `38;2;0;0;0`.
- **Not tested.** The live switch inside Ghostty.
- **Timing.** The hues now follow Ghostty live. `crust` still switches at the next prompt, through the existing `precmd` hook.

### bat

- **Edit.** Replace both lines of `dotfiles/bat/config` with `--theme=ansi`.
- **What `ansi` uses.** bat's README says `ansi` "uses 3-bit colors: black, red, green, yellow, blue, magenta, cyan, and white" ([README L505-511](https://github.com/sharkdp/bat/blob/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e/README.md#L505-L511)). In practice the theme file uses only slots 1–6 for foregrounds, plus the default text colour (`ansi.tmTheme`, decoded above).
- **Tested** on the host: `bat --theme=ansi` emitted SGR 32, 34 and 35.
- **Cost.** Comments and strings share green, so syntax colouring has fewer distinctions than Catppuccin's. That is taste.
- **Named themes bat ships**, from `bat --list-themes`: Catppuccin (all four), GitHub (light only), gruvbox-dark and gruvbox-light, Solarized (dark) and (light), OneHalfDark and OneHalfLight, Nord, Coldark, and others. There is no Modus, Xcode, Rose Pine, Tokyo Night, Everforest or Kanagawa.

### delta

- **Edit.** In `dotfiles/git/config`, replace the two sections `[delta "catppuccin-latte"]` and `[delta "catppuccin-mocha"]` with:

  ```ini
  [delta]
  	syntax-theme = ansi
  ```

  Then drop `DELTA_FEATURES="catppuccin-…"` from both branches of `_follow_appearance` in `dotfiles/zsh/zshrc`.
- **Why it works.** delta reads ANSI-encoded theme colours ([`src/utils/bat/terminal.rs` L6-12](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/utils/bat/terminal.rs#L6-L12)). It still asks the terminal for light or dark on every run ([`src/options/theme.rs` L71-102](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/options/theme.rs#L71-L102)), so its diff backgrounds follow too.
  - **Caveat.** If detection fails, as with redirected output that is not `--color-only`, a theme named `ansi` counts as dark (L40-50).
- **Tested** on the host: `delta --syntax-theme ansi --light` drew added lines with SGR 32, 34 and 35 on `#d0ffd0`.
- **Contrast on delta's default diff backgrounds** ([`src/color.rs` L156-184](https://github.com/dandavison/delta/blob/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd/src/color.rs#L156-L184)). Removed lines are drawn in the default text colour. Added lines are syntax-coloured.

  | Theme | removed line, fg | added line, worst of 1–6 | added and emphasised, worst of 1–6 |
  |---|---|---|---|
  | Modus Operandi | 17.0 | 6.3 | 5.2 |
  | Modus Vivendi | 17.3 | 5.4 | 2.6 (red on `#006000`) |
  | Catppuccin Latte (`ansi`, for comparison) | 6.5 | 2.4 | 1.9 |

  Vivendi's emphasised added words are the weak spot. delta's `plus-emph-style` can override that background if it matters.

### fzf

No edit. `--color=16` draws with the terminal's colours ([appearance.md](appearance.md#fzf-0744)). fzf's current line is the one place the bundled Operandi is unreadable (slot 15 on slot 8, 1.0:1). `minimum-contrast = 1.1` fixes it.

### VS Code

VS Code is not a Dotfile in this repo today. The host's settings set `window.autoDetectColorScheme: true` with the Catppuccin pair.

- **Theme ID gotcha.** VS Code matches `workbench.preferred*ColorTheme` against a theme's `id` if it has one, and only otherwise against its label ([`colorThemeData.ts` L719-725](https://github.com/microsoft/vscode/blob/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/src/vs/workbench/services/themes/common/colorThemeData.ts#L719-L725), 1.139.1). The Modus extension sets IDs, so the settings values are `modus-operandi` and `modus-vivendi`.
- **`wroyca.modus` 0.5.2** (Marketplace API, 2026-10-03).
  - Its manifest says "Accessible themes conforming to the highest standard for color contrast (WCAG AAA)", and it ports all eight Modus themes.
  - Cautions: the publisher is not domain-verified; it has 1,316 installs; it ships code (`main: ./out/extension.js`).
  - It is a third-party port. Its colours were not measured here.
- **Built-in alternative.** VS Code ships `Default High Contrast Light` and `Default High Contrast` ([`extensions/theme-defaults/package.json`](https://github.com/microsoft/vscode/blob/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1/extensions/theme-defaults/package.json)). They need no install.

### Cost per candidate

Once Starship, bat and delta use ANSI colours, the per-theme cost is the Ghostty line, the two `crust` values (the theme's backgrounds), and VS Code. Marketplace facts are from its API on 2026-10-03.

| Pair | Ghostty `theme =` | Starship `crust` light / dark | bat/delta named theme (if not `ansi`) | VS Code extension (verified publisher?) → settings IDs |
|---|---|---|---|---|
| Modus | `light:Modus Operandi,dark:Modus Vivendi` | `#ffffff` / `#000000` | none | `wroyca.modus` (no) → `modus-operandi` / `modus-vivendi` |
| Modus Tinted | `light:Modus Operandi Tinted,dark:Modus Vivendi Tinted` | `#fbf7f0` / `#0d0e1c` | none | `wroyca.modus` (no) → `modus-operandi-tinted` / `modus-vivendi-tinted` |
| Xcode hc | `light:Xcode Light hc,dark:Xcode Dark hc` | `#ffffff` / `#1f1f24` | none | no hc port found; `MateoCERQUETELLA.xcode-12-theme` (no) has non-hc Xcode themes |
| GitHub High Contrast | `light:GitHub Light High Contrast,dark:GitHub Dark High Contrast` | `#ffffff` / `#0a0c10` | `GitHub` (light only) | `GitHub.github-vscode-theme` (yes) → `GitHub Light High Contrast` / `GitHub Dark High Contrast` |
| Catppuccin (current) | unchanged | `#eff1f5` / `#1e1e2e` | `Catppuccin Latte` / `Catppuccin Mocha` | `Catppuccin.catppuccin-vsc` (yes, installed) → `Catppuccin Latte` / `Catppuccin Mocha` |
| Gruvbox | `light:Gruvbox Light,dark:Gruvbox Dark` | `#fbf1c7` / `#282828` | `gruvbox-light` / `gruvbox-dark` | `jdinhlife.gruvbox` (no) → `Gruvbox Light Medium` / `Gruvbox Dark Medium` |
| Rose Pine | `light:Rose Pine Dawn,dark:Rose Pine Moon` | `#faf4ed` / `#232136` | none | `mvllow.rose-pine` (no) → `Rosé Pine Dawn` / `Rosé Pine Moon` |
| Tokyo Night | `light:TokyoNight Day,dark:TokyoNight Night` | `#e1e2e7` / `#1a1b26` | none | `enkia.tokyo-night` (no) → `Tokyo Night Light` / `Tokyo Night` |
| Solarized | `light:iTerm2 Solarized Light,dark:iTerm2 Solarized Dark` | `#fdf6e3` / `#002b36` | `Solarized (light)` / `Solarized (dark)` | built in: `Solarized Light` / `Solarized Dark` |
| One Half | `light:One Half Light,dark:One Half Dark` | `#fafafa` / `#282c34` | `OneHalfLight` / `OneHalfDark` | not checked |
| Everforest | `light:Everforest Light Med,dark:Everforest Dark Hard` | `#efebd4` / `#1e2326` | none | `sainnhe.everforest` (no) → `Everforest Light` / `Everforest Dark` |
| Kanagawa | `light:Kanagawa Lotus,dark:Kanagawa Wave` | `#f2ecbc` / `#1f1f28` | none | `qufiwefefwoyn.kanagawa` (no) → `Kanagawa` (dark only) |

## 3. Font

### Candidates and their install channel

Each cask was checked against `https://formulae.brew.sh/api/cask/<token>.json` on 2026-10-03. None is deprecated or disabled.

| Font | Install channel | Version |
|---|---|---|
| JetBrains Mono | **Embedded in Ghostty** (variable, 2.304); cask `font-jetbrains-mono` 2.304; `font-jetbrains-mono-nerd-font` 3.5.1 already installed | [`build.zig.zon` L105-109](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/build.zig.zon#L105-L109) |
| SF Mono | cask `font-sf-mono` (Apple's DMG). Not visible to apps by default: `ghostty +list-fonts` does not list it. The system copy `/System/Library/Fonts/SFNSMono.ttf` is a hidden system face | latest |
| Atkinson Hyperlegible Mono | cask `font-atkinson-hyperlegible-mono` (from google/fonts) | latest |
| IBM Plex Mono | cask `font-ibm-plex-mono` | 2.5.0 |
| Iosevka | cask `font-iosevka` | 34.9.0 |
| Fira Code | cask `font-fira-code` | 6.2 |
| Cascadia Code / Mono | casks `font-cascadia-code`, `font-cascadia-mono` | 2407.24 |
| Monaspace | cask `font-monaspace` | 1.400 |
| Maple Mono | cask `font-maple-mono` | 7.9 |
| Geist Mono | cask `font-geist-mono` | 1.7.2 |
| Commit Mono | cask `font-commit-mono` | 1.143 |
| Source Code Pro | cask `font-source-code-pro` (from google/fonts) | latest |

**SF Mono's licence.** Apple's fonts page licenses its downloadable fonts "solely for creating mock-ups of user interfaces" ([developer.apple.com/fonts](https://developer.apple.com/fonts/), read through a fetch summary). Using it as a terminal font is outside that wording. That rules it out for a public setup repo.

### Measurements

**Method.** One Regular file per family was downloaded from the cask's own URL into scratch space. Variable fonts were set to weight 400 with `fonttools varLib.instancer`. Heights were measured with `uvx --from fonttools` as the top of the outline of `x` and `H`. Advance width is that of `0`. "Line" is the font's own line height (typo or hhea metrics). Stroke is the width of `|` divided by cap height. DGUV asks for strokes of 8–17% of character height and lowercase near 70% of capitals [DGUV p. 34]; every font passes both.

| Font | x-height / em | cap / em | x / cap | advance / em | line / em | stroke / cap |
|---|---|---|---|---|---|---|
| Maple Mono 7.900 | 0.560 | 0.740 | 0.76 | 0.600 | 1.32 | 0.122 |
| **JetBrains Mono 2.304** | **0.550** | 0.730 | 0.75 | 0.600 | 1.32 | 0.123 |
| Commit Mono 1.143 | 0.540 | 0.700 | 0.77 | 0.600 | 1.10 | 0.111 |
| Fira Code 6.002 | 0.540 | 0.706 | 0.76 | 0.615 | 1.23 | 0.109 |
| Geist Mono 1.700 | 0.530 | 0.710 | 0.75 | 0.600 | 1.30 | 0.113 |
| SF Mono (system copy) | 0.530 | 0.705 | 0.75 | 0.618 | 1.18 | 0.108 |
| Iosevka 34.9.0 | 0.520 | 0.735 | 0.71 | **0.500** | 1.25 | 0.106 |
| Cascadia Mono 2407.24 | 0.518 | 0.693 | 0.75 | 0.586 | 1.16 | 0.146 |
| IBM Plex Mono 2.005 | 0.516 | 0.698 | 0.74 | 0.600 | 1.30 | 0.100 |
| Monaspace Neon 1.400 | 0.513 | 0.730 | 0.70 | 0.620 | 1.25 | 0.133 |
| Atkinson Hyperlegible Mono 2.001 | 0.496 | 0.668 | 0.74 | **0.632** | 1.30 | 0.126 |
| Source Code Pro 1.026 | 0.486 | 0.656 | 0.74 | 0.600 | 1.26 | 0.113 |

**Character disambiguation.** A specimen of `Il1|`, `O0o`, `rn m` and quotes was rendered with Pillow at 64 px for each font and inspected. All twelve pass:

- `I` has serifs, `l` has a tail, `1` has a flag and a foot, and `|` is taller.
- `0` is dotted (Cascadia, IBM Plex, Monaspace, Source Code Pro, JetBrains Mono) or slashed (Atkinson, Commit, Fira, Geist, Iosevka, Maple, SF Mono), so it is distinct from `O`. DGUV requires that zero and capital O cannot be confused [DGUV p. 35].
- `rn` versus `m` is not an issue in a monospaced font, because `rn` takes two cells.
- Straight quote and backtick are distinct.

So disambiguation does not separate the candidates.

### What research exists

- **Bigelow 2019** reviews legibility research and makes no claim that any typeface reduces fatigue [S15] (already in eye-strain.md).
- **Beier and Thiessen 2026** (Ergonomics, review) conclude "there is no such thing as the most legible typeface, as typeface legibility varies depending on the reading situation". Their summary favours the following [BT26]:
  - simple designs, open counters and wider letters;
  - avoiding condensed fonts and extreme weights;
  - noting that "Larger x-heights aid recognition".

  By that standard, Iosevka's default width (0.500 em) is condensed. Atkinson is the widest of the set, and JetBrains and Maple have the largest x-heights.
- **Mansfield, Legge and Bane 1996** is the one controlled study found that compares a fixed-width font (Courier) with a proportional one (Times) [MLB96]. It used 50 normal and 42 low-vision readers on MNREAD charts.
  - Courier gave slightly better acuity and a smaller critical print size.
  - Times was 5% faster at full size for normal readers.
  - "For print sizes close to the acuity limit, choice of font could make a significant difference."

  The lesson for this note: font matters most when text is near too small. Fix size first.
- **Arditi and Cho 2005.** Serifs made no difference to reading speed [AC05].
- **Atkinson Hyperlegible.** The Braille Institute says the family "focuses on letterform distinction" for "low vision readers". It calls Mono "an entirely new typeface inspired by the Atkinson Hyperlegible font", which can be "scanned quickly in table-based and coding environments" ([brailleinstitute.org/freefont](https://www.brailleinstitute.org/freefont/)). The page claims it can "Reduce eye strain", but cites no study. PubMed has no study of Atkinson Hyperlegible (searched 2026-10-03). That claim is **Unsupported**.
- **No study was found** of programming fonts, ligatures, or monospaced fonts and eye strain.

**Grade for font choice and eye strain: Unsupported** (unchanged from eye-strain.md row 19). **Recommendation: keep JetBrains Mono (taste).** It costs nothing, it is the second-largest x-height per point, and it is not condensed. If the owner dislikes it, Atkinson Hyperlegible Mono is the runner-up for its documented design aim. Maple Mono or IBM Plex Mono are equally defensible. Pick by eye at the new size, not by reputation.

### Nerd Font symbols with a non-Nerd font

Yes, they still render in Ghostty 1.3.1:

- Configured fonts are added first ([`SharedGridSet.zig` L178-257](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/font/SharedGridSet.zig#L178-L257)).
- Ghostty then always appends its embedded JetBrains Mono (L259-317) and an embedded "Symbols Nerd Font" as fallbacks (L319-333; [`embedded.zig` L8-13](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/font/embedded.zig#L8-L13); Nerd Fonts Symbols Only 3.4.0, [`build.zig.zon` L110-113](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/build.zig.zon#L110-L113)).
- The docs say Ghostty "embeds a default font (JetBrains Mono), has built-in nerd fonts" ([`docs/config/index.mdx`](https://github.com/ghostty-org/website/blob/7962e91e190ff226be1a4983eb9368b7ddb4dff9/docs/config/index.mdx)). The 1.2.0 notes say symbols come from "a standalone symbols-only font" and are resized to the cell ([`1-2-0.mdx`](https://github.com/ghostty-org/website/blob/7962e91e190ff226be1a4983eb9368b7ddb4dff9/docs/install/release-notes/1-2-0.mdx)).
- Powerline separators and box drawing are drawn by Ghostty's own sprite face, whatever the font ([`sprite/Face.zig` L1-2, L67](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/font/sprite/Face.zig)).

So no Nerd-patched font is needed in Ghostty. The installed `font-jetbrains-mono-nerd-font` cask serves other apps only.

## 4. Size

### The arithmetic

1. **One macOS point.** The XDR is 218 pixels per inch (Apple [AP2] in eye-strain.md). At "2560 × 1440" it draws 2 pixels per point (`backingScaleFactor` 2). So one point = 2 / 218 × 25.4 = **0.2330 mm**.
2. **Ghostty's size.** Ghostty sets its DPI to 72 × the backing scale ([`Surface.zig` L494-510](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/Surface.zig#L494-L510)) and converts with points × DPI / 72 ([`face.zig` L46-58](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/font/face.zig#L46-L58)). So `font-size = N` gives an em of 2N pixels, which is N × 0.2330 mm.
3. **Character heights.** Cap height = em × cap/em, and x-height = em × x/em, from the table above.
4. **Visual angle** in minutes of arc = 2 × atan(h / 2d) × (180/π) × 60, which is about 3438 × h / d.

To plug in your own distance d (mm): the smallest font size for a target angle A (arcmin) is

> N = 2 · d · tan(A / 120°) / (fraction × 0.2330)

where "fraction" is the font's x/em or cap/em.

**The built-in display** is 254 ppi at "1512 × 982" ([AP1] in eye-strain.md), so one point is 0.200 mm. The same `font-size` is 14% smaller there, usually at a shorter distance.

### JetBrains Mono on the XDR

| font-size | em px | cap mm | cap ′ at 60 / 70 / 80 cm | x-height mm | x-height ′ at 60 / 70 / 80 cm |
|---|---|---|---|---|---|
| 13 (Ghostty default) | 26 | 2.21 | 12.7 / 10.9 / 9.5 | 1.67 | 9.5 / 8.2 / 7.2 |
| 14 | 28 | 2.38 | 13.6 / 11.7 / 10.2 | 1.79 | 10.3 / 8.8 / 7.7 |
| **15 (today)** | 30 | 2.55 | 14.6 / 12.5 / 11.0 | 1.92 | **11.0** / 9.4 / 8.3 |
| 16 | 32 | 2.72 | 15.6 / 13.4 / 11.7 | 2.05 | 11.7 / 10.1 / 8.8 |
| 17 | 34 | 2.89 | 16.6 / 14.2 / 12.4 | 2.18 | 12.5 / 10.7 / 9.4 |
| **18** | 36 | 3.06 | 17.5 / 15.0 / 13.2 | 2.31 | **13.2** / 11.3 / 9.9 |
| 20 | 40 | 3.40 | 19.5 / 16.7 / 14.6 | 2.56 | 14.7 / 12.6 / 11.0 |
| 22 | 44 | 3.74 | 21.4 / 18.4 / 16.1 | 2.82 | 16.2 / 13.8 / 12.1 |
| 24 | 48 | 4.08 | 23.4 / 20.1 / 17.5 | 3.08 | 17.6 / 15.1 / 13.2 |

### What the standards and studies ask for

- **Critical print size, 12′ x-height.** Legge and Bigelow 2011 (review) [LB11]:
  - Reading runs at full speed over x-heights "from approximately 0.2° to 2°".
  - Below the critical print size, reading speed "begins to decline sharply".
  - That size "typically lies in the range from about 0.15° to 0.3° depending on the individual", with a consensus of 0.2° (12′).
  - This is a reading-speed finding, not an eye-strain one. It is the strongest primary evidence on size that applies here.
- **DGUV, 22–31′ cap height.** DGUV Information 215-410 (German Social Accident Insurance, September 2015) [DGUV pp. 34-35]:
  - Capital height (for example "E") should appear "unter einem Sehwinkel zwischen 22 Bogenminuten und 31 Bogenminuten".
  - That is distance / 155 for 22′, and distance / 110 for 31′.
  - Its table: 3.9–5.5 mm at 600 mm, 4.5–6.4 mm at 700 mm, 5.2–7.3 mm at 800 mm.
  - It lists DIN EN ISO 9241-303 as further reading.
- **ISO 9241-303:2011.** Paywalled and not read. The ANSI preview returned HTTP 403. Eye-strain.md's figures (16′ minimum, 20–22′ preferred) come from a secondary summary [S8]. DGUV's 22′ floor is stricter than that summary's preferred range.
- **HSE**: text "large enough to read easily ... when sitting in a normal comfortable working position" [H2].

### Smallest font-size per font, at 60 / 70 / 80 cm

| Font | x-height 12′ (critical print size) | x-height 18′ (top of the individual range) | cap 16′ (ISO, secondary) | cap 22′ (DGUV floor) |
|---|---|---|---|---|
| JetBrains Mono | 16.3 / 19.1 / 21.8 | 24.5 / 28.6 / 32.7 | 16.4 / 19.2 / 21.9 | 22.6 / 26.3 / 30.1 |
| Maple Mono | 16.0 / 18.7 / 21.4 | 24.1 / 28.1 / 32.1 | 16.2 / 18.9 / 21.6 | 22.3 / 26.0 / 29.7 |
| Commit Mono | 16.6 / 19.4 / 22.2 | 25.0 / 29.1 / 33.3 | 17.1 / 20.0 / 22.8 | 23.5 / 27.5 / 31.4 |
| Fira Code | 16.6 / 19.4 / 22.2 | 25.0 / 29.1 / 33.3 | 17.0 / 19.8 / 22.6 | 23.3 / 27.2 / 31.1 |
| Geist Mono | 17.0 / 19.8 / 22.6 | 25.4 / 29.7 / 33.9 | 16.9 / 19.7 / 22.5 | 23.2 / 27.1 / 30.9 |
| SF Mono | 17.0 / 19.8 / 22.6 | 25.4 / 29.7 / 33.9 | 17.0 / 19.8 / 22.7 | 23.4 / 27.3 / 31.2 |
| Iosevka | 17.3 / 20.2 / 23.0 | 25.9 / 30.2 / 34.6 | 16.3 / 19.0 / 21.7 | 22.4 / 26.2 / 29.9 |
| Cascadia Code / Mono | 17.4 / 20.2 / 23.1 | 26.0 / 30.4 / 34.7 | 17.3 / 20.2 / 23.1 | 23.8 / 27.7 / 31.7 |
| IBM Plex Mono | 17.4 / 20.3 / 23.2 | 26.1 / 30.5 / 34.8 | 17.2 / 20.0 / 22.9 | 23.6 / 27.5 / 31.5 |
| Monaspace Neon | 17.5 / 20.4 / 23.4 | 26.3 / 30.7 / 35.0 | 16.4 / 19.2 / 21.9 | 22.6 / 26.3 / 30.1 |
| Atkinson Hyperlegible Mono | 18.1 / 21.1 / 24.2 | 27.2 / 31.7 / 36.2 | 17.9 / 20.9 / 23.9 | 24.7 / 28.8 / 32.9 |
| Source Code Pro | 18.5 / 21.6 / 24.7 | 27.7 / 32.4 / 37.0 | 18.3 / 21.3 / 24.4 | 25.1 / 29.3 / 33.5 |

Ghostty takes half points ("13.5pt @ 2px/pt = 27px", `+show-config --docs`), so round up to the next 0.5.

**Recommendation: `font-size = 18` for JetBrains Mono as a floor. Grade: Guidance only** (as eye-strain.md row 9).

- At 60–66 cm, 18 clears both the critical print size and the secondary ISO minimum.
- At 70 cm or more, use 20.
- With Atkinson Hyperlegible Mono, use 19, or 21 at 70 cm or more.
- DGUV's guidance would put it at 23–26. The display has room: at 20 points, a half-screen window is still about 106 columns wide (1280 points / (20 × 0.6)).
- The owner can measure eye-to-screen distance once and read the right size off the table.
- An alternative that scales every app is the macOS setting Displays > resolution ("Larger Text"). That is the owner's choice, and is already in eye-strain.md.

## 5. Ghostty options that bear on eye comfort

From `ghostty +show-config --default --docs` on 1.3.1 (host), unless cited otherwise.

| Option (default) | What it does | Grade for eye strain | Recommendation |
|---|---|---|---|
| `theme` | Light/dark pair following macOS | Contrast: **Guidance only**; polarity for strain: **Unsupported** | `light:Modus Operandi,dark:Modus Vivendi` |
| `font-size` (13) | Points; 1 pt = 2 px here | **Guidance only** | `18`, or 20 at 70 cm or more |
| `minimum-contrast` (1) | Below the floor, text becomes pure white or black | **Guidance only** | `1.1` (see [above](#what-minimum-contrast-does)) |
| `font-family` (embedded JetBrains Mono) | Primary font; Nerd symbols still fall back | **Unsupported** | Leave unset (taste) |
| `font-thicken` (false), `font-thicken-strength` (255) | "Draw fonts with a thicker stroke", macOS only. It uses Core Graphics font smoothing ([`coretext.zig` L478-505](https://github.com/ghostty-org/ghostty/blob/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28/src/font/face/coretext.zig#L478-L505)) | **Unsupported** (no studies; eye-strain.md row 20 for smoothing) | Leave default. Try it if dark-on-light strokes look thin; taste |
| `alpha-blending` (`native` on macOS) | `linear` "makes dark text look much thinner"; `linear-corrected` looks "nearly or completely identical to `native`" | **Unsupported** | Leave default. Never `linear` with a light theme |
| `window-colorspace` (`srgb`) | `display-p3` reads theme hex values as P3, making them more saturated | **Unsupported** | Leave default. The contrast figures assume sRGB |
| `adjust-cell-height` / `adjust-cell-width` (none) | Line and column spacing | **Unsupported** (eye-strain.md row 20). DGUV asks only for at least one pixel between descenders and ascenders [DGUV p. 34]; every font's own line height (1.10–1.32 em) gives more | Leave default (taste). Issue #45's `10%` is taste |
| `window-padding-x/y` (2), `-balance` (false) | Space at the window edge | **Unsupported** | Taste |
| `background-opacity` (1), `background-blur` (false) | Lets what is behind the window show through | **Unsupported**. By arithmetic, any opacity below 1 mixes in the desktop and lowers contrast by an unknown amount, against contrast guidance | Leave at 1 |
| `cursor-style` (block), `cursor-style-blink` (unset, blinks) | Cursor shape and blinking. Shell integration sets a bar at the prompt | **Unsupported** | Taste |
| `bold-color` (unset) | `bright` draws bold in the bright palette | **Unsupported** | Leave default. Modus's bright hues are also ≥ 7:1 |
| `faint-opacity` (0.5) | Dims SGR 2 text. Measured faint fg: Operandi 4.0, Vivendi 5.3, Latte 2.3 (gamma-space approximation) | **Unsupported** | Leave default. Faint is meant to be dim |
| `font-feature` (none) | `-calt` turns off programming ligatures | **Unsupported** (no studies) | Taste |
| `palette` overrides | One `palette = N=#…` line applies to both themes of a pair | **Unsupported** | None needed with Modus |
| `selection-foreground/background` (from theme) | Selection colours | **Guidance only** (contrast) | Leave to the theme: Modus 11.2 / 6.9, Latte 3.7 |
| `unfocused-split-opacity` (0.7) | Overlays unfocused splits with the background colour. Measured fg there: Operandi 8.5, Vivendi 10.0, Latte 3.5 | **Unsupported** | Leave default. It marks focus, and Modus keeps it readable |

## 6. Display settings that touch the terminal

Keep these short; eye-strain.md has the detail.

- **Brightness matched to the room**, with "Automatically Adjust Brightness" on (it was on: `system_profiler`). Row 7, **Guidance only**. On a light theme this matters more than the theme's background colour (see [Background luminance](#background-luminance-and-pure-white-on-a-bright-5k-display)).
- **Presets and reference modes.** Apple lists modes for the Studio Display XDR, such as "Apple XDR Display (P3-2000 nits)", "Design and Print (P3-D50)" and "Medical Imaging (DICOM-350 nits)". Apple warns that "True Tone, Night Shift, Auto Brightness, brightness slider, and brightness keyboard controls might not be available with your selected mode" ([Apple, "Use presets and reference modes with your Apple display"](https://support.apple.com/en-us/108321), 2026-04-29). A fixed-luminance reference mode can therefore defeat brightness-to-room. **Unsupported** for eye strain. Keep the general-purpose preset for daily work.
- **Refresh rate.** Leave Adaptive. Row 16, **Unsupported**. Ghostty's `window-vsync` (true) needs no change.

## Where this note adds to or disagrees with the existing notes

- **Character size.** Eye-strain.md took ISO 9241-303's 16′/20–22′ from a secondary summary. DGUV 215-410, a primary statutory guide, asks for 22–31′ capital height, which is stricter. Legge and Bigelow add a measured floor in x-height (0.2°). Both say today's 15 points is small. Eye-strain.md's estimate (16′ needs about 18 points at 63.5 cm) agrees with this note's arithmetic.
- **Polarity.** DGUV adds occupational guidance for dark-on-light: fewer disturbing reflections, and less re-adaptation [DGUV p. 33]. The eye-strain grades do not change.
- **Issue #45's `minimum-contrast = 3` option.** With Latte it blackens green, yellow and magenta, so git's staged-file green turns black. With Vivendi it whitens autosuggestions. `1.1` is the safe value.
- **appearance.md's Catppuccin plumbing** (Starship palettes, `DELTA_FEATURES`, bat's pair) can be retired by moving to ANSI colours. Five of the light Starship prompt's six segments measured 2.0–2.5:1 today.
- **Fonts.** Eye-strain.md row 19 stands (**Unsupported**). This note adds the one controlled monospace study [MLB96] and a 2026 review [BT26]. Neither changes the grade. Both say size matters more than face.
- **VS Code's editor font** on the host is set to `'FiraCode Nerd Font'`, which is not installed (`ghostty +list-fonts` shows only the JetBrains Mono Nerd families). That is outside the Dotfiles. It is noted here only because it means the editor silently falls back.

## Could not verify

- **ISO 9241-303:2011's own clause** on character height. The standard is paywalled, and the ANSI preview returned HTTP 403. ANSI/HFES 100-2007 was not read either. DGUV 215-410 was read in its September 2015 edition, from a university mirror ([fernuni-hagen.de](https://www.fernuni-hagen.de/uniintern/arbeitssicherheit/docs/dguv_215-410.pdf)). Whether DGUV has revised it since was not checked.
- **The owner's viewing distance.** The sizes are tabulated for 60–80 cm.
- **The live switches inside Ghostty**: Ghostty's theme flip, the ANSI-mapped Starship prompt, and bat and delta in a real Ghostty window. Each was tested only as program output in this shell.
- **What the XDR's current preset or reference mode is.** It was not read.
- **Mini-LED blooming** around light text on Vivendi's pure-black background. No primary source or measurement was found. Tinted (`#0d0e1c`) is the hedge if it bothers the owner.
- **Contrast of the VS Code ports** (`wroyca.modus`, GitHub, the built-in high-contrast themes). Not measured.
- **Faint and unfocused-split figures.** These blend in gamma space as an approximation of Ghostty's `native` (Display P3) blending. They are not measured on screen.
- **SF Mono's licence.** The wording comes from a fetch summary of Apple's page, not the full licence PDF.
- **rustc's diagnostic colours.** The source moved and was not traced.
- **Any study** of light/dark terminal themes, off-white backgrounds, ligatures, `font-thicken`, cursor blinking, or programming fonts and eye strain. None was found; the absence is the finding.

## Sources

Ghostty and its themes:

- Ghostty v1.3.1 at [`332b2ae`](https://github.com/ghostty-org/ghostty/tree/332b2aefc6e72d363aa93ab6ecfc86eeeeb5ed28): `src/renderer/shaders/shaders.metal`, `src/Surface.zig`, `src/font/face.zig`, `src/font/face/coretext.zig`, `src/font/SharedGridSet.zig`, `src/font/embedded.zig`, `src/font/sprite/Face.zig`, `build.zig.zon`.
- Ghostty website docs at [`7962e91`](https://github.com/ghostty-org/website/tree/7962e91e190ff226be1a4983eb9368b7ddb4dff9): `docs/config/index.mdx`, `docs/install/release-notes/1-2-0.mdx`, `docs/features/theme.mdx`.
- Host: `ghostty +version`, `ghostty +show-config --default --docs`, `ghostty +list-fonts`, `ghostty +validate-config` on scratch files, and the theme files in `/Applications/Ghostty.app/Contents/Resources/ghostty/themes/`.
- Modus themes 5.3.0 at [`2d044ac`](https://github.com/protesilaos/modus-themes/tree/2d044ac89f3bca7011fa2bfda003cf80ce115f70): `doc/modus-themes.org`, `modus-themes.el`; [protesilaos.com/emacs/modus-themes](https://protesilaos.com/emacs/modus-themes).

Standards and guidance:

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/), W3C Recommendation: SC 1.4.3, 1.4.6, 1.4.11; contrast ratio and relative luminance.
- [WCAG 3.0 Working Draft](https://www.w3.org/TR/wcag-3.0/), 10 September 2026.
- [DGUV] DGUV Information 215-410, "Bildschirm- und Büroarbeitsplätze – Leitfaden für die Gestaltung", September 2015, pp. 33-35. Publisher: Deutsche Gesetzliche Unfallversicherung ([publikationen.dguv.de](https://publikationen.dguv.de/)). Read from [this copy](https://www.fernuni-hagen.de/uniintern/arbeitssicherheit/docs/dguv_215-410.pdf).
- ISO 9241-303:2011, https://www.iso.org/standard/57992.html (not read; paywalled).
- [H2], [S1], [S2], [S8], [S15], [AP1], [AP2]: as listed in [eye-strain.md](eye-strain.md#sources).

Studies (abstracts and full text via NCBI E-utilities):

- [LB11] Legge GE, Bigelow CA. "Does print size matter for reading? A review of findings from vision science and typography." J Vis 2011;11(5):8. PMID 21828237, PMC3428264.
- [MLB96] Mansfield JS, Legge GE, Bane MC. "Psychophysics of reading. XV: Font effects in normal and low vision." Invest Ophthalmol Vis Sci 1996;37:1492–501. PMID 8675391.
- [AC05] Arditi A, Cho J. "Serifs and font legibility." Vision Res 2005;45:2926–33. PMID 16099015.
- [BT26] Beier S, Thiessen M. "Applying cognitive and perceptual science to typeface choices." Ergonomics 2026;69(9):1943–55. PMID 40817624.

Tools in the chain:

- Starship v1.26.0 at [`fca92d8`](https://github.com/starship/starship/tree/fca92d8dcbd5981b0160af2f7ed7a430b6475a72): `src/config.rs`, `docs/advanced-config/README.md`; issue [#6991](https://github.com/starship/starship/issues/6991).
- bat v0.26.1 at [`979ba22`](https://github.com/sharkdp/bat/tree/979ba22628bc9d8171f2cffca2bd5c90c9fc0a9e): `README.md`, `assets/themes/ansi.tmTheme`, `src/terminal.rs`.
- delta 0.19.2 at [`1502986`](https://github.com/dandavison/delta/tree/1502986e81c8e3fa27bfb5b84bac6b281a6b1edd): `src/options/theme.rs`, `src/color.rs`, `src/utils/bat/terminal.rs`.
- fzf v0.74.4 at [`a140afe`](https://github.com/junegunn/fzf/tree/a140afeb4d733cad3c96a56bf6db7e26853b6757): `src/tui/tui.go`.
- git v2.55.0 at [`e9019fc`](https://github.com/git/git/tree/e9019fcafe0040228b8631c30f97ae1adb61bcdc): `diff.c`, `wt-status.c`, `log-tree.c`, `builtin/branch.c`.
- LLVM at [`6a61012`](https://github.com/llvm/llvm-project/tree/6a61012344ec10ce7ec109d490fc201d1fa56bef): `clang/lib/Frontend/TextDiagnostic.cpp`.
- VS Code 1.139.1 at [`04c0d99`](https://github.com/microsoft/vscode/tree/04c0d99f4fb0d8afe6ce4f0c58e31e183ac3e4b1): `colorThemeData.ts`, `extensions/theme-defaults/package.json`.
- Visual Studio Marketplace extension query API, 2026-10-03: `wroyca.modus`, `GitHub.github-vscode-theme`, `Catppuccin.catppuccin-vsc`, `mvllow.rose-pine`, `jdinhlife.gruvbox`, `enkia.tokyo-night`, `sainnhe.everforest`, `qufiwefefwoyn.kanagawa`, `MateoCERQUETELLA.xcode-12-theme`, and their manifests.
- Host: `bat --list-themes`, `delta --list-syntax-themes`, test runs of `bat`, `delta` and `starship prompt` on scratch files, `man ls`, the zsh plugin files under `/opt/homebrew/share/`, `code --list-extensions`.

Fonts:

- Homebrew cask API, 2026-10-03: `https://formulae.brew.sh/api/cask/<token>.json` for every cask named in section 3.
- Font files from each cask's URL. Atkinson Hyperlegible Mono is from google/fonts at [`95f4904`](https://github.com/google/fonts/tree/95f4904fc8bcf26d3420fe315560c96417c6dec7/ofl/atkinsonhyperlegiblemono), and Source Code Pro at [`bd62bd8`](https://github.com/google/fonts/tree/bd62bd8b4715f007af6905b0c9fd030f8410b289/ofl/sourcecodepro).
- Measured with `fonttools` (`uvx`); specimens rendered with Pillow.
- [Braille Institute, Atkinson Hyperlegible fonts](https://www.brailleinstitute.org/freefont/).
- [Apple, Fonts for Apple platforms](https://developer.apple.com/fonts/).

Apple:

- [Use presets and reference modes with your Apple display](https://support.apple.com/en-us/108321), 2026-04-29.
- Host: `system_profiler SPDisplaysDataType`, `NSScreen` via JXA, `/Library/Preferences/com.apple.windowserver.displays.plist`, `sw_vers`.
