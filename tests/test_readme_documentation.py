import re
import unittest
from pathlib import Path


class TestReadmeDocumentation(unittest.TestCase):
    def setUp(self):
        self.repo_root = Path(__file__).resolve().parents[1]
        self.readme = self.repo_root / "README.md"
        self.license = self.repo_root / "LICENSE"

    def _readme_text(self):
        self.assertTrue(self.readme.is_file(), "README.md must exist at repo root")
        return self.readme.read_text(encoding="utf-8")

    def test_readme_has_required_top_level_sections(self):
        body = self._readme_text()
        required_sections = (
            "Overview",
            "Prerequisites",
            "Quick Start",
            "What Gets Installed",
            "Customization",
            "Running Specific Roles",
            "Re-running",
            "Troubleshooting",
            "Project Structure",
            "Adding New Tools",
        )
        for section in required_sections:
            with self.subTest(section=section):
                # Accept either "## Section" or "## Section — ..." forms.
                pattern = rf"(?m)^##\s+{re.escape(section)}\b"
                self.assertRegex(
                    body,
                    pattern,
                    f"Expected README to have a `## {section}` heading",
                )

    def test_quick_start_has_curl_bash_command_with_real_repo_url(self):
        body = self._readme_text()
        # Must include a curl | bash one-liner pointing at the raw bootstrap.sh
        # on the iamivanhx/macos-setup GitHub repo.
        self.assertRegex(
            body,
            r"curl\s+-fsSL\s+https://raw\.githubusercontent\.com/iamivanhx/macos-setup/[^/]+/bootstrap\.sh\s*\|\s*bash",
            "Expected a `curl -fsSL https://raw.githubusercontent.com/"
            "iamivanhx/macos-setup/<branch>/bootstrap.sh | bash` command",
        )

    def test_customization_documents_group_vars_all_yml(self):
        body = self._readme_text()
        self.assertIn(
            "group_vars/all.yml",
            body,
            "Expected README to reference group_vars/all.yml for customization",
        )
        for list_name in (
            "homebrew_formulae",
            "homebrew_casks",
            "npm_global_packages",
        ):
            with self.subTest(list=list_name):
                self.assertIn(
                    list_name,
                    body,
                    f"Expected README to mention the {list_name} list",
                )

    def test_running_specific_roles_documents_tags_usage(self):
        body = self._readme_text()
        # At least three concrete --tags examples must appear.
        tag_matches = re.findall(r"--tags\s+[a-z_]+", body)
        self.assertGreaterEqual(
            len(tag_matches),
            3,
            "Expected at least three concrete `--tags <role>` examples",
        )
        # Spot-check that a few known roles appear as tag examples.
        joined = " ".join(tag_matches)
        for role in ("homebrew", "git_setup", "verify"):
            with self.subTest(role=role):
                self.assertIn(
                    role,
                    joined,
                    f"Expected `--tags {role}` to appear as an example",
                )

    def test_troubleshooting_covers_four_scenarios(self):
        body = self._readme_text()
        # Find the Troubleshooting section and count sub-bullets/headings.
        match = re.search(
            r"##\s+Troubleshooting\b(.*?)(?=^##\s|\Z)",
            body,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(match, "Troubleshooting section not found")
        ts = match.group(1)
        # Accept either `### subheading` or `- **bold:**` style entries.
        subheading_count = len(re.findall(r"^###\s+\S", ts, flags=re.MULTILINE))
        bold_bullet_count = len(re.findall(r"^-\s+\*\*[^*]+\*\*", ts, flags=re.MULTILINE))
        self.assertGreaterEqual(
            subheading_count + bold_bullet_count,
            4,
            "Expected at least 4 troubleshooting scenarios "
            "(as `### heading` or `- **label**` entries)",
        )
        # Must mention the scenarios called out in the issue.
        for keyword in ("App Store", "pnpm", "logout", "Galaxy"):
            with self.subTest(keyword=keyword):
                self.assertIn(
                    keyword,
                    ts,
                    f"Expected troubleshooting to mention {keyword!r}",
                )

    def test_project_structure_tree_matches_actual_top_level_layout(self):
        body = self._readme_text()
        # Required top-level entries the tree must mention.
        for entry in (
            "bootstrap.sh",
            "playbook.yml",
            "ansible.cfg",
            "requirements.yml",
            "group_vars",
            "inventory",
            "roles",
            "tests",
        ):
            with self.subTest(entry=entry):
                self.assertIn(
                    entry,
                    body,
                    f"Expected project structure tree to mention {entry}",
                )

    def test_license_file_exists_and_is_mit(self):
        self.assertTrue(
            self.license.is_file(),
            "LICENSE file must exist at repo root",
        )
        text = self.license.read_text(encoding="utf-8")
        self.assertIn("MIT License", text)
        self.assertIn("Ivan E. Hernandez T.", text)
        self.assertIn("2026", text)
        # MIT boilerplate sanity check
        self.assertIn(
            "THE SOFTWARE IS PROVIDED \"AS IS\"",
            text,
            "Expected standard MIT warranty disclaimer",
        )
