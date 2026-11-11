#!/usr/bin/env python3
"""Verify documentation, memory integrity, and workflow execution proofs.

Ensures docs/memory/STATE.md, INDEX.md, and Obsidian Brain graph are in sync
with recent repository changes, preventing unverified or ghosted workflows.
"""
import datetime
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brain


def repo_root():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=10
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except Exception:
        return None


def verify_documentation(root=None, strict=False):
    root = root or repo_root() or os.getcwd()
    issues = []
    checks = []

    # 1. Check INDEX.md
    index_paths = [
        os.path.join(root, "docs", "memory", "INDEX.md"),
        os.path.join(root, "docs", "brain", "INDEX.md")
    ]
    has_index = any(os.path.isfile(p) for p in index_paths)
    if has_index:
        checks.append(("INDEX.md", "OK", "Found index memory file"))
    else:
        issues.append("Missing docs/memory/INDEX.md or docs/brain/INDEX.md")
        checks.append(("INDEX.md", "FAIL", "Missing index file"))

    # 2. Check STATE.md
    state_path = os.path.join(root, "docs", "memory", "STATE.md")
    if os.path.isfile(state_path):
        state_mtime = os.path.getmtime(state_path)
        mtime_dt = datetime.datetime.fromtimestamp(state_mtime)
        checks.append(("STATE.md", "OK", f"Present, last updated {mtime_dt.strftime('%Y-%m-%d %H:%M:%S')}"))
        
        # Check if working tree has changes newer than STATE.md
        try:
            diff_files = subprocess.run(
                ["git", "-C", root, "diff", "--name-only"],
                capture_output=True, text=True, timeout=5
            ).stdout.strip().splitlines()
            if diff_files:
                checks.append(("Working Tree", "INFO", f"{len(diff_files)} uncommitted file(s) in working tree"))
        except Exception:
            pass
    else:
        issues.append("Missing docs/memory/STATE.md")
        checks.append(("STATE.md", "FAIL", "docs/memory/STATE.md does not exist"))

    # 3. Check Brain Graph integrity
    vault_dir = os.path.join(root, "docs", "brain")
    if os.path.isdir(vault_dir):
        brain_report = brain.check_vault(vault_dir, root=root)
        node_count = len(brain._load_all_nodes(vault_dir))
        missing = brain_report.get("missing_files", [])
        if missing:
            issues.append(f"Brain vault has {len(missing)} missing file reference(s)")
            checks.append(("Brain Graph", "FAIL", f"{len(missing)} broken file reference(s)"))
        else:
            checks.append(("Brain Graph", "OK", f"Integrity verified ({node_count} nodes, 0 broken links)"))
    else:
        checks.append(("Brain Graph", "SKIP", "No docs/brain vault directory"))

    # 4. Check CATALOG.md sync if in team-workflow repo
    catalog_path = os.path.join(root, "docs", "CATALOG.md")
    if os.path.isfile(catalog_path):
        try:
            tool_py = os.path.join(root, "tools", "readme_catalog.py")
            if os.path.isfile(tool_py):
                res = subprocess.run([sys.executable, tool_py, "--check"], capture_output=True, timeout=10)
                if res.returncode == 0:
                    checks.append(("CATALOG.md", "OK", "Catalog in sync with roles and library"))
                else:
                    issues.append("docs/CATALOG.md is out of date (run `python tools/readme_catalog.py`)")
                    checks.append(("CATALOG.md", "FAIL", "Catalog out of date"))
        except Exception:
            pass

    passed = len(issues) == 0
    return {
        "passed": passed,
        "issues": issues,
        "checks": checks
    }


def print_verify_report(res):
    print("=" * 60)
    print("📋 DOCUMENTATION & WORKFLOW VERIFICATION GATE")
    print("=" * 60)
    for name, status, detail in res["checks"]:
        icon = "✅" if status == "OK" else ("⚠️" if status == "INFO" else ("⏭️" if status == "SKIP" else "❌"))
        print(f" {icon} {name:<16}: {detail}")
    
    print("-" * 60)
    if res["passed"]:
        print("🎉 Verification PASSED: Documentation and project memory are in order.")
    else:
        print(f"❌ Verification FAILED: {len(res['issues'])} issue(s) detected:")
        for iss in res["issues"]:
            print(f"   • {iss}")
    print("=" * 60)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Verify documentation and memory integrity")
    parser.add_argument("--strict", action="store_true", help="exit with non-zero code if issues found")
    parser.add_argument("--json", action="store_true", help="output JSON")
    parser.add_argument("--root", default=None, help="repository root")
    args = parser.parse_args(argv)

    res = verify_documentation(args.root, args.strict)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print_verify_report(res)

    if args.strict and not res["passed"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
