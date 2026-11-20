"""Offline tests for the Neural Cortex Router, Project Genome Assimilation & Meta-Skill Evolution."""
import isolate_home  # noqa: F401
import json
import os
import sys
import unittest

from test_scripts import SCRIPTS, ScriptTest

sys.path.insert(0, SCRIPTS)
import autolearn  # noqa: E402
import cortex  # noqa: E402
import omniscience  # noqa: E402
import roles  # noqa: E402
import scan  # noqa: E402
import settings  # noqa: E402
import talk  # noqa: E402


class CortexTest(ScriptTest):
    def _write_hw(self, status="OK", cpu_temp=50, gpu_temp=48, ram_pct=40):
        hw_dir = settings.hardware_dir()
        os.makedirs(hw_dir, exist_ok=True)
        with open(os.path.join(hw_dir, "hardware_status.json"), "w", encoding="utf-8") as f:
            json.dump({
                "Status": status,
                "CPU": {"Temp_C": cpu_temp, "LoadPercent": 25},
                "GPU": {"Temp_C": gpu_temp},
                "RAM": {"PercentUsed": ram_pct},
            }, f)

    def test_perceive_resources_and_thermal_throttling(self):
        self._write_hw(status="OK", cpu_temp=55, gpu_temp=50, ram_pct=42)
        res_ok = cortex.perceive_resources(self.root, app="claude")
        self.assertEqual(res_ok["hardware_health"]["status"], "OK")
        self.assertEqual(res_ok["hardware_health"]["capacity_factor"], 1.0)
        self.assertEqual(res_ok["config"]["effective_max_agents"], 4)

        self._write_hw(status="CRITICAL", cpu_temp=92, gpu_temp=86, ram_pct=96)
        res_crit = cortex.perceive_resources(self.root, app="claude")
        self.assertEqual(res_crit["hardware_health"]["status"], "CRITICAL")
        self.assertEqual(res_crit["hardware_health"]["capacity_factor"], 0.35)
        self.assertEqual(res_crit["config"]["effective_max_agents"], 1)

        plan = cortex.route_and_orchestrate(
            "Architect and implement full oauth backend and frontend dashboard",
            root=self.root,
            app="claude",
        )
        self.assertEqual(len(plan["activated_neurons"]), 1)
        self.assertIn(plan["activated_neurons"][0]["effort"], ("low", "medium"))

    def test_neural_routing_activates_domain_roles_and_skills(self):
        self._write_hw(status="OK", cpu_temp=48, gpu_temp=45, ram_pct=35)
        self.write("package.json", json.dumps({
            "dependencies": {
                "react": "^19.0.0",
                "next": "^15.0.0",
                "tailwindcss": "^4.0.0",
                "@shadcn/ui": "^1.0.0",
            }
        }))
        fe_plan = cortex.route_and_orchestrate(
            "Build accessible responsive modal dialog UI component",
            root=self.root,
            app="agy",
            files=["src/components/Modal.tsx"],
        )
        fe_roles = [n["role"] for n in fe_plan["activated_neurons"]]
        self.assertTrue(any(r in fe_roles for r in ("frontend-dev", "design-engineer")))
        self.assertIn("visual-check", fe_plan["verification_gates"])
        self.assertTrue(any(s["id"] in ("shadcn-ui", "ui-styling", "frontend-design") for s in fe_plan["bound_skills"]))

        sec_plan = cortex.route_and_orchestrate(
            "Audit JWT authentication for SQL injection and XSS exploit vulnerabilities",
            root=self.root,
            app="claude",
        )
        sec_roles = [n["role"] for n in sec_plan["activated_neurons"]]
        self.assertIn("security-reviewer", sec_roles)
        self.assertEqual(sec_plan["topology"], "adversarial-gate")
        self.assertIn("gate", sec_plan["verification_gates"])

    def test_assimilate_project_knowledge_extracts_hubs_and_cochanges(self):
        self.write("core/engine.py", "def run():\n    return 1\n")
        self.write("api/routes.py", "from core.engine import run\n\ndef handle():\n    return run()\n")
        self.write("tests/test_engine.py", "import unittest\nfrom core.engine import run\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feat: initial engine and routes")

        self.write("core/engine.py", "def run():\n    return 2\n")
        self.write("api/routes.py", "from core.engine import run\n\ndef handle():\n    return run() + 1\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "fix: engine return contract")

        self.write("core/engine.py", "def run():\n    return 3\n")
        self.write("api/routes.py", "from core.engine import run\n\ndef handle():\n    return run() + 2\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "fix: prevent crash on routes engine call")

        knowledge = cortex.assimilate_project_knowledge(self.root)
        self.assertTrue(os.path.isfile(knowledge["knowledge_json"]))
        self.assertTrue(os.path.isfile(knowledge["genome_md"]))

        hubs = [h["file"] for h in knowledge["architectural_hubs"]]
        self.assertIn("core/engine.py", hubs)

        pairs = {(c["file_a"], c["file_b"]) for c in knowledge["co_change_clusters"]}
        self.assertIn(("api/routes.py", "core/engine.py"), pairs)

        hotspot_files = [h["file"] for h in knowledge["fragility_hotspots"]]
        self.assertIn("core/engine.py", hotspot_files)

        route = cortex.route_and_orchestrate("Modify engine.py logic", root=self.root, files=["core/engine.py"])
        self.assertTrue(len(route["co_change_alerts"]) >= 1)

    def test_evolve_skills_synthesizes_meta_and_learned_skills(self):
        self.write("auth.py", "def login():\n    return True\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "init auth")

        autolearn.record_learning(
            root=self.root,
            title="Validate JWT expiry strictly",
            trigger="Expired tokens accepted when exp claim missing",
            anti_pattern="jwt.decode without require=['exp']",
            solution="Always enforce options={'require': ['exp', 'sub']}",
            applies_to=["backend-dev", "auth.py"],
            category="security",
        )
        m1 = talk.post("auth-hardening", "pentester", "Missing exp validation on JWT", kind="challenge", to="backend-dev", cwd=self.root)
        talk.post("auth-hardening", "pentester", "Approved after enforcing exp claim check", kind="verdict", re_id=m1["id"], cwd=self.root)

        evolved = cortex.evolve_skills(self.root)
        ids = {s["id"] for s in evolved["synthesized"]}
        self.assertIn("team-meta-cortex", ids)
        self.assertIn("project-security-guard", ids)

        learned = cortex.load_learned_skills(self.root)
        self.assertIn("team-meta-cortex", learned)
        self.assertIn("project-security-guard", learned)

        plan = cortex.route_and_orchestrate("Harden auth.py JWT login", root=self.root, files=["auth.py"])
        self.assertTrue(len(plan["learned_skills_triggered"]) >= 1)

        out = self.run_script("tw.py", "questions", "--app", "claude", "--task", "auth", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        qdata = json.loads(out.stdout)
        skill_labels = [
            o["label"]
            for c in qdata["calls"] if c["step"] == "skills"
            for q in c["questions"]
            for o in q["options"]
        ]
        self.assertTrue(any(s in skill_labels for s in ("team-meta-cortex", "project-security-guard")))

    def test_hebbian_feedback_updates_synaptic_weights(self):
        w1 = cortex.record_feedback(
            root=self.root,
            outcome="pass",
            roles_used=["design-engineer"],
            skills_used=["shadcn-ui"],
            task_text="Build accessible React UI card",
        )
        self.assertGreater(w1["roles"]["design-engineer"], 0.0)
        self.assertGreater(w1["skills"]["shadcn-ui"], 0.0)
        self.assertEqual(w1["stats"]["passes"], 1)

        w2 = cortex.record_feedback(
            root=self.root,
            outcome="fail",
            roles_used=["backend-dev"],
            skills_used=["legacy-skill"],
            task_text="Fix backend API crash",
        )
        self.assertLess(w2["roles"]["backend-dev"], 0.0)
        self.assertGreater(w2["roles"]["tester"], 0.0)
        self.assertGreater(w2["roles"]["code-reviewer"], 0.0)
        self.assertEqual(w2["stats"]["failures"], 1)

    def test_vibecode_booster_extracts_ast_skeleton_and_reduces_cost(self):
        self.write(
            "service/billing.py",
            "class InvoiceEngine:\n    def compute_total(self, items):\n        return sum(items)\n\ndef apply_discount(total, pct):\n    return total * (1 - pct)\n",
        )
        self.write(
            "ui/CheckoutButton.tsx",
            "export function CheckoutButton({ total }: { total: number }) {\n  return null;\n}\n",
        )
        self.git("add", "-A")
        self.git("commit", "-qm", "feat: add billing service and checkout button")

        boost = cortex.vibecode_boost(
            "make checkout faster and fix discount bug",
            root=self.root,
            app="agy",
            files=["service/billing.py", "ui/CheckoutButton.tsx"],
        )
        booster = boost["agent_booster"]
        directive_ids = [d["id"] for d in booster["directives"]]
        self.assertEqual(
            directive_ids,
            ["caveman-telemetry", "ponytail-yagni", "karpathy-surgical", "context-mode-diet"],
        )
        self.assertGreaterEqual(boost["cost_optimization"]["total_estimated_cost_savings_pct"], 50)
        skel_by_file = {item["file"]: item["symbols"] for item in booster["skeleton_map"]}
        self.assertIn("service/billing.py", skel_by_file)
        self.assertTrue(any("InvoiceEngine" in s and "L1:" in s for s in skel_by_file["service/billing.py"]))
        self.assertTrue(any("apply_discount" in s and "L5:" in s for s in skel_by_file["service/billing.py"]))
        self.assertIn("ui/CheckoutButton.tsx", skel_by_file)
        self.assertTrue(any("CheckoutButton" in s and "L1:" in s for s in skel_by_file["ui/CheckoutButton.tsx"]))
        self.assertTrue(len(boost["expanded_briefs"]) >= 1)
        self.assertIn("AST Symbol Skeleton", boost["expanded_briefs"][0]["brief_text"])
        arsenal_ids = {t["id"] for t in boost["vibecoding_arsenal"]["tools"]}
        self.assertTrue({"caveman", "ponytail", "context-mode", "serena", "repomix", "task-master", "magic-21st"} <= arsenal_ids)

        out = self.run_script("tw.py", "cortex", "boost", "make", "checkout", "faster", "--json", cwd=self.root)
        self.assertEqual(out.returncode, 0, out.stderr)
        cli_boost = json.loads(out.stdout)
        self.assertGreaterEqual(cli_boost["cost_optimization"]["total_estimated_cost_savings_pct"], 50)

    def test_tw_cortex_cli_commands(self):
        self.write("app.py", "def main():\n    return 0\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feat: add app")

        for sub_args in (
            ["cortex", "status", "--json"],
            ["cortex", "assimilate", "--json"],
            ["cortex", "evolve", "--json"],
            ["cortex", "feedback", "--outcome", "pass", "--roles", "backend-dev,tester", "--json"],
            ["cortex", "route", "Fix", "backend", "API", "--json"],
        ):
            out = self.run_script("tw.py", *sub_args, cwd=self.root)
            self.assertEqual(out.returncode, 0, f"{sub_args} failed: {out.stderr}")
            parsed = json.loads(out.stdout)
            self.assertIsInstance(parsed, dict)

    def test_scan_auto_assimilates_and_evolves_without_dirtying_git(self):
        self.write("svc/main.py", "def run():\n    return 1\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feat: add svc")

        report = scan.scan_repository(self.root)
        self.assertTrue(report["git"]["is_clean"])
        self.assertIn("cortex", report)
        self.assertTrue(report["cortex"]["vibecode_shield"])
        self.assertIn("team-meta-cortex", report["cortex"]["learned_skills"])
        self.assertTrue(os.path.isfile(os.path.join(self.root, ".team-workflow", ".gitignore")))
        self.assertTrue(os.path.isfile(os.path.join(self.root, ".team-workflow", "project_knowledge.json")))
        # Repeated scan sees clean git status because .team-workflow is gitignored
        report2 = scan.scan_repository(self.root)
        self.assertEqual(report2["git"]["modified_files"], 0)

    def test_native_roles_include_vibecode_booster_shield(self):
        _, body = roles.load("backend-dev")
        self.assertIn("## Vibecode Booster & Cost Shield", body)
        self.assertIn("Caveman telemetry", body)
        self.assertIn("Ponytail YAGNI", body)

    def test_prompt_command_injects_booster_and_answers_cortex_zero_token(self):
        self.write("app.py", "def login():\n    return True\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "feat: login")

        out_team = self.run_script("prompt_command.py", hook={"prompt": "/team build login API", "cwd": self.root})
        self.assertEqual(out_team.returncode, 0, out_team.stderr)
        payload = json.loads(out_team.stdout)
        ctx = payload["hookSpecificOutput"]["additionalContext"]
        self.assertIn("[VIBECODE AGENT BOOSTER", ctx)

        out_cmd = self.run_script("prompt_command.py", hook={"prompt": "/team:cortex status --json", "cwd": self.root})
        self.assertEqual(out_cmd.returncode, 0, out_cmd.stderr)
        blocked = json.loads(out_cmd.stdout)
        self.assertEqual(blocked["decision"], "block")
        self.assertIn("resources", blocked["reason"])

    def test_omniscient_environment_sensor_detects_missing_env_keys_safely(self):
        self.write(".env.example", "DATABASE_URL=postgres://example\nJWT_SECRET=changeme\nSTRIPE_KEY=sk_test_x\n")
        self.write(".env", "DATABASE_URL=postgres://real-secret-value-not-leaked\n")
        env = omniscience.sense_environment(self.root)
        self.assertEqual(env["missing_env_keys"], ["JWT_SECRET", "STRIPE_KEY"])
        self.assertFalse(env["healthy"])
        self.assertNotIn("real-secret-value-not-leaked", json.dumps(env))

    def test_shadow_spec_synthesizes_unwritten_invariants_and_signatures(self):
        self.write("payments.py", "def charge_card(user_id, amount_cents, currency='usd'):\n    return True\n")
        spec = omniscience.synthesize_shadow_spec(
            "fix checkout payment auth bug",
            root=self.root,
            files=["payments.py"],
            domains=["backend", "security", "database"],
        )
        joined = "\n".join(spec["invariants"])
        self.assertIn("RLS", joined)
        self.assertIn("idempotent", joined)
        self.assertTrue(any("charge_card(user_id, amount_cents, currency)" in s for s in spec["preserved_signatures"]))

    def test_anti_tamper_shield_catches_test_deletion_and_silent_except(self):
        diff = """diff --git a/tests/test_auth.py b/tests/test_auth.py
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -1,4 +1,4 @@
 def test_token():
-    assert validate_token(expired) is False
+    @unittest.skip("temp")
     pass
diff --git a/app/api.py b/app/api.py
--- a/app/api.py
+++ b/app/api.py
@@ -1,2 +1,7 @@
 try:
     fetch_user()
+except Exception:
+    pass
+POLICY = "CREATE POLICY all_ok ON orders USING (true);"
"""
        res = omniscience.audit_anti_tamper(self.root, diff_text=diff)
        self.assertFalse(res["passed"])
        kinds = {v["kind"] for v in res["violations"]}
        self.assertIn("test_assertion_tampering", kinds)
        self.assertIn("silent_exception_swallow", kinds)
        self.assertIn("security_guard_weakening", kinds)

    def test_ast_contract_simulator_catches_breaking_signature_changes(self):
        before = "def compute(order_id, tax=0.2):\n    return order_id\n\ndef legacy():\n    return 1\n"
        after = "def compute(order_id, tax, currency):\n    return order_id\n"
        res = omniscience.check_ast_contracts(before_source=before, after_source=after, file_label="billing.py")
        self.assertFalse(res["ok"])
        reasons = [b["reason"] for b in res["breaking_changes"]]
        self.assertTrue(any("Required arguments increased" in r for r in reasons))
        self.assertTrue(any("Public symbol removed" in r for r in reasons))

    def test_circuit_breaker_trips_on_repeated_error_fingerprint(self):
        err1 = "AssertionError at C:/repo/app.py:42 ptr=0x7ffe1234 expected 200 got 500"
        err2 = "AssertionError at C:/repo/app.py:49 ptr=0xdeadbeef expected 200 got 500"
        s1 = omniscience.record_attempt_and_check_circuit(self.root, command="pytest", error_text=err1)
        self.assertFalse(s1["tripped"])
        self.assertEqual(s1["state"], "CLOSED")

        s2 = omniscience.record_attempt_and_check_circuit(self.root, command="pytest", error_text=err2)
        self.assertTrue(s2["tripped"])
        self.assertEqual(s2["state"], "OPEN")
        self.assertIn("CIRCUIT OPEN", s2["counterfactual_prescription"])

        s3 = omniscience.record_attempt_and_check_circuit(self.root, command="pytest", reset=True)
        self.assertFalse(s3["tripped"])
        self.assertEqual(s3["state"], "CLOSED")

    def test_darwin_godel_role_mutation_evolves_project_agent_override(self):
        w = cortex.record_feedback(
            root=self.root,
            outcome="fail",
            roles_used=["backend-dev"],
            skills_used=["rules-python"],
            task_text="fix order schema",
            notes="Changed required arg count without updating caller",
        )
        self.assertTrue(w.get("mutated_roles"))
        override_path = os.path.join(self.root, ".team-workflow", "agents", "backend-dev.md")
        self.assertTrue(os.path.isfile(override_path))
        _, body = roles.load("backend-dev", self.root)
        self.assertIn("## Darwin-Godel Learned Mutations (Project TextGrad)", body)
        self.assertIn("Changed required arg count without updating caller", body)


if __name__ == "__main__":
    unittest.main()
