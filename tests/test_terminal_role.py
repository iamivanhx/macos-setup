import unittest
import yaml
from pathlib import Path


class TestTerminalRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.tasks_file = self.repo_root / "roles" / "terminal" / "tasks" / "main.yml"
        self.vars_file = self.repo_root / "group_vars" / "all.yml"

    def _load_tasks(self):
        self.assertTrue(self.tasks_file.is_file(), f"Expected tasks file to exist: {self.tasks_file}")
        tasks = yaml.safe_load(self.tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {self.tasks_file} to contain a YAML list")
        return tasks

    def test_installs_nerd_font_via_homebrew_cask(self):
        tasks = self._load_tasks()

        cask_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.homebrew_cask" in task
            and isinstance(task["community.general.homebrew_cask"], dict)
            and "nerd_font_cask" in str(
                task["community.general.homebrew_cask"].get("name", "")
            )
        ]
        self.assertGreaterEqual(
            len(cask_tasks),
            1,
            "Expected a community.general.homebrew_cask task installing "
            "{{ nerd_font_cask }}",
        )
        for task in cask_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["community.general.homebrew_cask"]
                self.assertEqual(cfg.get("state"), "present")
                self.assertIs(
                    cfg.get("accept_external_apps"),
                    True,
                    "Expected accept_external_apps: true on Nerd Font cask install",
                )

    def test_ensures_dot_config_directory_exists(self):
        tasks = self._load_tasks()
        matches = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.file" in task
            and isinstance(task["ansible.builtin.file"], dict)
            and task["ansible.builtin.file"].get("state") == "directory"
            and str(task["ansible.builtin.file"].get("path", "")).endswith("/.config")
        ]
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected an ansible.builtin.file task creating ~/.config as a directory",
        )
        for task in matches:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["ansible.builtin.file"]
                self.assertIn(
                    str(cfg.get("mode")),
                    ("0755", "755", "u=rwx,go=rx"),
                    "Expected ~/.config directory mode 0755",
                )

    def test_generates_starship_gruvbox_preset_idempotently(self):
        tasks = self._load_tasks()
        preset_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "starship preset" in str(task["ansible.builtin.command"])
            and "gruvbox-rainbow" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(preset_tasks),
            1,
            "Expected an ansible.builtin.command running "
            "`starship preset gruvbox-rainbow`",
        )

        for task in preset_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cmd_str = str(task["ansible.builtin.command"])
                self.assertIn(
                    "starship.toml",
                    cmd_str,
                    "Expected the preset to be written to starship.toml",
                )
                # Idempotency: the task must use `creates:` so existing
                # (possibly user-customized) starship.toml files are preserved.
                module_cfg = task["ansible.builtin.command"]
                creates_value = None
                if isinstance(module_cfg, dict):
                    creates_value = module_cfg.get("creates")
                if not creates_value:
                    creates_value = (task.get("args") or {}).get("creates")
                self.assertTrue(
                    creates_value,
                    "Expected starship preset task to use `creates:` so "
                    "re-runs don't clobber a user-customized starship.toml",
                )
                self.assertIn(
                    "starship.toml",
                    str(creates_value),
                    "Expected `creates:` to point at starship.toml",
                )

    def test_adds_starship_init_to_zshrc_idempotently(self):
        tasks = self._load_tasks()
        lineinfile_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.lineinfile" in task
            and isinstance(task["ansible.builtin.lineinfile"], dict)
            and str(task["ansible.builtin.lineinfile"].get("path", "")).endswith(".zshrc")
        ]
        self.assertGreaterEqual(
            len(lineinfile_tasks),
            1,
            "Expected an ansible.builtin.lineinfile task editing ~/.zshrc",
        )
        for task in lineinfile_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["ansible.builtin.lineinfile"]
                line = str(cfg.get("line", ""))
                self.assertIn(
                    "starship init zsh",
                    line,
                    "Expected lineinfile to add `eval \"$(starship init zsh)\"`",
                )
                self.assertIn("eval", line)
                self.assertIs(
                    cfg.get("create"),
                    True,
                    "Expected lineinfile create: true so ~/.zshrc is created if missing",
                )
