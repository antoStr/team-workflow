#!/usr/bin/env python3
"""Repository scanner and stack profiler for team-workflow.

Analyzes repository structure, git status, detected languages, frameworks,
frontend UI components stack, and project documentation/memory health.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import brain
import roles
import settings


def repo_root():
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
        )
        return out.stdout.strip() if out.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def git_info(root):
    if not root or not os.path.isdir(os.path.join(root, ".git")):
        return {"is_git": False}
    info = {"is_git": True}
    try:
        branch = subprocess.run(
            ["git", "-C", root, "branch", "--show-current"],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        info["branch"] = branch or "detached"
        
        status = subprocess.run(
            ["git", "-C", root, "status", "--porcelain", "-uno"],
            capture_output=True, text=True, timeout=30
        ).stdout.strip().splitlines()
        info["modified_files"] = len(status)
        info["is_clean"] = len(status) == 0
        
        last_commit = subprocess.run(
            ["git", "-C", root, "log", "-1", "--format=%h - %s (%cr)"],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()
        info["last_commit"] = last_commit
    except Exception as e:
        info["error"] = str(e)
    return info


def detect_stack(root):
    stack = {
        "languages": [],
        "frameworks": [],
        "ui_components": [],
        "testing": [],
        "package_managers": []
    }
    if not root:
        return stack

    # 1. Check package.json
    pkg_path = os.path.join(root, "package.json")
    if os.path.isfile(pkg_path):
        stack["languages"].append("JavaScript/TypeScript")
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                pkg = json.load(f)
            deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
            
            # Frameworks
            if "next" in deps:
                stack["frameworks"].append(f"Next.js ({deps.get('next')})")
            elif "react" in deps:
                stack["frameworks"].append(f"React ({deps.get('react')})")
            if "vue" in deps:
                stack["frameworks"].append("Vue.js")
            if "svelte" in deps:
                stack["frameworks"].append("Svelte")
            if "tailwindcss" in deps:
                stack["frameworks"].append("Tailwind CSS")

            # UI components and primitives
            ui_libs = [
                ("shadcn", "@shadcn/ui"),
                ("base-ui", "@base-ui-components/react"),
                ("radix", "@radix-ui/react-"),
                ("sonner", "sonner"),
                ("vaul", "vaul"),
                ("cmdk", "cmdk"),
                ("number-flow", "@number-flow/react"),
                ("magic-ui", "magicui"),
                ("framer-motion", "framer-motion"),
                ("motion", "motion"),
                ("lucide", "lucide-react")
            ]
            for label, pattern in ui_libs:
                found = any(k.startswith(pattern) or k == pattern for k in deps)
                if found:
                    stack["ui_components"].append(label)

            # Testing
            for test_tool in ("playwright", "@playwright/test", "vitest", "jest", "cypress"):
                if test_tool in deps:
                    stack["testing"].append(test_tool)
        except Exception:
            pass

    # 2. Check Python
    py_files = ["pyproject.toml", "requirements.txt", "Pipfile", "setup.py", "pytest.ini"]
    has_py = any(os.path.isfile(os.path.join(root, f)) for f in py_files) or any(
        f.endswith(".py") for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))
    )
    if has_py:
        stack["languages"].append("Python")
        if os.path.isfile(os.path.join(root, "pytest.ini")) or os.path.isdir(os.path.join(root, "tests")):
            stack["testing"].append("pytest")

    # 3. Check Rust, Go, .NET
    if os.path.isfile(os.path.join(root, "Cargo.toml")):
        stack["languages"].append("Rust")
    if os.path.isfile(os.path.join(root, "go.mod")):
        stack["languages"].append("Go")
    if any(f.endswith(".csproj") or f.endswith(".sln") for f in os.listdir(root)):
        stack["languages"].append("C# / .NET")

    return stack


def check_docs_memory(root):
    memory = {
        "index_md": False,
        "state_md": False,
        "state_last_modified": None,
        "brain_vault": False,
        "brain_nodes": 0,
        "active_vaccines": 0
    }
    if not root:
        return memory

    index_path = os.path.join(root, "docs", "memory", "INDEX.md")
    if not os.path.isfile(index_path):
        index_path = os.path.join(root, "docs", "brain", "INDEX.md")
    memory["index_md"] = os.path.isfile(index_path)

    state_path = os.path.join(root, "docs", "memory", "STATE.md")
    if os.path.isfile(state_path):
        memory["state_md"] = True
        try:
            mtime = os.path.getmtime(state_path)
            import datetime
            memory["state_last_modified"] = datetime.datetime.fromtimestamp(mtime).isoformat()
        except Exception:
            pass

    vault_dir = os.path.join(root, "docs", "brain")
    if os.path.isdir(vault_dir):
        memory["brain_vault"] = True
        nodes_dir = os.path.join(vault_dir, "nodes")
        if os.path.isdir(nodes_dir):
            memory["brain_nodes"] = len([f for f in os.listdir(nodes_dir) if f.endswith(".md")])
        learn_dir = os.path.join(vault_dir, "learnings")
        if os.path.isdir(learn_dir):
            memory["active_vaccines"] = len([f for f in os.listdir(learn_dir) if f.startswith("learn-") and f.endswith(".md")])

    return memory


def scan_repository(root=None):
    root = root or repo_root() or os.getcwd()
    git = git_info(root)
    stack = detect_stack(root)
    memory = check_docs_memory(root)
    
    return {
        "root": root,
        "git": git,
        "stack": stack,
        "memory": memory
    }


def print_scan_report(report):
    print("=" * 60)
    print("🔍 REPOSITORY & ENVIRONMENT SCAN REPORT")
    print("=" * 60)
    print(f"📁 Path: {report['root']}")
    
    git = report["git"]
    if git.get("is_git"):
        clean_status = "Pulito (Clean)" if git.get("is_clean") else f"{git.get('modified_files')} file modificati"
        print(f"🌿 Git Branch: {git.get('branch')} | Stato: {clean_status}")
        print(f"📌 Ultimo Commit: {git.get('last_commit')}")
    else:
        print("⚠️ Non è una repository Git")

    stack = report["stack"]
    langs = ", ".join(stack["languages"]) or "Nessun linguaggio primario rilevato"
    fws = ", ".join(stack["frameworks"]) or "Nessun framework rilevato"
    ui = ", ".join(stack["ui_components"]) or "Nessuna libreria UI componente rilevata"
    test = ", ".join(stack["testing"]) or "Nessun framework test rilevato"

    print("\n🛠️ Tech Stack:")
    print(f"  • Linguaggi:  {langs}")
    print(f"  • Frameworks: {fws}")
    print(f"  • UI Stack:   {ui}")
    print(f"  • Test Suite: {test}")

    mem = report["memory"]
    print("\n🧠 Memory & Documentazione:")
    print(f"  • INDEX.md:        {'✅ Presente' if mem['index_md'] else '❌ Assente (crea con init_memory)'}")
    print(f"  • STATE.md:        {'✅ Presente' if mem['state_md'] else '❌ Assente'}" + (f" (aggiornato: {mem['state_last_modified']})" if mem['state_last_modified'] else ""))
    print(f"  • Brain Vault:     {'✅ Attivo' if mem['brain_vault'] else '❌ Inattivo'} ({mem['brain_nodes']} nodi mappati)")
    print(f"  • Vaccini Attivi:  🛡️ {mem['active_vaccines']} anti-pattern registrati")

    print("\n💡 Raccomandazioni:")
    if not mem["state_md"]:
        print("  - Genera docs/memory/STATE.md per tracciare lo stato del progetto.")
    if "JavaScript/TypeScript" in stack["languages"] and not stack["ui_components"]:
        print("  - Se sviluppi frontend, consulta `tw.py library search pick-ui-library shadcn-ui base-ui sonner` per un'architettura componenti moderna.")
    if git.get("modified_files", 0) > 0:
        print(f"  - Attenzione: ci sono {git.get('modified_files')} modifiche non committate nel working tree.")
    print("=" * 60)


def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description="Scan repository structure, stack and memory")
    parser.add_argument("--json", action="store_true", help="output JSON")
    parser.add_argument("--root", default=None, help="repository root")
    args = parser.parse_args(argv)

    report = scan_repository(args.root)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_scan_report(report)


if __name__ == "__main__":
    main()
