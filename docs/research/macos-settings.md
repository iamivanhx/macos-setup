# Which macOS settings can be scripted on macOS 27?

Research findings for the ticket [Which macOS settings can be scripted on macOS 27?](https://github.com/iamivanhx/macos-setup/issues/8), on the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Researched 2026-09-27.

## How to read this note

- **Host** means the target Mac, read-only: `sw_vers` reports macOS 27.0, build `26A428`, on a `Mac15,6` with SIP enabled. No setting was written. Every host observation is a `defaults read`, `plutil -p`, `man`, `pmset -g`, `scutil --get`, or a byte search of a system binary.
- **Carried over** means the evidence comes from macOS 26 (Tahoe) or earlier and has not been confirmed on 27. macos-defaults.com, the best-maintained public key reference, has tested nothing newer than Sequoia (15) (see [Sources](#sources)).
- **Binary string search.** A preference key is usually a string literal in the program that reads it. A key found in a macOS 27 binary is still referenced on 27, but that does not prove it is honoured: `com.apple.mouse.scaling` is still present on 27 and was reported a no-op on 26.1 ([macos-defaults#438](https://github.com/yannbertrand/macos-defaults/issues/438)). A key **not** found is weak evidence when it is 15 bytes or shorter, because Swift stores strings that short inline in code rather than as C strings ([`SmallString.swift`, capacity 15](https://github.com/swiftlang/swift/blob/dd2b2263096c1da3103638de88b34460505cddb1/stdlib/public/core/SmallString.swift#L81-L91)).

## The answer in brief

- **`defaults write` is still the mechanism for almost every user-level setting** (Finder, Dock, keyboard, text input, screenshots). Every key the Ansible role writes still appears in a macOS 27 binary, except `expose-animation-duration` and the Xcode key; Xcode is not installed on the host. The owner's own clicks in System Settings on 27 still wrote the classic keys `com.apple.dock autohide`, `NSAutomaticCapitalizationEnabled`, and `NSAutomaticPeriodSubstitutionEnabled` (host).
- **Settings outside the user's preferences use purpose-built tools, all needing admin or root:** `pmset` for power, `scutil --set` for names, `systemsetup` for time zone and remote login, `sysadminctl` for the screen lock, and `socketfilterfw` for the firewall.
- **The hard walls are permissions, not keys.** On current macOS a script cannot grant itself Full Disk Access, Accessibility, Automation, or Screen Recording. It cannot install a configuration profile from the command line, cannot change the default browser without a consent click, and on 27 cannot read or write the local TCC database. Settings stored in sandboxed Apple apps' containers (Safari) fail silently unless the terminal has Full Disk Access.
- **From the Ansible list:** 23 settings are expected to work, `expose-animation-duration` is expected to fail, and 3 are unverified: `AppleKeyboardUIMode = 3`, the Xcode key, and the omitted battery percentage.

## Mechanisms

| Mechanism | What it is for | Privilege | Source |
| --- | --- | --- | --- |
| `defaults write` | User preferences in a domain (`com.apple.finder`), in `NSGlobalDomain` (`-g`), or per-host (`-currentHost`, the files under `~/Library/Preferences/ByHost/`). Typed values: `-string -int -float -bool -date -data -array[-add] -dict[-add]`. Also `read-type`, `export`/`import` of a whole domain as a plist. | none for the user's own domains; `sudo` for `/Library/Preferences/...` | `man defaults` on the host (page dated 2025-09-15) |
| `PlistBuddy` | Editing nested entries in a plist **file** (arrays of dicts, such as the Dock's `persistent-apps`). It edits the file directly, not through the preferences daemon, so a running app can overwrite the change. | file permissions | `man PlistBuddy` on the host; see the note on running apps below |
| `pmset` | Power management: sleep timers, `displaysleep`, `powernap`, `womp`, `lidwake`, `autorestart`, `hibernatemode`, `standby`, per power source (`-a`, `-b`, `-c`). Settings are system-wide, stored in `/Library/Preferences/SystemConfiguration/com.apple.PowerManagement.plist`. | "pmset must be run as root in order to modify any settings" | `man pmset` on the host |
| `scutil --set` | `ComputerName`, `LocalHostName`, `HostName`. | "The --set option requires super-user access" | `man scutil` on the host |
| `systemsetup` | Date, time, time zone, network time, sleep, wake on network, restart after power failure or freeze, remote login (SSH), remote Apple events, computer name, startup disk. | "requires at least admin privileges"; `-setremotelogin` and `-setremoteappleevents` also "Require Full Disk Access". On 27 even `-gettimezone` exits with "You need administrator access" when not run as root (host). | `man systemsetup` on the host (page dated 2020-07-30) |
| `sysadminctl` | Guest account, SMB/AFP guest access, automatic time, and `-screenLock <immediate or off or seconds> -password <password>`. | needs the user's password on the command line | `sysadminctl` usage output on the host |
| `socketfilterfw` | Application firewall on/off and stealth mode (`/usr/libexec/ApplicationFirewall/socketfilterfw`). | reading works as a normal user (host: "Firewall is disabled"); writing is expected to need root (unverified) | host |
| `/etc/pam.d/sudo_local` | Touch ID for `sudo`. The shipped template says it "survives system update"; uncommenting `auth sufficient pam_tid.so` enables it. | `sudo` | `/etc/pam.d/sudo_local.template` on the host |
| `osascript` | AppleScript/JXA: the wallpaper, login items, and anything reachable through System Events or app dictionaries. UI scripting of System Settings is possible but brittle. | Automation permission for each app it controls; Accessibility for UI scripting. Both are granted by the user in Privacy & Security. | `man osascript`; Apple: [Allow apps to control other apps](https://support.apple.com/en-ca/guide/mac-help/mchl07817563/mac), [Allow accessibility apps](https://support.apple.com/en-is/guide/mac-help/mh43185/mac) |
| Configuration profiles | Declarative, enforced settings (managed preferences, Dock, restrictions). | "Starting with macOS 11.0 ... this tool cannot be used to install configuration profiles"; the user must add them in System Settings > General > Device Management. Some payloads, including Privacy Preferences Policy Control, "Requires a device management service to install". | `man profiles` on the host; Apple: [Change Device Management settings](https://support.apple.com/guide/mac-help/change-device-management-settings-mh35474/mac) (covers macOS 27); [PPPC payload](https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-dep38df53c2a/web) |
| `NSWorkspace` / default-app tools | The default browser and other default handlers. | "If a change requires user consent, the system asks ... for consent" | Apple: [`setDefaultApplication(at:toOpenURLsWithScheme:completion:)`](https://developer.apple.com/documentation/appkit/nsworkspace/setdefaultapplication(at:toopenurlswithscheme:completion:)) |
| `hidutil property --set` | Live HID properties such as mouse acceleration. Reported as the only way to change mouse speed on 26.1, but not reflected in System Settings and not shown to persist. | none | carried over, lead only: [macos-defaults#438](https://github.com/yannbertrand/macos-defaults/issues/438) |

**Running apps.** `man defaults`: "If you change a default in a domain that belongs to a running application, the application won't see the change and might even overwrite the default." This is why scripts `killall Finder`, `Dock`, `SystemUIServer`, and (OpenBoot) `ControlCenter` after writing. Editing a plist file directly bypasses the preferences cache. hola's source works around this by forcing `CFPreferencesSynchronize` before it reads ([`macos_defaults.zig`](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_defaults.zig#L369-L379)). Prefer `defaults` over `PlistBuddy` unless the value is a nested structure `defaults` cannot express.

**`defaults` on file paths may go away.** The macOS 27 man page repeats: "WARNING: The defaults command will be changed in an upcoming major release to only operate on preferences domains." Scripts should address domains by name, not by plist path.

## What each category of setting needs

| Needs | Settings | Evidence |
| --- | --- | --- |
| Nothing extra | User-domain `defaults write` for keys read at use time (Finder view options, screenshot location, text substitution in newly launched apps) | `man defaults` |
| **Restart of a process** | `com.apple.finder` → `killall Finder`; `com.apple.dock` (Dock and Mission Control) → `killall Dock`; `com.apple.screencapture` → `killall SystemUIServer`; menu bar and Control Center items → `killall ControlCenter` | macos-defaults pages pair each key with its `killall`; OpenBoot restarts all four ([`macos.go`](https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/macos.go)) |
| **Logout (or app relaunch)** | `NSGlobalDomain` keyboard and text keys: `ApplePressAndHoldEnabled`, `KeyRepeat`, `InitialKeyRepeat`, `NSAutomatic*`; trackpad gestures | macos-defaults: "Restarting the Mac, closing the session or restarting the application is necessary" for `ApplePressAndHoldEnabled` (carried over, tested to Ventura). The same need for the other keys is a common lead, unverified on 27. |
| **`sudo` / admin** | Power (`pmset`), names (`scutil --set`), time zone, network time, remote login (`systemsetup`), firewall, Touch ID for sudo (`/etc/pam.d/sudo_local`), anything in `/Library/Preferences` (such as `com.apple.SoftwareUpdate`, readable but owned by root) | man pages above; host |
| **User's password as an argument** | Screen-lock delay (`sysadminctl -screenLock ... -password`) | host usage output. A public repo cannot hold the password, so the script has to prompt for it. |
| **Full Disk Access for the terminal** | Preferences of sandboxed Apple apps (Safari, Mail): on 27, `defaults read com.apple.Safari` says "Domain ... not found" and listing the container says "Operation not permitted" (host). Also `systemsetup -setremotelogin` and `-setremoteappleevents` (man page). Third-party containers: on 27, access to "other developer teams' app data containers ... [is] denied by default", and a process without a bundle ID (a shell script) can only be allowed via Full Disk Access. | host; [macOS 27 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes), System Integrity Protection (161835690) and Privacy & Security Settings known issue (184660124) |
| **Automation / Accessibility grant** | Anything done through `osascript` against System Events, Finder, or System Settings | Apple support pages above |
| **A click in System Settings** | Installing any configuration profile; changing the default browser; granting any privacy permission | `man profiles`; NSWorkspace doc; PPPC doc |

## Known not to be scriptable on current macOS

| Setting | Why | Confirmed on 27? |
| --- | --- | --- |
| Granting Full Disk Access, Accessibility, Automation, Screen Recording, and similar | Without MDM there is no supported path: the PPPC payload "Requires a device management service to install"; `tccutil` only offers `reset`; on 27 "Apps can no longer access the local TCC database directly" (TCC, 90775556). | Yes: `man tccutil` on the host and the 27 release notes. The PPPC page is dated 2024-07-29. |
| Installing a configuration profile from the command line | `profiles` "cannot be used to install configuration profiles" since macOS 11. The user adds it in System Settings > General > Device Management. | Yes: `man profiles` on the host; the Apple guide page covers 27 |
| Default browser (and other default handlers that need consent) | The system asks the user for consent | API doc (macOS 12+); not tested on 27 |
| Safari settings | Sandboxed container, TCC-protected. Reads and writes from a terminal without Full Disk Access fail silently. `ShowFullURLInSmartSearchField` was reported broken on Ventura and "Does not work in Tahoe either" ([macos-defaults#411](https://github.com/yannbertrand/macos-defaults/issues/411)). | Container protection yes (host). Key behaviour carried over from 26. |
| Mouse and trackpad tracking speed (`com.apple.mouse.scaling`, `com.apple.trackpad.scaling`) | Reported a no-op on 26.1, with System Settings no longer writing them ([macos-defaults#438](https://github.com/yannbertrand/macos-defaults/issues/438)). Both strings are still in the 27 shared cache (host), which proves nothing either way. | Carried over from 26.1 |
| Battery percentage in the menu bar | **Disputed, not settled.** The Ansible role and the README say `defaults write com.apple.controlcenter BatteryShowPercentage` is ignored since Ventura, the value living in the `bentoboxes` blob. On 27 that blob (`ByHost/com.apple.controlcenter.bentoboxes.<UUID>.plist`) is JSON holding the Control Center module grid and contains no battery entry (host). `BatteryShowPercentage` is still present in the 27 shared cache (host). Blog leads say the per-host form `defaults -currentHost write com.apple.controlcenter BatteryShowPercentage -bool true` works on 13+. On 27 the UI path is System Settings > Menu Bar > Battery > Battery Options > Show Percentage ([Apple](https://support.apple.com/guide/mac-help/change-menu-bar-settings-mchlad96d366/mac)). | Unverified: needs a write, so test it in the trial VM |

Also note a macOS 26.0 known issue: "Users who enable path bar or status bar in Finder and use list view might be unable to access the last item in the list" (151917092, [macOS 26 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes)). It is not listed as fixed or as a known issue in the 27 notes.

## The Ansible role's settings on macOS 27

Source: [`roles/macos_defaults/tasks/main.yml` at `4b8f39e`](https://github.com/iamivanhx/macos-setup/blob/4b8f39e36647b150fe16f170ae45e331cce864e0/roles/macos_defaults/tasks/main.yml). Evidence codes:

- **B**: key string found in a macOS 27 binary on the host (Finder, Dock, `screencapture`, or the dyld shared cache that holds AppKit and the other frameworks).
- **U**: macOS 27's own System Settings wrote the key on the host.
- **M**: the newest macOS on which macos-defaults.com lists the key as tested ([pages at `ae534d9`](https://github.com/yannbertrand/macos-defaults/tree/ae534d931241dd8c62a813818bcb921c8c9313d8/docs)); "not sure" means the repo's own [`broken.md`](https://github.com/yannbertrand/macos-defaults/blob/ae534d931241dd8c62a813818bcb921c8c9313d8/broken.md) lists it as doubtful.

| # | Setting (domain, key = value) | Mark on 27 | Evidence | Needs |
| --- | --- | --- | --- | --- |
| 1 | `com.apple.finder AppleShowAllFiles = true` | expected to work | B (Finder); M Sonoma | `killall Finder` |
| 2 | `NSGlobalDomain AppleShowAllExtensions = true` | expected to work | B (Finder); M Sonoma | `killall Finder` |
| 3 | `com.apple.finder ShowPathbar = true` | expected to work | B (Finder); M Sonoma; 26.0 list-view known issue above | `killall Finder` |
| 4 | `com.apple.finder ShowStatusBar = true` | expected to work | B (Finder); M Sequoia; same known issue | `killall Finder` |
| 5 | `com.apple.finder _FXSortFoldersFirst = true` | expected to work | B (Finder); M Sonoma | `killall Finder` |
| 6 | `com.apple.finder NewWindowTarget = PfHm` | expected to work | B for the key (Finder). The 4-byte value `PfHm` is too short for a string search to mean anything. Not on macos-defaults; OpenBoot and install.sh still ship it. | `killall Finder` |
| 7 | `com.apple.finder NewWindowTargetPath = file://$HOME/` | expected to work | B (Finder) | `killall Finder` |
| 8 | `com.apple.finder FXEnableExtensionChangeWarning = false` | expected to work | B (Finder); M Sonoma | `killall Finder` |
| 9 | `com.apple.dock autohide = true` | expected to work | **U** (already `1` on the host); B (Dock); M Sequoia | `killall Dock` |
| 10 | `com.apple.dock autohide-delay = 0.0` | expected to work | B (Dock); M Sequoia | `killall Dock` |
| 11 | `com.apple.dock autohide-time-modifier = 0.0` | expected to work | B (Dock); M Sequoia | `killall Dock` |
| 12 | `com.apple.dock minimize-to-application = true` | expected to work | B (Dock); a System Settings toggle; not on macos-defaults | `killall Dock` |
| 13 | `com.apple.dock expose-animation-duration = 0.1` | **expected to fail** | The 25-byte key is not found in the 27 Dock binary, anywhere in `Dock.app` or `WindowManager.app`, or in the shared cache (host). At 25 bytes it would be stored as a literal if it were read, so its absence is meaningful. Not on macos-defaults. Confirm in the VM. | n/a |
| 14 | `NSGlobalDomain ApplePressAndHoldEnabled = false` | expected to work | B (cache); M Ventura, "not sure" | logout or app relaunch |
| 15 | `NSGlobalDomain KeyRepeat = 1` | expected to work | B (cache). `1` is faster than the System Settings slider allows. Whether 27 honours a value below the slider's range is unverified. | logout |
| 16 | `NSGlobalDomain InitialKeyRepeat = 15` | expected to work | B (cache) | logout |
| 17 | `NSGlobalDomain AppleKeyboardUIMode = 3` | **unverified** | B (cache). macos-defaults documents the values `0` and `2` for Sonoma and Sequoia, so `3` is the pre-Sonoma value; whether 27 treats `3` as enabled is unknown. Use `2`. | app relaunch |
| 18 | `NSGlobalDomain NSAutomaticSpellingCorrectionEnabled = false` | expected to work | B (cache) | app relaunch |
| 19 | `NSGlobalDomain NSAutomaticQuoteSubstitutionEnabled = false` | expected to work | B (cache) | app relaunch |
| 20 | `NSGlobalDomain NSAutomaticDashSubstitutionEnabled = false` | expected to work | B (cache) | app relaunch |
| 21 | `NSGlobalDomain NSAutomaticCapitalizationEnabled = false` | expected to work | **U** (the host holds `1`, written by 27's UI); B (cache) | app relaunch |
| 22 | `NSGlobalDomain NSAutomaticPeriodSubstitutionEnabled = false` | expected to work | **U** (the host holds `1`); B (cache) | app relaunch |
| 23 | `com.apple.screencapture location = ~/Downloads` | expected to work | B (`screencapture` and `screencaptureui`); M Sonoma | `killall SystemUIServer` |
| 24 | `com.apple.screencapture disable-shadow = true` | expected to work | B (cache); M Sonoma | `killall SystemUIServer` |
| 25 | `com.apple.dt.Xcode ShowBuildOperationDuration = true` | **unverified** | Depends on the Xcode version, not macOS. Xcode is not installed on the host, so nothing to search. M Catalina only, "not sure". | quit Xcode |
| 26 | `com.apple.TimeMachine DoNotOfferNewDisksForBackup = true` | expected to work | B: macOS 27's `/System/Library/CoreServices/TimeMachine/TMHelperAgent.app` (a per-user launch agent, `/System/Library/LaunchAgents/com.apple.TMHelperAgent.plist`) contains the log string "Not offering '%@' for Time Machine - DoNotOfferNewDisksForBackup default set to TRUE in com.apple.TimeMachine domain", plus a second one for the `com.apple.TMHelperAgent` domain. M Catalina only, "not sure". | none (read when a disk is attached) |
| (27) | Battery percentage (omitted by the role) | **unverified** | see "Known not to be scriptable" above | n/a |

The role's non-`defaults` task, "ensure `~/Downloads` exists", is trivially fine: the folder exists on every Fresh Mac.

## How each candidate approach expresses a macOS setting

While this ticket was open, [Which tools can set up a fresh Mac, and how do they compare?](https://github.com/iamivanhx/macos-setup/issues/5#issuecomment-5853465730) shortlisted three approaches for trial: plain pieces with thin glue, mise bootstrap, and chezmoi over a Brewfile. hola and OpenBoot were not shortlisted. All five are covered here.

- **Plain script (shortlisted).** One `defaults write <domain> <key> -<type> <value>` line per setting, then one `killall` per affected process. The reference design, [donnybrilliant/install.sh](https://github.com/donnybrilliant/install.sh/blob/f659cf869273f39bd839b0ca2ff0ba2a101ebade/config#L74-L107), keeps them as a `SETTINGS=( "defaults write ..." ... )` array of command strings in one `config` file. `defaults write` is itself idempotent. Anything else (`pmset`, `scutil`, `osascript`) is just another line, with `sudo` where needed.
- **mise bootstrap (shortlisted)** ([docs at `dc2b6c3`](https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/macos-defaults.md)).
  - Friendly TOML sections `[bootstrap.macos.dock|finder|keyboard|trackpad]` map fixed names to raw keys. For example, `autohide_delay` maps to `com.apple.dock autohide-delay`, and `tap_to_click` writes both trackpad domains.
  - Raw `[bootstrap.macos.defaults."<domain>"] key = value` accepts any domain. The type comes from TOML, including arrays and tables (dicts); dates and binary data are not supported.
  - `[[bootstrap.macos.defaults_entries]]` adds `host = "current"` for ByHost keys, and `path = [...]` to patch one nested dictionary value, such as a single symbolic hotkey.
  - `[bootstrap.macos.dock] apps = [...]` owns the order of `persistent-apps`.
  - `mise bootstrap macos defaults status` reports drift, and `apply` writes only unset or differing values.
  - It "deliberately does not kill applications": the restart goes in a `post-defaults` hook.
  - It never uses `sudo` ("`sudo defaults` system domains are not supported"), so `pmset`, `scutil`, and `systemsetup` stay in a script.
  - For sandboxed apps it writes the container plist, and the docs note the terminal may need Full Disk Access. That matches the host finding above.
  - Of the Ansible list, the friendly keys cover Dock autohide, delay, and animation; Finder hidden files, path bar, status bar, folders first, and extension warning; and key repeat, initial repeat, press-and-hold, capitalization, and spelling correction. The rest need raw entries.
- **chezmoi over a Brewfile (shortlisted)** ([docs at `57eb0f7`](https://github.com/twpayne/chezmoi/tree/57eb0f7e557227c2980d92e12ca5c83926c0f0e9/assets/chezmoi.io/docs/user-guide)).
  - chezmoi has no settings resource. Settings are a shell script in the source directory, for example `run_onchange_after_macos-defaults.sh`, holding the same `defaults write` and `killall` lines as the plain script.
  - `run_onchange_` scripts "are only executed if their content" changes. "All scripts should be idempotent" ([use-scripts-to-perform-actions.md](https://github.com/twpayne/chezmoi/blob/57eb0f7e557227c2980d92e12ca5c83926c0f0e9/assets/chezmoi.io/docs/user-guide/use-scripts-to-perform-actions.md)).
  - Its macOS page shows the same pattern for `brew bundle`, and uses `scutil --get ComputerName` for a stable hostname ([machines/macos.md](https://github.com/twpayne/chezmoi/blob/57eb0f7e557227c2980d92e12ca5c83926c0f0e9/assets/chezmoi.io/docs/user-guide/machines/macos.md)).
  - What chezmoi adds over a plain script is re-run control and templating, not a settings format.
- **hola (not shortlisted)** ([`8b1cea3`](https://github.com/ratazzi/hola/tree/8b1cea3bc9a4fe79459da2a749d259cf19591c8c)).
  - A `macos_defaults 'name' do domain '…' (or global true); key '…'; value …; current_host true end` resource in `provision.rb`. The type is inferred from the Ruby value: String, Integer, true/false, Float, Array, Hash ([resource](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_defaults_resource.rb)).
  - The backend reads the current value through CFPreferences and writes only on a change. It then restarts Finder, Dock, or SystemUIServer, but only for the domains `com.apple.finder`, `com.apple.dock`, and `com.apple.systemuiserver`; `NSGlobalDomain` and `com.apple.screencapture` get no restart ([`macos_defaults.zig` L152-L200](https://github.com/ratazzi/hola/blob/8b1cea3bc9a4fe79459da2a749d259cf19591c8c/src/resources/macos_defaults.zig#L152-L200)).
  - A separate `macos_dock` resource sets Dock apps, `tilesize`, `orientation`, `autohide`, `magnification`, and `largesize`. Non-`defaults` settings need an `execute` resource.
- **OpenBoot (not shortlisted)** ([`259b119`](https://github.com/openbootdotdev/openboot/tree/259b119109d3c45fc46b9e8ab3a3bed08c6580a1)).
  - A built-in catalogue of 64 preferences in [`internal/macos/categories.go`](https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/categories.go), used by presets, the wizard, and the dashboard. From a config file it is not limited to that list: the field `macos_prefs: [{domain, key, type, value, desc, host}]` takes any scalar tuple (see [Is OpenBoot safe to depend on?](https://github.com/iamivanhx/macos-setup/issues/7#issuecomment-5853457304)). The type is limited to `string`/`int`/`bool`/`float`, with no arrays or dicts; `host: "currentHost"` selects ByHost ([`types.go`](https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/types.go), [`validate.go`](https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/config/validate.go)).
  - It shells out to `defaults write` for each entry, then `killall`s Finder, Dock, SystemUIServer, and ControlCenter ([`macos.go`](https://github.com/openbootdotdev/openboot/blob/259b119109d3c45fc46b9e8ab3a3bed08c6580a1/internal/macos/macos.go)). `dock_apps` and `login_items` are separate fields.
  - Some catalogue entries are doubtful on 27. The `NSStatusItem Visible *` keys go in the main `com.apple.controlcenter` domain, but the 27 host keeps per-host integers (`Bluetooth = 2`, `Sound = 16`) in the ByHost file. `com.apple.screensaver askForPassword*` may be superseded by `sysadminctl -screenLock`. Both are unverified.
  - Whether the config can live in this repo is the OpenBoot ticket's question.

All five end in the same `defaults` writes, so the limits in this note apply equally to each. They differ in four ways:

- **Drift reporting:** mise's `status`; hola's compare-before-write.
- **Restarts:** OpenBoot and hola restart automatically; mise and plain scripts need a hook or a line.
- **Nested values:** mise's tables and `path`; hola's Hash; neither OpenBoot nor a plain `defaults write` handles them well.
- **Non-`defaults` settings** (`pmset`, `scutil`, `systemsetup`, `sudo`): a script line in every approach.

## Not verified (would need a write)

Each is a candidate check for the trial VM ([Set up the trial VM](https://github.com/iamivanhx/macos-setup/issues/12)). The method: record `defaults read` before, write, restart the process, then look at the UI and read the value back.

1. `expose-animation-duration`: confirm it is ignored on 27.
2. `AppleKeyboardUIMode = 3` against `2` on 27.
3. `KeyRepeat = 1` (below the slider) is honoured, and which keyboard keys need a logout rather than an app relaunch.
4. `DoNotOfferNewDisksForBackup` in the user domain actually suppresses the offer. The key is referenced on 27, but this was not exercised.
5. Battery percentage: toggle it in System Settings and diff `~/Library/Preferences/ByHost/com.apple.controlcenter.*.plist`, then try `defaults -currentHost write com.apple.controlcenter BatteryShowPercentage -bool true`.
6. Menu bar item visibility keys on 27 (`NSStatusItem Visible *` against the per-host integers).
7. Whether a manually installed profile's managed preferences apply on 27 (only relevant if profiles are chosen).
8. Whether `socketfilterfw --setglobalstate` needs `sudo` (expected).
9. Whether `defaults write` to a third-party sandboxed app's container is blocked on 27 by the new cross-team container rule, or passes because `cfprefsd` does the write.

## Sources

Host (macOS 27.0, `26A428`), read-only: `sw_vers`; `man defaults`, `man pmset`, `man scutil`, `man systemsetup`, `man PlistBuddy`, `man profiles`, `man tccutil`, `man osascript`; `sysadminctl` usage; `pmset -g`, `pmset -g custom`; `scutil --get`; `defaults read` and `read-type` of the domains above; `plutil -p` of `~/Library/Preferences/ByHost/com.apple.controlcenter*.plist`; `/etc/pam.d/sudo_local.template`; byte search of `/System/Library/CoreServices/{Finder,Dock}.app`, `/System/Library/CoreServices/TimeMachine/`, `/usr/sbin/screencapture`, `screencaptureui.app`, and `/System/Volumes/Preboot/Cryptexes/OS/System/Library/dyld/dyld_shared_cache_arm64e*`.

Apple:
- [macOS 27 Golden Gate release notes](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes) (JSON at `developer.apple.com/tutorials/data/documentation/macos-release-notes/macos-27-release-notes.json`)
- [macOS 26 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-26-release-notes)
- [Privacy Preferences Policy Control payload](https://support.apple.com/guide/deployment/privacy-preferences-policy-control-payload-dep38df53c2a/web)
- [Dock payload](https://support.apple.com/guide/deployment/dock-payload-settings-depef1fdf19/web)
- [Change Device Management settings on Mac](https://support.apple.com/guide/mac-help/change-device-management-settings-mh35474/mac)
- [Change Menu Bar settings on Mac](https://support.apple.com/guide/mac-help/change-menu-bar-settings-mchlad96d366/mac)
- [NSWorkspace setDefaultApplication](https://developer.apple.com/documentation/appkit/nsworkspace/setdefaultapplication(at:toopenurlswithscheme:completion:))
- [Allow apps to control other apps](https://support.apple.com/en-ca/guide/mac-help/mchl07817563/mac)
- [Allow accessibility apps](https://support.apple.com/en-is/guide/mac-help/mh43185/mac)

References and code:
- [yannbertrand/macos-defaults at `ae534d9`](https://github.com/yannbertrand/macos-defaults/tree/ae534d931241dd8c62a813818bcb921c8c9313d8) (last content commit 2026-07-03), issues [#411](https://github.com/yannbertrand/macos-defaults/issues/411), [#438](https://github.com/yannbertrand/macos-defaults/issues/438), [#450](https://github.com/yannbertrand/macos-defaults/issues/450) (a macOS 27 comment reports `NSSplitViewItemSidebarDefaultsToFloatingAppearance` working)
- [ratazzi/hola at `8b1cea3`](https://github.com/ratazzi/hola/tree/8b1cea3bc9a4fe79459da2a749d259cf19591c8c)
- [openbootdotdev/openboot at `259b119`](https://github.com/openbootdotdev/openboot/tree/259b119109d3c45fc46b9e8ab3a3bed08c6580a1)
- [jdx/mise `docs/bootstrap/macos-defaults.md` at `dc2b6c3`](https://github.com/jdx/mise/blob/dc2b6c3626aeea98a022c275847adfe57a8bb299/docs/bootstrap/macos-defaults.md)
- [twpayne/chezmoi docs at `57eb0f7`](https://github.com/twpayne/chezmoi/tree/57eb0f7e557227c2980d92e12ca5c83926c0f0e9/assets/chezmoi.io/docs/user-guide)
- [donnybrilliant/install.sh at `f659cf8`](https://github.com/donnybrilliant/install.sh/tree/f659cf869273f39bd839b0ca2ff0ba2a101ebade)
- [swiftlang/swift `SmallString.swift`](https://github.com/swiftlang/swift/blob/dd2b2263096c1da3103638de88b34460505cddb1/stdlib/public/core/SmallString.swift)

Blog posts found by search (for example the Medium dotfile and igeeksblog pages on `BatteryShowPercentage`) were used only as leads and are not cited as evidence.
