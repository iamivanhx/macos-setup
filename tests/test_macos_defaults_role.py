import unittest
import yaml
from pathlib import Path


class TestMacosDefaultsRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.role_dir = self.repo_root / "roles" / "macos_defaults"
        self.tasks_file = self.role_dir / "tasks" / "main.yml"
        self.handlers_file = self.role_dir / "handlers" / "main.yml"

    def _load_yaml(self, path):
        self.assertTrue(path.is_file(), f"Expected file to exist: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list, f"Expected {path} to contain a YAML list")
        return data

    def _tasks(self):
        return self._load_yaml(self.tasks_file)

    def _defaults_tasks(self, domain=None, key=None):
        result = []
        for task in self._tasks():
            if not isinstance(task, dict):
                continue
            cfg = task.get("community.general.osx_defaults")
            if not isinstance(cfg, dict):
                continue
            if domain is not None and cfg.get("domain") != domain:
                continue
            if key is not None and cfg.get("key") != key:
                continue
            result.append(task)
        return result

    def test_defaults_applied_only_via_osx_defaults_module(self):
        """All system preference changes must use community.general.osx_defaults.

        Raw shell/command invocations of `defaults write` bypass idempotency
        and type handling.
        """
        tasks = self._tasks()
        for task in tasks:
            if not isinstance(task, dict):
                continue
            for module_key in ("ansible.builtin.command", "ansible.builtin.shell"):
                if module_key in task:
                    body = str(task[module_key])
                    self.assertNotIn(
                        "defaults write",
                        body,
                        f"Task {task.get('name')!r} uses raw `defaults write`; "
                        "use community.general.osx_defaults instead",
                    )
                    self.assertNotIn(
                        "defaults delete",
                        body,
                        f"Task {task.get('name')!r} uses raw `defaults delete`; "
                        "use community.general.osx_defaults instead",
                    )

        osx_defaults_tasks = [
            t for t in tasks
            if isinstance(t, dict) and "community.general.osx_defaults" in t
        ]
        self.assertGreaterEqual(
            len(osx_defaults_tasks),
            1,
            "Expected at least one community.general.osx_defaults task",
        )

    def test_finder_category_defaults_present(self):
        required_keys = {
            "AppleShowAllFiles",
            "AppleShowAllExtensions",
            "ShowPathbar",
            "ShowStatusBar",
            "_FXSortFoldersFirst",
            "NewWindowTarget",
            "FXEnableExtensionChangeWarning",
        }
        finder_tasks = self._defaults_tasks(domain="com.apple.finder")
        # Some keys (AppleShowAllExtensions) live in NSGlobalDomain; accept both.
        global_tasks = self._defaults_tasks(domain="NSGlobalDomain")
        seen_keys = {
            t["community.general.osx_defaults"].get("key")
            for t in finder_tasks + global_tasks
        }
        missing = required_keys - seen_keys
        self.assertFalse(
            missing,
            f"Missing Finder-related osx_defaults keys: {sorted(missing)}",
        )

    def test_dock_category_defaults_present(self):
        required_keys = {
            "autohide",
            "autohide-delay",
            "autohide-time-modifier",
            "minimize-to-application",
            "expose-animation-duration",
        }
        dock_tasks = self._defaults_tasks(domain="com.apple.dock")
        seen = {t["community.general.osx_defaults"].get("key") for t in dock_tasks}
        missing = required_keys - seen
        self.assertFalse(
            missing,
            f"Missing Dock-related osx_defaults keys: {sorted(missing)}",
        )

    def test_keyboard_and_input_defaults_present(self):
        required_keys = {
            "ApplePressAndHoldEnabled",
            "KeyRepeat",
            "InitialKeyRepeat",
            "AppleKeyboardUIMode",
            "NSAutomaticSpellingCorrectionEnabled",
            "NSAutomaticQuoteSubstitutionEnabled",
            "NSAutomaticDashSubstitutionEnabled",
            "NSAutomaticCapitalizationEnabled",
            "NSAutomaticPeriodSubstitutionEnabled",
        }
        global_tasks = self._defaults_tasks(domain="NSGlobalDomain")
        seen = {t["community.general.osx_defaults"].get("key") for t in global_tasks}
        missing = required_keys - seen
        self.assertFalse(
            missing,
            f"Missing NSGlobalDomain keyboard/input keys: {sorted(missing)}",
        )

    def test_screenshot_defaults_present(self):
        tasks = self._defaults_tasks(domain="com.apple.screencapture")
        seen = {t["community.general.osx_defaults"].get("key") for t in tasks}
        self.assertIn("location", seen)
        self.assertIn("disable-shadow", seen)
        # Location value should reference Downloads
        location_tasks = [
            t for t in tasks
            if t["community.general.osx_defaults"].get("key") == "location"
        ]
        for task in location_tasks:
            self.assertIn(
                "Downloads",
                str(task["community.general.osx_defaults"].get("value", "")),
                "Expected screencapture location to point at ~/Downloads",
            )

    def test_xcode_build_duration_default_present(self):
        tasks = self._defaults_tasks(
            domain="com.apple.dt.Xcode",
            key="ShowBuildOperationDuration",
        )
        self.assertGreaterEqual(
            len(tasks),
            1,
            "Expected Xcode ShowBuildOperationDuration osx_defaults task",
        )

    def test_handlers_restart_finder_dock_and_systemuiserver(self):
        handlers = self._load_yaml(self.handlers_file)
        by_name = {h.get("name"): h for h in handlers if isinstance(h, dict)}

        for handler_name, target in (
            ("restart Finder", "Finder"),
            ("restart Dock", "Dock"),
            ("restart SystemUIServer", "SystemUIServer"),
        ):
            with self.subTest(handler=handler_name):
                self.assertIn(
                    handler_name,
                    by_name,
                    f"Expected handler named {handler_name!r}",
                )
                handler = by_name[handler_name]
                cmd_module = handler.get("ansible.builtin.command")
                self.assertIsNotNone(
                    cmd_module,
                    f"Expected handler {handler_name!r} to use ansible.builtin.command",
                )
                cmd_str = str(cmd_module)
                self.assertIn("killall", cmd_str)
                self.assertIn(target, cmd_str)

    def test_tasks_notify_the_correct_handlers(self):
        """Finder tasks should notify `restart Finder`, Dock tasks should
        notify `restart Dock`, and screenshot/menu-bar tasks should notify
        `restart SystemUIServer`."""
        tasks = self._tasks()

        def notify_list(task):
            notify = task.get("notify", [])
            if isinstance(notify, str):
                return [notify]
            return notify

        for task in tasks:
            if not isinstance(task, dict):
                continue
            cfg = task.get("community.general.osx_defaults")
            if not isinstance(cfg, dict):
                continue
            domain = cfg.get("domain")
            notify = notify_list(task)

            if domain == "com.apple.finder":
                with self.subTest(task=task.get("name"), category="finder"):
                    self.assertIn("restart Finder", notify)
            elif domain == "com.apple.dock":
                with self.subTest(task=task.get("name"), category="dock"):
                    self.assertIn("restart Dock", notify)
            elif domain == "com.apple.screencapture":
                with self.subTest(task=task.get("name"), category="screencapture"):
                    self.assertIn("restart SystemUIServer", notify)

    def test_ensures_downloads_directory(self):
        tasks = self._tasks()
        matches = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.file" in t
            and isinstance(t["ansible.builtin.file"], dict)
            and t["ansible.builtin.file"].get("state") == "directory"
            and str(t["ansible.builtin.file"].get("path", "")).endswith("/Downloads")
        ]
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected an ansible.builtin.file task ensuring ~/Downloads exists",
        )

    def test_system_defaults_time_machine_present(self):
        tm = self._defaults_tasks(
            domain="com.apple.TimeMachine",
            key="DoNotOfferNewDisksForBackup",
        )
        self.assertGreaterEqual(
            len(tm),
            1,
            "Expected TimeMachine DoNotOfferNewDisksForBackup osx_defaults task",
        )

    def test_does_not_try_to_set_battery_show_percentage(self):
        """macOS Ventura+ (including Tahoe 26.x) stores the Control Center
        battery percentage toggle inside an opaque base64-encoded binary
        plist under the `boxes` key of
        com.apple.controlcenter.bentoboxes.<UUID>.plist. It is NOT writable
        via `defaults write com.apple.controlcenter BatteryShowPercentage`
        (the task silently no-ops). Must not be in the role."""
        tasks = self._tasks()
        for task in tasks:
            if not isinstance(task, dict):
                continue
            cfg = task.get("community.general.osx_defaults")
            if not isinstance(cfg, dict):
                continue
            self.assertNotEqual(
                cfg.get("key"),
                "BatteryShowPercentage",
                "BatteryShowPercentage is not writable via defaults on "
                "Ventura+ / Tahoe \u2014 remove this task",
            )

    def test_does_not_set_legacy_crashreporter_dialog_type(self):
        """CrashReporter DialogType is a legacy key not documented by the
        actively-maintained yannbertrand/macos-defaults reference. Unverified
        on Tahoe 26.x. Removed per user decision."""
        tasks = self._defaults_tasks(
            domain="com.apple.CrashReporter",
            key="DialogType",
        )
        self.assertEqual(
            len(tasks),
            0,
            "CrashReporter DialogType is unverified on Tahoe \u2014 remove it",
        )
