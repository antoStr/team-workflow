#!/usr/bin/env python3
"""Install team-workflow into OpenCode (~/.config/opencode, or <repository>/.opencode).

What it writes, every file marked as ours so updates and uninstall touch nothing else:
    skills/team-workflow/            the team-workflow skill: SKILL.md, WIZARD, TEAMS, scripts, roles
    commands/team-workflow:<name>.md one command per workflow (/team-workflow:setup-memory, ...)
    plugins/team-workflow.js         memory in the system prompt, no-token commands, STATE reminder
    agents/<role>.md                 the enabled roles as OpenCode subagents (roles.py)

    python3 install_opencode.py [--workspace REPOSITORY] [--source URL_OR_PATH]
    python3 install_opencode.py --uninstall
"""
import argparse
import json
import os
import re
import shutil

import roles

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
PLUGIN = os.path.normpath(os.path.join(SKILL, "..", ".."))
NAME = "team-workflow"
MARK = "<!-- team-workflow command: written by install_opencode.py -->"
REPO = "https://github.com/antoStr/team-workflow"


def config_dir(workspace=None):
    return os.path.join(workspace, ".opencode") if workspace else os.path.join(
        os.path.expanduser("~"), ".config", "opencode")


def payload_dir(workspace=None):
    return os.path.join(config_dir(workspace), "skills", NAME)


def own_version():
    for rel in (os.path.join(".claude-plugin", "plugin.json"), "plugin.json"):
        try:
            with open(os.path.join(PLUGIN, rel), encoding="utf-8") as f:
                return json.load(f).get("version")
        except (OSError, ValueError):
            continue
    try:
        with open(os.path.join(SKILL, "VERSION"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def installed_version(workspace=None):
    try:
        with open(os.path.join(payload_dir(workspace), "VERSION"), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def installed_source(workspace=None):
    try:
        with open(os.path.join(payload_dir(workspace), ".source"), encoding="utf-8") as f:
            return f.read().strip() or None
    except OSError:
        return None


def command_text(skill_md, scripts):
    """An OpenCode command from one of our workflow skills."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", skill_md, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    body = m.group(2).strip().replace("<team-workflow skill folder>", os.path.dirname(scripts))
    description = meta.get("description", "").strip().strip('"')
    return f"---\ndescription: {json.dumps(description)}\n---\n{MARK}\n\n{body}\n"


def remove_commands(folder, keep=()):
    removed = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        if name in keep or not name.startswith(NAME + ":"):
            continue
        with open(path, encoding="utf-8", errors="replace") as f:
            if MARK in f.read():
                os.remove(path)
                removed.append(name)
    return removed


def install(workspace=None, source=None):
    conf = config_dir(workspace)
    payload = payload_dir(workspace)
    if os.path.isdir(payload):
        shutil.rmtree(payload)
    shutil.copytree(SKILL, payload, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    with open(os.path.join(payload, "VERSION"), "w", encoding="utf-8") as f:
        f.write((own_version() or "0.0.0") + "\n")
    with open(os.path.join(payload, ".source"), "w", encoding="utf-8") as f:
        f.write((source or REPO) + "\n")
    scripts = os.path.join(payload, "scripts")

    commands = os.path.join(conf, "commands")
    os.makedirs(commands, exist_ok=True)
    wanted = set()
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        path = os.path.join(PLUGIN, "skills", name, "SKILL.md")
        if name == NAME or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = command_text(f.read(), scripts)
        target = f"{NAME}:{name}.md"
        wanted.add(target)
        with open(os.path.join(commands, target), "w", encoding="utf-8") as f:
            f.write(text)
    removed = remove_commands(commands, keep=wanted)

    plugins = os.path.join(conf, "plugins")
    os.makedirs(plugins, exist_ok=True)
    with open(os.path.join(SKILL, "opencode", "team-workflow.js"), encoding="utf-8") as f:
        js = f.read().replace("__SCRIPTS__", scripts)
    with open(os.path.join(plugins, "team-workflow.js"), "w", encoding="utf-8") as f:
        f.write(js)

    agents = roles.sync("opencode", dest=roles.native_dir("opencode", workspace))
    return {"payload": payload, "commands": len(wanted), "stale_commands_removed": removed,
            "agents": agents["written"], "agents_not_ours": agents["skipped"]}


def uninstall(workspace=None):
    conf = config_dir(workspace)
    done = [f"removed command {n}" for n in remove_commands(os.path.join(conf, "commands"))]
    plugin = os.path.join(conf, "plugins", "team-workflow.js")
    if os.path.isfile(plugin):
        os.remove(plugin)
        done.append(f"removed {plugin}")
    folder = roles.native_dir("opencode", workspace)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8", errors="replace") as f:
            ours = roles.ours(f.read())
        if ours:
            os.remove(path)
            done.append(f"removed agent {name}")
    if os.path.isdir(payload_dir(workspace)):
        shutil.rmtree(payload_dir(workspace))
        done.append(f"removed {payload_dir(workspace)}")
    return done


def main():
    ap = argparse.ArgumentParser(description="Install team-workflow into OpenCode.")
    ap.add_argument("--workspace", help="install for one repository (.opencode)")
    ap.add_argument("--source", help="where updates come from (default: the GitHub repository)")
    ap.add_argument("--uninstall", action="store_true")
    args = ap.parse_args()
    if args.uninstall:
        print("\n".join(uninstall(args.workspace)) or "nothing to remove")
        return
    result = install(args.workspace, args.source)
    print(f"team-workflow {own_version()} installed in OpenCode: {result['payload']}")
    print(f"{result['commands']} commands (/team-workflow:<name>), the plugin, "
          f"{len(result['agents'])} agents written or refreshed")
    if result["agents_not_ours"]:
        print("agents with these names already exist and were left alone: "
              + ", ".join(result["agents_not_ours"]))
    print("Restart OpenCode to load them.")


if __name__ == "__main__":
    main()
