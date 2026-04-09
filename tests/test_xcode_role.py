import unittest
import yaml
from pathlib import Path


class TestXcodeRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_checks_for_existing_xcode_installation_via_stat(self):
        tasks_file = self.repo_root / "roles" / "xcode" / "tasks" / "main.yml"

        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML list")

        stat_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.stat" in task
            and isinstance(task["ansible.builtin.stat"], dict)
        ]

        self.assertGreaterEqual(
            len(stat_tasks),
            1,
            f"Expected at least one ansible.builtin.stat task in {tasks_file}",
        )

        matching_tasks = [
            task
            for task in stat_tasks
            if task["ansible.builtin.stat"].get("path") == "/Applications/Xcode.app"
        ]

        self.assertGreaterEqual(
            len(matching_tasks),
            1,
            "Expected at least one ansible.builtin.stat task to check /Applications/Xcode.app",
        )

        for task in matching_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertIn("register", task, "Expected stat task to define a register key")
                self.assertIsInstance(task["register"], str, "Expected register value to be a string")
                self.assertTrue(task["register"], "Expected register value to be a non-empty string")

    def _load_tasks(self):
        tasks_file = self.repo_root / "roles" / "xcode" / "tasks" / "main.yml"
        self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")
        tasks = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {tasks_file} to contain a YAML list")
        return tasks

    def test_checks_mas_account_signin_status(self):
        tasks = self._load_tasks()

        mas_account_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "mas account" in str(task["ansible.builtin.command"])
        ]

        self.assertGreaterEqual(
            len(mas_account_tasks),
            1,
            "Expected at least one ansible.builtin.command task running 'mas account'",
        )

        for task in mas_account_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertIn("register", task, "Expected mas account task to define a register key")
                self.assertEqual(
                    task.get("changed_when"),
                    False,
                    "Expected mas account check to set changed_when: false",
                )
                self.assertEqual(
                    task.get("failed_when"),
                    False,
                    "Expected mas account check to set failed_when: false so pause can handle it",
                )


    def test_pauses_when_user_not_signed_into_app_store(self):
        tasks = self._load_tasks()

        pause_tasks = [
            task
            for task in tasks
            if isinstance(task, dict) and "ansible.builtin.pause" in task
        ]

        self.assertGreaterEqual(
            len(pause_tasks),
            1,
            "Expected at least one ansible.builtin.pause task to handle HITL sign-in",
        )

        for task in pause_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                pause_config = task["ansible.builtin.pause"]
                self.assertIsInstance(pause_config, dict)
                self.assertIn(
                    "prompt",
                    pause_config,
                    "Expected pause task to include a prompt explaining sign-in",
                )
                self.assertIn(
                    "when",
                    task,
                    "Expected pause task to be conditional (when:) on sign-in status",
                )
                when_str = str(task["when"])
                self.assertIn(
                    "mas_account_result",
                    when_str,
                    "Expected pause 'when' clause to reference mas_account_result",
                )


    def test_installs_xcode_via_mas_with_app_store_id(self):
        tasks = self._load_tasks()

        install_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "mas install" in str(task["ansible.builtin.command"])
        ]

        self.assertGreaterEqual(
            len(install_tasks),
            1,
            "Expected at least one ansible.builtin.command task running 'mas install'",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cmd_str = str(task["ansible.builtin.command"])
                self.assertIn(
                    "xcode_app_store_id",
                    cmd_str,
                    "Expected mas install task to reference xcode_app_store_id variable",
                )
                self.assertTrue(
                    task.get("ignore_errors") is True or str(task.get("ignore_errors")).lower() == "yes",
                    "Expected mas install task to set ignore_errors: yes (best-effort)",
                )
                self.assertIn(
                    "when",
                    task,
                    "Expected mas install task to be conditional on Xcode not already installed",
                )
                self.assertIn(
                    "xcode_app_stat",
                    str(task["when"]),
                    "Expected mas install 'when' clause to reference xcode_app_stat",
                )

    def test_xcode_app_store_id_is_declared_in_group_vars(self):
        vars_file = self.repo_root / "group_vars" / "all.yml"
        self.assertTrue(vars_file.is_file())
        data = yaml.safe_load(vars_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)
        self.assertEqual(
            data.get("xcode_app_store_id"),
            497799835,
            "Expected xcode_app_store_id to be declared as 497799835 in group_vars/all.yml",
        )


    def test_accepts_xcode_license_with_sudo(self):
        tasks = self._load_tasks()

        license_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "xcodebuild" in str(task["ansible.builtin.command"])
            and "-license" in str(task["ansible.builtin.command"])
            and "accept" in str(task["ansible.builtin.command"])
        ]

        self.assertGreaterEqual(
            len(license_tasks),
            1,
            "Expected at least one task running 'xcodebuild -license accept'",
        )

        for task in license_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertTrue(
                    task.get("become") is True,
                    "Expected xcodebuild -license accept task to set become: true (needs sudo)",
                )

    def test_rechecks_mas_account_after_pause_and_fails_if_still_not_signed_in(self):
        tasks = self._load_tasks()

        # Find indices of the pause task and mas install task to assert ordering.
        pause_idx = None
        install_idx = None
        mas_account_task_indices = []

        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
            if "ansible.builtin.pause" in task:
                pause_idx = idx
            cmd = str(task.get("ansible.builtin.command", ""))
            if "mas account" in cmd:
                mas_account_task_indices.append(idx)
            if "mas install" in cmd:
                install_idx = idx

        self.assertIsNotNone(pause_idx, "Expected a pause task")
        self.assertIsNotNone(install_idx, "Expected a mas install task")

        # There must be at least two mas account checks (initial + post-pause recheck),
        # OR a single check that occurs after the pause and gates the install.
        post_pause_account_checks = [i for i in mas_account_task_indices if i > pause_idx]
        self.assertGreaterEqual(
            len(post_pause_account_checks),
            1,
            "Expected a mas account re-check AFTER the pause to verify sign-in before install",
        )

        # The install task must come after the post-pause recheck.
        self.assertTrue(
            any(i < install_idx for i in post_pause_account_checks),
            "Expected mas install to come after the post-pause mas account recheck",
        )

    def test_license_accept_task_is_idempotent_on_reruns(self):
        tasks = self._load_tasks()

        license_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "xcodebuild" in str(task["ansible.builtin.command"])
            and "-license" in str(task["ansible.builtin.command"])
        ]

        self.assertGreaterEqual(len(license_tasks), 1)

        for task in license_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                changed_when = str(task.get("changed_when", ""))
                # On a rerun against an already-accepted license, rc == 0 and
                # stdout is empty. changed_when must NOT include "rc == 0"
                # since that marks every rerun as changed (non-idempotent).
                self.assertNotIn(
                    "rc == 0",
                    changed_when,
                    "Expected changed_when to not rely on 'rc == 0' (breaks idempotency on reruns)",
                )

    def test_verifies_xcode_functional_via_xcodebuild_version(self):
        tasks = self._load_tasks()

        verify_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "xcodebuild" in str(task["ansible.builtin.command"])
            and "-version" in str(task["ansible.builtin.command"])
        ]

        self.assertGreaterEqual(
            len(verify_tasks),
            1,
            "Expected at least one task running 'xcodebuild -version' to verify installation",
        )

        for task in verify_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertEqual(
                    task.get("changed_when"),
                    False,
                    "Expected xcodebuild -version verification to set changed_when: false",
                )
                self.assertNotEqual(
                    task.get("failed_when"),
                    False,
                    "Expected verification task to fail when xcodebuild -version fails "
                    "(acceptance criterion: xcodebuild -version must succeed after role completes)",
                )
                self.assertIsNot(
                    task.get("ignore_errors"),
                    True,
                    "Expected verification task to NOT ignore errors — it must surface failure",
                )


if __name__ == "__main__":
    unittest.main()
