"""The library: the skills, commands and rules of Everything Claude Code (ECC), imported by
tools/import_ecc.py into ../library/<id>/MAIN.md with ../library/index.json.

The orchestrator searches it (`tw.py library search <words>`) and gives an agent the path of the
entries its work needs; no app loads them by itself. The entries the user switches on
(settings library.packs.<pack>, library.skills.<id>) are installed as native skills:
    Claude Code  ~/.claude/skills/<id>/SKILL.md
    agy          ~/.gemini/config/skills/<id>/SKILL.md
    OpenCode     ~/.config/opencode/skills/<id>/SKILL.md
A folder holds MARK when team-workflow wrote it; any other folder with the same name is left alone.
"""
import json
import os
import re
import shutil

import settings

HERE = os.path.dirname(os.path.abspath(__file__))
LIBRARY = os.path.normpath(os.path.join(HERE, "..", "library"))
MARK = ".team-workflow-library"  # inside an installed folder: the hash of the entry it holds


def index():
    try:
        with open(os.path.join(LIBRARY, "index.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {"source": {}, "packs": {}, "entries": []}


def entries():
    return {e["id"]: e for e in index()["entries"]}


def main_file(eid):
    return os.path.join(LIBRARY, eid, "MAIN.md")


def search(words, limit=20):
    """Entries ranked by how many of the words their id and description contain (id counts more)."""
    terms = [w for w in re.split(r"\W+", " ".join(words).lower()) if len(w) > 1]
    ranked = []
    for e in entries().values():
        eid, text = e["id"].lower(), (e["id"] + " " + e["description"] + " " + e["pack"]).lower()
        score = sum(3 * (t in eid) + text.count(t) for t in terms)
        hits = sum(t in text for t in terms)
        if hits:
            ranked.append((-hits, -score, e["id"], e))
    return [e for *_, e in sorted(ranked)[:limit]]


def is_on(config, entry):
    table = config.get("library", {})
    chosen, packs = table.get("skills", {}), table.get("packs", {})
    if entry["id"] in chosen and entry["id"] != "default":
        return bool(chosen[entry["id"]])
    return bool(packs.get(entry["pack"], packs.get("default")))


def wanted(config):
    """The ids to install: the entries switched on and what they require."""
    found = entries()
    ids = {i for i, e in found.items() if is_on(config, e)}
    for i in list(ids):
        ids.update(r for r in found[i].get("requires", []) if r in found)
    return ids


def native_dir(app):
    home = os.path.expanduser("~")
    return {"claude": os.path.join(home, ".claude", "skills"),
            "agy": os.path.join(home, ".gemini", "config", "skills"),
            "opencode": os.path.join(home, ".config", "opencode", "skills")}[app]


def installed_hash(folder):
    try:
        with open(os.path.join(folder, MARK), encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return None


def sync(app, config=None, root=None, dest=None, dry_run=False):
    """Install the entries switched on as skills of one app and remove ours that are off.
    Returns {"written", "removed", "skipped"} (skipped: a folder with that name is not ours)."""
    config = config or settings.load(root)
    dest = dest or native_dir(app)
    found, ids = entries(), wanted(config)
    result = {"written": [], "removed": [], "skipped": []}
    for eid in sorted(ids):
        target = os.path.join(dest, eid)
        have = installed_hash(target)
        if os.path.exists(target) and have is None:
            result["skipped"].append(eid)
            continue
        if have == found[eid]["hash"]:
            continue
        if not dry_run:
            shutil.rmtree(target, ignore_errors=True)
            shutil.copytree(os.path.join(LIBRARY, eid), target)
            os.replace(os.path.join(target, "MAIN.md"), os.path.join(target, "SKILL.md"))
            with open(os.path.join(target, MARK), "w", encoding="utf-8") as f:
                f.write(found[eid]["hash"] + "\n")
        result["written"].append(eid)
    for name in sorted(os.listdir(dest)) if os.path.isdir(dest) else []:
        target = os.path.join(dest, name)
        if name not in ids and installed_hash(target) is not None:
            if not dry_run:
                shutil.rmtree(target, ignore_errors=True)
            result["removed"].append(name)
    return result


def pack_rows(config):
    """(pack, entries, on, description) for `tw.py library`."""
    data, found = index(), entries().values()
    rows = []
    for pack, about in data["packs"].items():
        mine = [e for e in found if e["pack"] == pack]
        rows.append((pack, len(mine), sum(is_on(config, e) for e in mine), about))
    return rows
