#!/usr/bin/env python3
"""Build the team-workflow plugin for agy (Antigravity CLI) from this Claude Code plugin.

agy discovers plugins in its customization roots: ~/.gemini/config/plugins/<name>/ for every
project, <repository>/.agents/plugins/<name>/ for one. agy reads the Claude Code agents and
commands as they are (it turns commands into skills); what differs is the manifest, the rules
file and the hooks, whose events and payloads are agy's own (PreInvocation, Stop).

    python3 install_agy.py [--workspace REPOSITORY | --dest DIR]
"""
import argparse
import json
import os
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
PLUGIN = os.path.normpath(os.path.join(SKILL, "..", ".."))
NAME = "team-workflow"
RULES = """# team-workflow

- Project memory: read `docs/memory/INDEX.md` first, then `STATE.md` and the area card of your task.
- Before spawning agents, run the assignment wizard of the team-workflow skill (`WIZARD.md`).
- End every task with a report: done, verified with evidence, findings, decisions. Ask before
  applying anything the user did not request.
- When files change, update `docs/memory/STATE.md`.
- Answer in the language the user writes in.
"""
HOOKS = {NAME: {
    "PreInvocation": [{"type": "command", "timeout": 10,
                       "command": "python3 skills/team-workflow/scripts/session_start.py"}],
    "Stop": [{"type": "command", "timeout": 10,
              "command": "python3 skills/team-workflow/scripts/stop_check.py"}],
}}


def ours(dest):
    try:
        with open(os.path.join(dest, "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("name") == NAME
    except (OSError, ValueError):
        return False


def build(dest):
    if os.path.exists(dest):
        if not ours(dest):
            raise SystemExit(f"{dest} exists and is not a team-workflow plugin: not touching it")
        shutil.rmtree(dest)  # a previous build of this same plugin
    shutil.copytree(SKILL, os.path.join(dest, "skills", NAME),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for part in ("agents", "commands"):  # agy reads Claude Code agents and turns commands into skills
        shutil.copytree(os.path.join(PLUGIN, part), os.path.join(dest, part))
    os.makedirs(os.path.join(dest, "rules"))
    with open(os.path.join(dest, "rules", "AGENTS.md"), "w", encoding="utf-8") as f:
        f.write(RULES)
    with open(os.path.join(dest, "hooks.json"), "w", encoding="utf-8") as f:
        json.dump(HOOKS, f, indent=2)
    with open(os.path.join(dest, "plugin.json"), "w", encoding="utf-8") as f:
        json.dump({"name": NAME}, f, indent=2)


def main():
    ap = argparse.ArgumentParser(description="Build the team-workflow plugin for agy.")
    where = ap.add_mutually_exclusive_group()
    where.add_argument("--workspace", help="install for one repository (.agents/plugins)")
    where.add_argument("--dest", help="explicit destination folder")
    args = ap.parse_args()
    dest = args.dest or (os.path.join(args.workspace, ".agents", "plugins", NAME) if args.workspace
                         else os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins", NAME))
    build(os.path.abspath(dest))
    print(f"agy plugin written to {dest}")
    if shutil.which("agy"):
        out = subprocess.run(["agy", "plugin", "validate", dest], capture_output=True, text=True)
        print((out.stdout + out.stderr).strip() or "agy plugin validate: no output")


if __name__ == "__main__":
    main()
