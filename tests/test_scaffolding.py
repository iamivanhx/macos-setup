import configparser
import unittest
import yaml
from pathlib import Path


class TestAnsibleScaffolding(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]

    def test_ansible_cfg_defaults(self):
        ansible_cfg = self.repo_root / "ansible.cfg"

        self.assertTrue(ansible_cfg.exists(), "ansible.cfg should exist at the repository root")

        config = configparser.ConfigParser()
        config.read(ansible_cfg)

        self.assertIn("defaults", config)
        defaults = config["defaults"]
        self.assertEqual(defaults["connection"], "local")
        self.assertEqual(defaults["inventory"], "inventory/hosts.yml")
        self.assertEqual(defaults["roles_path"], "roles")
        self.assertEqual(defaults["interpreter_python"], "auto_silent")
        self.assertEqual(defaults["host_key_checking"], "False")


    def test_role_task_stubs_exist_with_debug_placeholders(self):
        repo_root = self.repo_root
        role_names = [
            "verify",
        ]

        for role_name in role_names:
            with self.subTest(role=role_name):
                role_dir = repo_root / "roles" / role_name
                tasks_file = role_dir / "tasks" / "main.yml"

                self.assertTrue(role_dir.is_dir(), f"Expected role directory to exist: {role_dir}")
                self.assertTrue(tasks_file.is_file(), f"Expected tasks file to exist: {tasks_file}")

                parsed = yaml.safe_load(tasks_file.read_text(encoding="utf-8"))
                self.assertIsInstance(parsed, list, f"Expected {tasks_file} to contain a YAML list")
                self.assertGreaterEqual(len(parsed), 1, f"Expected at least one task in {tasks_file}")

                debug_tasks = [
                    task
                    for task in parsed
                    if isinstance(task, dict) and "ansible.builtin.debug" in task
                ]
                self.assertGreaterEqual(
                    len(debug_tasks),
                    1,
                    f"Expected at least one ansible.builtin.debug task in {tasks_file}",
                )

                debug_config = debug_tasks[0]["ansible.builtin.debug"]
                self.assertIsInstance(
                    debug_config,
                    dict,
                    f"Expected ansible.builtin.debug configuration to be a mapping in {tasks_file}",
                )
                self.assertIn("msg", debug_config, f"Expected debug task to define msg in {tasks_file}")
                self.assertIn(
                    "implemented",
                    str(debug_config["msg"]).lower(),
                    f"Expected debug msg to contain 'implemented' in {tasks_file}",
                )

    def test_playbook_lists_all_roles_with_matching_tags_for_localhost(self):
        repo_root = self.repo_root
        playbook_file = repo_root / "playbook.yml"

        self.assertTrue(playbook_file.exists(), "playbook.yml should exist at the repository root")

        playbook = yaml.safe_load(playbook_file.read_text())

        self.assertIsInstance(playbook, list, "playbook.yml should parse to a list of plays")
        self.assertTrue(playbook, "playbook.yml should contain at least one play")

        first_play = playbook[0]
        self.assertIsInstance(first_play, dict, "the first play should be a mapping")
        self.assertEqual(first_play.get("hosts"), "localhost")

        roles = first_play.get("roles")
        self.assertIsInstance(roles, list, "the first play should define roles as a list")

        expected_roles = {
            "homebrew": "homebrew",
            "cask_apps": "cask_apps",
            "xcode": "xcode",
            "languages": "languages",
            "npm_globals": "npm_globals",
            "git_setup": "git_setup",
            "terminal": "terminal",
            "macos_defaults": "macos_defaults",
            "verify": "verify",
        }

        seen_roles = set()
        role_tags = {role: set() for role in expected_roles}

        for role_entry in roles:
            if isinstance(role_entry, str):
                role_name = role_entry
                tags = []
            elif isinstance(role_entry, dict):
                role_name = role_entry.get("role")
                tags_value = role_entry.get("tags", [])
                if isinstance(tags_value, str):
                    tags = [tags_value]
                else:
                    self.assertIsInstance(tags_value, list, "role tags should be a string or list")
                    tags = tags_value
            else:
                self.fail("each role entry should be a string or mapping")

            if role_name in expected_roles:
                seen_roles.add(role_name)
                role_tags[role_name].update(tags)

        self.assertTrue(
            set(expected_roles).issubset(seen_roles),
            f"playbook.yml should include all expected roles: {sorted(expected_roles)}",
        )

        for role_name, expected_tag in expected_roles.items():
            with self.subTest(role=role_name):
                self.assertIn(expected_tag, role_tags[role_name])

    def test_group_vars_all_defines_non_empty_package_lists(self):
        repo_root = self.repo_root
        group_vars_file = repo_root / "group_vars" / "all.yml"

        self.assertTrue(group_vars_file.exists(), "group_vars/all.yml should exist")

        group_vars = yaml.safe_load(group_vars_file.read_text())

        self.assertIsInstance(group_vars, dict, "group_vars/all.yml should parse to a mapping")

        for key in ("homebrew_formulae", "homebrew_casks", "npm_global_packages"):
            with self.subTest(key=key):
                self.assertIn(key, group_vars)
                self.assertIsInstance(group_vars[key], list, f"{key} should be a list")
                self.assertTrue(group_vars[key], f"{key} should be a non-empty list")

    def test_requirements_yml_includes_community_general_collection(self):
        repo_root = self.repo_root
        requirements_file = repo_root / "requirements.yml"

        self.assertTrue(requirements_file.exists(), "requirements.yml should exist at the repository root")

        requirements = yaml.safe_load(requirements_file.read_text())

        self.assertIsInstance(requirements, dict, "requirements.yml should parse to a mapping")
        self.assertIn("collections", requirements)

        collections = requirements["collections"]
        self.assertIsInstance(collections, list, "collections should be a list")
        self.assertTrue(
            any(
                isinstance(collection, dict) and collection.get("name") == "community.general"
                for collection in collections
            ),
            "requirements.yml should include the community.general collection",
        )

    def test_inventory_hosts_defines_localhost_local_connection(self):
        repo_root = self.repo_root
        inventory_file = repo_root / "inventory" / "hosts.yml"

        self.assertTrue(inventory_file.exists(), "inventory/hosts.yml should exist")

        inventory = yaml.safe_load(inventory_file.read_text())

        self.assertIsInstance(inventory, dict, "inventory/hosts.yml should parse to a mapping")
        self.assertIn("all", inventory)

        all_group = inventory["all"]
        self.assertIsInstance(all_group, dict, "all group should be a mapping")
        self.assertIn("hosts", all_group)

        hosts = all_group["hosts"]
        self.assertIsInstance(hosts, dict, "all.hosts should be a mapping")
        self.assertIn("localhost", hosts)

        localhost = hosts["localhost"]
        self.assertIsInstance(localhost, dict, "localhost entry should be a mapping")
        self.assertEqual(localhost.get("ansible_connection"), "local")


if __name__ == "__main__":
    unittest.main()
