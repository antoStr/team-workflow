#!/usr/bin/env python3
"""Copy the team-workflow plugin into an agy (Antigravity CLI) plugins folder.

The repository itself is an agy plugin: the usual install is
`agy plugin install https://github.com/antoStr/team-workflow` (or a local path). Use this script
for one project only (--workspace) or to copy just the files agy needs.

agy discovers plugins in its customization roots: ~/.gemini/config/plugins/<name>/ for every
project, <repository>/.agents/plugins/<name>/ for one. agy loads skills/<name>/SKILL.md (the
workflows are skills, so both harnesses read them), rules/, hooks.json and plugin.json.

agy does not offer a plugin's agents/ as subagents: it takes them from ~/.gemini/config/agents/
(or <repository>/.agents/agents/), in its own format. sync_agents() writes the roles there, and
agy silently skips a file whose frontmatter it cannot use (a Claude model name such as
`model: sonnet`, or an unquoted description containing ": "), so both are converted. The agy
hook refreshes them at every session; --agents-only does it by hand.

    python3 install_agy.py [--workspace REPOSITORY | --dest DIR] [--agents-only]
"""
import argparse
import json
import os
import re
import shutil
import subprocess

import settings

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


AGY_TOOLS = {"Read": ["view_file"], "Grep": ["grep_search"], "Glob": ["find_by_name", "list_dir"],
             "Bash": ["run_command"], "Edit": ["replace_file_content"], "Write": ["write_to_file"],
             "WebSearch": ["search_web"], "WebFetch": ["read_url_content"]}
MARK = "<!-- team-workflow agent: regenerated from the plugin, edit agents/<role>.md there -->"


def agents_dir(workspace=None):
    base = os.path.join(workspace, ".agents") if workspace else os.path.join(
        os.path.expanduser("~"), ".gemini", "config")
    return os.path.join(base, "agents")


def agy_agent(text, model):
    """A Claude Code agent file in agy's custom agent format."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError("agent file without frontmatter")
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    lines = ["---", f"name: {meta['name']}", f"description: {json.dumps(meta['description'])}",
             f"model: {model}"]
    if "tools" in meta:
        tools = [t for name in json.loads(meta["tools"]) for t in AGY_TOOLS.get(name, [])]
        lines.append(f"tools: {json.dumps(tools)}")
    return "\n".join(lines + ["---", MARK, "", m.group(2).strip(), ""])


def sync_agents(dest, source=None, config=None):
    """Write every role in agy's format into dest; returns the roles written or refreshed.
    A file with the same name that team-workflow did not write is left alone."""
    source = source or os.path.join(PLUGIN, "agents")
    config = config or settings.load()
    os.makedirs(dest, exist_ok=True)
    changed = []
    for name in sorted(os.listdir(source)):
        if not name.endswith(".md"):
            continue
        role = name[:-3]
        with open(os.path.join(source, name), encoding="utf-8") as f:
            text = agy_agent(f.read(), settings.role_value(config, "models", role, "agy"))
        path = os.path.join(dest, name)
        try:
            with open(path, encoding="utf-8") as f:
                old = f.read()
        except OSError:
            old = None
        if old == text or (old is not None and MARK not in old):
            continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        changed.append(role)
    return changed


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
        out = subprocess.run(["agy", "plugin", "validate", dest], capture_output=True, text=True)
        print((out.stdout + out.stderr).strip() or "agy plugin validate: no output")


if __name__ == "__main__":
    main()
