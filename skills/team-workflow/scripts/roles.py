"""Roles: the agents team-workflow can launch, grouped in packs, and the native agent files each
app loads, written from the settings (type, model and effort per role and per app).

Sources, later ones win for the same role name:
    <plugin>/skills/team-workflow/roles/<pack>/<role>.md   core and the optional packs
    ~/.team-workflow/agents/<role>.md                        your own roles or overrides
    <repository>/.team-workflow/agents/<role>.md             roles for one project

Native files, written only for enabled roles whose type is "custom" and marked as ours:
    Claude Code  ~/.claude/agents/<role>.md
    agy          ~/.gemini/config/agents/<role>.md   (agy drops a file whose `model` is not
                 inherit, flash or pro, or whose description has an unquoted ": ")
"""
import json
import os
import re

import settings

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES_DIR = os.path.normpath(os.path.join(HERE, "..", "roles"))
MARK = "<!-- team-workflow agent: generated from its role file; change it with `tw.py agents` -->"
AGY_TOOLS = {"Read": ["view_file"], "Grep": ["grep_search"], "Glob": ["find_by_name", "list_dir"],
             "Bash": ["run_command"], "Edit": ["replace_file_content"], "Write": ["write_to_file"],
             "WebSearch": ["search_web"], "WebFetch": ["read_url_content"]}
APPS = ("claude", "agy")


def parse(text):
    """(frontmatter dict, body) of an agent file."""
    m = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.S)
    if not m:
        raise ValueError("agent file without frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v[:1] == '"' and v[-1:] == '"':
                v = json.loads(v)
            meta[k.strip()] = v
    return meta, m.group(2).strip()


def user_dir():
    return os.path.join(settings.home_dir(), "agents")


def catalog(root=None):
    """{role: {"pack", "path", "origin"}} from the plugin, the user and the project."""
    found = {}
    for pack in sorted(os.listdir(ROLES_DIR)):
        folder = os.path.join(ROLES_DIR, pack)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if name.endswith(".md"):
                found[name[:-3]] = {"pack": pack, "path": os.path.join(folder, name), "origin": "plugin"}
    extra = [(user_dir(), "user")] + ([(os.path.join(root, ".team-workflow", "agents"), "project")]
                                      if root else [])
    for folder, origin in extra:
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if name.endswith(".md"):
                role = name[:-3]
                pack = found.get(role, {}).get("pack", "custom")
                found[role] = {"pack": pack, "path": os.path.join(folder, name), "origin": origin}
    return found


def load(role, root=None):
    info = catalog(root).get(role)
    if not info:
        raise ValueError(f"unknown role {role!r}")
    with open(info["path"], encoding="utf-8") as f:
        return parse(f.read())


def is_enabled(config, role, pack):
    packs, enabled = config["packs"], config["enabled"]
    return bool(packs.get(pack, packs.get("default"))) and bool(enabled.get(role, enabled.get("default")))


def plan(config, role, app):
    """{"type", "model", "effort"} of a role in an app, from the settings."""
    return {"type": settings.role_value(config, "type", role, app),
            "model": settings.role_value(config, "models", role, app),
            "effort": settings.role_value(config, "effort", role)}


def efforts(model):
    """Efforts a Claude model accepts, from pricing.json; None when unknown (then any)."""
    try:
        with open(os.path.join(HERE, "..", "pricing.json"), encoding="utf-8") as f:
            pricing = json.load(f)
    except (OSError, ValueError):
        return None
    mid = pricing.get("aliases", {}).get(model, model)
    entry = pricing.get("models", {}).get(mid)
    return entry.get("effort") if entry and "effort" in entry else None


def native_text(app, role, meta, body, p):
    lines = ["---", f"name: {role}", f"description: {json.dumps(meta.get('description', role))}"]
    tools = json.loads(meta["tools"]) if meta.get("tools") else None
    if app == "claude":
        lines.append(f"model: {p['model']}")
        allowed = efforts(p["model"])
        if p["effort"] and (allowed is None or p["effort"] in allowed):
            lines.append(f"effort: {p['effort']}")
        if tools:
            lines.append(f"tools: {json.dumps(tools)}")
        if meta.get("color"):
            lines.append(f"color: {meta['color']}")
    else:
        lines.append(f"model: {p['model']}")
        if tools:
            lines.append(f"tools: {json.dumps([t for n in tools for t in AGY_TOOLS.get(n, [])])}")
    return "\n".join(lines + ["---", MARK, "", body, ""])


def native_dir(app, workspace=None):
    if app == "claude":
        base = os.path.join(workspace, ".claude") if workspace else os.path.join(
            os.path.expanduser("~"), ".claude")
    else:
        base = os.path.join(workspace, ".agents") if workspace else os.path.join(
            os.path.expanduser("~"), ".gemini", "config")
    return os.path.join(base, "agents")


def sync(app, config=None, root=None, dest=None):
    """Write the native files of one app; returns {"written", "removed", "skipped"}.
    A file with the same name that team-workflow did not write is never touched."""
    config = config or settings.load(root)
    dest = dest or native_dir(app)
    os.makedirs(dest, exist_ok=True)
    result = {"written": [], "removed": [], "skipped": []}
    roles = catalog(root)
    for role, info in roles.items():
        path = os.path.join(dest, role + ".md")
        try:
            with open(path, encoding="utf-8") as f:
                old = f.read()
        except OSError:
            old = None
        if old is not None and MARK not in old:
            result["skipped"].append(role)
            continue
        p = plan(config, role, app)
        if not is_enabled(config, role, info["pack"]) or p["type"] != "custom":
            if old is not None:
                os.remove(path)
                result["removed"].append(role)
            continue
        with open(info["path"], encoding="utf-8") as f:
            meta, body = parse(f.read())
        text = native_text(app, role, meta, body, p)
        if text != old:
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            result["written"].append(role)
    for name in os.listdir(dest):  # ours, for roles that no longer exist
        path = os.path.join(dest, name)
        if name.endswith(".md") and name[:-3] not in roles and os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                if MARK in f.read():
                    os.remove(path)
                    result["removed"].append(name[:-3])
    return result


def table(config, root=None):
    """Rows for `tw.py agents`: role, pack, on/off, then type/model/effort per app."""
    rows = []
    for role, info in catalog(root).items():
        c, a = plan(config, role, "claude"), plan(config, role, "agy")
        effort = c["effort"] if efforts(c["model"]) != [] else "-"
        origin = "" if info["origin"] == "plugin" else f" ({info['origin']})"
        rows.append((role, info["pack"] + origin,
                     "on" if is_enabled(config, role, info["pack"]) else "off",
                     f"{c['type']} {c['model']} {effort}", f"{a['type']} {a['model']}"))
    return rows


TEMPLATE = """---
name: {role}
description: "Use this agent when ... (what it does and when the orchestrator should pick it)."
tools: ["Read", "Grep", "Glob", "Bash"]
---

You are ... (the role in one sentence).

## When to invoke

- ...

## How you work

1. ...

## Output

- ...

## Boundaries

- Write only the files you are assigned; report anything outside them.
"""


def new_role(role, root=None):
    """Create an editable role file in ~/.team-workflow/agents (or the project with root)."""
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", role):
        raise ValueError("role names use lowercase letters, digits and dashes")
    folder = os.path.join(root, ".team-workflow", "agents") if root else user_dir()
    path = os.path.join(folder, role + ".md")
    if os.path.exists(path):
        raise ValueError(f"{path} exists")
    os.makedirs(folder, exist_ok=True)
    info = catalog().get(role)
    if info:  # an override starts from the current role
        with open(info["path"], encoding="utf-8") as f:
            text = f.read()
    else:
        text = TEMPLATE.format(role=role)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
