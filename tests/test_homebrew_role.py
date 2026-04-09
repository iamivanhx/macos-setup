import unittest
import yaml
from pathlib import Path


class TestHomebrewRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_install_task_uses_community_general_homebrew_module_with_loop(self):
        tasks_file = self.repo_root / "roles" / "homebrew" / "tasks" / "main.yml"

        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML list")
        self.assertGreaterEqual(len(tasks), 1, f"Expected at least one task in {tasks_file}")

        install_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.homebrew" in task
            and ("loop" in task or "with_items" in task)
        ]

        self.assertGreaterEqual(
            len(install_tasks),
            1,
            f"Expected at least one looping community.general.homebrew task in {tasks_file}",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertNotIn("ansible.builtin.shell", task)
                self.assertNotIn("ansible.builtin.command", task)

                module_config = task["community.general.homebrew"]
                self.assertIsInstance(
                    module_config,
                    dict,
                    "Expected community.general.homebrew configuration to be a mapping",
                )
                self.assertEqual(module_config.get("name"), "{{ item }}")
                self.assertEqual(module_config.get("state"), "present")

                loop_key = next((key for key in ("loop", "with_items") if key in task), None)
                self.assertIsNotNone(
                    loop_key,
                    "Expected community.general.homebrew task to define loop or with_items",
                )
                self.assertIn(
                    "homebrew_formulae",
                    str(task[loop_key]),
                    "Expected loop source to reference homebrew_formulae",
                )


    def test_role_updates_homebrew_before_installing_formulae(self):
        tasks_path = self.repo_root / "roles" / "homebrew" / "tasks" / "main.yml"
        with tasks_path.open("r", encoding="utf-8") as f:
            tasks = yaml.safe_load(f)

        self.assertIsInstance(tasks, list, "Expected roles/homebrew/tasks/main.yml to contain a task list")

        homebrew_tasks = []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            config = task.get("community.general.homebrew")
            if isinstance(config, dict):
                homebrew_tasks.append(config)

        self.assertTrue(
            homebrew_tasks,
            "Expected at least one community.general.homebrew task in roles/homebrew/tasks/main.yml",
        )
        self.assertTrue(
            any(task.get("update_homebrew") == True for task in homebrew_tasks),
            "Expected at least one community.general.homebrew task to set update_homebrew: true",
        )


    def test_required_formulae_are_declared_in_group_vars(self):
        vars_file = self.repo_root / "group_vars" / "all.yml"

        self.assertTrue(vars_file.is_file(), f"Expected group vars file to exist: {vars_file}")

        data = yaml.safe_load(vars_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, f"Expected {vars_file} to contain a YAML mapping")

        formulae = data.get("homebrew_formulae")
        self.assertIsInstance(
            formulae,
            list,
            "Expected homebrew_formulae to be declared as a YAML list",
        )

        required_formulae = [
            "git", "gh", "vim", "mas", "starship", "curl", "wget",
            "jq", "tree", "ripgrep", "fd", "bat", "htop", "tldr",
        ]

        for formula in required_formulae:
            with self.subTest(formula=formula):
                self.assertIn(formula, formulae)


    def test_update_task_runs_before_install_task(self):
        tasks_file = self.repo_root / "roles" / "homebrew" / "tasks" / "main.yml"
        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML task list")

        update_idx = None
        install_idx = None

        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue

            module_config = task.get("community.general.homebrew")
            if not isinstance(module_config, dict):
                continue

            if update_idx is None and module_config.get("update_homebrew") is True:
                update_idx = idx

            has_loop = "loop" in task or "with_items" in task
            installs_item = module_config.get("name") == "{{ item }}"
            if install_idx is None and has_loop and installs_item:
                install_idx = idx

        self.assertIsNotNone(
            update_idx,
            "Expected a community.general.homebrew task with update_homebrew: true in roles/homebrew/tasks/main.yml",
        )
        self.assertIsNotNone(
            install_idx,
            "Expected a looping community.general.homebrew install task with name: '{{ item }}' in roles/homebrew/tasks/main.yml",
        )
        self.assertLessEqual(
            update_idx,
            install_idx,
            "Expected Homebrew update task to run before or on the same task as the looping install task",
        )


if __name__ == "__main__":
    unittest.main()
