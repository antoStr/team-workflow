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
    # At the first team-workflow task of every conversation: choose preset, roles, model and
    # effort per role among what the app offers now, for this conversation or as new defaults.
    "session_wizard": True,
    "max_agents": 4,               # largest team proposed without asking
    "launch": "native",            # native subagents, or headless workers (exact model/effort)
    "worker_edits": False,         # workers may change files without asking each time
    "auto_security_review": True,  # add security-reviewer on sensitive changes
    "end_report": "full",          # full | short
    "update_check": True,          # tell at session start when a new version is out (daily)
    "stop_check": True,            # remind to update docs/memory/STATE.md at the end of a turn
    # Model per role, per app. Claude Code: haiku, sonnet, opus, fable or a model id.
    # agy subagents: inherit (the session's model), flash or pro. OpenCode: inherit or
    # provider/model from `opencode models`. "default" covers the roles not listed.
    "models": {
        "claude": {"default": "sonnet", "architect": "opus", "security-reviewer": "opus",
                   "doc-keeper": "haiku"},
        "agy": {"default": "inherit"},  # the session's model (/model); pro is Gemini 3.1 Pro
        "opencode": {"default": "inherit"},
    },
    # Effort per role: low, medium, high, xhigh, max (Claude Code agents and workers; agy puts
    # the effort in the worker's model id; OpenCode writes it as the agent's variant, except
    # medium). Models without effort (haiku) ignore it.
    "effort": {"default": "medium", "architect": "high", "security-reviewer": "high"},
    # Agent type per role, per app. custom = our generated subagent (default); worker = a
    # headless process with exact model and effort; or a built-in type of the app, briefed with
    # the role: Claude Code general-purpose, Explore, Plan; agy self, research; OpenCode
    # general, explore.
    "type": {"claude": {"default": "custom"}, "agy": {"default": "custom"},
             "opencode": {"default": "custom"}},
    # Packs of roles (core, languages, quality...) on or off; a role inside an enabled pack can
    # still be switched off with enabled.<role> false.
    "packs": {"default": False, "core": True, "custom": True},
    "enabled": {"default": True},
    # Add-on plugins chosen with `tw.py addons add`; `update` refreshes them too.
    "addons": {},
}

# Presets that change several settings at once (`tw.py profile <name>`); balanced restores the
# defaults of every key a profile touches.
PROFILES = {
    "budget": {"wizard": "quick", "max_agents": 2, "models.claude.default": "haiku",
               "models.claude.architect": "sonnet", "models.claude.security-reviewer": "sonnet",
               "models.agy.default": "flash", "effort.default": "low", "end_report": "short"},
    "fast": {"wizard": "off", "max_agents": 2, "effort.default": "low", "end_report": "short"},
    "balanced": {},
    "thorough": {"wizard": "full", "max_agents": 6, "models.claude.default": "opus",
                 "effort.default": "high", "packs.quality": True, "auto_security_review": True},
    "security": {"auto_security_review": True, "packs.quality": True, "worker_edits": False,
                 "models.claude.security-reviewer": "opus", "effort.security-reviewer": "max"},
    "research": {"packs.planning": True, "effort.market-researcher": "high",
                 "effort.data-analyst": "high", "effort.code-explorer": "high",
                 "type.claude.code-explorer": "Explore"},
}

CHOICES = {
    "wizard": ("quick", "full", "off"),
    "launch": ("native", "worker"),
    "end_report": ("full", "short"),
    "models.agy": ("inherit", "flash", "pro"),
    "effort": ("low", "medium", "high", "xhigh", "max"),
    "type.claude": ("custom", "worker", "general-purpose", "Explore", "Plan"),
    "type.agy": ("custom", "worker", "self", "research"),
    "type.opencode": ("custom", "worker", "general", "explore"),
}
ROLE_TABLES = ("models", "effort", "type", "packs", "enabled")  # any role name is a valid key inside these


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
    if key.startswith("models.opencode.") and value != "inherit" and "/" not in value:
        raise ValueError(f"{key} is inherit or provider/model (see `opencode models`)")
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


def default_of(key):
    """The built-in value of a dotted key, or None."""
    return dict(flatten(DEFAULTS)).get(key)


def apply_profile(name, root=None):
    """Save a profile's values (or, for balanced, the defaults they replace); returns the changes."""
    if name not in PROFILES:
        raise ValueError(f"profiles: {', '.join(PROFILES)}")
    if name == "balanced":
        keys = sorted({k for p in PROFILES.values() for k in p})
        changes = [(k, None) for k in keys]
    else:
        changes = list(PROFILES[name].items())
    for key, value in changes:
        save(key, value, root)
    return changes


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
