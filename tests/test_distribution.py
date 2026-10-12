"""Verify the self-contained skill directory is the distribution boundary."""
import os
import re
import stat
import unittest
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
SKILL = PROJECT / "skills/hygienist"
FILES = {
    "SKILL.md", "LICENSE", "agents/openai.yaml",
    "references/ADD-RULE.md", "references/EDIT-RULE.md", "references/CHECKER.md",
    "references/HELPERS.md", "references/INIT.md",
    "references/INSPECT.md", "references/RUN.md",
    "references/SAFETY.md", "references/checker-result.schema.json",
    "scripts/list-tasks.sh", "scripts/renumber-rules.sh",
    "templates/10-env-example.md", "templates/20-os-artifacts.md",
    "templates/30-conflict-markers.md", "templates/helpers/env-keys.py",
}


class DistributionTests(unittest.TestCase):
    def test_self_contained_runtime_bundle(self):
        self.assertTrue(SKILL.is_dir())
        self.assertFalse(SKILL.is_symlink())
        self.assertFalse(os.path.lexists(PROJECT / "SKILL.md"))
        expected_directories = {
            str(parent)
            for name in FILES
            for parent in Path(name).parents
            if parent != Path(".")
        }
        files, directories = set(), set()
        for base, dirnames, filenames in os.walk(SKILL, followlinks=False):
            for name in dirnames + filenames:
                path = Path(base) / name
                mode = path.lstat().st_mode
                relative = str(path.relative_to(SKILL))
                self.assertFalse(stat.S_ISLNK(mode), relative)
                if stat.S_ISDIR(mode):
                    directories.add(relative)
                else:
                    self.assertTrue(stat.S_ISREG(mode), relative)
                    files.add(relative)
        self.assertEqual(files, FILES)
        self.assertEqual(directories, expected_directories)
        self.assertEqual((SKILL / "LICENSE").read_bytes(),
                         (PROJECT / "LICENSE").read_bytes())
        for name in sorted(FILES):
            if not name.endswith(".md"):
                continue
            path = SKILL / name
            for link in re.findall(r"\]\(([^)]+)\)", path.read_text()):
                if "://" in link or link.startswith("#"):
                    continue
                target = (path.parent / link.split("#", 1)[0]).resolve()
                try:
                    target.relative_to(SKILL)
                except ValueError:
                    self.fail(f"Link escapes the skill directory: {name}: {link}")
                self.assertTrue(target.is_file(), (name, link))


if __name__ == "__main__":
    unittest.main()
