"""Filesystem tests for discovery and renumbering; no agent execution needed."""
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]


class RuleScriptTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="hygienist-rules-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name) / "project with spaces"
        self.rules = self.root / ".hygienist"
        self.rules.mkdir(parents=True)

    def run_script(self, name, success=True):
        result = subprocess.run(
            ["bash", str(PROJECT / "scripts" / name), str(self.root)],
            capture_output=True, text=True,
        )
        if success:
            self.assertEqual(result.returncode, 0, result.stderr)
            return json.loads(result.stdout)
        self.assertNotEqual(result.returncode, 0)
        return result

    def add(self, name, content):
        (self.rules / name).write_bytes(content)

    def test_requested_sequence_preserves_contents(self):
        for name, content in (("20-a.md", b"a"), ("25-b.md", b"b"), ("30-c.md", b"c")):
            self.add(name, content)
        report = self.run_script("renumber-rules.sh")
        self.assertEqual(report["tasks"], [".hygienist/10-a.md", ".hygienist/20-b.md", ".hygienist/30-c.md"])
        for name, content in (("10-a.md", b"a"), ("20-b.md", b"b"), ("30-c.md", b"c")):
            self.assertEqual((self.rules / name).read_bytes(), content)
        self.assertEqual(self.run_script("renumber-rules.sh")["renamed"], [])

    def test_overlapping_names_and_unrelated_files(self):
        self.add("20-same.md", b"first")
        self.add("30-same.md", b"second")
        self.add("README.md", b"keep")
        self.run_script("renumber-rules.sh")
        self.assertEqual((self.rules / "10-same.md").read_bytes(), b"first")
        self.assertEqual((self.rules / "20-same.md").read_bytes(), b"second")
        self.assertEqual((self.rules / "README.md").read_bytes(), b"keep")
        self.assertFalse(any(p.name.startswith(".renumber-") for p in self.rules.iterdir()))

    def test_more_than_nine_rules_discover_in_numeric_order(self):
        for index in range(12):
            self.add(f"{index + 20:02d}-rule-{index}.md", str(index).encode())
        report = self.run_script("renumber-rules.sh")
        self.assertEqual(report["tasks"], [f".hygienist/{(index + 1) * 10:02d}-rule-{index}.md" for index in range(12)])
        self.assertEqual(self.run_script("list-tasks.sh")["tasks"], report["tasks"])

    def test_existing_destination_is_never_overwritten(self):
        self.add("20-a.md", b"keep source")
        (self.rules / "10-a.md").mkdir()
        self.run_script("renumber-rules.sh", success=False)
        self.assertEqual((self.rules / "20-a.md").read_bytes(), b"keep source")
        self.assertTrue((self.rules / "10-a.md").is_dir())

    def test_broken_destination_symlink_is_never_overwritten(self):
        self.add("20-a.md", b"keep source")
        (self.rules / "10-a.md").symlink_to("missing")
        self.run_script("renumber-rules.sh", success=False)
        self.assertEqual((self.rules / "20-a.md").read_bytes(), b"keep source")
        self.assertEqual((self.rules / "10-a.md").readlink(), Path("missing"))

    def test_linked_rule_directory_and_equal_prefixes(self):
        fixtures = self.root / "fixtures"
        self.rules.rename(fixtures)
        self.rules.symlink_to("fixtures", target_is_directory=True)
        self.add("25-b.md", b"second")
        self.add("25-a.md", b"first")
        report = self.run_script("renumber-rules.sh")
        self.assertEqual(report["tasks"], [".hygienist/10-a.md", ".hygienist/20-b.md"])
        self.assertEqual((fixtures / "10-a.md").read_bytes(), b"first")
        self.assertTrue(self.rules.is_symlink())

    def test_empty_and_missing_rule_directory(self):
        self.assertEqual(self.run_script("renumber-rules.sh"), {"renamed": [], "tasks": []})
        self.rules.rmdir()
        self.run_script("renumber-rules.sh", success=False)


if __name__ == "__main__":
    unittest.main()
