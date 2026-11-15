"""The Claude Code hooks run through hooks/run-py.cmd, which finds a Python that really runs."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
WRAPPER = os.path.join(ROOT, "hooks", "run-py.cmd")


class HookWrapperTest(unittest.TestCase):
    def test_every_claude_hook_goes_through_the_wrapper(self):
        with open(os.path.join(ROOT, "hooks", "hooks.json"), encoding="utf-8") as f:
            hooks = json.load(f)["hooks"]
        commands = [h["command"] for groups in hooks.values() for g in groups for h in g["hooks"]]
        self.assertEqual(len(commands), 3)
        for cmd in commands:  # a fixed python3 is the Microsoft Store alias on many Windows PCs
            self.assertTrue(cmd.startswith('"${CLAUDE_PLUGIN_ROOT}/hooks/run-py.cmd" '), cmd)
            self.assertTrue(os.path.isfile(os.path.join(ROOT, "skills", "team", "scripts", cmd.split()[-1])))
        with open(WRAPPER, "rb") as f:
            self.assertNotIn(b"\r", f.read())  # the shell half breaks on CRLF

    @unittest.skipIf(os.name == "nt" or not shutil.which("bash"), "POSIX shell with fake commands on PATH")
    def test_skips_a_python3_that_does_not_run_and_keeps_the_hook_input(self):
        with tempfile.TemporaryDirectory() as bin_dir:
            fake = os.path.join(bin_dir, "python3")
            with open(fake, "w") as f:  # like the Store alias: prints and fails
                f.write("#!/bin/sh\necho 'Python was not found' >&2\nexit 49\n")
            os.chmod(fake, 0o755)
            os.symlink(sys.executable, os.path.join(bin_dir, "python"))
            out = subprocess.run([shutil.which("bash"), WRAPPER, "prompt_command.py"],
                                 input='{"prompt": "/team hardware --json"}', capture_output=True,
                                 text=True, env={"PATH": bin_dir, "HOME": os.environ["HOME"]}, timeout=120)
        self.assertEqual(out.returncode, 0, out.stderr)
        self.assertEqual(json.loads(out.stdout)["decision"], "block")  # the real Python read the input


if __name__ == "__main__":
    unittest.main()
