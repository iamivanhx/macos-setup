import unittest
import yaml
from pathlib import Path


class TestGitSetupRole(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.tasks_file = self.repo_root / "roles" / "git_setup" / "tasks" / "main.yml"

    def _load_tasks(self):
        self.assertTrue(self.tasks_file.is_file(), f"Expected tasks file to exist: {self.tasks_file}")
        tasks = yaml.safe_load(self.tasks_file.read_text(encoding="utf-8"))
        self.assertIsInstance(tasks, list, f"Expected {self.tasks_file} to contain a YAML list")
        return tasks

    def _git_config_tasks(self, tasks, config_name):
        return [
            task
            for task in tasks
            if isinstance(task, dict)
            and "community.general.git_config" in task
            and isinstance(task["community.general.git_config"], dict)
            and task["community.general.git_config"].get("name") == config_name
        ]

    def test_sets_global_git_user_name_from_extra_var(self):
        tasks = self._load_tasks()
        matches = self._git_config_tasks(tasks, "user.name")
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected a community.general.git_config task setting user.name",
        )
        for task in matches:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["community.general.git_config"]
                self.assertEqual(cfg.get("scope"), "global")
                self.assertIn("git_user_name", str(cfg.get("value", "")))
                self.assertNotIn("ansible.builtin.command", task)
                self.assertNotIn("ansible.builtin.shell", task)

    def test_sets_global_git_user_email_from_extra_var(self):
        tasks = self._load_tasks()
        matches = self._git_config_tasks(tasks, "user.email")
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected a community.general.git_config task setting user.email",
        )
        for task in matches:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["community.general.git_config"]
                self.assertEqual(cfg.get("scope"), "global")
                self.assertIn("git_user_email", str(cfg.get("value", "")))

    def test_ensures_dot_ssh_dir_has_mode_700(self):
        tasks = self._load_tasks()
        matches = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.file" in task
            and isinstance(task["ansible.builtin.file"], dict)
            and task["ansible.builtin.file"].get("state") == "directory"
            and ".ssh" in str(task["ansible.builtin.file"].get("path", ""))
        ]
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected an ansible.builtin.file task creating ~/.ssh as a directory",
        )
        for task in matches:
            with self.subTest(task=task.get("name", "unnamed")):
                cfg = task["ansible.builtin.file"]
                self.assertIn(
                    str(cfg.get("mode")),
                    ("0700", "700", "u=rwx,go="),
                    "Expected ~/.ssh directory mode to be 0700",
                )

    def _find_indices(self, tasks, predicate):
        return [idx for idx, task in enumerate(tasks) if isinstance(task, dict) and predicate(task)]

    def test_stats_existing_ed25519_key(self):
        tasks = self._load_tasks()
        matches = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.stat" in task
            and isinstance(task["ansible.builtin.stat"], dict)
            and "id_ed25519" in str(task["ansible.builtin.stat"].get("path", ""))
            and not str(task["ansible.builtin.stat"].get("path", "")).endswith(".pub")
        ]
        self.assertGreaterEqual(
            len(matches),
            1,
            "Expected an ansible.builtin.stat task probing ~/.ssh/id_ed25519",
        )
        for task in matches:
            with self.subTest(task=task.get("name", "unnamed")):
                self.assertIn("register", task)
                self.assertTrue(task["register"])

    def test_pauses_to_confirm_overwrite_when_key_exists(self):
        tasks = self._load_tasks()
        pause_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.pause" in task
            and "ssh" in str(task["ansible.builtin.pause"]).lower()
        ]
        self.assertGreaterEqual(
            len(pause_tasks),
            1,
            "Expected an ansible.builtin.pause prompting the user when an "
            "SSH key already exists",
        )
        for task in pause_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                when_clause = str(task.get("when", ""))
                self.assertIn(
                    "stat.exists",
                    when_clause,
                    "Expected pause to be gated on the stat result showing the key exists",
                )
                self.assertIn("register", task, "Expected pause to register user's answer")

    def _command_tokens(self, task):
        """Return a flat list of argv-style tokens whether the command module
        uses `argv:` list form or the plain string form."""
        cmd = task.get("ansible.builtin.command")
        if isinstance(cmd, dict) and "argv" in cmd:
            return [str(tok) for tok in cmd["argv"]]
        return str(cmd).split()

    def test_generates_ed25519_key_when_missing_or_overwrite(self):
        tasks = self._load_tasks()
        keygen_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "ssh-keygen" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(keygen_tasks),
            1,
            "Expected an ansible.builtin.command task running ssh-keygen",
        )
        for task in keygen_tasks:
            with self.subTest(task=task.get("name", "unnamed")):
                tokens = self._command_tokens(task)
                self.assertIn("-t", tokens)
                self.assertIn("ed25519", tokens)
                self.assertTrue(
                    any("id_ed25519" in tok for tok in tokens),
                    "Expected ssh-keygen to target id_ed25519",
                )
                self.assertTrue(
                    any("git_user_email" in tok for tok in tokens),
                    "Expected ssh-keygen comment to reference git_user_email",
                )
                # Passphrase flag must be empty string for automation.
                # In argv form this is the pair ["-N", ""]; in string form
                # the literal `-N ""` must appear.
                if isinstance(task["ansible.builtin.command"], dict):
                    self.assertIn("-N", tokens)
                    n_idx = tokens.index("-N")
                    self.assertEqual(
                        tokens[n_idx + 1],
                        "",
                        "Expected -N to be followed by an empty string passphrase",
                    )
                else:
                    self.assertIn(
                        '-N ""',
                        str(task["ansible.builtin.command"]).replace("'", '"'),
                    )
                # Must be gated on absence of key OR explicit overwrite choice.
                when_clause = str(task.get("when", ""))
                self.assertTrue(
                    "not" in when_clause and "stat.exists" in when_clause,
                    "Expected keygen to be gated on the key not existing (with "
                    "optional overwrite escape hatch)",
                )
                # When the key does NOT exist, the overwrite-choice variable
                # is never registered (pause is skipped). The when clause
                # must not raise on an undefined var — either it uses
                # `is defined` guard or defaults the whole mapping.
                self.assertTrue(
                    "is defined" in when_clause or "default({}" in when_clause.replace(" ", ""),
                    "Expected keygen when-clause to guard against "
                    "ssh_key_overwrite_choice being undefined (first-run case)",
                )

    def test_enforces_ssh_key_file_permissions(self):
        tasks = self._load_tasks()
        file_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.file" in task
            and isinstance(task["ansible.builtin.file"], dict)
        ]

        private_tasks = [
            t for t in file_tasks
            if "id_ed25519" in str(t["ansible.builtin.file"].get("path", ""))
            and not str(t["ansible.builtin.file"].get("path", "")).endswith(".pub")
            and t["ansible.builtin.file"].get("state") != "absent"
            and t["ansible.builtin.file"].get("mode") is not None
        ]
        public_tasks = [
            t for t in file_tasks
            if str(t["ansible.builtin.file"].get("path", "")).endswith("id_ed25519.pub")
            and t["ansible.builtin.file"].get("state") != "absent"
            and t["ansible.builtin.file"].get("mode") is not None
        ]

        self.assertGreaterEqual(
            len(private_tasks),
            1,
            "Expected a file task setting mode on the private SSH key",
        )
        self.assertGreaterEqual(
            len(public_tasks),
            1,
            "Expected a file task setting mode on the public SSH key",
        )

        for task in private_tasks:
            with self.subTest(task=task.get("name", "unnamed"), kind="private"):
                self.assertIn(
                    str(task["ansible.builtin.file"].get("mode")),
                    ("0600", "600", "u=rw,go="),
                    "Expected private key mode 0600",
                )

        for task in public_tasks:
            with self.subTest(task=task.get("name", "unnamed"), kind="public"):
                self.assertIn(
                    str(task["ansible.builtin.file"].get("mode")),
                    ("0644", "644", "u=rw,go=r"),
                    "Expected public key mode 0644",
                )

    def test_adds_ssh_key_to_agent(self):
        tasks = self._load_tasks()
        ssh_add_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "ssh-add" in str(task["ansible.builtin.command"])
            and "id_ed25519" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(ssh_add_tasks),
            1,
            "Expected an ansible.builtin.command task running ssh-add on the SSH key",
        )

    def test_checks_gh_auth_status_then_pauses_and_uploads_key(self):
        tasks = self._load_tasks()

        # A `gh auth status` probe must run, tolerant of failure, registered.
        auth_status_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "gh auth status" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(auth_status_tasks),
            1,
            "Expected a `gh auth status` probe task",
        )
        for task in auth_status_tasks:
            with self.subTest(task=task.get("name", "unnamed"), stage="probe"):
                self.assertIn("register", task)
                self.assertIs(
                    task.get("failed_when"),
                    False,
                    "Expected gh auth status to tolerate non-zero exit for the probe",
                )
                self.assertEqual(task.get("changed_when"), False)

        # A pause task must prompt the user to run `gh auth login`
        # when the probe reported not authenticated.
        gh_pause_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.pause" in task
            and "gh auth login" in str(task["ansible.builtin.pause"]).lower()
        ]
        self.assertGreaterEqual(
            len(gh_pause_tasks),
            1,
            "Expected a pause task prompting the user to run `gh auth login`",
        )
        for task in gh_pause_tasks:
            with self.subTest(task=task.get("name", "unnamed"), stage="pause"):
                when_clause = str(task.get("when", ""))
                self.assertIn(
                    "rc",
                    when_clause,
                    "Expected gh auth pause to be gated on the probe's rc != 0",
                )

        # After the pause there must be a re-check of gh auth status.
        self.assertGreaterEqual(
            len(auth_status_tasks),
            2,
            "Expected a second `gh auth status` recheck task after the pause",
        )

        # And a failing task if still unauthenticated.
        gh_fail_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.fail" in task
            and "gh" in str(task["ansible.builtin.fail"]).lower()
        ]
        self.assertGreaterEqual(
            len(gh_fail_tasks),
            1,
            "Expected an ansible.builtin.fail task for still-unauthenticated gh",
        )

        # And finally a `gh ssh-key add` task referencing the public key.
        gh_key_add_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.command" in task
            and "gh ssh-key add" in str(task["ansible.builtin.command"])
            and "id_ed25519.pub" in str(task["ansible.builtin.command"])
        ]
        self.assertGreaterEqual(
            len(gh_key_add_tasks),
            1,
            "Expected a `gh ssh-key add` task uploading the public key",
        )

    def test_displays_public_key_at_end(self):
        tasks = self._load_tasks()

        # Public key content must be read first (slurp) then displayed.
        slurp_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.slurp" in task
            and isinstance(task["ansible.builtin.slurp"], dict)
            and "id_ed25519.pub" in str(task["ansible.builtin.slurp"].get("src", ""))
        ]
        self.assertGreaterEqual(
            len(slurp_tasks),
            1,
            "Expected an ansible.builtin.slurp task reading id_ed25519.pub",
        )
        for task in slurp_tasks:
            self.assertIn("register", task)

        # And a debug task that displays it.
        debug_tasks = [
            task
            for task in tasks
            if isinstance(task, dict)
            and "ansible.builtin.debug" in task
            and isinstance(task["ansible.builtin.debug"], dict)
        ]
        pubkey_debug = [
            t for t in debug_tasks
            if "b64decode" in str(t["ansible.builtin.debug"]) or "pub" in str(t["ansible.builtin.debug"]).lower()
        ]
        self.assertGreaterEqual(
            len(pubkey_debug),
            1,
            "Expected a debug task displaying the decoded public key contents",
        )
