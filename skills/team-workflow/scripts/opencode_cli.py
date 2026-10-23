"""OpenCode, as the scripts see it: where its CLI is, which version, which models the user can
pick (every provider they connected, with the model's name and reasoning variants), the models
they use most, and how a model with a variant is passed to `opencode run`.

OpenCode 2.x (the desktop app ships the CLI as resources/opencode-cli) lists the models with
names and variants through its local server (`opencode api GET /api/model`); 1.x only prints
`provider/model` ids (`opencode models`), and those are what is returned there.
"""
import functools
import json
import os
import re
import shutil
import sqlite3
import subprocess
import sys


def candidates():
    home = os.path.expanduser("~")
    local = os.environ.get("LOCALAPPDATA") or os.path.join(home, "AppData", "Local")
    exe = ".exe" if os.name == "nt" else ""
    return [os.environ.get("TEAM_WORKFLOW_OPENCODE_BIN"), shutil.which("opencode"),
            shutil.which("opencode-cli"),
            os.path.join(local, "Programs", "@opencodedesktop", "resources", "opencode-cli" + exe),
            os.path.join(home, ".opencode", "bin", "opencode" + exe)]


@functools.lru_cache(maxsize=None)
def binary():
    """The OpenCode CLI, or None when OpenCode is not installed."""
    for path in candidates():
        if path and (os.path.isfile(path) or shutil.which(path)):
            return path
    return None


def run(*args, timeout=60):
    """stdout of an OpenCode command, "" when it fails."""
    exe = binary()
    if not exe:
        return ""
    try:  # MSYS_NO_PATHCONV: Git Bash would turn /api/model into a Windows path
        out = subprocess.run([exe, *args], capture_output=True, text=True, encoding="utf-8",
                             errors="replace", timeout=timeout, stdin=subprocess.DEVNULL,
                             env=dict(os.environ, MSYS_NO_PATHCONV="1"))
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout if out.returncode == 0 else ""


@functools.lru_cache(maxsize=None)
def version():
    """(major, minor, patch) of the installed OpenCode, None when unknown."""
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", run("--version", timeout=20))
    return tuple(int(x) for x in m.groups()) if m else None


def is_v2(ver=None):
    ver = ver if ver is not None else version()
    return bool(ver) and ver[0] >= 2


def model_args(model, variant=None, ver=None):
    """`opencode run` flags for a model and its reasoning variant: 2.x writes provider/model#variant,
    1.x has --variant."""
    if not variant:
        return ["-m", model]
    if is_v2(ver):
        return ["-m", f"{model}#{variant}"]
    return ["-m", model, "--variant", variant]


def api(path, directory=None):
    """JSON from OpenCode 2.x's local server, None when it is not there."""
    args = ["api", "GET", path] + (["-H", f"x-opencode-directory:{directory}"] if directory else [])
    try:
        return json.loads(run(*args))
    except ValueError:
        return None


def catalog():
    """Every model the user can pick now: [{"id": "provider/model", "provider", "provider_name",
    "name", "variants", "status"}], sorted by provider and name. Disabled models are left out."""
    data = api("/api/model") if is_v2() else None
    if data and isinstance(data.get("data"), list):
        names = {p.get("id"): p.get("name") for p in (api("/api/provider") or {}).get("data", [])}
        out = []
        for m in data["data"]:
            if m.get("enabled") is False:
                continue
            provider = m.get("providerID", "")
            out.append({"id": f"{provider}/{m.get('id')}", "provider": provider,
                        "provider_name": names.get(provider) or provider,
                        "name": m.get("name") or m.get("id"),
                        "variants": [v.get("id") for v in m.get("variants") or [] if v.get("id")],
                        "status": m.get("status", "")})
        return sorted(out, key=lambda m: (m["provider"], m["name"].lower()))
    out = []
    for line in run("models").splitlines():
        line = line.strip()
        if "/" in line and " " not in line:
            provider = line.split("/", 1)[0]
            out.append({"id": line, "provider": provider, "provider_name": provider,
                        "name": line.split("/", 1)[1], "variants": [], "status": ""})
    return out


def providers(models):
    """{provider: {"name", "models"}} in the catalog."""
    out = {}
    for m in models:
        p = out.setdefault(m["provider"], {"name": m["provider_name"], "models": 0})
        p["models"] += 1
    return out


def search(models, provider=None, text=None):
    """The models of one provider, or whose id or name contains every word of text."""
    words = (text or "").lower().split()
    return [m for m in models if (not provider or m["provider"] == provider)
            and all(w in (m["id"] + " " + m["name"]).lower() for w in words)]


def db_path(home=None):
    return os.path.join(home or os.path.expanduser("~"), ".local", "share", "opencode", "opencode.db")


def state_models(home=None):
    """The models the user starred and picked lately in OpenCode (state/model.json): favorites
    first. [("provider/model", 0)]"""
    path = os.path.join(home or os.path.expanduser("~"), ".local", "state", "opencode", "model.json")
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return []
    out = []
    for key in ("favorite", "recent"):
        for m in data.get(key) or []:
            if isinstance(m, dict) and m.get("providerID") and m.get("modelID"):
                item = (f"{m['providerID']}/{m['modelID']}", 0)
                if item not in out:
                    out.append(item)
    return out


def recent(limit=8, home=None):
    """Favorites and recent picks of OpenCode, then the models the user ran most:
    [("provider/model", sessions)]."""
    picked = state_models(home)
    seen = {k for k, _ in picked}
    return (picked + [kv for kv in used_most(home) if kv[0] not in seen])[:limit]


def used_most(home=None):
    """The models the user ran most in OpenCode, most used first: [("provider/model", sessions)]."""
    path = db_path(home)
    if not os.path.isfile(path):
        return []
    counts = {}
    try:
        db = sqlite3.connect(f"file:{path}?mode=ro", uri=True, timeout=2)
        try:
            tables = {r[0] for r in db.execute("select name from sqlite_master where type='table'")}
            if "session_v2" in tables:  # 2.x: one model per session
                for (raw,) in db.execute("select model from session_v2 where model is not null"):
                    try:
                        m = json.loads(raw)
                    except ValueError:
                        continue
                    if m.get("providerID") and m.get("id"):
                        key = f"{m['providerID']}/{m['id']}"
                        counts[key] = counts.get(key, 0) + 1
            elif "message" in tables:  # 1.x: the assistant messages carry it
                for (raw,) in db.execute("select data from message"):
                    try:
                        m = json.loads(raw)
                    except ValueError:
                        continue
                    if m.get("role") == "assistant" and m.get("providerID") and m.get("modelID"):
                        key = f"{m['providerID']}/{m['modelID']}"
                        counts[key] = counts.get(key, 0) + 1
        finally:
            db.close()
    except sqlite3.Error:
        return []
    return sorted(counts.items(), key=lambda kv: -kv[1])


@functools.lru_cache(maxsize=None)
def python_command():
    """How to start Python in a shell on this machine. On Windows `python3` is often the Microsoft
    Store placeholder, which prints an error and exits: the first name that really runs wins,
    else the interpreter running this script."""
    for name in ("python3", "python", "py"):
        if not shutil.which(name):
            continue
        cmd = [name, "-3"] if name == "py" else [name]
        try:
            ok = subprocess.run(cmd + ["-c", "import sys; sys.exit(sys.version_info < (3, 9))"],
                                capture_output=True, timeout=20).returncode == 0
        except (OSError, subprocess.SubprocessError):
            ok = False
        if ok:
            return " ".join(cmd)
    exe = sys.executable.replace("\\", "/")
    return f'"{exe}"' if " " in exe else exe
