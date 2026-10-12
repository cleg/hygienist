"""Verify the secret boundary using only disposable dotenv fixtures."""
import contextlib
import importlib.util
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / "skills/hygienist/templates/helpers/env-keys.py"
SPEC = importlib.util.spec_from_file_location("env_keys", HELPER)
ENV_KEYS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ENV_KEYS)
CANARY = "secret-canary-7c41b3"


class EnvKeysTests(unittest.TestCase):
    def setUp(self):
        self.workspace = tempfile.TemporaryDirectory(prefix="hygienist-env-")
        self.addCleanup(self.workspace.cleanup)
        self.root = Path(self.workspace.name) / "project with spaces"
        self.root.mkdir()
        self.source = self.root / ".env"

    def run_helper(self, content=None, code=0, output=None):
        if content is not None:
            self.source.write_bytes(content.encode("utf-8"))
        before = self.source.read_bytes() if self.source.is_file() else None
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(HELPER), str(self.root)],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, code, result.stderr)
        self.assertNotIn(CANARY, result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        if code:
            self.assertEqual(result.stdout, "")
        if output is not None:
            self.assertEqual(result.stdout, output)
        if before is not None:
            self.assertEqual(self.source.read_bytes(), before)
        return result

    def test_assignments_export_comments_and_crlf(self):
        self.run_helper(
            f"# {CANARY}\r\n\r\n export FIRST = {CANARY} # comment\r\n"
            f"SECOND='{CANARY}'\r\nTHIRD=\"{CANARY}\" # comment\r\n"
            "EMPTY=\r\nREFERENCE=${FIRST}\r\nCOMMAND=$(touch /unused)\r\n",
            output="FIRST=\nSECOND=\nTHIRD=\nEMPTY=\nREFERENCE=\nCOMMAND=\n",
        )

    def test_multiline_cannot_inject_assignments(self):
        self.run_helper(
            f'MULTI="{CANARY}\nFAKE={CANARY}\n# {CANARY}\nlast"\n'
            f"SINGLE='first\nPHANTOM={CANARY}\nlast'\nREAL={CANARY}\n",
            output="MULTI=\nSINGLE=\nREAL=\n",
        )

    def test_escaped_quotes_and_backslashes(self):
        self.run_helper(
            'DOUBLE="escaped \\" quote"\nSINGLE=\'escaped \\\' quote\'\n'
            'BACKSLASH="ends with \\\\"\n',
            output="DOUBLE=\nSINGLE=\nBACKSLASH=\n",
        )

    def test_empty_and_comment_only(self):
        self.run_helper("", output="")
        self.run_helper(f" \t\n# {CANARY}\n", output="")

    def test_duplicate_reports_key_without_partial_output(self):
        result = self.run_helper(f"FIRST={CANARY}\nFIRST=other\n", code=1)
        self.assertIn("Duplicate key FIRST at line 2", result.stderr)

    def test_unsupported_syntax_and_unterminated_quotes(self):
        for invalid in (
            f"{CANARY}", f"bad-key={CANARY}", f'OTHER="{CANARY}',
            f'OTHER="closed" {CANARY}', f"OTHER={CANARY}\\",
            f"OTHER=prefix'{CANARY}'", f"OTHER={CANARY}\x00",
        ):
            with self.subTest(invalid=invalid):
                self.run_helper(f"FIRST={CANARY}\n{invalid}\n", code=1)

    def test_absent(self):
        self.run_helper(code=3)
        self.assertFalse(self.source.exists())

    def test_symlinks_including_broken_are_rejected(self):
        other = self.root / "private-input"
        other.write_text(f"OTHER={CANARY}\n")
        for destination in (other, self.root / "absent"):
            with self.subTest(destination=destination.name):
                self.source.symlink_to(destination)
                self.run_helper(code=1)
                self.source.unlink()
        self.assertEqual(other.read_text(), f"OTHER={CANARY}\n")

    def test_directory_and_fifo_are_rejected(self):
        self.source.mkdir()
        self.run_helper(code=1)
        self.source.rmdir()
        ENV_KEYS.os.mkfifo(self.source)
        self.run_helper(code=1)

    def test_invalid_encoding(self):
        self.source.write_bytes(b"FIRST=\xff\n")
        self.run_helper(code=1)

    def test_permission_error_is_redacted(self):
        self.source.write_text(f"FIRST={CANARY}\n")
        stdout, stderr = io.StringIO(), io.StringIO()
        with patch.object(ENV_KEYS.os, "open", side_effect=PermissionError(CANARY)):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = ENV_KEYS.main([str(HELPER), str(self.root)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertEqual(stderr.getvalue(), "Cannot read or decode .env.\n")

    def test_isolated_installed_helper_ignores_neighbor_modules(self):
        helpers = self.root / ".hygienist" / "helpers"
        helpers.mkdir(parents=True)
        installed = helpers / "env-keys.py"
        shutil.copyfile(HELPER, installed)
        marker = self.root / "neighbor-executed"
        (helpers / "re.py").write_text(
            f"open({str(marker)!r}, 'w').close()\nraise RuntimeError('import probe')\n"
        )
        self.source.write_text(f"TOKEN={CANARY}\n")
        # Disable site startup for the control so preloaded modules cannot mask
        # the vulnerable import lookup. All inputs/code here are synthetic.
        control = subprocess.run(
            [sys.executable, "-S", "-B", str(installed), str(self.root)],
            capture_output=True, text=True,
        )
        self.assertNotEqual(control.returncode, 0)
        self.assertTrue(marker.exists())
        marker.unlink()
        for options in (("-I", "-B"), ("-I", "-S", "-B")):
            with self.subTest(options=options):
                result = subprocess.run(
                    [sys.executable, *options, str(installed), str(self.root)],
                    capture_output=True, text=True,
                )
                self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "TOKEN=\n", ""))
                self.assertFalse(marker.exists())
                self.assertFalse(list(helpers.rglob("__pycache__")))
        self.assertEqual(self.source.read_text(), f"TOKEN={CANARY}\n")

    def test_isolation_ignores_pythonpath_startup_code(self):
        injected = self.root / "injected"
        injected.mkdir()
        marker = self.root / "startup-executed"
        (injected / "sitecustomize.py").write_text(f"open({str(marker)!r}, 'w').close()\n")
        self.source.write_text(f"TOKEN={CANARY}\n")
        environment = dict(os.environ, PYTHONPATH=str(injected), PYTHONPYCACHEPREFIX=str(self.root / "cache"))
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(HELPER), str(self.root)],
            env=environment, capture_output=True, text=True,
        )
        self.assertEqual((result.returncode, result.stdout, result.stderr), (0, "TOKEN=\n", ""))
        self.assertFalse(marker.exists())
        self.assertFalse((self.root / "cache").exists())

    def test_unsupported_platform_fails_before_reading_source(self):
        for missing in ("O_NOFOLLOW", "O_NONBLOCK"):
            with self.subTest(missing=missing):
                saved = getattr(ENV_KEYS.os, missing)
                delattr(ENV_KEYS.os, missing)
                try:
                    stdout, stderr = io.StringIO(), io.StringIO()
                    with patch.object(ENV_KEYS.os, "open") as opened:
                        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                            code = ENV_KEYS.main([str(HELPER), str(self.root)])
                    self.assertEqual(code, 1)
                    opened.assert_not_called()
                    self.assertEqual(stdout.getvalue(), "")
                    self.assertIn("Unsupported platform:", stderr.getvalue())
                    self.assertNotIn("Traceback", stderr.getvalue())
                finally:
                    setattr(ENV_KEYS.os, missing, saved)

    def test_invalid_invocation_and_missing_target(self):
        result = subprocess.run([sys.executable, "-I", "-B", str(HELPER)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, "")
        self.root.rmdir()
        self.run_helper(code=1)


if __name__ == "__main__":
    unittest.main()
