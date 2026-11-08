#!/usr/bin/env python3
"""Copy the team-workflow plugin into an agy (Antigravity CLI) plugins folder.

The repository itself is an agy plugin: the usual install is
`agy plugin install https://github.com/antoStr/team-workflow` (or a local path). Use this script
for one project only (--workspace) or to copy just the files agy needs.

agy discovers plugins in its customization roots: ~/.gemini/config/plugins/<name>/ for every
project, <repository>/.agents/plugins/<name>/ for one. agy loads skills/<name>/SKILL.md (the
workflows are skills, so both harnesses read them), rules/, hooks.json and plugin.json.

agy does not offer a plugin's agents as subagents: it takes them from ~/.gemini/config/agents/
(or <repository>/.agents/agents/), in its own format. sync_agents() writes the roles there
(roles.py); the agy hook refreshes them at every session; --agents-only does it by hand.

    python3 install_agy.py [--workspace REPOSITORY | --dest DIR] [--agents-only]
"""
import argparse
import json
import os
import shutil
import subprocess

import roles
from common import utf8_output

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


def agents_dir(workspace=None):
    return roles.native_dir("agy", workspace)


def sync_agents(dest, config=None):
    """Write the enabled roles as agy subagents into dest; returns the roles written."""
    return roles.sync("agy", config=config, dest=dest)["written"]


def safe_rmtree(path):
    if not os.path.exists(path):
        return

    def on_error(func, p, excinfo):
        import stat
        try:
            os.chmod(p, stat.S_IWRITE)
            func(p)
        except Exception:
            pass

    try:
        shutil.rmtree(path, onerror=on_error)
    except Exception:
        pass


def build(dest):
    if os.path.exists(dest):
        if not ours(dest):
            raise SystemExit(f"{dest} exists and is not a team-workflow plugin: not touching it")
        safe_rmtree(dest)  # a previous build of this same plugin
    shutil.copytree(os.path.join(PLUGIN, "skills"), os.path.join(dest, "skills"),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    # In the plugin, remove skills/team so agy does NOT register duplicate /team-workflow:team
    plugin_team = os.path.join(dest, "skills", "team")
    if os.path.isdir(plugin_team):
        shutil.rmtree(plugin_team, ignore_errors=True)
    # Ensure team-workflow folder does not contain SKILL.md so it does not create duplicate slash command
    tw_skill = os.path.join(dest, "skills", "team-workflow", "SKILL.md")
    if os.path.isfile(tw_skill):
        try:
            os.remove(tw_skill)
        except OSError:
            pass
    # Install top-level /team skill directly into agy's global skills directory (~/.gemini/config/skills/team)
    top_team_dir = os.path.join(os.path.expanduser("~"), ".gemini", "config", "skills", "team")
    try:
        shutil.rmtree(top_team_dir, ignore_errors=True)
        shutil.copytree(os.path.join(PLUGIN, "skills", "team"), top_team_dir)
    except Exception:
        pass
    shutil.copytree(os.path.join(PLUGIN, "rules"), os.path.join(dest, "rules"))
    for name in ("plugin.json", "hooks.json"):  # agy's manifest and hooks, kept at the repo root
        shutil.copy(os.path.join(PLUGIN, name), dest)


def main():
    utf8_output()
    ap = argparse.ArgumentParser(description="Build the team-workflow plugin for agy.")
    where = ap.add_mutually_exclusive_group()
    where.add_argument("--workspace", help="install for one repository (.agents/plugins)")
    where.add_argument("--dest", help="explicit destination folder")
    ap.add_argument("--agents-only", action="store_true", help="only write the agy subagents")
    args = ap.parse_args()
    if not args.dest:  # an explicit --dest is a bare build: the subagents stay untouched
        target = agents_dir(args.workspace)
        changed = sync_agents(target)
        print(f"agy subagents in {target}: {len(changed)} written or refreshed")
    if args.agents_only:
        return
    dest = args.dest or (os.path.join(args.workspace, ".agents", "plugins", NAME) if args.workspace
                         else os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins", NAME))
    build(os.path.abspath(dest))
    print(f"agy plugin written to {dest}")
    if shutil.which("agy"):
        out = subprocess.run(["agy", "plugin", "validate", dest], capture_output=True, text=True, encoding="utf-8", errors="replace")
        print((out.stdout + out.stderr).strip() or "agy plugin validate: no output")


if __name__ == "__main__":
    main()
