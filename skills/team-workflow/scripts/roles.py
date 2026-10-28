"""Roles: the agents team-workflow can launch, grouped in packs, and the native agent files each
app loads, written from the settings (type, model and effort per role and per app).

Sources, later ones win for the same role name:
    <plugin>/skills/team-workflow/roles/<pack>/<role>.md   core and the optional packs
    <plugin>/skills/team-workflow/roles/languages/<lang>.md one pack per language: with the
        _reviewer.md and _build-fixer.md templates it gives <lang>-reviewer, <lang>-build-fixer
    ~/.team-workflow/agents/<role>.md                        your own roles or overrides
    <repository>/.team-workflow/agents/<role>.md             roles for one project

Shared blocks in roles/_shared/<name>.md are appended to the body of a role: team-talk and
untrusted-input to every role, the others when the role's frontmatter lists them in `includes`.
Roles with `source: "imported ..."` come from tools/import_upstream.py (MIT, see library/NOTICE.md).

Native files, written only for enabled roles whose type is "custom" and marked as ours:
    Claude Code  ~/.claude/agents/<role>.md
    agy          ~/.gemini/config/agents/<role>.md   (agy drops a file whose `model` is not
                 inherit, flash or pro, or whose description has an unquoted ": ")
    OpenCode     ~/.config/opencode/agents/<role>.md
    Codex        ~/.codex/agents/<role>.toml, listed in ~/.codex/config.toml (install_codex.py)
"""
import glob
import json
import os
import re

import settings

HERE = os.path.dirname(os.path.abspath(__file__))
ROLES_DIR = os.path.normpath(os.path.join(HERE, "..", "roles"))
MARK = "<!-- team-workflow agent: generated from its role file; change it with `tw.py agents` -->"
OLD_MARKS = ("<!-- team-workflow agent: regenerated from the plugin",)  # written by 0.5.0


def ours(text):
    """True when team-workflow wrote this agent file (this version or an older one)."""
    return MARK in text or any(m in text for m in OLD_MARKS)

AGY_TOOLS = {"Read": ["view_file"], "Grep": ["grep_search"], "Glob": ["find_by_name", "list_dir"],
             "Bash": ["run_command"], "Edit": ["replace_file_content"], "Write": ["write_to_file"],
             "WebSearch": ["search_web"], "WebFetch": ["read_url_content"]}
APPS = ("claude", "agy", "opencode", "codex")
EXT = {"codex": ".toml"}  # the native agent file of each app; .md for the others
COLORS = {"red": "#E5484D", "orange": "#F76B15", "yellow": "#FFC53D", "green": "#46A758",
          "cyan": "#00A2C7", "blue": "#3E63DD", "purple": "#8E4EC6", "pink": "#D6409F"}


def installed_apps():
    """The apps present on this machine (their command, or their config folder)."""
    import shutil
    config = {"claude": ("~/.claude",), "agy": ("~/.gemini",), "opencode": ("~/.config/opencode",),
              "codex": ("~/.codex",)}
    return [a for a in APPS if shutil.which(a) or any(os.path.isdir(os.path.expanduser(p))
                                                      for p in config[a])]


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


def read(info):
    """Text of a catalog entry: its file, or the text expanded from a language template."""
    if "text" in info:
        return info["text"]
    with open(info["path"], encoding="utf-8") as f:
        return f.read()


def sections(body):
    """{"Heading": text} for the `## Heading` sections of a body."""
    parts = re.split(r"^## (.+)$", body, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def languages():
    """{slug: (frontmatter, sections)} of the language packs."""
    folder = os.path.join(ROLES_DIR, "languages")
    found = {}
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if name.endswith(".md") and not name.startswith("_"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                meta, body = parse(f.read())
            found[name[:-3]] = (meta, sections(body))
    return found


def language_roles():
    """{role: entry} for <lang>-reviewer and <lang>-build-fixer of every language."""
    folder = os.path.join(ROLES_DIR, "languages")
    templates = {}
    for kind in ("reviewer", "build-fixer"):
        path = os.path.join(folder, f"_{kind}.md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                templates[kind] = f.read()
    found = {}
    for slug, (meta, parts) in languages().items():
        values = dict(meta, checklist=parts.get("Checklist", ""), build=parts.get("Build", ""),
                      tools=parts.get("Tools", ""))
        for kind, template in templates.items():
            text = re.sub(r"\{(\w+)\}", lambda m: str(values.get(m.group(1), m.group(0))), template)
            found[f"{slug}-{kind}"] = {"pack": slug, "origin": "plugin", "text": text}
    return found


def detect(root):
    """Language packs whose marker files are in the repository root or one folder below."""
    found = []
    for slug, (meta, _) in languages().items():
        try:
            markers = json.loads(meta.get("detect") or "[]")
        except ValueError:
            markers = []
        if any(glob.glob(os.path.join(root, m)) or glob.glob(os.path.join(root, "*", m))
               for m in markers):
            found.append(slug)
    return found


def compose(meta, body):
    """The full instructions of a role: its body plus the shared blocks it includes."""
    try:
        names = json.loads(meta.get("includes") or "[]")
    except ValueError:
        names = []
    blocks = []
    for name in list(names) + ["team-talk", "untrusted-input"]:
        path = os.path.join(ROLES_DIR, "_shared", name + ".md")
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                blocks.append(f.read().strip())
    return "\n\n".join([body] + blocks)


def user_dir():
    return os.path.join(settings.home_dir(), "agents")


def catalog(root=None):
    """{role: {"pack", "path", "origin"}} from the plugin, the user and the project."""
    found = language_roles()
    for pack in sorted(os.listdir(ROLES_DIR)):
        if pack == "languages" or pack.startswith("_"):
            continue
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
    meta, body = parse(read(info))
    return meta, compose(meta, body)


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


def toml_text(value):
    """A TOML string: literal multi-line when it can be, else basic with escapes."""
    if "'''" not in value:
        return "'''\n" + value + "'''"
    return json.dumps(value)


def codex_text(role, meta, body, p):
    """A Codex agent (config file of [agents.<role>] in config.toml)."""
    tools = json.loads(meta["tools"]) if meta.get("tools") else None
    writes = tools is None or bool({"Edit", "Write", "Bash"} & set(tools))
    lines = [f"# {MARK}", f"# {role}: {meta.get('description', role)}"[:400].replace("\n", " ")]
    if p["model"] and p["model"] != "inherit":
        lines.append(f"model = {json.dumps(p['model'])}")
    if p["effort"]:
        lines.append(f"model_reasoning_effort = {json.dumps(p['effort'])}")
    lines.append(f"sandbox_mode = {json.dumps('workspace-write' if writes else 'read-only')}")
    lines.append(f"developer_instructions = {toml_text(body)}")
    return "\n".join(lines) + "\n"


def native_text(app, role, meta, body, p):
    if app == "codex":
        return codex_text(role, meta, body, p)
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
    elif app == "agy":
        lines.append(f"model: {p['model']}")
        if tools:
            lines.append(f"tools: {json.dumps([t for n in tools for t in AGY_TOOLS.get(n, [])])}")
    else:  # OpenCode: a subagent; no model means the model of the agent that calls it
        lines.append("mode: subagent")
        if p["model"] and p["model"] != "inherit":
            lines.append(f"model: {p['model']}")
        if p["effort"] and p["effort"] != "medium":
            lines.append(f"variant: {p['effort']}")
        if meta.get("color") in COLORS:
            lines.append(f'color: "{COLORS[meta["color"]]}"')
        if tools:
            lines += ["permission:",
                      f"  edit: {'allow' if {'Edit', 'Write'} & set(tools) else 'deny'}",
                      f"  bash: {'allow' if 'Bash' in tools else 'deny'}",
                      f"  webfetch: {'allow' if 'WebFetch' in tools else 'deny'}",
                      f"  websearch: {'allow' if 'WebSearch' in tools else 'deny'}"]
    return "\n".join(lines + ["---", MARK, "", body, ""])


def native_dir(app, workspace=None):
    if app == "codex":
        base = os.path.join(workspace, ".codex") if workspace else os.environ.get(
            "CODEX_HOME") or os.path.join(os.path.expanduser("~"), ".codex")
        return os.path.join(base, "agents")
    if app == "claude":
        base = os.path.join(workspace, ".claude") if workspace else os.path.join(
            os.path.expanduser("~"), ".claude")
    elif app == "opencode":
        base = os.path.join(workspace, ".opencode") if workspace else os.path.join(
            os.path.expanduser("~"), ".config", "opencode")
    else:
        base = os.path.join(workspace, ".agents") if workspace else os.path.join(
            os.path.expanduser("~"), ".gemini", "config")
    return os.path.join(base, "agents")


def sync(app, config=None, root=None, dest=None, dry_run=False):
    """Write the native files of one app; returns {"written", "removed", "skipped"}.
    A file with the same name that team-workflow did not write is never touched.
    With dry_run nothing changes: the result says what a sync would do."""
    config = config or settings.load(root)
    dest = dest or native_dir(app)
    if not dry_run:
        os.makedirs(dest, exist_ok=True)
    result = {"written": [], "removed": [], "skipped": []}
    roles = catalog(root)
    ext = EXT.get(app, ".md")
    for role, info in roles.items():
        path = os.path.join(dest, role + ext)
        try:
            with open(path, encoding="utf-8") as f:
                old = f.read()
        except OSError:
            old = None
        if old is not None and not ours(old):
            result["skipped"].append(role)
            continue
        p = plan(config, role, app)
        if not is_enabled(config, role, info["pack"]) or p["type"] != "custom":
            if old is not None:
                if not dry_run:
                    os.remove(path)
                result["removed"].append(role)
            continue
        meta, body = parse(read(info))
        text = native_text(app, role, meta, compose(meta, body), p)
        if text != old:
            if not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(text)
            result["written"].append(role)
    for name in os.listdir(dest) if os.path.isdir(dest) else []:  # ours, for vanished roles
        path = os.path.join(dest, name)
        if name.endswith(ext) and name[:-len(ext)] not in roles and os.path.isfile(path):
            with open(path, encoding="utf-8") as f:
                mine = ours(f.read())
            if mine:  # closed first: Windows cannot delete an open file
                if not dry_run:
                    os.remove(path)
                result["removed"].append(name[:-len(ext)])
    if app == "codex" and not dry_run:
        import install_codex  # the agents are listed in config.toml
        install_codex.register_agents(dest)
    return result


def shadowed(app, root, config=None):
    """Enabled roles that a project-level agent with the same name, not written by us, replaces
    in this repository (<root>/.claude/agents or <root>/.agents/agents): the app prefers it."""
    if not root:
        return []
    config = config or settings.load(root)
    folder = native_dir(app, root)
    found = []
    for role, info in catalog(root).items():
        path = os.path.join(folder, role + ".md")
        if (os.path.isfile(path) and is_enabled(config, role, info["pack"])
                and plan(config, role, app)["type"] == "custom"):
            with open(path, encoding="utf-8", errors="replace") as f:
                if not ours(f.read()):
                    found.append(role)
    return found


def table(config, root=None):
    """Rows for `tw.py agents`: role, pack, on/off, then type/model/effort per app."""
    rows = []
    for role, info in catalog(root).items():
        c, a, o, x = (plan(config, role, app) for app in APPS)
        effort = c["effort"] if efforts(c["model"]) != [] else "-"
        origin = "" if info["origin"] == "plugin" else f" ({info['origin']})"
        rows.append((role, info["pack"] + origin,
                     "on" if is_enabled(config, role, info["pack"]) else "off",
                     f"{c['type']} {c['model']} {effort}", f"{a['type']} {a['model']}",
                     f"{o['type']} {o['model']}" + (f" {o['effort']}" if o["effort"] != "medium" else ""),
                     f"{x['type']} {x['model']} {x['effort']}"))
    return sorted(rows, key=lambda r: (r[1] != "core", r[2] == "off", r[1], r[0]))


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
        text = read(info)
    else:
        text = TEMPLATE.format(role=role)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path
