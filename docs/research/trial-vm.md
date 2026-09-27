# How can a disposable macOS VM run on this Mac?

Research findings for the wayfinder ticket [How can a disposable macOS VM run on this Mac?](https://github.com/iamivanhx/macos-setup/issues/9), part of the map [Map: replace Ansible with simple, maintainable Mac setup tooling](https://github.com/iamivanhx/macos-setup/issues/4). Researched 2026-09-27 against primary sources. Nothing was installed and no VM was created; every claim below is from documentation, source code, registry metadata, or the host's own read-only state.

## Answer in brief

Use **tart** (`brew install openai/tools/tart`). Build one "golden" guest from Apple's macOS 27 restore image with `tart create --from-ipsw=latest`, let macOS 27's new guest-provisioning API create the user on first boot (`tart run --provisioning-opts=...`), shut it down, and never boot it again. Each trial is an APFS copy-on-write clone of the golden guest (`tart clone`), deleted afterwards. Repo files reach the guest through a read-only virtio-fs share (`tart run --dir=repo:<path>:ro`), or by cloning from GitHub inside the guest.

A prebuilt macOS 27 image, `ghcr.io/cirruslabs/macos-golden-gate-vanilla:latest` (tag `27.0`), also exists and is the fastest way in. It is further from a Fresh Mac, though: Gatekeeper is off, Screen Sharing is on, and a keyboard-navigation setting has been changed. The self-built guest is the recommendation, and the vanilla image is the fallback.

What the guest cannot do: sign in to the **Mac App Store**, so `mas get`, `mas install` and `mas update` cannot be trialled, and neither can App Store installs of Xcode. It has no Touch ID, Wi-Fi, or Bluetooth hardware. Apple's licence allows at most **two** macOS guests running at once on this Mac.

## The host

Read on 2026-09-27 with `sw_vers`, `sysctl`, `df -h /`, and `system_profiler SPHardwareDataType`:

| Fact | Value |
| --- | --- |
| Model | MacBook Pro, `Mac15,6`, Apple M3 Pro |
| CPU | 12 cores (6 performance, 6 efficiency) |
| Memory | 36 GB (`hw.memsize` 38,654,705,664) |
| macOS | 27.0, build `26A428` |
| Boot volume free | 849 GiB of 926 GiB |
| VM tools present | none (`tart`, `utmctl`, `prlctl` not found); Homebrew present |

## Candidates

All four candidates run macOS guests on Apple silicon through Apple's Virtualization framework. They therefore share the framework's limits: App Store sign-in, the two-guest cap, and which devices exist. They differ in packaging, scripting, and how current they are for macOS 27.

### tart: recommended

- **What and who.** A CLI "to build, run and manage macOS and Linux virtual machines (VMs) on Apple Silicon" using `Virtualization.Framework` ([README](https://github.com/openai/tart/blob/main/README.md)). Cirrus Labs announced on 2026-04-07 that it was joining OpenAI, and said it would relicense Tart "under a more permissive license" and had "stopped charging licensing fees" ([cirruslabs.org](https://cirruslabs.org/)). The repository is now `openai/tart`: the API redirects `cirruslabs/tart` there, and it was last pushed 2026-09-26.
- **Licence.** FSL-1.1-ALv2. Permitted purposes include "your internal use and access", and each version converts to Apache 2.0 on its second anniversary ([LICENSE](https://github.com/openai/tart/blob/main/LICENSE); relicensed 2026-06-05 in commit "Relicense under FSL-1.1-ALv2 (#1238)"). Trialling setup tooling on your own Mac is internal use.
- **Currency.** Release 2.39.0 shipped 2026-09-26, after 2.38.0 on 2026-09-24 and 2.37.0 on 2026-09-09 ([releases](https://github.com/openai/tart/releases)).
- **Install.** `brew install openai/tools/tart`, from the README and [docs/quick-start.md](https://github.com/openai/tart/blob/main/docs/quick-start.md). The tap formula is `openai/homebrew-tools` `Formula/tart.rb`: version 2.38.0, `license "FSL-1.1-ALv2"`, `depends_on "openai/tools/softnet"`, and macOS Ventura or later ([formula](https://github.com/openai/homebrew-tools/blob/main/Formula/tart.rb)). Two traps: the old tap `cirruslabs/cli/tart` is frozen at 2.32.1 ([cirruslabs/homebrew-cli `tart.rb`](https://github.com/cirruslabs/homebrew-cli/blob/main/tart.rb)), and tart is not in homebrew-core (`brew info tart` finds no formula). The hosted page at tart.run still showed the old tap when fetched, but the source in the repo shows the new one.
- **macOS 27 support.** `tart run --provisioning-opts` is present in [Run.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Run.swift): "Provision a macOS guest on first boot using the guest provisioning API … Requires the host to be running macOS 27 (or newer) and only takes effect on the first boot after creation of a macOS 27 (or newer) guest VM". Its supported keys are `fullName`, `username`, `password`, `logsInAutomatically`, and `enablesRemoteLogin`. Cirrus Labs' own macOS 27 image template notes that it "Requires Tart 2.33.0+ and macOS 27+ on both the host and guest VM" ([vanilla-golden-gate.pkr.hcl](https://github.com/cirruslabs/macos-image-templates/blob/main/templates/vanilla-golden-gate.pkr.hcl)).
- **Scripting.** Every operation is a CLI subcommand: `create clone run stop suspend delete set ip exec pull push prune list get rename export import login logout` ([Commands/](https://github.com/openai/tart/tree/main/Sources/tart/Commands)).

### UTM: passed over

- Apache-2.0, actively developed ([utmapp/UTM](https://github.com/utmapp/UTM)). The latest **stable** release is v4.7.5, from 2026-01-03, before macOS 27 existed. The 5.0.x line (v5.0.6, 2026-09-24) is marked prerelease ([releases](https://github.com/utmapp/UTM/releases)). Its Homebrew cask is `utm` 4.7.5.
- The docs require "Apple Silicon hosts running macOS 12 or higher" for macOS guests. They list save states and snapshots as unsupported before macOS 14 ([docs.getutm.app macOS guest](https://docs.getutm.app/guest-support/macos/)).
- Scripting goes through `utmctl`, "a wrapper around the AppleScript interface" ([scripting docs](https://docs.getutm.app/scripting/scripting/)). Provisioning of macOS 27 guests ("scripting: provision macOS guests on first boot", 2026-09-19) and snapshot scripting (2026-09-21) exist only on unreleased `main`. The snapshot commit of 2026-08-20 says "Apple virtualization reports the feature as unsupported" ([UTMCtl.swift history](https://github.com/utmapp/UTM/commits/main/utmctl/UTMCtl.swift)).
- **Why passed over.** The released version predates macOS 27 and cannot skip Setup Assistant. It is GUI-first, scripting it needs the app running, and it resets a macOS guest no better than tart does.

### VirtualBuddy: passed over

- BSD-2-Clause and GUI-only, with no CLI ([README](https://github.com/insidegui/VirtualBuddy/blob/main/README.md)). The latest stable is 2.1, from 2025-09-14. The 2.2 line is in beta (2.2-b5, 2026-09-14), and the README requires "VirtualBuddy 2.2 beta 2 or later" for macOS Golden Gate ([releases](https://github.com/insidegui/VirtualBuddy/releases)). Its Homebrew cask is `virtualbuddy` 2.1.
- It resets a guest by duplicating it in Finder (APFS clone), and it has save/restore of VM state (README, "Taking Advantage of APFS").
- **Why passed over.** It cannot be scripted, and the release that supports macOS 27 is still a beta.

### Parallels Desktop: passed over

- Commercial and closed-source. The command-line interface is listed as a **Pro Edition** feature, not a Standard one ([buy page](https://www.parallels.com/products/desktop/buy/)). Its cask is `parallels` 27.0.2.
- macOS guests on Apple silicon run on Apple's Virtualization framework and inherit its limits. Snapshots came in Parallels Desktop 20. Running "more than two" macOS VMs at once is impossible. "Signing in to the App Store in a macOS virtual machine may fail due to limitations of the Apple Virtualization Framework" ([KB 128867](https://kb.parallels.com/128867), updated 2026-01-27).
- **Why passed over.** It needs a paid Pro subscription for scripting and adds nothing for macOS guests that tart lacks.

## Guest image: what exists for macOS 27

- **Apple restore image (IPSW).** `tart create --from-ipsw=latest` looks up "the latest supported IPSW automatically" ([Create.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Create.swift)) through Apple's `VZMacOSRestoreImage`, which "Fetches the latest restore image supported by this host from the network" ([Apple docs](https://developer.apple.com/documentation/virtualization/vzmacosrestoreimage/fetchlatestsupported(completionhandler:))). The macOS 27.0 IPSW is `UniversalMac_27.0_26A428_Restore.ipsw` on `updates.cdn-apple.com`, 26,626,436,228 bytes (about 26.6 GB), last modified 2026-09-04. The URL is from the Cirrus template above, and the size is from an HTTP `HEAD` on it. Its build, `26A428`, matches the host.
- **Prebuilt tart images.** Cirrus Labs' README lists `macos-{golden-gate,tahoe,sequoia,sonoma}-{vanilla,base}` ([macos-image-templates README](https://github.com/cirruslabs/macos-image-templates/blob/main/README.md)). The ghcr.io registry, queried anonymously on 2026-09-27, returned these:
  - `ghcr.io/cirruslabs/macos-golden-gate-vanilla`, tags `latest` and `27.0`, uploaded 2026-09-21. The download is about 30.9 GB compressed, the uncompressed disk is 35.7 GB, and the disk format is ASIF. The VM config is 4 CPUs and 8 GiB memory (minimum 2 CPUs and 4 GiB), with a 1024x768 display.
  - `ghcr.io/cirruslabs/macos-golden-gate-base`, tag `latest`, uploaded 2026-09-21. The download is about 33.8 GB. It is a CI image with Homebrew, rbenv, Node, the GitHub Actions runner, and more pre-installed ([base.pkr.hcl](https://github.com/cirruslabs/macos-image-templates/blob/main/templates/base.pkr.hcl)), so it is unsuitable as a Fresh Mac.
- The tart docs' image list stops at Tahoe (macOS 26) ([quick-start.md](https://github.com/openai/tart/blob/main/docs/quick-start.md)). The Golden Gate images are real, but the docs have not caught up.

**So a macOS 27 guest is available today for tart, both from Apple's IPSW and as a prebuilt image.** "Golden Gate" is macOS 27's name, per Apple's [macOS 27 Golden Gate Release Notes](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes).

## Skipping Setup Assistant (new in macOS 27)

- Apple added `VZMacGuestProvisioningOptions`, introduced in macOS 27.0: "automated setup capabilities for macOS virtual machines that allow hosts to configure a user account and initial setup workflows without manual intervention during the guest boot process … macOS only evaluates these options on the first boot after restore" ([Apple docs](https://developer.apple.com/documentation/virtualization/vzmacguestprovisioningoptions)). Its properties are `fullName`, `username`, `password`, `logsInAutomatically`, and `enablesRemoteLogin`.
- In WWDC26 session 224, Apple shows Setup Assistant running unattended: "Setup assistant automatically creates a new user … the guest has logged into the account", and "these settings are only honored if the guest has not already been set up" ([WWDC26 session 224](https://developer.apple.com/videos/play/wwdc2026/224/)).
- Cirrus Labs' macOS 27 template waits 120 s after the first provisioned boot before sending keystrokes ([vanilla-golden-gate.pkr.hcl](https://github.com/cirruslabs/macos-image-templates/blob/main/templates/vanilla-golden-gate.pkr.hcl)). That is the best available guide to how long first boot takes.
- **Not verified.** Whether any other Setup Assistant pane still appears after provisioning (Apple Account, Location Services, Analytics, Screen Time, appearance). Neither Apple's docs nor the session list which panes are skipped. The Cirrus template's keystrokes start in Terminal right after the wait, which suggests no pane blocks the desktop. That is an inference, not a documented fact.
- Before macOS 27, tart's own docs said "you'll need to manually go through the macOS installation process" after `tart create --from-ipsw` ([quick-start.md](https://github.com/openai/tart/blob/main/docs/quick-start.md)). That manual path is still there if provisioning misbehaves.

## Recommended setup, step by step

These steps are for the task ticket [Set up the trial VM](https://github.com/iamivanhx/macos-setup/issues/12), which the owner confirms before anything is installed. Names are suggestions.

1. **Install tart** (writes to the host):
   ```sh
   brew install openai/tools/tart
   tart --version        # expect 2.38.0 or newer; provisioning needs 2.33.0+
   ```
2. **Create the golden guest from Apple's IPSW.** This downloads about 26.6 GB and installs macOS 27 into a new VM:
   ```sh
   tart create --from-ipsw=latest --disk-size 60 --disk-format asif fresh-27
   tart set fresh-27 --cpu 4 --memory 8192
   ```
   `--disk-format asif` "provides better performance but requires macOS 26 Tahoe or later" ([Create.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Create.swift)). Without `--disk-size` the disk is 50 GB, which is enough for most trials. Without `tart set` a VM gets 2 CPUs and 4 GB ([quick-start](https://tart.run/quick-start/)), which is tight for Homebrew builds.
3. **First boot with provisioning.** This happens once only. It creates the user, turns on auto-login, and turns on SSH:
   ```sh
   tart run --provisioning-opts="fullName=Trial,username=admin,password=admin,logsInAutomatically=true,enablesRemoteLogin=true" fresh-27
   ```
   Wait for the desktop, check that the guest is on macOS 27.0 (`sw_vers` in its Terminal), then shut it down from the Apple menu. The throwaway password is fine because the guest is disposable; it goes into no committed file. Leave `enablesRemoteLogin=false` for the most faithful Fresh Mac, at the cost of scripted access (see "How far a guest is from a Fresh Mac").
4. **Freeze the fresh state.** Never run `fresh-27` again: it is the saved fresh state. Every trial runs on a clone:
   ```sh
   tart clone fresh-27 trial        # APFS copy-on-write: near-instant, near-zero space
   tart run --dir=repo:/path/to/macos-setup:ro trial
   ```
   The `clone` help says: "Due to copy-on-write magic in Apple File System, a cloned VM won't actually claim all the space right away. Only changes to a cloned disk will be written and claim new space" ([Clone.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Clone.swift)).
5. **Reset to fresh** = throw the clone away and clone again:
   ```sh
   tart stop trial ; tart delete trial ; tart clone fresh-27 trial
   ```
6. **Run things in the guest from the host** over SSH:
   ```sh
   ssh admin@$(tart ip trial)
   ```
   `tart ip` reads the host's DHCP lease file by default and needs no guest agent. `tart exec` needs the Tart Guest Agent ([IP.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/IP.swift), [Exec.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Exec.swift)). Neither the vanilla image nor a self-built guest has the agent; Cirrus installs it only in `base` ([search](https://github.com/cirruslabs/macos-image-templates/blob/main/templates/base.pkr.hcl)). SSH is the channel.

**Fallback if the IPSW path fails:** `tart clone ghcr.io/cirruslabs/macos-golden-gate-vanilla:latest fresh-27`, then steps 4 to 6. Its differences from a Fresh Mac are listed below.

**Optional:** `tart clone --stacked` builds a stacked disk over a remote image's immutable base, using macOS 27's DiskImageKit ([Clone.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Clone.swift); DiskImageKit per the [macOS 27 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes)). It works only from a registry image, so it does not apply to the self-built golden guest, and plain APFS clones are enough here.

## How files from this repo reach the guest

- **Read-only share (recommended for uncommitted or branch work).** `tart run --dir=repo:<host path>:ro <vm>`. With the default mount tag, macOS guests auto-mount shares at `/Volumes/My Shared Files/<name>`. `ro` mounts read-only, so a trial cannot write back into the repo. This needs macOS 13 or later on host and guest ([Run.swift `--dir` help](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Run.swift)). Point it at a worktree or a clean checkout, not the owner's main checkout with uncommitted work, unless that work is what is being trialled.
- **From GitHub (the real Bootstrap path).** The repo is public, so the guest can fetch it over the network exactly as a Fresh Mac would (the `curl | bash` one-liner, or a download). This tests the first-run path, including the Xcode Command Line Tools prompt that `/usr/bin/git` triggers on a Mac without them.
- **scp** over the SSH channel, `scp -r <path> admin@$(tart ip trial):`, for one-off files.

## Disk, memory, and time

| Resource | Needed | Host has | Verdict |
| --- | --- | --- | --- |
| Disk: IPSW | about 26.6 GB (tart keeps an IPSW cache; `tart prune --entries caches` removes it, per [Prune.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Prune.swift)) | 849 GiB free | ample |
| Disk: golden guest | up to its logical size, 50 to 60 GB; a fresh macOS 27 install fills about 36 GB, judging by the vanilla image's 35.7 GB uncompressed disk | | ample |
| Disk: each clone | only what the trial writes (copy-on-write); a full Bootstrap with apps plausibly adds 10 to 30 GB, which is not verified | | ample |
| Disk: vanilla image path instead | about 31 GB download plus about 36 GB unpacked | | ample |
| Memory | 8 GB per guest recommended (the Cirrus images default to 8 GiB with a 4 GiB minimum) | 36 GB | leaves 28 GB for the host; two guests at once still fit |
| CPU | 4 vCPUs per guest | 12 cores | fine |

Time estimates. None of these were measured, because measuring requires the download and a VM:

- IPSW download: 26.6 GB takes about 36 minutes at 100 Mbit/s and about 7 minutes at 500 Mbit/s. The vanilla image, about 31 GB, takes a little longer.
- macOS install into the VM from the IPSW: not documented anywhere I found. Budget 15 to 30 minutes.
- First provisioned boot: about 2 minutes, going by the Cirrus template's 120 s wait.
- Clone: seconds (APFS copy-on-write). Boot of a clone: about a minute. Neither is documented.

Total first-time setup: about an hour with a typical connection. Each reset after that is under two minutes.

## Licence limits on macOS guests

- The **macOS 27 software licence**, Apple document EA2005, is served at [macOSGoldenGate.pdf](https://www.apple.com/legal/sla/docs/macOSGoldenGate.pdf), identical to `macOS27.pdf`, and was last modified 2026-09-24. Section 2B(iii) grants the right "to install, use and run up to two (2) additional copies or instances of the Apple Software, or any prior macOS or OS X operating system software or subsequent release of the Apple Software, within virtual operating system environments on each Apple-branded computer you own or control that is already running the Apple Software, for purposes of: (a) software development; (b) testing during software development; (c) using macOS Server; or (d) personal, non-commercial use". It forbids "service bureau, time-sharing, terminal sharing, relay service" use.
  - Compared with macOS 26 (EA1955, [macOSTahoe.pdf](https://www.apple.com/legal/sla/docs/macOSTahoe.pdf)), the text is the same except that macOS 27 adds a leading "except as otherwise provided in writing, signed, or issued by an authorized representative of Apple".
  - The grant sits under 2B, "Mac App Store License", which covers Apple software obtained "from the Mac App Store or through an automatic download". A macOS 27 install downloaded from Apple falls under it.
- Trialling this repo's setup tooling fits "testing during software development" and "personal, non-commercial use".
- The framework enforces the cap: `VZError.Code.virtualMachineLimitExceeded` ([Apple docs](https://developer.apple.com/documentation/virtualization/vzerror/code)). Parallels documents that more than two macOS VMs cannot run at once ([KB 128867](https://kb.parallels.com/128867)). The cap counts running guests. Stopped clones and the stopped golden guest do not count, since the grant is about copies run at once. That reading is inferred from the framework error and Parallels' wording, not tested.

## What a guest cannot do

- **Mac App Store sign-in: not supported.** Parallels' page for its current version says: "Even on macOS Sequoia 15 and later, signing into the Mac App Store from within the virtual machine is still not supported" ([KB 131160](https://kb.parallels.com/en/131160), updated 2026-07-07). KB 128867 attributes this to the Virtualization framework. The [macOS 27 release notes](https://developer.apple.com/documentation/macos-release-notes/macos-27-release-notes) have a Virtualization section that does not mention the App Store, and WWDC26 session 224 does not mention it either. **This is carried over from macOS 15 and 26 evidence and is not confirmed for macOS 27.**
  - Consequence for `mas`: `get`, `install`, `lucky`, `update`, and `outdated --accurate` "require an Apple Account signed in to the App Store" ([mas README](https://github.com/mas-cli/mas/blob/main/README.md)). In a guest these cannot be trialled, beyond checking that `mas` itself installs and that `mas list` and `mas outdated` run. App Store apps in the Bootstrap need proving on real hardware, or at least keeping out of the VM trial's pass/fail.
  - Consequence for Xcode: an App Store install cannot be trialled. The Command Line Tools install (`xcode-select --install` or `softwareupdate`) does not depend on the App Store, but was not verified in a guest.
- **Apple Account / iCloud sign-in: supported**, with conditions. "In macOS 15 and later, Virtualization supports access to iCloud accounts and resources … When you create a VM in macOS 15 from a macOS 15 software image". A VM upgraded from an older version gets no iCloud support. A VM moved to another host, or a copy started while its twin is running, gets a new identity and must re-authenticate ([Apple: Using iCloud with macOS virtual machines](https://developer.apple.com/documentation/virtualization/using-icloud-with-macos-virtual-machines)). A self-built macOS 27 guest meets these conditions. The documentation is written for macOS 15 and was not re-confirmed for 27. Apple DTS confirmed that a macOS 26.1 bug broke Apple Account sign-in in VMs and that it was fixed in 26.2 ([Developer Forums thread 809367](https://developer.apple.com/forums/thread/809367)).
- **Hardware the framework does not provide.** The Virtualization framework's device categories are audio, graphics, keyboards and pointing devices, memory, network, randomization, serial ports, shared directories, sockets, storage, consoles, clipboard sharing, USB devices, and custom drivers ([Apple: Virtualization](https://developer.apple.com/documentation/virtualization)). There is no biometric, Wi-Fi, Bluetooth, or battery device. So Touch ID (including Touch ID for `sudo`), Wi-Fi and Bluetooth settings, and battery or energy settings cannot be exercised meaningfully. The guest's network is virtual Ethernet behind NAT.
- **Nested virtualization** is Linux-only ([tart FAQ](https://tart.run/faq/)), which is irrelevant here.

## How far a guest is from a true Fresh Mac

A **self-built guest** (IPSW plus provisioning) differs from a Fresh Mac in these ways:

- **The user.** It was created by provisioning, not by a person clicking through Setup Assistant. Choices that Setup Assistant normally asks for, if it skips them, stay at defaults: Apple Account not signed in, and so on (see "Not verified").
- **Auto-login and SSH.** These are on only if requested. Turning SSH on is a deviation, but a Bootstrap that does not touch Remote Login is not affected by it.
- **Hardware.** It is a virtual Mac, with no Touch ID, Wi-Fi, or Bluetooth.
- **App Store.** It cannot be signed in (above).
- **Everything else.** Gatekeeper, SIP, FileVault defaults, and system settings are as Apple ships them. The Mac also has no Xcode Command Line Tools, no Homebrew, and no apps beyond those bundled with macOS. That is closer to a Fresh Mac than the target Mac is today, since the target Mac already has Homebrew, `gh`, apps, and the Command Line Tools.

The **Cirrus vanilla image** has all of the above, plus these changes made by its [template](https://github.com/cirruslabs/macos-image-templates/blob/main/templates/vanilla-golden-gate.pkr.hcl):

- It has user `admin`/`admin` ("Managed via Tart"), with auto-login and SSH on.
- `sudo` needs no password (`/etc/sudoers.d/admin-nopasswd`). This hides the `sudo` prompts that a real Bootstrap meets.
- **Gatekeeper is disabled** (`spctl --global-disable`). This hides quarantine and Gatekeeper prompts for downloaded apps and casks.
- **Screen Sharing is enabled.**
- `NSGlobalDomain AppleKeyboardUIMode` is set to 3. That is a macOS setting, and it would confound trials of macOS settings.
- The timezone is GMT, and the screensaver, sleep, and screen lock are off.
- Safari has been launched once, and `safaridriver --enable` has been run.

These are why the vanilla image is the fallback rather than the recommendation.

## Risks and exit cost

- **Single vendor.** tart belongs to OpenAI now. The licence permits internal use, and each release becomes Apache 2.0 after two years.
- **The exit is cheap.** tart is trial infrastructure only, never part of the Bootstrap, so nothing in this repo depends on it. A tart VM is a directory in `~/.tart/vms/` ([FAQ](https://tart.run/faq/)) holding a disk image, NVRAM, and a config file. If tart went away, the same flow (IPSW, provisioning, APFS copy) is available in UTM once its 5.0 line with provisioning is released, or in VirtualBuddy.
- **DHCP leases.** Each new clone gets a new MAC address whenever another local VM already has the source's MAC, which is always true when cloning the golden guest ([Clone.swift](https://github.com/openai/tart/blob/main/Sources/tart/Commands/Clone.swift)). With the default one-day lease, many resets in a day can exhaust the pool. tart's formula caveat and FAQ suggest shortening the lease to 600 s with a `sudo defaults write` on the host ([FAQ](https://tart.run/faq/)). That is a host change for the owner to decide on, and it is only needed if `tart ip` starts failing.

## Not verified without running a VM

- That `tart create --from-ipsw=latest` completes on this host, and how long the install takes.
- That provisioning in tart 2.38/2.39 works on this host, and which Setup Assistant panes, if any, still appear afterwards.
- That Mac App Store sign-in still fails in a macOS 27 guest. The evidence is from macOS 15 and 26.
- That Apple Account / iCloud sign-in works in a macOS 27 guest. Apple's docs are written for macOS 15.
- That the Xcode Command Line Tools install from inside a guest.
- Real download speed, clone boot time, and how much disk a full Bootstrap trial writes.
- That the two-guest cap counts only running guests. This is inferred, not tested.
