#!/usr/bin/env python3
"""Install team-workflow into OpenCode (~/.config/opencode, or <repository>/.opencode).

What it writes, every file marked as ours so updates and uninstall touch nothing else:
    skills/team-workflow/            the team-workflow skill: SKILL.md, WIZARD, TEAMS, scripts, roles
    commands/team-workflow/<name>.md one command per workflow: /team-workflow/<name>
    agents/<role>.md                 the enabled roles as OpenCode subagents (roles.py)
    OpenCode 2.x: a team-workflow block in AGENTS.md (~/.config/opencode/AGENTS.md, or the
                  repository's AGENTS.md): load the memory at the first task, the notes.
                  The commands that need no reasoning print tw.py's output (!`...` in the
                  command), so the model only shows it.
    OpenCode 1.x: plugins/team-workflow.js: memory in the system prompt, no-token commands,
                  STATE reminder. OpenCode 2.x plugins cannot do that, so it is not written.

The commands live in a folder because a colon is not allowed in a Windows file name.

    python3 install_opencode.py [--workspace REPOSITORY] [--source URL_OR_PATH]
    python3 install_opencode.py --uninstall
"""
import argparse
import json
import os
import re
import shutil
import sys

import opencode_cli
import roles

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
PLUGIN = os.path.normpath(os.path.join(SKILL, "..", ".."))
NAME = "team-workflow"
MARK = "<!-- team-workflow command: written by install_opencode.py -->"
BEGIN = "<!-- team-workflow:begin (written by install_opencode.py; edits inside are overwritten) -->"
END = "<!-- team-workflow:end -->"
REPO = "https://github.com/antoStr/team-workflow"
# workflows answered by tw.py alone: the model only shows the output
NO_MODEL = {"update-plugin": "update", "settings": "settings", "models": "models", "addons": "addons",
            "agents": "agents", "profile": "profile", "audit": "audit", "doctor": "doctor",
            "ci-init": "ci-init", "options": "options",
            "library": "library", "talk": "talk"}


def config_dir(workspace=None):
    return os.path.join(workspace, ".opencode") if workspace else os.path.join(
        os.path.expanduser("~"), ".config", "opencode")


def payload_dir(workspace=None):
    return os.path.join(config_dir(workspace), "skills", NAME)


def commands_dir(workspace=None):
    return os.path.join(config_dir(workspace), "commands", NAME)


def agents_md(workspace=None):
    """The instructions file OpenCode reads: the global one, or the repository's."""
    return os.path.join(workspace, "AGENTS.md") if workspace else os.path.join(config_dir(), "AGENTS.md")


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


def posix(path):
    """A path every shell OpenCode may use (bash, PowerShell, cmd) reads the same way."""
    return path.replace("\\", "/")


def with_python(text, python):
    """`python3 ` in commands and docs becomes the Python that runs here (python3 can be the
    Microsoft Store placeholder on Windows)."""
    return text if python == "python3" else re.sub(r"(?<![\w/.-])python3 ", python + " ", text)


def command_text(name, skill_md, scripts, python, v2=True):
    """An OpenCode command from one of our workflow skills."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", skill_md, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    description = meta.get("description", "").strip().strip('"')
    description = re.sub(r"\s*\((?:no tokens in Claude Code|[^()]*run `!team-workflow)[^()]*(?:`[^`]*`[^()]*)*\)\s*$",
                         "", description)  # Claude Code and agy notes mean nothing here
    head =f"---\ndescription: {json.dumps(description)}\n---\n{MARK}\n\n"
    if v2 and name in NO_MODEL:
        app = " --app opencode" if name in ("options", "models") else ""
        tw = f'{python} "{posix(os.path.join(scripts, "tw.py"))}" {NO_MODEL[name]}{app} $ARGUMENTS'
        return (head + "team-workflow ran this command without you. Show the user the output below "
                "exactly as it is, in a code block, and add nothing else.\n\n"
                f"!`{tw}`\n")
    body = m.group(2).strip().replace("<team-workflow skill folder>", posix(os.path.dirname(scripts)))
    return head + with_python(body, python) + "\n"


def ours(path):
    """A command file we wrote. Read and closed before any removal: Windows cannot delete an
    open file."""
    with open(path, encoding="utf-8", errors="replace") as f:
        return MARK in f.read()


def remove_commands(conf, keep=()):
    """Our commands: commands/team-workflow/<name>.md, and the older commands/team-workflow:<name>.md
    (on Windows those became hidden streams of an empty `team-workflow` file)."""
    removed = []
    folder = os.path.join(conf, "commands")
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        if name.startswith(NAME + ":") and os.path.isfile(path) and ours(path):
            os.remove(path)
            removed.append(name)
        elif name == NAME and os.path.isfile(path) and os.path.getsize(path) == 0:
            os.remove(path)  # the empty file that held the Windows streams
            removed.append(name)
    nested = os.path.join(folder, NAME)
    for name in sorted(os.listdir(nested)) if os.path.isdir(nested) else []:
        path = os.path.join(nested, name)
        if name in keep or not name.endswith(".md"):
            continue
        if ours(path):
            os.remove(path)
            removed.append(f"{NAME}/{name}")
    if os.path.isdir(nested) and not os.listdir(nested):
        os.rmdir(nested)
    return removed


def agents_block(scripts, python):
    s = posix(scripts)
    return "\n".join([
        BEGIN,
        "# team-workflow",
        "",
        f"- At the first task of every conversation, run `{python} \"{s}/session_start.py\" "
        "--text` from the working folder and follow what it prints: the project memory, the settings "
        "and the session setup. Run it once per conversation. It prints nothing outside a git "
        "repository: the session setup in WIZARD.md still applies there.",
        "- The workflows are the /team-workflow/<name> commands and the team-workflow skill. When the "
        "user calls the team-workflow skill, start with its session setup (question tool), even "
        "without a task.",
        "- Launch a role with the subagent tool, `agent` = the role (for example `tester`); several "
        "independent roles in the same message. The roles are the subagents in the agents folder.",
        "- Ask the user with the question tool; several answers only when choosing roles.",
        f"- Run the team-workflow scripts as `{python} \"{s}/<script>.py\"` (they are in {s}).",
        "- When files change, update docs/memory/STATE.md before you finish the task.",
        "- Answer in the language the user writes in.",
        END,
    ])


def write_block(path, block):
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    text = strip_block(text)
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write((text.rstrip() + "\n\n" if text.strip() else "") + block + "\n")


def strip_block(text):
    return re.sub(re.escape(BEGIN) + r".*?" + re.escape(END) + r"\n?", "", text, flags=re.S)


def remove_block(path):
    """Take our block out of an AGENTS.md; the file goes when nothing else is left."""
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    if BEGIN not in text:
        return False
    rest = strip_block(text)
    if rest.strip():
        with open(path, "w", encoding="utf-8") as f:
            f.write(rest.rstrip() + "\n")
    else:
        os.remove(path)
    return True


def install(workspace=None, source=None, version=None):
    version = version if version is not None else opencode_cli.version()
    v2 = version is None or opencode_cli.is_v2(version)  # unknown: the current OpenCode
    python = opencode_cli.python_command()
    conf = config_dir(workspace)
    payload = payload_dir(workspace)
    if os.path.isdir(payload):
        shutil.rmtree(payload)
    shutil.copytree(SKILL, payload, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if python != "python3":
        for dirpath, _, files in os.walk(payload):
            for name in files:
                if name.endswith(".md"):
                    path = os.path.join(dirpath, name)
                    with open(path, encoding="utf-8") as f:
                        text = f.read()
                    if "python3 " in text:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(with_python(text, python))
    with open(os.path.join(payload, "VERSION"), "w", encoding="utf-8") as f:
        f.write((own_version() or "0.0.0") + "\n")
    with open(os.path.join(payload, ".source"), "w", encoding="utf-8") as f:
        f.write((source or REPO) + "\n")
    scripts = os.path.join(payload, "scripts")

    commands = commands_dir(workspace)
    removed = remove_commands(conf)  # first: an old empty `team-workflow` file blocks the folder
    os.makedirs(commands, exist_ok=True)
    wanted = set()
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        path = os.path.join(PLUGIN, "skills", name, "SKILL.md")
        if name == NAME or not os.path.isfile(path):
            continue
        with open(path, encoding="utf-8") as f:
            text = command_text(name, f.read(), scripts, python, v2)
        wanted.add(name + ".md")
        with open(os.path.join(commands, name + ".md"), "w", encoding="utf-8") as f:
            f.write(text)
    removed = [r for r in removed if r.split("/")[-1] not in wanted]

    plugin = os.path.join(conf, "plugins", "team-workflow.js")
    if v2:  # a 1.x plugin does not load in 2.x: the AGENTS.md block does its work
        if os.path.isfile(plugin):
            os.remove(plugin)
        write_block(agents_md(workspace), agents_block(scripts, python))
    else:
        os.makedirs(os.path.dirname(plugin), exist_ok=True)
        with open(os.path.join(SKILL, "opencode", "team-workflow.js"), encoding="utf-8") as f:
            js = (f.read().replace("__SCRIPTS__", posix(scripts))
                  .replace('"__PYTHON__"', json.dumps(sys.executable)))
        with open(plugin, "w", encoding="utf-8") as f:
            f.write(js)
        remove_block(agents_md(workspace))

    agents = roles.sync("opencode", dest=roles.native_dir("opencode", workspace))
    return {"payload": payload, "commands": len(wanted), "stale_commands_removed": removed,
            "agents": agents["written"], "agents_not_ours": agents["skipped"],
            "opencode": ".".join(map(str, version)) if version else None, "v2": v2,
            "python": python, "instructions": agents_md(workspace) if v2 else plugin}


def uninstall(workspace=None):
    conf = config_dir(workspace)
    done = [f"removed command {n}" for n in remove_commands(conf)]
    plugin = os.path.join(conf, "plugins", "team-workflow.js")
    if os.path.isfile(plugin):
        os.remove(plugin)
        done.append(f"removed {plugin}")
    if remove_block(agents_md(workspace)):
        done.append(f"removed the team-workflow block of {agents_md(workspace)}")
    folder = roles.native_dir("opencode", workspace)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        with open(path, encoding="utf-8", errors="replace") as f:
            mine = roles.ours(f.read())
        if mine:
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
    print(f"team-workflow {own_version()} installed in OpenCode {result['opencode'] or '(version unknown)'}: "
          f"{result['payload']}")
    print(f"{result['commands']} commands (/team-workflow/<name>), {len(result['agents'])} agents written "
          f"or refreshed; {'instructions in' if result['v2'] else 'plugin'} {result['instructions']}")
    print(f"Python for the scripts: {result['python']}")
    if result["agents_not_ours"]:
        print("agents with these names already exist and were left alone: "
              + ", ".join(result["agents_not_ours"]))
    print("Restart OpenCode to load them.")


if __name__ == "__main__":
    main()
