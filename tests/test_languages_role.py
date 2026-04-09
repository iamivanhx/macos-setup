import unittest
import yaml
from pathlib import Path


class TestLanguagesRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.tasks_file = self.repo_root / "roles" / "languages" / "tasks" / "main.yml"
        self.vars_file = self.repo_root / "group_vars" / "all.yml"

    def _load_tasks(self):
        self.assertTrue(self.tasks_file.is_file(), f"Expected tasks file to exist: {self.tasks_file}")
        tasks = yaml.safe_load(self.tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {self.tasks_file} to contain a YAML list")
        return tasks

    def test_pnpm_installer_url_declared_in_group_vars(self):
        self.assertTrue(self.vars_file.is_file(), f"Expected group vars file to exist: {self.vars_file}")
        data = yaml.safe_load(self.vars_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict, f"Expected {self.vars_file} to contain a YAML mapping")

        url = data.get("pnpm_install_url")
        self.assertIsInstance(
            url,
            str,
            "Expected pnpm_install_url to be declared as a string in group_vars/all.yml",
        )
        self.assertEqual(
            url,
            "https://get.pnpm.io/install.sh",
            "Expected pnpm_install_url to point at https://get.pnpm.io/install.sh",
        )

    def test_installs_uv_via_community_general_homebrew(self):
        tasks = self._load_tasks()

        uv_install_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.homebrew" in task
            and isinstance(task["community.general.homebrew"], dict)
            and task["community.general.homebrew"].get("name") == "uv"
        ]

        self.assertGreaterEqual(
            len(uv_install_tasks),
            1,
            "Expected a community.general.homebrew task installing uv with name: uv",
        )

        for task in uv_install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                module_config = task["community.general.homebrew"]
                self.assertEqual(module_config.get("state"), "present")
                self.assertNotIn("ansible.builtin.shell", task)
                self.assertNotIn("ansible.builtin.command", task)


    def test_installs_pnpm_via_shell_using_standalone_installer(self):
        tasks = self._load_tasks()

        shell_tasks = [
            task
            for task in tasks
            if isinstance(task, dict) and "ansible.builtin.shell" in task
        ]

        pnpm_install_tasks = [
            task
            for task in shell_tasks
            if "pnpm_install_url" in str(task.get("ansible.builtin.shell", ""))
        ]

        self.assertGreaterEqual(
            len(pnpm_install_tasks),
            1,
            "Expected an ansible.builtin.shell task running the pnpm standalone "
            "installer by referencing pnpm_install_url",
        )

        for task in pnpm_install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cmd_str = str(task["ansible.builtin.shell"])
                self.assertIn(
                    "curl",
                    cmd_str,
                    "Expected pnpm install task to invoke curl to fetch the installer",
                )
                # Must be guarded so reruns are idempotent: either a `creates:`
                # arg on the shell module, or a preceding `command -v pnpm`
                # check whose result gates this task via `when:`.
                module_cfg = task["ansible.builtin.shell"]
                has_creates = (
                    isinstance(module_cfg, dict) and bool(module_cfg.get("creates"))
                ) or bool(task.get("args", {}).get("creates"))
                has_when_guard = "when" in task and "pnpm" in str(task["when"]).lower()
                self.assertTrue(
                    has_creates or has_when_guard,
                    "Expected pnpm install shell task to be idempotent via "
                    "`creates:` or a `when:` guard referencing a prior pnpm presence check",
                )

    def test_pnpm_install_runs_after_uv_install(self):
        tasks = self._load_tasks()

        uv_idx = None
        pnpm_idx = None
        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
            hb = task.get("community.general.homebrew")
            if isinstance(hb, dict) and hb.get("name") == "uv" and uv_idx is None:
                uv_idx = idx
            shell = task.get("ansible.builtin.shell")
            if shell and "pnpm_install_url" in str(shell) and pnpm_idx is None:
                pnpm_idx = idx

        self.assertIsNotNone(uv_idx, "Expected a uv install task")
        self.assertIsNotNone(pnpm_idx, "Expected a pnpm install shell task")
        self.assertLess(
            uv_idx,
            pnpm_idx,
            "Expected uv install to run before pnpm install (uv comes from Homebrew, "
            "pnpm bootstraps Node later in the role)",
        )


    def test_installs_node_lts_via_pnpm_env_use(self):
        tasks = self._load_tasks()

        node_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "pnpm" in str(task["ansible.builtin.command"])
            and "env" in str(task["ansible.builtin.command"])
            and "use" in str(task["ansible.builtin.command"])
            and "lts" in str(task["ansible.builtin.command"]).lower()
        ]

        self.assertGreaterEqual(
            len(node_tasks),
            1,
            "Expected an ansible.builtin.command task running `pnpm env use --global lts` "
            "to install Node LTS",
        )

        for task in node_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cmd_str = str(task["ansible.builtin.command"])
                self.assertIn(
                    "--global",
                    cmd_str,
                    "Expected pnpm env use to pass --global",
                )
                # pnpm is not on PATH when the role runs — must use absolute path
                self.assertIn(
                    ".local/share/pnpm/pnpm",
                    cmd_str,
                    "Expected Node install task to use the absolute path to pnpm "
                    "(~/.local/share/pnpm/pnpm) since PATH isn't refreshed mid-run",
                )

    def test_node_install_runs_after_pnpm_install(self):
        tasks = self._load_tasks()

        pnpm_idx = None
        node_idx = None
        for idx, task in enumerate(tasks):
            if not isinstance(task, dict):
                continue
            shell = task.get("ansible.builtin.shell")
            if shell and "pnpm_install_url" in str(shell) and pnpm_idx is None:
                pnpm_idx = idx
            cmd = str(task.get("ansible.builtin.command", ""))
            if "pnpm" in cmd and "env" in cmd and "lts" in cmd.lower() and node_idx is None:
                node_idx = idx

        self.assertIsNotNone(pnpm_idx)
        self.assertIsNotNone(node_idx)
        self.assertLess(
            pnpm_idx,
            node_idx,
            "Expected pnpm install to run before `pnpm env use --global lts`",
        )


    def test_verifies_uv_pnpm_node_versions_surface_failure(self):
        tasks = self._load_tasks()

        def verify_tasks_for(tool):
            return [
                task
                for task in tasks
                if isinstance(task, dict)
                and "ansible.builtin.command" in task
                and tool in str(task["ansible.builtin.command"])
                and "--version" in str(task["ansible.builtin.command"])
            ]

        for tool in ("uv", "pnpm", "node"):
            with self.subTest(tool=tool):
                found = verify_tasks_for(tool)
                self.assertGreaterEqual(
                    len(found),
                    1,
                    f"Expected a verification task running `{tool} --version`",
                )
                for task in found:
                    self.assertEqual(
                        task.get("changed_when"),
                        False,
                        f"Expected {tool} --version to set changed_when: false",
                    )
                    self.assertIsNot(
                        task.get("ignore_errors"),
                        True,
                        f"Expected {tool} --version to NOT ignore errors — "
                        "acceptance criterion requires failure to surface",
                    )
                    self.assertNotEqual(
                        task.get("failed_when"),
                        False,
                        f"Expected {tool} --version to let failures bubble up",
                    )


if __name__ == "__main__":
    unittest.main()
