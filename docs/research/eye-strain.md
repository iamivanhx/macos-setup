# Eye strain: how should the Mac be set up, and how strong is the evidence?

Research note for the ticket [How should a Mac be set up to avoid eye strain?](https://github.com/iamivanhx/macos-setup/issues/18), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Written 2026-09-27. Vocabulary (Bootstrap, Fresh Mac, Package, Dotfile, macOS setting) is the map's.

This is general information, not medical advice. Persistent or worsening symptoms are a matter for an optometrist or ophthalmologist.

**Method.** Clinical guidance was read from the bodies that publish it: the American Academy of Ophthalmology (AAO), the American Optometric Association (AOA), the UK Health and Safety Executive (HSE), and OSHA. Studies were read as abstracts through NCBI's E-utilities API (PubMed). IEEE 1789 was read in full. Apple's documentation was read for what each display feature does, and for the hardware. The target Mac's display state was read with `system_profiler`, `ioreg` and `defaults read`. Nothing was changed on the Mac. Where a claim rests on a third-party measurement or a secondary summary, it says so.

**Evidence grades.**

- **Supported**: recommended by clinical or occupational-health guidance, and backed by at least one controlled study or a systematic review.
- **Guidance only**: consistent clinical or occupational-health advice, but little direct trial evidence. Reasonable to follow. Not proven.
- **Mixed**: studies disagree, or are small, short, or uncontrolled.
- **Unsupported**: popular, but no good evidence that it reduces eye strain. Some of these have evidence for something else, such as sleep. Where that is the case, the row says so.

## Answer in brief

What eye strain from screens is, per the TFOS Lifestyle report (a 2023 international consensus review) [T1]: symptoms that come mainly from blinking less often and less completely, from uncorrected or partly corrected vision, and from binocular vision problems. The demands of the task and the screen's position, size, brightness and glare add to it. The report says "in general, interventions are not well established." Its best-supported advice is to fully correct refraction for the working distance, improve blinking, optimise the work environment and take regular breaks. It says blue-light blocking "do[es] not appear to be an effective management strategy" [T1]. The AAO and HSE agree that screen work does not cause permanent eye damage [A1][H1][H2].

Most of what helps is done by hand: an eye exam, the room, the desk and habits. Few measures are software settings. The display settings that matter are brightness matched to the room, text size, and dark-on-light text. **True Tone, Night Shift, dark mode, blue-light filters, refresh rate and font choice have no good evidence of reducing eye strain.** Night Shift and dark mode are sometimes claimed to help sleep, but the evidence there is weak or negative too. The Bootstrap's part is small: a few defaults, the terminal and editor text size in Dotfiles, and an optional break-reminder Package.

## Measures

"Applied as" uses the map's terms. For a macOS setting, the name is the one shown in System Settings on macOS 27. Whether the Bootstrap can script it belongs to [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8) and is not decided here.

| # | Measure | Recommendation | Evidence | Applied as |
|---|---|---|---|---|
| 1 | Eye exam and correct glasses | Get a full eye exam, and wear a correction made for screen distance if needed; even small uncorrected astigmatism raises symptoms | **Supported** [T1][O1][H2][S9] | By hand |
| 2 | Breaks | Take short, frequent breaks from screen work (NIOSH field studies used 5 min each hour) | **Supported** [S3][S4][H2] | By hand; optional reminder Package (row 17) |
| 3 | 20-20-20 rule specifically | Every 20 min, look 20 ft away for 20 s. Cheap and harmless, but the 20-second version is not proven | **Mixed** [S5][S6][O1][A2] | By hand; reminder Package |
| 4 | Blinking | Blink fully and often, especially during demanding work | **Guidance only** (mechanism well shown; trials small) [T1][S7][A1][H2] | By hand |
| 5 | Screen distance and height | Screen at about arm's length (50–100 cm), top at or slightly below eye level, gaze 15–20° down | **Guidance only** [O1][A1][OS1][H2] | By hand (workspace) |
| 6 | Glare and room lighting | Screen at right angles to windows; diffuse, even room light; no bright light behind or reflected in the screen | **Supported** [OS1][OS2][H2][O1][S10] | By hand (workspace) |
| 7 | Brightness matched to the room | Screen brightness close to the room's, not much brighter or darker | **Guidance only** [A1][A3][H2][OS2] | macOS setting: Displays > Brightness (by hand, varies with room) |
| 8 | Automatic brightness | Keep it on; it applies row 7 automatically | **Guidance only** (it implements row 7; no study of the feature itself) [AP5][AP6] | macOS setting: Displays > "Automatically adjust brightness" |
| 9 | Text size | Make text large enough to read easily from your normal seat; larger is the safe direction | **Guidance only** [H2][OS1][S8] | macOS setting: Accessibility > Display > "Text size", and Displays > resolution ("Larger Text"); Dotfile: terminal and editor font size |
| 10 | Text polarity (light vs dark mode) | Prefer dark text on a light background for reading and detail work; use dark mode only if you prefer it | Dark mode for eye strain: **Unsupported** [S1][S2][S11]; light mode is better for legibility, not shown to reduce strain [S1][S2] | macOS setting: Appearance > Light / Dark / Auto; Dotfile: terminal and editor theme |
| 11 | Contrast | Keep strong luminance contrast between text and background; avoid low-contrast and red-on-blue themes | **Guidance only** [A1][H2][S2] | macOS setting: Accessibility > Display > "Increase contrast", "Display contrast"; Dotfile: theme choice, Ghostty `minimum-contrast` |
| 12 | Reduce transparency | Optional; reduces visual clutter. No eye-strain evidence | **Unsupported** (no studies found) | macOS setting: Accessibility > Display > "Reduce transparency" |
| 13 | Blue-light filters (glasses, apps) | Do not buy or rely on them for eye strain | **Unsupported** (Cochrane: probably no short-term benefit) [C1][T1][A2][S12] | None |
| 14 | Night Shift | Optional, a matter of taste. It does not reduce eye strain, and on its own did not protect sleep in trials; dimming and stopping screen use before bed matter more | Eye strain: **Unsupported**. Sleep: **Mixed to negative** [S13][S14][C1] | macOS setting: Displays > Night Shift |
| 15 | True Tone | A matter of taste; Apple claims only that images look "more natural" | **Unsupported** (no studies found) [AP4] | macOS setting: Displays > "True Tone" |
| 16 | Refresh rate | Leave at the default (ProMotion / Adaptive); no evidence that 60 vs 120 Hz changes eye strain on modern LCDs | **Unsupported** (no studies found) [AP7] | macOS setting: Displays > "Refresh rate" |
| 17 | Break-reminder app | Optional aid to rows 2–3; the evidence is for breaks, not for any app | **Mixed** (helps breaks happen [S5]) | Package: `breaktimer` or `time-out` cask (see below) |
| 18 | Flicker (PWM) | Prefer displays without low-frequency flicker; both of the owner's displays look fine on the evidence available | **Mixed** (strong for flicker under ~100 Hz; little for displays in the kHz range) [I1] | By hand (a buying choice) |
| 19 | Terminal and editor font choice | Any clear font at an adequate size; no font has been shown to reduce eye strain | **Unsupported** (no studies found) [S15] | Dotfile |
| 20 | Line height, font smoothing | Preference only | **Unsupported** (no studies found) | Dotfile (line height); font smoothing has had no System Settings control since macOS 11 |
| 21 | Artificial tears | For dry, gritty eyes; a pharmacist or optometrist can advise | **Mixed** (recommended, trials inconclusive) [A1][T1] | By hand |
| 22 | Humidifier / room humidity | Worth trying in dry rooms (OSHA: 30–60% relative humidity) | **Mixed, leaning supported** (one small RCT) [S16][T1][OS2] | By hand |
| 23 | Anti-glare screen filter | Only if glare cannot be fixed by moving the screen or light; the Studio Display XDR's glass already has an anti-reflective coating | **Mixed** [A1][S10][S17][AP2] | By hand |

## What matters most

In order of evidence strength, not popularity:

1. **Get an eye exam and wear the right correction for screen distance.** Every body consulted puts this first [T1][O1][H2]. Uncorrected astigmatism of only 1 D raised symptoms in a controlled trial [S9].
2. **Take regular short breaks.** Two NIOSH field studies (42 and 51 data-entry workers) found less eye strain with extra 5-minute breaks each hour, with no loss of output [S3][S4]. The exact 20-20-20 rule is less certain (item 5 below).
3. **Control glare and room lighting.** Keep windows and bright lamps out of the screen's reflection and out of your line of sight, and light the room evenly [OS1][OS2][H2]. In one controlled study, glare raised visual-fatigue scores and a glare-free display lowered them [S10].
4. **Set distance and height.** Arm's length (50–100 cm), with the top of the screen at or just below eye level [O1][A1][OS1]. A lower gaze also exposes less of the eye's surface, which fits the dry-eye mechanism [S18].
5. **Blink and look away.** Blinking fully, and 20-20-20 as a habit, are cheap and harmless. The evidence is weaker: one uncontrolled study found symptoms improved with 20-20-20 reminders [S5], and one crossover study found no effect of 20-second breaks over 40 minutes [S6].
6. **Match brightness to the room, keep text large enough, and keep contrast high.** Leave automatic brightness on [A1][A3][H2]. Light mode (dark-on-light text) reads better [S1][S2]. All three are guidance only.

**Popular measures without support for eye strain:** blue-light glasses and filters [C1][A2][T1], Night Shift [S13][S14], dark mode [S1][S11], True Tone, higher refresh rates, and particular coding fonts or themes. The case for Night Shift and blue-light filtering is sleep, not eye strain, and even there the evidence is weak. In a 167-person RCT, Night Shift made no difference to sleep [S14]. In a 12-person lab study it did not change melatonin suppression unless brightness was also lowered [S13]. Cochrane rated the effect of blue-light lenses on sleep "indeterminate" [C1].

## Measure by measure

### Vision correction

- TFOS: people with digital eye strain "should be provided with a full refractive correction for the appropriate working distances" [T1]. Sheppard and Wolffsohn's review lists correcting refractive error and presbyopia first among management approaches [S19].
- The AOA names uncorrected vision problems as a major contributor, and recommends "a thorough eye exam every year" [O1]. UK law requires employers to provide eye tests to screen users, "to ensure users can comfortably see the screen and work effectively without visual fatigue" [H2].
- Rosenfield et al. 2012: in 12 subjects reading from a screen, adding 1 D and 2 D of astigmatism raised median symptom scores from 2 to 6.5 and 40. Reading speed was unchanged [S9]. The study is small, but the effect is large.

**Grade: Supported.** Applied by hand.

### Breaks and 20-20-20

- Galinsky et al. 2000 (NIOSH, 42 workers, within-subjects): with a 5-minute break in each otherwise unbroken hour, "eyestrain [was] significantly lower" and output was unchanged [S3]. The 2007 follow-up (51 workers) found the same: "supplementary breaks reliably minimize discomfort and eyestrain without impairing productivity" [S4].
- HSE: "Short, frequent breaks are better than longer, infrequent ones"; "Look into the distance from time to time, and blink often" [H2].
- 20-20-20 is recommended by the AOA [O1] and the AAO [A2]. The trials are few and disagree:
  - Talens-Estarelles et al. 2023: 29 symptomatic users with reminder software for 2 weeks. Eye-strain and dry-eye symptoms fell, but the gain was gone one week after stopping. There was no control group, and signs on the eye's surface did not change [S5].
  - Johnson and Rosenfield 2023: 30 subjects doing a 40-minute tablet task, with 20-second breaks every 5, 10, 20 or 40 minutes. The schedule had "no significant effect" on symptoms; the authors note "relatively little peer-reviewed evidence to support this rule" [S6].

**Grades:** breaks are **Supported**; the 20-20-20 rule specifically is **Mixed**. The honest reading: breaks help, and 20 seconds may be too short to show an effect in a lab.

### Blinking

- AAO: normal blink rate is about 15 per minute and "can be cut in half when staring at screens or doing other near work activities" [A3].
- Chu, Rosenfield and Portello 2014 matched screen reading against paper (25 subjects). Blink rate was the same (14.9 vs 13.6 per minute), but incomplete blinks were more common on screen (7.0% vs 4.3%). The authors suggest cognitive demand, not the screen itself, lowers blink rate [S7].
- TFOS: "Improving blinking … may help" [T1]. The trial evidence for blinking exercises is thin. The one RCT found (Sadhwani 2024, 38 patients) also reports implausible effects on refractive error, so it is not relied on here.

**Grade: Guidance only.** Applied by hand.

### Workspace: distance, height, glare, lighting

- **Distance.** AOA: 20–28 inches (51–71 cm) [O1]. AAO: about 25 inches, "right about at arm's length" [A1]. OSHA: 20–40 inches (50–100 cm) [OS1].
- **Height.** AOA: centre of the screen 15–20° (about 4–5 inches) below eye level [O1]. OSHA: "top of the monitor should be at or slightly below eye level" [OS1]. HSE: eyes at the height of the top of the screen [H2].
- **Glare.** OSHA: place the monitor at right angles to windows, use diffuse, shielded lighting, and tilt the screen slightly down to avoid overhead reflections [OS1][OS2]. HSE: the screen should not face windows or bright lights; use blinds [H2]. Lin et al. 2019: a glare environment raised visual-fatigue scores; a glare-free display lowered them; uniform extra lighting was better than dim or uneven light [S10].
- **Room light level.** OSHA: 20–50 foot-candles (about 215–540 lux) for office work, and more (up to 73 fc) for LCDs [OS2]. OSHA also warns that "high contrast between light and dark areas of the computer screen, horizontal work surface, and surrounding areas can cause eye fatigue and headaches" [OS2]. That is the case against working on a bright screen in a dark room.
- **Anti-glare filters.** AAO suggests "a matte screen filter to cut glare" [A1]. One small non-randomised study (7 subjects) found an anti-reflection film reduced symptoms [S17]. The Studio Display XDR's standard glass already has an anti-reflective coating with 1.65% reflectance; a nano-texture (matte) version is sold for "less-controlled lighting" [AP2].

**Grades:** distance and height, **Guidance only**. Glare and lighting, **Supported**. All applied by hand; the Bootstrap cannot do them.

### Brightness and automatic brightness

- AAO: "Adjust your screen brightness to match the level of light around you" [A1], and "adjusting the brightness and contrast of your screen and dimming the lighting near your screen can also help reduce eye strain" [A3]. HSE: "Adjust the brightness and contrast controls on the screen to suit lighting conditions in the room" [H2].
- Apple: "Automatically adjust brightness … based on current ambient lighting conditions" [AP5]. On the Studio Display XDR, "dual ambient light sensors dynamically adjust display brightness, black point, and white point (with True Tone enabled)". Apple adds: "avoid placing direct light sources pointed at the display, or directly behind" [AP2].
- No study was found that tests automatic brightness for eye strain. It is simply a way of following the guidance above.

**Grade: Guidance only.** The System Settings names are Displays > "Brightness" and Displays > "Automatically adjust brightness" (on some displays, "Ambient light compensation") [AP5]. At the time of reading, "Automatically Adjust Brightness: Yes" was on for the Studio Display XDR (`system_profiler`).

### Appearance: light vs dark mode, contrast, transparency

- **Dark mode does not reduce eye strain on the evidence.**
  - Buchner and Baumgartner 2007: dark-on-light text gave better proofreading in every lighting condition. Self-reported "eyestrain, headache" did **not** differ between polarities [S2].
  - Piepenbrock et al. 2014: the advantage of dark-on-light text grows as text gets smaller; "especially with small font sizes, negative polarity displays should be avoided" [S1].
  - Sengsoon and Intaruk 2025 (30 tablet users): "no statistically significant difference in visual fatigue" between light and dark mode. The authors still conclude dark mode "may help", on secondary measures [S11]. Small and short.
  - AAO pages mention dark or night mode in the evening, but for **brightness and sleep** reasons [A3]. A 2019 AAO page runs night mode and dark mode together and cites no study [A4].
  - **Myopia is a separate question.** Aleman et al. 2018 found the choroid thinned by about 16 µm after an hour of reading black-on-white and thickened by about 10 µm with white-on-black. They propose dark mode might slow myopia [S20]. That is a short-term marker in a small study, about myopia, not eye strain. Treat it as a hypothesis.
- **Contrast.** AAO: "try increasing the contrast on your screen" [A1]. HSE: "Select colours that are easy on the eye (avoid red text on a blue background, or vice versa)" [H2]. Colour contrast "could not compensate for a lack of luminance contrast" [S2]. That argues against low-contrast "easy on the eyes" themes.
- **Reduce transparency.** No studies were found. Apple describes it only as replacing transparent backgrounds with solid ones [AP3].
- **Automatic switching.** Apple: "Auto switches the appearance from light to dark based on the Night Shift schedule you set." It waits until the Mac has been idle for at least a minute [AP8]. No eye-strain evidence either way.

**Grades:** dark mode for eye strain, **Unsupported**. Light mode for legibility, supported by lab studies, though not shown to reduce strain. Contrast, **Guidance only**. Transparency, **Unsupported**.

System Settings names [AP3][AP8]: Appearance > "Light" / "Dark" / "Auto"; Accessibility > Display > "Increase contrast", "Reduce transparency", "Display contrast". Apple notes that "increase contrast … might turn off True Tone" [AP4]. At the time of reading, the Mac was in Light mode (no `AppleInterfaceStyle` key) and neither Increase contrast nor Reduce transparency was set.

### Text: size, font, line height, smoothing

- **Size.** HSE: "choose text that is large enough to read easily on screen when sitting in a normal comfortable working position" [H2]. OSHA: "text size may need to be increased for smaller monitors" [OS1]. Small text also makes light-on-dark worse [S1].
- **ISO 9241-303** is widely summarised as requiring a character height of at least 16 minutes of arc, with 20–22 preferred. The standard is paywalled and was not read, so these figures come from secondary summaries [S8]. If "character height" means capital-letter height, then at 25 inches (63.5 cm) on the Studio Display XDR at its default scaling (one macOS point ≈ 0.233 mm, because 2 pixels at 218 ppi [AP2]):
  - a 13-point font gives roughly 11 arcmin;
  - 16 arcmin needs roughly 18 point;
  - 20 arcmin needs roughly 23 point.

  This is my arithmetic, assuming capital height ≈ 0.7 of the font size. It is a rough check, not a target. The practical rule is HSE's: if you lean in to read, the text is too small.
- **Where to set it.** Accessibility > Display > "Text size" works for "compatible apps and system features" [AP3]. Displays > resolution scales everything; the default and "Larger Text" choices trade space for size [AP5]. The terminal and editor have their own sizes: Ghostty `font-size`, and `adjust-cell-height` for line height [G1]. Those belong in Dotfiles.
- **Font choice.** Bigelow's 2019 review of legibility research makes no claim that any typeface reduces fatigue [S15]. No study was found showing that one coding font reduces eye strain. **Unsupported.** This is preference; which fonts to install belongs to [Which software is recommended for development on a Mac?](https://github.com/iamivanhx/macos-setup/issues/16).
- **Line height.** No studies were found on line height and eye strain. **Unsupported**; preference.
- **Font smoothing.** The "Use font smoothing when available" checkbox was removed from System Preferences in macOS 11 Big Sur. The `AppleFontSmoothing` defaults key still works but is undocumented by Apple (reported by MacRumors [M1]). No eye-strain evidence. On 218–254 ppi Retina panels, leave it at the default. At the time of reading, the key was absent (default).

### Colour themes

- Luminance contrast matters most. Colour contrast alone does not make up for low luminance contrast [S2], and HSE warns against red/blue pairs [H2].
- Polarity: see the appearance section above. Dark themes have no eye-strain advantage; light themes read better, especially at small sizes [S1][S2].
- Colour temperature of a theme ("warm" backgrounds): no studies were found linking it to eye strain. **Unsupported.**
- Ghostty can follow the system appearance with `theme = light:<name>,dark:<name>`, and can enforce a floor on text contrast with `minimum-contrast` (a ratio from 1 to 21) [G1]. Both are Dotfile lines, so a theme choice costs one edit in one place. Which theme to use is the owner's taste.

### Blue light, Night Shift and True Tone

- **Blue-light filters for eye strain: Unsupported.**
  - Cochrane (Singh et al. 2023; 17 RCTs, 619 people): "blue-light filtering lenses may not reduce short-term eyestrain associated with computer work". Low-certainty evidence, follow-up under a week for that outcome [C1].
  - Effect on sleep: "indeterminate" (6 RCTs, 148 people, very low certainty) [C1].
  - TFOS: blue-light blocking does "not appear to be an effective management strategy" [T1].
  - AAO: "does not recommend blue light-blocking glasses", and "there is no scientific evidence that blue light from digital devices causes damage to your eye" [A2][A5].
  - A double-masked trial (24 subjects) found no difference in symptoms between blue-blocking and clear lenses [S12].
- **Night Shift.**
  - Apple's claim: "Warmer screen colors are easier on your eyes when you use your Mac at night" [AP5], and bright blue light in the evening "can affect your circadian rhythms and make it harder to fall asleep" [AP9]. Apple cites no evidence for the eye-strain claim, and none was found.
  - On sleep, Nagare, Plitnick and Figueiro 2019 (12 adults, iPad): melatonin suppression "did not significantly differ between the two Night Shift interventions … changing the spectral composition … without changing their brightness settings may be insufficient" [S13].
  - Duraccio et al. 2021 (167 young adults, randomised, 7 nights): "no differences in sleep outcomes attributable to Night Shift" [S14].
  - AAO's own sleep advice is to limit screen time 2–3 hours before bed [A5].
  - **Grades:** eye strain, **Unsupported**; sleep, **Mixed to negative**. The System Settings name is Displays > "Night Shift…", with a schedule and a colour-temperature slider [AP9].
- **True Tone** "adjust[s] the color and intensity of your display … to match the ambient light, so that images appear more natural" [AP4]. Apple makes no comfort claim, and no study was found. **Unsupported**; taste. True Tone works on Apple's own displays, including the Studio Display XDR, and on other external displays up to 32 inches only when a Mac laptop's lid is open [AP4]. System Settings name: Displays > "True Tone".

### Refresh rate and flicker

- **Refresh rate.** Apple: ProMotion is "an adaptive refresh rate up to 120Hz" on 14- and 16-inch MacBook Pro, and "Adaptive (47–120 Hertz)" on the Studio Display XDR. Fixed rates are also offered [AP7]. Apple makes no comfort claim, and no study was found linking 60 vs 120 Hz on a modern LCD to eye strain. **Unsupported.** Keep the default.
  - The flicker problems of old CRT refresh rates do not carry over: an LCD holds its image between frames. The flicker that matters is the backlight's (next point).
  - IEEE 1789 does record one case report of migraines at 60 Hz on a CRT, gone at 75 Hz [I1]. That concerns CRTs, not today's panels.
- **Backlight flicker (PWM).**
  - IEEE 1789-2015 (written for LED lighting, not displays) links flicker to "headaches, eyestrain". It cites a double-masked study in which 100 Hz fluorescent-lamp modulation doubled headaches in office workers, mostly in a sensitive minority.
  - Its recommended practice: above 1250 Hz, "no restriction on Modulation (%)" for low risk; above 3000 Hz, none for "no observable effect level" [I1]. It also notes that flicker "can be perceived during saccades at frequencies in excess of 1 kHz" [I1].
  - **Grade: Mixed.** The evidence is strong for flicker around 100 Hz and in lighting; there is little for displays in the kHz range. On both of the owner's displays this is a buying question, not a setting (next section).

### Break-reminder apps (Package)

The evidence is for breaks, not for software. Talens-Estarelles used reminder software as the intervention [S5], so an app can help breaks happen. Candidates as Homebrew casks, read from Homebrew's API on 2026-09-27 [B1]:

- `breaktimer` 2.0.3: active.
- `time-out` 3.1 (Dejal): active; requires macOS 26 or later.
- `stretchly` 1.22.1: **disabled** since 2026-09-01, reason `fails_gatekeeper_check`. Do not use it.

Whether one goes on the Fresh Mac is for [Which packages and apps belong on a fresh Mac?](https://github.com/iamivanhx/macos-setup/issues/10).

## The target Mac's displays

`system_profiler SPDisplaysDataType` on 2026-09-27 listed **one online display, a Studio Display XDR (Retina XDR LCD, 5120 × 2880), as Main Display**. The built-in panel was not listed, which suggests the lid was closed. So **the owner does use an external monitor**, though not necessarily all the time.

The WindowServer display configuration (`/Library/Preferences/com.apple.windowserver.displays.plist`) holds these configurations:

- Studio Display XDR at 2560 × 1440 points, scale 2, **120.04 Hz, VRR on**.
- The built-in panel at 1512 × 982 points, scale 2, 120 Hz VRR.
- A 1920 × 1080 display at 60 Hz, seen at some point.

### Built-in: MacBook Pro 14-inch (M3 Pro, Nov 2023), `Mac15,6`

| Fact | Value | Source |
|---|---|---|
| Panel | 14.2-inch Liquid Retina XDR (mini-LED), 3024 × 1964 at 254 ppi | Apple [AP1] |
| Brightness | SDR 600 nits; XDR 1000 nits sustained, 1600 nits peak (HDR only) | Apple [AP1] |
| Refresh | ProMotion adaptive up to 120 Hz; fixed 47.95, 48, 50, 59.94, 60 Hz | Apple [AP1][AP7] |
| Ambient light sensor, True Tone | Yes, both | Apple [AP1] |
| Brightness control method | **Not documented by Apple.** Notebookcheck reports PWM at about **15 kHz** at all brightness levels on the 14-inch M3 panel, and says mini-LED flicker "is not comparable with typical PWM flickering" | **Third-party**, seen only as search-engine excerpts: Notebookcheck's pages returned HTTP 403 to every direct fetch [N1] |

If the ~15 kHz figure is right, it is well above IEEE 1789's 3000 Hz no-effect threshold [I1]. Some users on Apple's forums report discomfort with this panel anyway; that is anecdote, not evidence.

### External: Studio Display XDR (2026)

| Fact | Value | Source |
|---|---|---|
| Panel | 27-inch 5K Retina XDR, 5120 × 2880 at 218 ppi, mini-LED with 2304 local-dimming zones | Apple [AP2] |
| Brightness | SDR up to 1000 nits (600 nits under typical conditions, rising in bright rooms); HDR peak 2000 nits | Apple [AP2] |
| Refresh | 120 Hz with Adaptive Sync, 47–120 Hz. Apple limits M1, M1 Pro/Max/Ultra, M2 and **M3** Macs to 60 Hz; **M3 Pro is not in that list**, and the host records 120 Hz VRR | Apple [AP2][AP7]; `ioreg` reports `MinimumRefreshRate=47`, `MaximumRefreshRate=120` |
| Ambient light sensors, True Tone | Dual (front and rear); both supported | Apple [AP2][AP4] |
| Glass | Anti-reflective, 1.65% reflectance ("reduces glare by 3x"); nano-texture optional | Apple [AP2]. Which glass this unit has was not determined |
| Backlight drive and flicker | Apple: "Local dimming is controlled at 8x the display's maximum refresh rate" (≈960 Hz at 120 Hz), and its frame scheduling prevents "flicker" from variable refresh. Apple does **not** say whether brightness is set by PWM, or at what frequency | Apple white paper, April 2026 [AP2]. **No third-party flicker measurement could be read** (RTINGS loads its results by script; Notebookcheck blocked) |
| Brightness control | Adjustable from macOS: `ioreg` reports `SupportsBacklightControl=Yes`; Apple lists "Brightness Control: User selectable" and automatic brightness and True Tone "can be disabled in Displays" | Apple [AP2]; host `ioreg` |

What the unknown dimming frequency means: if brightness is modulated at the ~960 Hz local-dimming rate, it would sit in IEEE 1789's 90–1250 Hz band, where risk depends on modulation depth [I1]. That is an inference from one Apple sentence, not a measurement; the sentence may describe only the zone-update rate. **Unverified.**

## What the Bootstrap can carry

A settings pass only. Whether each item can be scripted belongs to [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8).

- **macOS settings with some support**, meaning they implement guidance: Displays > "Automatically adjust brightness" on; Accessibility > Display > "Text size"; Appearance (Light or Auto, the owner's taste); optionally Accessibility > Display > "Increase contrast".
- **macOS settings that are pure taste**, with no eye-strain case: Night Shift, True Tone, "Reduce transparency", refresh rate. Leave them at the defaults unless the owner wants otherwise.
- **Dotfiles**: terminal and editor font size, line height and theme (for example Ghostty `font-size`, `adjust-cell-height`, `theme = light:…,dark:…`, `minimum-contrast`) [G1]. Size and contrast are the parts with an eye-strain case.
- **Package** (optional): a break reminder (`breaktimer` or `time-out`), not `stretchly` [B1].
- **By hand**, and outside the Bootstrap: eye exam, desk and screen position, glare and room lighting, humidity, breaks and blinking. The Bootstrap could at most print these as a checklist; that is the map's "Steps that cannot be scripted" fog.

## What could not be verified

- **PWM or flicker on the Studio Display XDR.** Apple does not state it, and no third-party measurement could be read.
- **PWM on the built-in panel.** The ~15 kHz figure was seen only as search excerpts of Notebookcheck's 14-inch M3 review; the pages returned 403. It was not confirmed for the M3 Pro unit specifically.
- **Night Shift and True Tone state on this Mac.** It lives in `CoreBrightness` preferences under the root account, which cannot be read without elevated privileges. It was not read.
- **Which glass (standard or nano-texture) the owner's Studio Display XDR has.**
- **ISO 9241-303 character-height figures.** The standard is paywalled; the figures and the "capital height" reading come from secondary summaries, and the point-size estimates are my arithmetic.
- **Blinking-exercise efficacy.** The one RCT found is small, and its claims are implausible.
- **Any study of automatic brightness, True Tone, refresh rate, font choice, line height or font smoothing** as they relate to eye strain. None was found; that absence is the finding.

## Sources

Clinical and occupational guidance:

- [A1] AAO, "Computers, Digital Devices, and Eye Strain", reviewed 2024-06-27. https://www.aao.org/eye-health/tips-prevention/computer-usage
- [A2] AAO, "Are Blue Light-Blocking Glasses Worth It?", 2021-03-05. https://www.aao.org/eye-health/tips-prevention/are-computer-glasses-worth-it
- [A3] AAO, "Digital Devices and Your Eyes", 2025-12-05. https://www.aao.org/eye-health/tips-prevention/digital-devices-your-eyes
- [A4] AAO, "Should You Use Night Mode to Reduce Blue Light?", 2019-05-07. https://www.aao.org/eye-health/tips-prevention/should-you-use-night-mode-to-reduce-blue-light
- [A5] AAO, "Should You Be Worried About Blue Light?", 2021-03-10. https://www.aao.org/eye-health/tips-prevention/should-you-be-worried-about-blue-light
- [O1] AOA, "Computer vision syndrome". https://www.aoa.org/healthy-eyes/eye-and-vision-conditions/computer-vision-syndrome
- [H1] HSE, "Display screen equipment: eye tests". https://www.hse.gov.uk/msd/dse/eye-tests.htm
- [H2] HSE, "Working with display screen equipment (DSE): A brief guide", INDG36(rev4), 2013. https://www.hse.gov.uk/pubns/indg36.pdf
- [OS1] OSHA Computer Workstations eTool, "Monitors". https://www.osha.gov/etools/computer-workstations/components/monitors
- [OS2] OSHA Computer Workstations eTool, "Workstation Environment". https://www.osha.gov/etools/computer-workstations/workstation-environment
- [I1] IEEE Std 1789-2015, "Recommended Practices for Modulating Current in High-Brightness LEDs for Mitigating Health Risks to Viewers". https://ieeexplore.ieee.org/document/7118618 (full text read from a copy hosted at https://25472181.fs1.hubspotusercontent-eu1.net/hubfs/25472181/PDF%20files/IEEE%201789%20-%20Recommended%20Practices%20for%20Modulating%20Current%20in%20High-Brightness%20LEDs%20for%20Mitigating%20Health%20Risks%20to%20Viewers.pdf; Recommended Practices 1 and 2, section 8)

Systematic reviews and consensus:

- [C1] Singh S et al. "Blue-light filtering spectacle lenses for visual performance, sleep, and macular health in adults." Cochrane Database Syst Rev 2023; CD013244. PMID 37593770. https://www.cochrane.org/evidence/CD013244_blue-light-filtering-spectacle-lenses-visual-performance-macular-back-part-eye-protection-and
- [T1] Wolffsohn JS et al. "TFOS Lifestyle: Impact of the digital environment on the ocular surface." Ocul Surf 2023;28:213–252. PMID 37062428.
- [S19] Sheppard AL, Wolffsohn JS. "Digital eye strain: prevalence, measurement and amelioration." BMJ Open Ophthalmol 2018;3:e000146. PMID 29963645.

Studies (PubMed IDs; abstracts read via https://eutils.ncbi.nlm.nih.gov/):

- [S1] Piepenbrock C, Mayr S, Buchner A. Hum Factors 2014;56:942–51. PMID 25141597.
- [S2] Buchner A, Baumgartner N. Ergonomics 2007;50:1036–63. PMID 17510822.
- [S3] Galinsky TL et al. Ergonomics 2000;43:622–38. PMID 10877480.
- [S4] Galinsky T et al. Am J Ind Med 2007;50:519–27. PMID 17514726.
- [S5] Talens-Estarelles C et al. Cont Lens Anterior Eye 2023;46:101744. PMID 35963776.
- [S6] Johnson S, Rosenfield M. Optom Vis Sci 2023;100:52–56. PMID 36473088.
- [S7] Chu CA, Rosenfield M, Portello JK. Optom Vis Sci 2014;91:297–302. PMID 24413278.
- [S8] ISO 9241-303:2011, requirements for electronic visual displays (not read; paywalled). https://www.iso.org/standard/57992.html. Figures are as summarised secondarily, e.g. https://github.com/danielrosehill/Claude-Monitor-Research/blob/main/docs/readability-geometry.md
- [S9] Rosenfield M et al. Ophthalmic Physiol Opt 2012;32:142–8. PMID 22150631.
- [S10] Lin CW et al. Clin Exp Optom 2019;102:513–20. PMID 30805993.
- [S11] Sengsoon P, Intaruk R. Int J Environ Res Public Health 2025;22:609. PMID 40283833.
- [S12] Rosenfield M, Li RT, Kirsch NT. Work 2020;65:343–48. PMID 32007978.
- [S13] Nagare R, Plitnick B, Figueiro MG. Light Res Technol 2019;51:373–83. PMID 31191118.
- [S14] Duraccio KM et al. "Does iPhone night shift mitigate negative effects of smartphone use on sleep outcomes in emerging adults?" Sleep Health 2021. https://www.sleephealthjournal.org/article/S2352-7218(21)00060-7/abstract
- [S15] Bigelow C. Vision Res 2019;165:162–72. PMID 31078662.
- [S16] Wang MTM et al. Optom Vis Sci 2017;94:1052–57. PMID 29035923.
- [S17] Miyake-Kashima M et al. Cornea 2005;24:567–70. PMID 15968162.
- [S18] Rosenfield M. "Computer vision syndrome: a review of ocular causes and potential treatments." Ophthalmic Physiol Opt 2011;31:502–15. PMID 21480937.
- [S20] Aleman AC, Wang M, Schaeffel F. Sci Rep 2018;8:10840. PMID 30022043.

Apple documentation:

- [AP1] MacBook Pro (14-inch, M3 Pro or M3 Max, Nov 2023) – Tech Specs. https://support.apple.com/en-us/117736
- [AP2] Studio Display XDR – Tech Specs, https://www.apple.com/studio-display-xdr/specs/ and https://support.apple.com/en-us/126323; Studio Display XDR Technology Overview white paper, April 2026, https://www.apple.com/studio-display-xdr/pdf/Studio_Display_XDR_Technology_Overview_White_Paper.pdf
- [AP3] Mac User Guide (macOS 27), "Change Display settings for accessibility on Mac". https://support.apple.com/en-us/guide/mac-help/unac089/mac
- [AP4] "Use True Tone on Mac". https://support.apple.com/en-us/102147
- [AP5] Mac User Guide (macOS 27), "Displays settings on Mac" (https://support.apple.com/en-us/guide/mac-help/mh40768/mac) and "Change your Mac display's brightness" (https://support.apple.com/en-us/guide/mac-help/mchlp2704/mac)
- [AP6] Same as AP5 (automatic brightness)
- [AP7] "Change the refresh rate on your MacBook Pro or Apple display". https://support.apple.com/en-us/102297
- [AP8] Mac User Guide (macOS 27), "Use a light or dark appearance on your Mac". https://support.apple.com/en-us/guide/mac-help/mchl52e1c2d2/mac
- [AP9] "Use Night Shift on your Mac", 2026-02-10. https://support.apple.com/en-us/102191

Other:

- [G1] Ghostty configuration reference. https://ghostty.org/docs/config/reference
- [B1] Homebrew cask API: https://formulae.brew.sh/api/cask/breaktimer.json, https://formulae.brew.sh/api/cask/time-out.json, https://formulae.brew.sh/api/cask/stretchly.json (read 2026-09-27)
- [N1] Notebookcheck, "Apple MacBook Pro 14 2023 M3 Review", https://www.notebookcheck.net/Apple-MacBook-Pro-14-2023-M3-Review-The-base-model-now-comes-without-a-Pro-SoC.765661.0.html, and "Apple MacBook Pro 14 2023 M3 Pro review", https://www.notebookcheck.net/Apple-MacBook-Pro-14-2023-M3-Pro-review-Improved-runtimes-and-better-performance.779538.0.html. **Third-party; seen only as search excerpts; HTTP 403 on fetch.**
- [M1] MacRumors, "How to Adjust or Disable Font Smoothing in macOS Big Sur". https://www.macrumors.com/how-to/disable-font-smoothing-in-macos-big-sur/ (secondary; Apple does not document the key)
