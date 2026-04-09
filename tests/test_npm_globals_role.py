import unittest
import yaml
from pathlib import Path


class TestNpmGlobalsRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.tasks_file = self.repo_root / "roles" / "npm_globals" / "tasks" / "main.yml"
        self.vars_file = self.repo_root / "group_vars" / "all.yml"

    def _load_tasks(self):
        self.assertTrue(self.tasks_file.is_file(), f"Expected tasks file to exist: {self.tasks_file}")
        tasks = yaml.safe_load(self.tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {self.tasks_file} to contain a YAML list")
        return tasks

    def test_required_npm_globals_declared_in_group_vars(self):
        self.assertTrue(self.vars_file.is_file())
        data = yaml.safe_load(self.vars_file.read_text(encoding="utf-8"))
        self.assertIsInstance(data, dict)

        packages = data.get("npm_global_packages")
        self.assertIsInstance(
            packages,
            list,
            "Expected npm_global_packages to be declared as a list in group_vars/all.yml",
        )

        for pkg in ("@socketsecurity/cli", "sfw"):
            with self.subTest(pkg=pkg):
                self.assertIn(pkg, packages)

        # The archived @githubnext/github-copilot-cli npm package must NOT be
        # installed here — Copilot CLI ships as the `copilot-cli` Homebrew
        # formula (installed via the homebrew role).
        self.assertNotIn(
            "@githubnext/github-copilot-cli",
            packages,
            "Copilot CLI must be installed via Homebrew formula "
            "`copilot-cli`, not the archived @githubnext npm package",
        )
        # Claude Code has its own official install script
        # (curl -fsSL https://claude.ai/install.sh | bash) — it must NOT
        # be installed as a pnpm global.
        self.assertNotIn(
            "@anthropic-ai/claude-code",
            packages,
            "Claude Code must be installed via its official install script, "
            "not as a pnpm global",
        )

    def test_claude_code_install_url_declared_in_group_vars(self):
        data = yaml.safe_load(self.vars_file.read_text(encoding="utf-8"))
        url = data.get("claude_code_install_url")
        self.assertIsInstance(
            url,
            str,
            "Expected claude_code_install_url to be declared in group_vars/all.yml",
        )
        self.assertEqual(
            url,
            "https://claude.ai/install.sh",
            "Expected claude_code_install_url to point at https://claude.ai/install.sh",
        )

    def test_claude_code_installed_via_official_install_script(self):
        """Claude Code ships via `curl -fsSL https://claude.ai/install.sh | bash`.

        Expect a shell task that runs this installer by referencing the
        `claude_code_install_url` group_var, guarded with `creates:` on the
        resulting binary path so re-runs are no-ops.
        """
        tasks = self._load_tasks()

        claude_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.shell" in task
            and "claude_code_install_url" in str(task["ansible.builtin.shell"])
        ]
        self.assertGreaterEqual(
            len(claude_tasks),
            1,
            "Expected an ansible.builtin.shell task that runs the Claude "
            "Code official install script (curl https://claude.ai/install.sh | bash)",
        )

        for task in claude_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                module_cfg = task["ansible.builtin.shell"]
                cmd_str = str(module_cfg)
                self.assertIn("curl", cmd_str)
                self.assertIn("-fsSL", cmd_str)

                # Must be guarded via `creates:` for idempotency.
                creates_value = None
                if isinstance(module_cfg, dict):
                    creates_value = module_cfg.get("creates")
                if not creates_value:
                    creates_value = (task.get("args") or {}).get("creates")
                self.assertTrue(
                    creates_value,
                    "Expected Claude Code install task to use `creates:` "
                    "for idempotency",
                )
                self.assertIn(
                    "claude",
                    str(creates_value),
                    "Expected `creates:` to point at the installed claude binary",
                )

    def test_copilot_cli_installed_via_homebrew_formula(self):
        data = yaml.safe_load(self.vars_file.read_text(encoding="utf-8"))
        formulae = data.get("homebrew_formulae") or []
        self.assertIn(
            "copilot-cli",
            formulae,
            "Expected `copilot-cli` Homebrew formula in homebrew_formulae "
            "(installs the GitHub Copilot CLI at /opt/homebrew/bin/copilot)",
        )

    def _install_tasks(self, tasks):
        return [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "pnpm" in str(task["ansible.builtin.command"])
            and "add" in str(task["ansible.builtin.command"])
            and "-g" in str(task["ansible.builtin.command"])
        ]

    def test_install_task_runs_pnpm_add_g_over_npm_global_packages(self):
        tasks = self._load_tasks()
        install_tasks = self._install_tasks(tasks)

        self.assertGreaterEqual(
            len(install_tasks),
            1,
            "Expected an ansible.builtin.command task running `pnpm add -g` "
            "over npm_global_packages",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cmd_str = str(task["ansible.builtin.command"])
                # pnpm is not on PATH during the run, use absolute path
                self.assertIn(
                    ".local/share/pnpm/pnpm",
                    cmd_str,
                    "Expected install task to use absolute path "
                    "~/.local/share/pnpm/pnpm since PATH isn't refreshed",
                )
                loop_key = next(
                    (key for key in ("loop", "with_items") if key in task),
                    None,
                )
                self.assertIsNotNone(
                    loop_key,
                    "Expected install task to loop over npm_global_packages",
                )
                self.assertIn(
                    "npm_global_packages",
                    str(task[loop_key]),
                    "Expected loop source to reference npm_global_packages",
                )
                self.assertIn(
                    "item",
                    cmd_str,
                    "Expected install command to reference {{ item }} from the loop",
                )

    def test_install_task_is_idempotent_via_precheck(self):
        """Re-runs must not reinstall packages that are already present.

        Either the install task has a `when:` guard referencing a previously
        registered pnpm list / presence check, or it uses `creates:`, or
        changed_when is wired to the command output so Ansible reports no
        change on re-runs.
        """
        tasks = self._load_tasks()
        install_tasks = self._install_tasks(tasks)
        self.assertGreaterEqual(len(install_tasks), 1)

        # There must be a preceding task that lists or probes installed
        # globals, registered for use by the install task's when guard.
        list_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "pnpm" in str(task["ansible.builtin.command"])
            and "list" in str(task["ansible.builtin.command"])
            and "-g" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(list_tasks),
            1,
            "Expected a preceding `pnpm list -g` task to probe installed "
            "global packages for idempotency",
        )

        register_names = {
            task.get("register")
            for task in list_tasks
            if task.get("register")
        }
        self.assertTrue(
            register_names,
            "Expected the pnpm list task to register its result",
        )

        for task in install_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                when_clause = str(task.get("when", ""))
                self.assertTrue(
                    any(reg in when_clause for reg in register_names),
                    "Expected install task to have a `when:` guard referencing "
                    "the registered pnpm list result",
                )
                # item must also appear in the guard so each loop iteration
                # is gated on whether that specific package is present.
                self.assertIn(
                    "item",
                    when_clause,
                    "Expected install task when-guard to be per-item, not global",
                )

    def test_install_task_best_effort_ignores_single_package_failure(self):
        tasks = self._load_tasks()
        for task in self._install_tasks(tasks):
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertIs(
                    task.get("ignore_errors"),
                    True,
                    "Expected install task to use ignore_errors: yes so a "
                    "single package failure doesn't block the rest",
                )

    def test_role_fails_clearly_when_pnpm_is_missing(self):
        """There must be a preflight step that stops the role with a clear
        error when ~/.local/share/pnpm/pnpm is missing. This must run before
        the install task so the failure is meaningful."""
        tasks = self._load_tasks()

        preflight_tasks = [
            (idx, task)
            for idx, task in enumerate(tasks)
            if isinstance(task, dict)
            and (
                "ansible.builtin.stat" in task
                or "ansible.builtin.assert" in task
                or "ansible.builtin.fail" in task
            )
        ]
        self.assertTrue(
            preflight_tasks,
            "Expected a preflight stat/assert/fail task to verify pnpm presence",
        )

        # Find the install task index
        install_idx = None
        for idx, task in enumerate(tasks):
            if isinstance(task, dict) and "ansible.builtin.command" in task:
                cmd = str(task["ansible.builtin.command"])
                if "pnpm" in cmd and "add" in cmd and "-g" in cmd:
                    install_idx = idx
                    break
        self.assertIsNotNone(install_idx)

        # There must be at least one assert/fail task referencing pnpm
        # that runs before the install task.
        guard_tasks = [
            (idx, task)
            for idx, task in preflight_tasks
            if (
                "ansible.builtin.assert" in task
                or "ansible.builtin.fail" in task
            )
            and "pnpm" in str(task).lower()
            and idx < install_idx
        ]
        self.assertTrue(
            guard_tasks,
            "Expected an assert/fail task referencing pnpm to run before the "
            "install task, providing a clear error message if pnpm is missing",
        )

        # The assert task should carry a human-readable fail_msg / msg.
        for _, task in guard_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task.get("ansible.builtin.assert") or task.get("ansible.builtin.fail")
                self.assertIsInstance(cfg, dict)
                msg_text = str(
                    cfg.get("fail_msg") or cfg.get("msg") or ""
                ).lower()
                self.assertIn(
                    "pnpm",
                    msg_text,
                    "Expected preflight failure message to mention pnpm",
                )
