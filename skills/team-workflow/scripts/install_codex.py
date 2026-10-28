#!/usr/bin/env python3
"""Install team-workflow into Codex (the OpenAI Codex CLI and app, also behind opencodex):

    ~/.codex/skills/team-workflow/                  the team-workflow skill: SKILL.md, WIZARD,
                                                    TEAMS, TALK, scripts, roles, library
    ~/.codex/skills/team-workflow-<name>/SKILL.md   one skill per workflow ($team-workflow-start,
                                                    $team-workflow-agents...)
    ~/.codex/agents/<role>.toml                     the enabled roles as Codex agents, listed in
                                                    ~/.codex/config.toml (a block we manage)
    ~/.codex/AGENTS.md                              a block: memory, settings and session setup
                                                    at the first task (session_start.py --text)
    ~/.codex/rules/team-workflow.rules              Codex's sandbox reads only the project: this
                                                    rule lets `<python> <our script>` run, and
                                                    nothing else

With --workspace the same goes into <repository>/.codex and the block into
<repository>/AGENTS.md. CODEX_HOME moves ~/.codex, as it does for Codex. Only what we wrote is
changed or removed: our files carry a mark, our config.toml lines sit between two markers.

    python3 install_codex.py [--workspace REPOSITORY] [--uninstall]
"""
import argparse
import json
import os
import re
import shutil
import sys

import install_opencode
import roles
from common import utf8_output

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, ".."))
PLUGIN = os.path.normpath(os.path.join(SKILL, "..", ".."))
NAME = "team-workflow"
MARK = "<!-- team-workflow skill: written by install_codex.py -->"
AGENTS_BEGIN = "# >>> team-workflow agents (written by team-workflow; edits inside are overwritten) >>>"
AGENTS_END = "# <<< team-workflow agents <<<"
MCP_BEGIN = "# >>> team-workflow mcp (written by `tw.py addons`; edits inside are overwritten) >>>"
MCP_END = "# <<< team-workflow mcp <<<"


def config_dir(workspace=None):
    if workspace:
        return os.path.join(workspace, ".codex")
    return os.environ.get("CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex")


def payload_dir(workspace=None):
    return os.path.join(config_dir(workspace), "skills", NAME)


def agents_md(workspace=None):
    return os.path.join(workspace, "AGENTS.md") if workspace else os.path.join(config_dir(), "AGENTS.md")


def python_path():
    """The Python that runs this installer, by absolute path: Codex runs commands in a sandbox
    whose PATH often has no python (only the py launcher with nothing behind it)."""
    exe = sys.executable.replace(chr(92), "/")
    return f'"{exe}"' if " " in exe else exe


def present():
    return bool(shutil.which("codex")) or os.path.isdir(config_dir())


# --- config.toml blocks ------------------------------------------------------------------

def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def split_block(text, begin, end):
    """(text outside the block, text inside it)."""
    m = re.search(re.escape(begin) + r"\n(.*?)" + re.escape(end) + r"\n?", text, re.S)
    if not m:
        return text, ""
    return text[:m.start()] + text[m.end():], m.group(1)


def write_block(path, begin, end, body):
    """Put our block at the end of a TOML file (none when body is empty); the rest stays."""
    outside, _ = split_block(read_text(path), begin, end)
    outside = outside.rstrip()
    text = outside + ("\n\n" if outside else "") + (f"{begin}\n{body.rstrip()}\n{end}\n" if body.strip() else "")
    if not text.strip() and not os.path.exists(path):
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text if text.endswith("\n") or not text else text + "\n")


def table_names(text, table):
    """The <name>s of the [table.<name>] headers in TOML text (quotes taken off)."""
    return {n.strip().strip('"') for n in re.findall(r"^\[" + table + r"\.([^\]]+)\]", text, re.M)}


def defined_outside(path, begin, end, table):
    """Names the user defined in [table.<name>] outside our block: never defined twice."""
    outside, _ = split_block(read_text(path), begin, end)
    return table_names(outside, table)


def toml_key(name):
    return name if re.fullmatch(r"[A-Za-z0-9_-]+", name) else '"' + name + '"'


def register_agents(agents_dir):
    """List our agent files in the config.toml next to the agents folder."""
    conf = os.path.join(os.path.dirname(agents_dir), "config.toml")
    taken = defined_outside(conf, AGENTS_BEGIN, AGENTS_END, "agents")
    lines = []
    for name in sorted(os.listdir(agents_dir)) if os.path.isdir(agents_dir) else []:
        path = os.path.join(agents_dir, name)
        role = name[:-len(".toml")]
        if not name.endswith(".toml") or role in taken or not roles.ours(read_text(path)):
            continue
        first = read_text(path).splitlines()[1:2]
        about = first[0][2:].split(": ", 1)[-1] if first else role
        lines += [f"[agents.{toml_key(role)}]", f"description = {json.dumps(about)}",
                  f'config_file = "agents/{name}"', ""]
    write_block(conf, AGENTS_BEGIN, AGENTS_END, "\n".join(lines))
    return True


def mcp_servers(workspace=None):
    """The names of every MCP server in Codex's config.toml."""
    return table_names(read_text(os.path.join(config_dir(workspace), "config.toml")), "mcp_servers")


def our_mcp(inside):
    """{name: {"command", "args"}} from our block (we write each value as JSON, valid TOML)."""
    found = {}
    for name, command, args in re.findall(
            r'^\[mcp_servers\.([^\]]+)\]\ncommand = (.*)\nargs = (.*)$', inside, re.M):
        found[name.strip('"')] = {"command": json.loads(command), "args": json.loads(args)}
    return found


def set_mcp(name, command, workspace=None):
    """Add (command) or remove (None) one MCP server in our block of config.toml."""
    conf = os.path.join(config_dir(workspace), "config.toml")
    if name in defined_outside(conf, MCP_BEGIN, MCP_END, "mcp_servers"):
        return True, f"MCP server {name} already configured, left as it is"
    _, inside = split_block(read_text(conf), MCP_BEGIN, MCP_END)
    servers = our_mcp(inside)
    servers.pop(name, None)
    if command:
        servers[name] = {"command": command[0], "args": command[1:]}
    body = "\n".join(f"[mcp_servers.{toml_key(n)}]\ncommand = {json.dumps(c['command'])}\n"
                     f"args = {json.dumps(c['args'])}\n" for n, c in sorted(servers.items()))
    write_block(conf, MCP_BEGIN, MCP_END, body)
    return True, f"MCP server {name} {'written to' if command else 'removed from'} {conf}"


# --- skills and instructions ----------------------------------------------------------------

def ours(path):
    return MARK in read_text(path)


def rules_path(workspace=None):
    return os.path.join(config_dir(workspace), "rules", "team-workflow.rules")


def write_rules(scripts, python, workspace=None):
    """Allow exactly `<python> <one of our scripts> ...`: on Windows Codex's sandbox cannot read
    the user profile, where both Python and the installed scripts live."""
    exe = python.strip('"')
    exes = list(dict.fromkeys([install_opencode.posix(exe), os.path.normpath(exe)]))
    names = sorted(n for n in os.listdir(scripts) if n.endswith(".py"))
    paths = list(dict.fromkeys(p for n in names for p in (
        install_opencode.posix(os.path.join(scripts, n)), os.path.normpath(os.path.join(scripts, n)))))
    targets = ", ".join(json.dumps(p) for p in paths)
    rules = "".join(f"prefix_rule(\n    pattern = [{json.dumps(e)}, [{targets}]],\n    decision = \"allow\",\n)\n"
                    for e in exes)
    text = f"# {MARK}\n# team-workflow: its own scripts, run with the Python that installed it.\n{rules}"
    path = rules_path(workspace)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def workflow_text(name, skill_md, scripts, python):
    """A Codex skill from one of our workflow skills."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", skill_md, re.S)
    meta = dict(line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)
    description = meta.get("description", "").strip().strip('"')
    description = re.sub(r"\s*\((?:no tokens in Claude Code|niente token in Claude Code|[^()]*`!team-workflow)[^()]*(?:`[^`]*`[^()]*)*\)\s*$",
                         "", description)
    head = (f"---\nname: {NAME}-{name}\ndescription: {json.dumps(description)}\n---\n{MARK}\n\n")
    tw = f'{python} "{install_opencode.posix(os.path.join(scripts, "tw.py"))}"'
    if name in install_opencode.NO_MODEL:
        app = " --app codex" if name in ("options", "models") else ""
        win = ', shell="bash"' if os.name == "nt" else ""
        return (head + f"Run `{tw} {install_opencode.NO_MODEL[name]}{app} <what the user wrote after the "
                f'skill name>` from the repository root (`exec_command` with `sandbox_permissions="require_escalated"`{win}) '
                "and show the user its output exactly as it is, in a code block. Add nothing else.\n")
    body = m.group(2).strip().replace("<team-workflow skill folder>",
                                      install_opencode.posix(os.path.dirname(scripts)))
    body = body.replace("$ARGUMENTS", "(what the user wrote after the skill name)")
    return head + install_opencode.with_python(body, python) + "\n"


def instructions_block(scripts, python):
    s = install_opencode.posix(scripts)
    return "\n".join([
        install_opencode.BEGIN,
        "# team-workflow",
        "",
        f"- At the first task of every conversation, run `{python} \"{s}/session_start.py\" --text "
        "--app codex` from the working folder (`exec_command` with "
        + ('`sandbox_permissions="require_escalated"`, `shell="bash"`) ' if os.name == "nt"
           else '`sandbox_permissions="require_escalated"`) ')
        + "and follow what it prints: the project memory, the settings and the session setup. "
        "Run it once per conversation.",
        "- The workflows are the team-workflow skills (`$team-workflow-start`, `$team-workflow-setup`, "
        "`$team-workflow-agents`...) and the team-workflow skill. When the user calls the "
        "team-workflow skill, start with its session setup, even without a task.",
        "- The roles are Codex agents (for example `tester`, `security-reviewer`): spawn the agent "
        "by its name; several independent roles at the same time.",
        "- Ask the user with your question tool (request_user_input) when it is available, "
        "recommended option first; without it, one question at a time as a short numbered list of "
        "options, and wait for the answer.",
        f"- Run the team-workflow scripts as `{python} \"{s}/<script>.py\"` (they are in {s}) with "
        '`sandbox_permissions="require_escalated"` (`rules/team-workflow.rules` allows them'
        + ('; on Windows pass `shell="bash"` too, never PowerShell `&`).' if os.name == "nt" else ")."),
        "- When files change, update docs/memory/STATE.md before you finish the task.",
        "- Answer in the language the user writes in.",
        install_opencode.END,
    ])


def remove_skills(conf):
    folder = os.path.join(conf, "skills")
    removed = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name, "SKILL.md")
        if name.startswith(NAME + "-") and os.path.isfile(path) and ours(path):
            shutil.rmtree(os.path.join(folder, name))
            removed.append(name)
    return removed


def install(workspace=None, source=None):
    python = python_path()
    conf = config_dir(workspace)
    payload = payload_dir(workspace)
    if os.path.isdir(payload):
        shutil.rmtree(payload)
    shutil.copytree(SKILL, payload, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    if python != "python3":
        for dirpath, _, files in os.walk(payload):
            for name in files:
                if name.endswith(".md") and not dirpath.startswith(os.path.join(payload, "library")):
                    path = os.path.join(dirpath, name)
                    text = read_text(path)
                    if "python3 " in text:
                        with open(path, "w", encoding="utf-8") as f:
                            f.write(install_opencode.with_python(text, python))
    with open(os.path.join(payload, "VERSION"), "w", encoding="utf-8") as f:
        f.write((install_opencode.own_version() or "0.0.0") + "\n")
    with open(os.path.join(payload, ".source"), "w", encoding="utf-8") as f:
        f.write((source or install_opencode.REPO) + "\n")
    scripts = os.path.join(payload, "scripts")
    remove_skills(conf)
    written = []
    for name in sorted(os.listdir(os.path.join(PLUGIN, "skills"))):
        path = os.path.join(PLUGIN, "skills", name, "SKILL.md")
        if name == NAME or not os.path.isfile(path):
            continue
        target = os.path.join(conf, "skills", f"{NAME}-{name}")
        os.makedirs(target, exist_ok=True)
        with open(os.path.join(target, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(workflow_text(name, read_text(path), scripts, python))
        written.append(name)
    install_opencode.write_block(agents_md(workspace), instructions_block(scripts, python))
    write_rules(scripts, python, workspace)
    agents = roles.sync("codex", dest=roles.native_dir("codex", workspace))
    return {"payload": payload, "skills": len(written), "agents": agents["written"],
            "agents_not_ours": agents["skipped"], "python": python,
            "instructions": agents_md(workspace)}


def uninstall(workspace=None):
    conf = config_dir(workspace)
    done = [f"removed skill {n}" for n in remove_skills(conf)]
    if os.path.isfile(rules_path(workspace)) and ours(rules_path(workspace)):
        os.remove(rules_path(workspace))
        done.append(f"removed {rules_path(workspace)}")
    if install_opencode.remove_block(agents_md(workspace)):
        done.append(f"removed the team-workflow block of {agents_md(workspace)}")
    folder = roles.native_dir("codex", workspace)
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        path = os.path.join(folder, name)
        if os.path.isfile(path) and roles.ours(read_text(path)):
            os.remove(path)
            done.append(f"removed agent {name}")
    register_agents(folder)
    if os.path.isdir(payload_dir(workspace)):
        shutil.rmtree(payload_dir(workspace))
        done.append(f"removed {payload_dir(workspace)}")
    return done


def models():
    """[{"id", "name", "efforts"}] of the models Codex offers (its catalog, or opencodex's)."""
    conf = config_dir()
    catalog = re.search(r'^model_catalog_json\s*=\s*"(.*)"', read_text(os.path.join(conf, "config.toml")), re.M)
    for path in ([catalog.group(1).replace("\\\\", "\\")] if catalog else []) + [
            os.path.join(conf, "models_cache.json")]:
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, ValueError):
            continue
        return [{"id": m["slug"], "name": m.get("display_name", m["slug"]),
                 "efforts": [e["effort"] for e in m.get("supported_reasoning_levels", [])]}
                for m in data.get("models", []) if isinstance(m, dict) and m.get("slug")]
    return []


def installed_version(workspace=None):
    return read_text(os.path.join(payload_dir(workspace), "VERSION")).strip() or None


def main():
    utf8_output()
    ap = argparse.ArgumentParser(description="Install team-workflow into Codex.")
    ap.add_argument("--workspace", help="install for one repository (.codex and its AGENTS.md)")
    ap.add_argument("--source", help="where updates come from (default: the GitHub repository)")
    ap.add_argument("--uninstall", action="store_true", help="remove what this installer wrote")
    args = ap.parse_args()
    if args.uninstall:
        print("\n".join(uninstall(args.workspace)) or "nothing to remove")
        return
    r = install(args.workspace, args.source)
    print(f"installed in Codex: {r['payload']}; {r['skills']} workflow skills ($team-workflow-<name>), "
          f"{len(r['agents'])} agents written or refreshed, instructions in {r['instructions']}. "
          "Restart Codex.")


if __name__ == "__main__":
    main()
