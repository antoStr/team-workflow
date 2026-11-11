import json
import os
import shutil
import tempfile
import unittest

# Import the new modules
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills", "team", "scripts")))

import components_cli
import patch_bridge
import preview
import talk
import visual_check


class TestV230Features(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_components_cli_list_and_add(self):
        # 1. Test listing
        items = components_cli.list_components()
        self.assertGreater(len(items), 5)
        ids = [i["id"] for i in items]
        self.assertIn("cmdk", ids)
        self.assertIn("sonner", ids)
        self.assertIn("number-flow", ids)
        self.assertIn("vaul", ids)

        # 2. Test adding component
        dest = os.path.join(self.tmp, "components", "cmdk")
        res = components_cli.add_component("cmdk", dest_dir=dest, root=self.tmp)
        self.assertTrue(res["ok"])
        self.assertTrue(os.path.isfile(os.path.join(dest, "cmdk.js")))
        self.assertTrue(os.path.isfile(os.path.join(dest, "cmdk.css")))

    def test_patch_bridge_apply_and_dry_run(self):
        # Create a sample file
        target_file = os.path.join(self.tmp, "sample.txt")
        with open(target_file, "w", encoding="utf-8") as f:
            f.write("alpha\nbeta\ngamma\n")

        diff = """--- a/sample.txt
+++ b/sample.txt
@@ -1,3 +1,3 @@
 alpha
-beta
+beta_modified
 gamma
"""
        # Dry-run
        dry_res = patch_bridge.apply_patch(diff, root=self.tmp, dry_run=True)
        self.assertTrue(dry_res["ok"])
        with open(target_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "alpha\nbeta\ngamma\n")

        # Apply
        res = patch_bridge.apply_patch(diff, root=self.tmp, dry_run=False)
        self.assertTrue(res["ok"])
        with open(target_file, "r", encoding="utf-8") as f:
            self.assertEqual(f.read(), "alpha\nbeta_modified\ngamma\n")

    def test_visual_check_audit(self):
        # Create valid responsive HTML & CSS
        html_file = os.path.join(self.tmp, "index.html")
        with open(html_file, "w", encoding="utf-8") as f:
            f.write("""<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <h1>Valid Title</h1>
  <button aria-label="Action">Click</button>
</body>
</html>""")

        css_file = os.path.join(self.tmp, "style.css")
        with open(css_file, "w", encoding="utf-8") as f:
            f.write("""
@media (prefers-reduced-motion: reduce) {
  * { animation: none !important; }
}
@media (max-width: 768px) {
  body { font-size: 14px; }
}
""")

        res = visual_check.run_visual_check(root=self.tmp)
        self.assertTrue(res["ok"])
        self.assertEqual(res["pages_audited"], 1)
        self.assertEqual(res["high_severity"], 0)

    def test_preview_port_and_detection(self):
        # Create mock project
        index = os.path.join(self.tmp, "index.html")
        with open(index, "w", encoding="utf-8") as f:
            f.write("<html><body>Test Preview</body></html>")

        cmd = preview.detect_command(self.tmp, 8085)
        self.assertIn("http.server", " ".join(cmd))
        self.assertIn("8085", " ".join(cmd))

    def test_talk_close_topic(self):
        topic = "test-close-topic"
        # Post a question
        talk.post(topic, "tester", "Is this ready?", kind="question", cwd=self.tmp)
        msgs = talk.read(topic, cwd=self.tmp)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(len(talk.open_threads(msgs)), 1)

        # Close topic
        res = talk.close_topic(topic, summary="Verified and closed", from_role="orchestrator", cwd=self.tmp)
        self.assertTrue(res["ok"])
        self.assertEqual(res["resolved_threads"], 1)

        # Check open threads are now 0
        msgs_after = talk.read(topic, cwd=self.tmp)
        self.assertEqual(len(talk.open_threads(msgs_after)), 0)
        last_msg = msgs_after[-1]
        self.assertEqual(last_msg["kind"], "decision")
        self.assertIn("CHANNEL CLOSED", last_msg["text"])


if __name__ == "__main__":
    unittest.main()
