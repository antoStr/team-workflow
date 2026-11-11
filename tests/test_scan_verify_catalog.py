"""Tests for repo scan, verify-docs, agents catalog, and frontend component skills."""
import isolate_home  # noqa: F401
import json
import os
import sys
import unittest

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import scan
import verify_docs
import library
import roles


class ScanVerifyCatalogTest(ScriptTest):
    def test_scan_detects_git_and_python_stack(self):
        self.write("app.py", "print('hello')\n")
        self.git("add", "app.py")
        self.git("commit", "-m", "initial commit")

        report = scan.scan_repository(self.root)
        self.assertTrue(report["git"]["is_git"])
        self.assertIn("Python", report["stack"]["languages"])
        self.assertEqual(report["git"]["modified_files"], 0)

    def test_scan_detects_frontend_components_in_package_json(self):
        pkg = {
            "dependencies": {
                "react": "^19.0.0",
                "next": "^15.0.0",
                "tailwindcss": "^3.4.0",
                "sonner": "^1.7.0",
                "vaul": "^1.1.0",
                "cmdk": "^1.0.0",
                "@base-ui-components/react": "^1.0.0",
                "@number-flow/react": "^0.3.0"
            }
        }
        self.write("package.json", json.dumps(pkg))
        report = scan.scan_repository(self.root)
        ui = report["stack"]["ui_components"]
        self.assertIn("sonner", ui)
        self.assertIn("vaul", ui)
        self.assertIn("cmdk", ui)
        self.assertIn("base-ui", ui)
        self.assertIn("number-flow", ui)

    def test_verify_docs_validates_memory(self):
        # Without docs, it reports missing files
        res = verify_docs.verify_documentation(self.root)
        self.assertFalse(res["passed"])
        self.assertTrue(any("INDEX.md" in issue for issue in res["issues"]))

        # Create memory docs
        self.init_memory()
        self.write("docs/memory/STATE.md", "# State\n\nAll good.\n")
        res2 = verify_docs.verify_documentation(self.root)
        self.assertTrue(res2["passed"])

    def test_library_search_finds_frontend_components(self):
        found = library.search(["shadcn", "sonner", "vaul"])
        ids = [e["id"] for e in found]
        self.assertIn("shadcn-ui", ids)
        self.assertIn("sonner-toast", ids)
        self.assertIn("vaul-drawer", ids)

    def test_design_engineer_role_exists(self):
        catalog = roles.catalog(self.root)
        self.assertIn("design-engineer", catalog)
        meta, body = roles.parse(roles.read(catalog["design-engineer"]))
        self.assertEqual(meta.get("mode"), "subagent")
        self.assertIn("shadcn/ui", meta.get("description", ""))


if __name__ == "__main__":
    unittest.main()
