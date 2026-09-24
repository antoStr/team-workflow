#!/usr/bin/env python3
"""Copy the team-workflow plugin into an agy (Antigravity CLI) plugins folder.

The repository itself is an agy plugin: the usual install is
`agy plugin install https://github.com/antoStr/team-workflow` (or a local path). Use this script
for one project only (--workspace) or to copy just the files agy needs.

agy discovers plugins in its customization roots: ~/.gemini/config/plugins/<name>/ for every
project, <repository>/.agents/plugins/<name>/ for one. agy loads skills/<name>/SKILL.md (the
workflows are skills, so both harnesses read them), rules/, hooks.json and plugin.json; it does
not load agents/ as subagents, which are copied for workers to brief from.

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
    shutil.copytree(os.path.join(PLUGIN, "skills"), os.path.join(dest, "skills"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    for part in ("agents", "rules"):
        shutil.copytree(os.path.join(PLUGIN, part), os.path.join(dest, part))
    for name in ("plugin.json", "hooks.json"):  # agy's manifest and hooks, kept at the repo root
        shutil.copy(os.path.join(PLUGIN, name), dest)


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
