"""Offline tests for Codex: install, agents in config.toml, MCP servers, uninstall."""
import isolate_home  # noqa: F401  (first: a throwaway home for the whole run)
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from test_scripts import SCRIPTS

sys.path.insert(0, SCRIPTS)
import addons  # noqa: E402
import install_codex  # noqa: E402
import roles  # noqa: E402

try:
    import tomllib
except ImportError:  # Python < 3.11: the TOML checks are skipped
    tomllib = None


class CodexTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = tmp.name
        self.repo = os.path.join(self.home, "repo")
        os.makedirs(self.repo)
        subprocess.run(["git", "init", "-q", self.repo], check=True)
        patcher = mock.patch.dict(os.environ, {"HOME": self.home, "USERPROFILE": self.home,
                                               "CODEX_HOME": os.path.join(self.home, ".codex")})
        patcher.start()
        self.addCleanup(patcher.stop)

    def conf(self, *parts):
        return os.path.join(self.repo, ".codex", *parts)

    def read(self, path):
        with open(path, encoding="utf-8") as f:
            return f.read()

    def test_install_writes_skills_agents_config_and_instructions_and_uninstall_removes_them(self):
        os.makedirs(self.conf())
        with open(self.conf("config.toml"), "w", encoding="utf-8") as f:
            f.write('model = "gpt-x"\n\n[agents.tester]\ndescription = "mine"\nconfig_file = "agents/mine.toml"\n')
        r = install_codex.install(self.repo)
        self.assertGreater(r["skills"], 20)
        skill = self.read(self.conf("skills", "team-workflow-agents", "SKILL.md"))
        self.assertIn("name: team-workflow-agents", skill)
        self.assertIn("tw.py\" agents", skill)  # answered by tw.py, the model only shows it
        self.assertTrue(os.path.isfile(self.conf("skills", "team-workflow", "SKILL.md")))
        self.assertTrue(os.path.isfile(self.conf("agents", "architect.toml")))
        config = self.read(self.conf("config.toml"))
        self.assertEqual(config.count("[agents.tester]"), 1)  # the user's own stays the only one
        self.assertIn("[agents.architect]", config)
        self.assertIn("--app codex", self.read(os.path.join(self.repo, "AGENTS.md")))
        if tomllib:
            parsed = tomllib.loads(config)
            self.assertEqual(parsed["agents"]["tester"]["description"], "mine")
            agent = tomllib.loads(self.read(self.conf("agents", "architect.toml")))
            self.assertEqual(agent["sandbox_mode"], "read-only")  # architect has no Edit or Write
            self.assertIn("## Team talk", agent["developer_instructions"])
        install_codex.uninstall(self.repo)
        self.assertFalse(os.path.exists(self.conf("skills", "team-workflow-agents")))
        self.assertFalse(os.path.exists(self.conf("agents", "architect.toml")))
        config = self.read(self.conf("config.toml"))
        self.assertNotIn("[agents.architect]", config)
        self.assertIn('[agents.tester]\ndescription = "mine"', config)
        self.assertFalse(os.path.exists(os.path.join(self.repo, "AGENTS.md")))

    def test_mcp_servers_go_in_our_block_and_the_users_are_left_alone(self):
        os.makedirs(install_codex.config_dir())
        conf = os.path.join(install_codex.config_dir(), "config.toml")
        with open(conf, "w", encoding="utf-8") as f:
            f.write('[mcp_servers.playwright]\ncommand = "mine"\n')
        ok, log = install_codex.set_mcp("context7", ["npx", "-y", "@upstash/context7-mcp"])
        self.assertTrue(ok, log)
        ok, log = install_codex.set_mcp("playwright", ["npx", "x"])
        self.assertIn("left as it is", log)
        self.assertEqual(install_codex.mcp_servers(), {"playwright", "context7"})
        if tomllib:
            self.assertEqual(tomllib.loads(self.read(conf))["mcp_servers"]["context7"]["args"],
                             ["-y", "@upstash/context7-mcp"])
        install_codex.set_mcp("context7", None)
        self.assertEqual(install_codex.mcp_servers(), {"playwright"})
        self.assertEqual(addons.codex_kind(addons.CATALOG["serena"]), "mcp")
        self.assertEqual(addons.codex_kind(addons.CATALOG["impeccable"]), "skills")

    def test_session_start_in_codex_names_its_skills_and_agents(self):
        out = subprocess.run([sys.executable, os.path.join(SCRIPTS, "session_start.py"), "--text",
                              "--app", "codex"], cwd=self.repo, capture_output=True, text=True,
                             encoding="utf-8", env=os.environ)
        self.assertIn("$team-workflow-<name>", out.stdout)
        self.assertIn("options --app codex", out.stdout)

    def test_roles_table_and_native_text_include_codex(self):
        self.assertIn("codex", roles.APPS)
        meta, body = roles.load("tester")
        text = roles.native_text("codex", "tester", meta, body,
                                 {"type": "custom", "model": "gpt-6-astra", "effort": "high"})
        self.assertIn('model = "gpt-6-astra"', text)
        self.assertIn('model_reasoning_effort = "high"', text)
        self.assertTrue(roles.ours(text))


if __name__ == "__main__":
    unittest.main()
