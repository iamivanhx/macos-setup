import unittest
import yaml
from pathlib import Path


class TestCaskAppsRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_install_task_uses_community_general_homebrew_cask_module_with_loop(self):
        tasks_file = self.repo_root / "roles" / "cask_apps" / "tasks" / "main.yml"

        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML list")
        self.assertGreaterEqual(len(tasks), 1, f"Expected at least one task in {tasks_file}")

        install_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.homebrew_cask" in task
            and ("loop" in task or "with_items" in task)
        ]

        self.assertGreaterEqual(
            len(install_tasks),
            1,
            f"Expected at least one looping community.general.homebrew_cask task in {tasks_file}",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertNotIn("ansible.builtin.shell", task)
                self.assertNotIn("ansible.builtin.command", task)

                module_config = task["community.general.homebrew_cask"]
                self.assertIsInstance(
                    module_config,
                    dict,
                    "Expected community.general.homebrew_cask configuration to be a mapping",
                )
                self.assertEqual(module_config.get("name"), "{{ item }}")
                self.assertEqual(module_config.get("state"), "present")

                loop_key = next((key for key in ("loop", "with_items") if key in task), None)
                self.assertIsNotNone(
                    loop_key,
                    "Expected community.general.homebrew_cask task to define loop or with_items",
                )
                self.assertIn(
                    "homebrew_casks",
                    str(task[loop_key]),
                    "Expected loop source to reference homebrew_casks",
                )

    def test_required_casks_are_declared_in_group_vars(self):
        vars_file = self.repo_root / "group_vars" / "all.yml"

        self.assertTrue(vars_file.is_file(), f"Expected group vars file to exist: {vars_file}")

        data = yaml.safe_load(vars_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, f"Expected {vars_file} to contain a YAML mapping")

        casks = data.get("homebrew_casks")
        self.assertIsInstance(
            casks,
            list,
            "Expected homebrew_casks to be declared as a YAML list",
        )

        required_casks = [
            "1password",
            "google-chrome",
            "discord",
            "obsidian",
            "visual-studio-code",
            "iterm2",
        ]

        for cask in required_casks:
            with self.subTest(cask=cask):
                self.assertIn(cask, casks)

    def test_install_task_sets_accept_external_apps_true(self):
        tasks_file = self.repo_root / "roles" / "cask_apps" / "tasks" / "main.yml"

        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML list")

        install_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.homebrew_cask" in task
            and isinstance(task["community.general.homebrew_cask"], dict)
            and task["community.general.homebrew_cask"].get("name") == "{{ item }}"
            and ("loop" in task or "with_items" in task)
        ]

        self.assertGreaterEqual(
            len(install_tasks),
            1,
            f"Expected at least one looping community.general.homebrew_cask install task in {tasks_file}",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                module_config = task["community.general.homebrew_cask"]
                self.assertTrue(
                    module_config.get("accept_external_apps") is True,
                    "Expected looping community.general.homebrew_cask install task to set accept_external_apps: true",
                )


if __name__ == "__main__":
    unittest.main()
