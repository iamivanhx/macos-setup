import unittest
import yaml
from pathlib import Path


class TestVerifyRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.role_dir = self.repo_root / "roles" / "verify"
        self.tasks_file = self.role_dir / "tasks" / "main.yml"
        self.defaults_file = self.role_dir / "defaults" / "main.yml"

    def _load_yaml_list(self, path):
        self.assertTrue(path.is_file(), f"Expected file to exist: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, list, f"Expected {path} to contain a YAML list")
        return data

    def _load_yaml_mapping(self, path):
        self.assertTrue(path.is_file(), f"Expected file to exist: {path}")
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, f"Expected {path} to contain a YAML mapping")
        return data

    def _tasks(self):
        return self._load_yaml_list(self.tasks_file)

    def _defaults(self):
        return self._load_yaml_mapping(self.defaults_file)

    def test_role_defaults_declare_required_check_lists(self):
        defaults = self._defaults()

        for key in (
            "verify_cli_tools",
            "verify_gui_apps",
            "verify_config_files",
            "verify_macos_defaults",
        ):
            with self.subTest(key=key):
                self.assertIn(
                    key,
                    defaults,
                    f"Expected role defaults to declare {key}",
                )
                self.assertIsInstance(defaults[key], list)
                self.assertTrue(defaults[key], f"{key} must be non-empty")

        cli = defaults["verify_cli_tools"]
        # Spot-check the expected binaries reflect the *actual* install
        # decisions from issues 003-010 (not the outdated names in the issue).
        for expected in (
            "git", "gh", "vim", "mas", "starship", "jq", "rg", "fd", "bat",
            "uv", "pnpm", "node",
            "copilot",       # from Homebrew copilot-cli, not the npm archived pkg
            "claude",        # from official install script at ~/.local/bin/claude
            "socket", "sfw", # pnpm globals
        ):
            with self.subTest(tool=expected):
                self.assertIn(expected, cli)

        gui = defaults["verify_gui_apps"]
        for app in (
            "1Password.app",
            "Google Chrome.app",
            "Discord.app",
            "Obsidian.app",
            "Visual Studio Code.app",
            "iTerm.app",
            "Xcode.app",
        ):
            with self.subTest(app=app):
                self.assertIn(app, gui)

        cfg = defaults["verify_config_files"]
        # config files entries should be mappings with `path` and `label`
        for entry in cfg:
            with self.subTest(entry=entry):
                self.assertIsInstance(entry, dict)
                self.assertIn("path", entry)
                self.assertIn("label", entry)
        cfg_paths = " ".join(str(e.get("path", "")) for e in cfg)
        self.assertIn("id_ed25519", cfg_paths)
        self.assertIn("starship.toml", cfg_paths)
        self.assertIn(".zshrc", cfg_paths)

    def test_cli_tool_probe_loops_over_verify_cli_tools_and_tolerates_failure(self):
        tasks = self._tasks()
        probe_tasks = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.shell" in t
            and "command -v" in str(t["ansible.builtin.shell"])
        ]
        self.assertGreaterEqual(
            len(probe_tasks),
            1,
            "Expected an ansible.builtin.shell probe running `command -v` "
            "to detect CLI tools",
        )
        for task in probe_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                loop_key = next((k for k in ("loop", "with_items") if k in task), None)
                self.assertIsNotNone(
                    loop_key,
                    "Expected CLI probe to loop over tools",
                )
                self.assertIn(
                    "verify_cli_tools",
                    str(task[loop_key]),
                    "Expected loop source to be verify_cli_tools",
                )
                self.assertIs(
                    task.get("failed_when"),
                    False,
                    "Expected CLI probe to tolerate non-zero (missing) tools",
                )
                self.assertEqual(task.get("changed_when"), False)
                self.assertIn(
                    "register",
                    task,
                    "Expected CLI probe to register its result for summarization",
                )
                # Role must augment PATH so Homebrew / pnpm / ~/.local/bin tools
                # resolve under Ansible's non-login shell.
                env = task.get("environment", {})
                path = str(env.get("PATH", ""))
                self.assertIn("/opt/homebrew/bin", path)
                self.assertIn(".local/bin", path)
                self.assertIn(".local/share/pnpm", path)

    def test_gui_app_probe_stats_applications_directory(self):
        tasks = self._tasks()
        stat_tasks = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.stat" in t
            and isinstance(t["ansible.builtin.stat"], dict)
            and "/Applications" in str(t["ansible.builtin.stat"].get("path", ""))
        ]
        self.assertGreaterEqual(
            len(stat_tasks),
            1,
            "Expected an ansible.builtin.stat task probing /Applications",
        )
        for task in stat_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                loop_key = next((k for k in ("loop", "with_items") if k in task), None)
                self.assertIsNotNone(loop_key)
                self.assertIn("verify_gui_apps", str(task[loop_key]))
                self.assertIn("register", task)

    def test_config_file_probe_stats_each_entry(self):
        tasks = self._tasks()
        stat_tasks = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.stat" in t
            and isinstance(t["ansible.builtin.stat"], dict)
            and "item.path" in str(t["ansible.builtin.stat"].get("path", ""))
        ]
        self.assertGreaterEqual(
            len(stat_tasks),
            1,
            "Expected an ansible.builtin.stat task looping over "
            "verify_config_files with item.path",
        )
        for task in stat_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                loop_key = next((k for k in ("loop", "with_items") if k in task), None)
                self.assertIsNotNone(loop_key)
                self.assertIn("verify_config_files", str(task[loop_key]))
                self.assertIn("register", task)

    def test_macos_defaults_spot_check_uses_defaults_read(self):
        tasks = self._tasks()
        probe_tasks = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.command" in t
            and "defaults read" in str(t["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(probe_tasks),
            1,
            "Expected at least one `defaults read` probe task",
        )
        for task in probe_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                loop_key = next((k for k in ("loop", "with_items") if k in task), None)
                self.assertIsNotNone(loop_key)
                self.assertIn("verify_macos_defaults", str(task[loop_key]))
                self.assertIs(task.get("failed_when"), False)
                self.assertEqual(task.get("changed_when"), False)
                self.assertIn("register", task)

    def test_summary_debug_reports_pass_fail_counts(self):
        tasks = self._tasks()
        debug_tasks = [
            t for t in tasks
            if isinstance(t, dict)
            and "ansible.builtin.debug" in t
            and isinstance(t["ansible.builtin.debug"], dict)
        ]
        # At least one debug task must mention "passed" with the
        # verify_total / verify_failed pattern.
        summary_tasks = [
            t for t in debug_tasks
            if "checks passed" in str(t["ansible.builtin.debug"]).lower()
        ]
        self.assertGreaterEqual(
            len(summary_tasks),
            1,
            "Expected a summary debug task rendering `<n>/<total> checks passed`",
        )
        for task in summary_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                body = str(task["ansible.builtin.debug"])
                self.assertIn("verify_total", body)
                self.assertIn("verify_failed", body)

    def test_role_is_strictly_read_only(self):
        """The verify role must never mutate system state. It can only read,
        stat, run read-only commands, register, set_fact, and debug."""
        tasks = self._tasks()

        forbidden_modules = {
            "ansible.builtin.copy",
            "ansible.builtin.template",
            "ansible.builtin.lineinfile",
            "ansible.builtin.blockinfile",
            "ansible.builtin.file",  # would create/modify paths
            "ansible.builtin.git",
            "ansible.builtin.pip",
            "ansible.builtin.unarchive",
            "community.general.homebrew",
            "community.general.homebrew_cask",
            "community.general.osx_defaults",
            "community.general.git_config",
            "ansible.builtin.user",
            "ansible.builtin.group",
        }

        # ansible.builtin.command / shell are allowed but must not run
        # state-mutating subcommands.
        mutating_substrings = (
            "defaults write",
            "defaults delete",
            "ssh-keygen",
            "ssh-add",
            "brew install",
            "brew uninstall",
            "pnpm add",
            "pnpm install",
            "git config --global --replace-all",
            "git config --global --unset",
            "killall ",
            "curl -fsSL",
            "tee ",
            "> ",
            ">> ",
        )

        for task in tasks:
            if not isinstance(task, dict):
                continue
            with self.subTest(task=task.get("name", "unnamed")):
                for module in forbidden_modules:
                    self.assertNotIn(
                        module,
                        task,
                        f"Forbidden state-mutating module {module!r} used in verify role",
                    )

                for module_key in ("ansible.builtin.command", "ansible.builtin.shell"):
                    if module_key in task:
                        body = str(task[module_key])
                        for frag in mutating_substrings:
                            self.assertNotIn(
                                frag,
                                body,
                                f"Task {task.get('name')!r} runs a mutating "
                                f"command containing {frag!r}",
                            )
