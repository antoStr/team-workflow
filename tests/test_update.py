"""Offline tests for the version parsing in update_plugin.py."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "..", "skills", "team", "scripts"))
import update_plugin  # noqa: E402


class UpdateTest(unittest.TestCase):
    def test_latest_tag_compares_numbers_not_text(self):
        out = "a\trefs/tags/v0.9.0\nb\trefs/tags/v0.10.0\nc\trefs/tags/v0.4.0-rc1\nd\trefs/tags/other\n"
        self.assertEqual(update_plugin.latest_tag(out), "0.10.0")
        self.assertIsNone(update_plugin.latest_tag(""))

    def test_claude_version_from_plugin_list(self):
        out = "  ❯ other@x\n    Version: 9.9.9\n  ❯ team-workflow@team-workflow\n    Version: 0.3.1\n"
        self.assertEqual(update_plugin.claude_version(out), "0.3.1")
        self.assertIsNone(update_plugin.claude_version("  ❯ other@x\n    Version: 1.0.0\n"))

    def test_update_targets_the_installed_plugin_id(self):
        legacy = "  ❯ team-workflow@team-workflow\n    Version: 2.3.0\n"
        current = "  ❯ team@team\n    Version: 2.4.0\n"
        self.assertEqual(update_plugin.claude_ids(legacy), ("team-workflow", "team-workflow@team-workflow"))
        self.assertEqual(update_plugin.claude_ids(current), ("team", "team@team"))
        self.assertEqual(update_plugin.claude_ids(legacy + current), ("team", "team@team"))
        self.assertEqual(update_plugin.claude_ids(""), ("team", "team@team"))  # not installed yet


if __name__ == "__main__":
    unittest.main()


class AutoUpdateTest(unittest.TestCase):
    def test_starts_one_detached_update_per_window_and_only_when_newer(self):
        import tempfile
        from unittest import mock
        home = tempfile.mkdtemp()
        versions = {"own_version": "9.9.9", "agy_version": None, "payload_version": None}
        patches = [mock.patch.object(update_plugin, n, return_value=v) for n, v in versions.items()]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        with mock.patch.object(update_plugin, "latest_version", return_value="9.9.9"), \
                mock.patch.object(update_plugin.subprocess, "Popen") as popen:
            self.assertIsNone(update_plugin.auto_update(home=home))  # everything current
            popen.assert_not_called()
        # this plugin is current, OpenCode is behind: still update every app
        with mock.patch.object(update_plugin, "latest_version", return_value="9.9.9"), \
                mock.patch.object(update_plugin, "payload_version", side_effect=lambda h: "9.9.8" if h == "opencode" else None), \
                mock.patch.object(update_plugin.subprocess, "Popen") as popen:
            self.assertEqual(update_plugin.auto_update(home=home), "9.9.9")
            self.assertEqual(update_plugin.auto_update(home=home), "9.9.9")  # locked: no second start
            popen.assert_called_once()
            cmd, kwargs = popen.call_args
            self.assertEqual(cmd[0][1:], [os.path.abspath(update_plugin.__file__), "--harness", "all"])
            self.assertEqual(kwargs["cwd"], os.path.join(home, ".team-workflow"))
        with open(os.path.join(home, ".team-workflow", "update.log"), encoding="utf-8") as f:
            self.assertIn("auto update to 9.9.9", f.read())

    def test_only_team_prompts_trigger_the_check(self):
        import prompt_command
        for prompt in ("/team fix the login", "/team", "/team:doctor", " /team-workflow:talk read x"):
            self.assertTrue(prompt_command.TEAM_PROMPT.match(prompt), prompt)
        for prompt in ("/teams", "please /team", "/teamwork now", "fix the team page"):
            self.assertFalse(prompt_command.TEAM_PROMPT.match(prompt), prompt)

    def test_finds_the_opencode_and_codex_installs_where_their_installers_put_them(self):
        import install_codex
        import install_opencode
        self.assertEqual(update_plugin.opencode_payload(), install_opencode.payload_dir())
        self.assertEqual(update_plugin.codex_payload(), install_codex.payload_dir())

    def test_update_opencode_clears_read_only_git_temp_dirs(self):
        import stat
        import tempfile
        from unittest import mock

        with tempfile.TemporaryDirectory() as home:
            payload_dir = os.path.join(home, "payload")
            os.makedirs(payload_dir)
            with open(os.path.join(payload_dir, ".source"), "w", encoding="utf-8") as f:
                f.write("https://example.invalid/team-workflow\n")

            tmp = os.path.join(home, ".team-workflow", "opencode-update")
            stale_pack = os.path.join(tmp, ".git", "objects", "pack")
            os.makedirs(stale_pack)
            stale_file = os.path.join(stale_pack, "pack-stale.idx")
            with open(stale_file, "w", encoding="utf-8") as f:
                f.write("stale")
            os.chmod(stale_file, stat.S_IREAD)

            def fake_run(*cmd, **kwargs):
                if cmd[:2] == ("git", "clone"):
                    self.assertFalse(os.path.exists(tmp), "stale temp dir must be removed before git clone")
                    new_pack = os.path.join(cmd[-1], ".git", "objects", "pack")
                    os.makedirs(new_pack)
                    pack_file = os.path.join(new_pack, "pack-new.pack")
                    with open(pack_file, "w", encoding="utf-8") as f:
                        f.write("pack")
                    os.chmod(pack_file, stat.S_IREAD)
                    return 0, ""
                return 0, "installed"

            with mock.patch("os.path.expanduser", return_value=home), \
                    mock.patch.dict(update_plugin.PAYLOADS, {"opencode": (lambda: payload_dir, "install_opencode.py")}), \
                    mock.patch.object(update_plugin, "run", side_effect=fake_run) as run_mock:
                ok, out = update_plugin.update_opencode("opencode")
            self.assertTrue(ok, out)
            self.assertEqual(run_mock.call_count, 2)
            self.assertFalse(os.path.exists(tmp))


class UpdateLockTest(unittest.TestCase):
    """The auto update and `tw.py update` ran together and broke each other: one run at a time."""

    def test_one_update_at_a_time(self):
        import tempfile
        import time
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "update.running")
            self.assertEqual(update_plugin.hold_lock(path, wait=0), path)
            self.assertIsNone(update_plugin.hold_lock(path, wait=0))  # held: the second run gives up
            old = time.time() - 3600
            os.utime(path, (old, old))  # a run that crashed an hour ago
            self.assertEqual(update_plugin.hold_lock(path, wait=0), path)

    def test_main_releases_the_lock(self):
        import tempfile
        from unittest import mock
        with tempfile.TemporaryDirectory() as home:
            with mock.patch("os.path.expanduser", return_value=home), \
                    mock.patch.object(update_plugin, "fetch_latest", return_value="9.9.9"), \
                    mock.patch.object(update_plugin, "installed", return_value=None):
                with self.assertRaises(SystemExit) as done:
                    update_plugin.main(["--harness", "claude"])
            self.assertEqual(done.exception.code, 0)
            self.assertFalse(os.path.exists(os.path.join(home, ".team-workflow", "update.running")))
