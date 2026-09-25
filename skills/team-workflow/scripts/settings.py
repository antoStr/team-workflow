"""team-workflow settings: defaults, then ~/.team-workflow/settings.json (every project), then
<repository>/.team-workflow.json (this project only). Read by the hooks, the scripts and the
orchestrator; changed with `tw.py settings set <key> <value>` or by editing the files."""
import json
import os

DEFAULTS = {
    # Assignment wizard: quick = the board with the recommended choices, questions only for the
    # agents the user wants to change; full = every question for every agent; off = no wizard,
    # launch with the recommended choices.
    "wizard": "quick",
    "max_agents": 4,               # largest team proposed without asking
    "launch": "native",            # native subagents, or headless workers (exact model/effort)
    "worker_edits": False,         # workers may change files without asking each time
    "auto_security_review": True,  # add security-reviewer on sensitive changes
    "end_report": "full",          # full | short
    "update_check": True,          # tell at session start when a new version is out (daily)
    "stop_check": True,            # remind to update docs/memory/STATE.md at the end of a turn
    # Model per role, per app. Claude Code: haiku, sonnet, opus, fable or a model id.
    # agy subagents: inherit (the session's model), flash or pro. "default" covers the rest.
    "models": {
        "claude": {"default": "sonnet", "architect": "opus", "security-reviewer": "opus",
                   "doc-keeper": "haiku"},
        "agy": {"default": "inherit", "architect": "pro", "security-reviewer": "pro",
                "doc-keeper": "flash"},
    },
    # Effort per role (workers in both apps): low, medium, high, xhigh, max.
    "effort": {"default": "medium", "architect": "high", "security-reviewer": "high"},
    # Add-on plugins chosen with `tw.py addons add`; `update` refreshes them too.
    "addons": {},
}

CHOICES = {
    "wizard": ("quick", "full", "off"),
    "launch": ("native", "worker"),
    "end_report": ("full", "short"),
    "models.agy": ("inherit", "flash", "pro"),
    "effort": ("low", "medium", "high", "xhigh", "max"),
}
ROLE_TABLES = ("models", "effort")  # any role name is a valid key inside these


def home_dir():
    return os.path.join(os.path.expanduser("~"), ".team-workflow")


def user_file():
    return os.path.join(home_dir(), "settings.json")


def project_file(root):
    return os.path.join(root, ".team-workflow.json")


def _read(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return {}
    return data if isinstance(data, dict) else {}


def _merge(base, over):
    out = dict(base)
    for k, v in over.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load(root=None):
    data = _merge(DEFAULTS, _read(user_file()))
    return _merge(data, _read(project_file(root))) if root else data


def role_value(data, section, role, app=None):
    """Model (with app) or effort of a role, falling back to "default"."""
    table = data[section][app] if app else data[section]
    return table.get(role, table.get("default"))


def parse_value(key, text):
    """Typed value for a dotted key, checked against the default's type and CHOICES."""
    parts = key.split(".")
    node = DEFAULTS
    for part in parts[:-1]:
        node = node.get(part) if isinstance(node, dict) else None
    if not isinstance(node, dict):
        raise ValueError(f"unknown setting {key!r}")
    role_table = parts[0] in ROLE_TABLES and not any(isinstance(v, dict) for v in node.values())
    default = node.get(parts[-1], node.get("default") if role_table else None)
    if default is None or isinstance(default, dict):
        raise ValueError(f"unknown setting {key!r}")
    if isinstance(default, bool):
        if text.lower() not in ("true", "false", "on", "off", "yes", "no", "1", "0"):
            raise ValueError(f"{key} is true or false")
        value = text.lower() in ("true", "on", "yes", "1")
    elif isinstance(default, int):
        value = int(text)
    else:
        value = text
    for prefix, allowed in CHOICES.items():
        if (key == prefix or key.startswith(prefix + ".")) and value not in allowed:
            raise ValueError(f"{key} is one of: {', '.join(allowed)}")
    return value


def save(key, value, root=None):
    """Write one dotted key (None removes it) to the user file, or the project file with root."""
    path = project_file(root) if root else user_file()
    data = _read(path)
    node = data
    parts = key.split(".")
    for part in parts[:-1]:
        node = node.setdefault(part, {})
    if value is None:
        node.pop(parts[-1], None)
    else:
        node[parts[-1]] = value
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return path


def flatten(data, prefix=""):
    for k, v in data.items():
        if isinstance(v, dict):
            yield from flatten(v, f"{prefix}{k}.")
        else:
            yield f"{prefix}{k}", v


def summary(data):
    """One line with the settings that differ from the defaults, for the session context."""
    defaults = dict(flatten(DEFAULTS))
    changed = [f"{k}={json.dumps(v)}" for k, v in flatten(data)
               if not k.startswith("addons.") and defaults.get(k, object()) != v]
    if data.get("addons"):
        changed.append("addons=" + ",".join(data["addons"]))
    return "team-workflow settings: " + (", ".join(changed) if changed else "defaults")
