"""Add-on plugins that team-workflow installs, updates and removes in Claude Code and agy.

The catalog lists the known ones; any other GitHub repository with a Claude Code marketplace
(or `plugin@marketplace` already known to Claude Code) can be added too. The chosen add-ons are
kept in the settings (`addons.<name>`), so `update` refreshes them with team-workflow.

How each app installs an add-on:
- Claude Code: its marketplace (`claude plugin marketplace add`, `claude plugin install`);
  "skills" (a repository without a marketplace): its skills copied into ~/.claude/skills.
- agy, "plugin": `agy plugin install <GitHub URL>` (the repository has a plugin.json).
- agy, "skills": agy has no plugin for it, so the repository's skills/<name>/SKILL.md folders
  (or <skills_dir>/<name>/SKILL.md) are copied into ~/.gemini/config/skills (marked, so only ours are ever removed).
- agy, "ecc": ECC's own Antigravity installer, per project (it writes <repository>/.agents).
- OpenCode, "skills": the skills copied into ~/.config/opencode/skills (OpenCode also reads
  ~/.claude/skills and ~/.agents/skills: skills already there are not copied twice).
- OpenCode, "plugin-file": the repository's .opencode/plugins/<name>.mjs, from a local clone,
  listed in the "plugin" array of ~/.config/opencode/opencode.json.
- OpenCode, "ecc": ECC's own OpenCode installer (it writes to ~/.config/opencode).
"""
import json
import os
import re
import shutil
import subprocess
import urllib.request

import settings

CATALOG = {
    "caveman": {
        "repo": "JuliusBrussee/caveman", "marketplace": "caveman", "plugin": "caveman",
        "agy": "skills", "opencode": "skills", "license": "MIT and BSL (see its LICENSING.md)",
        "about": "compressed answers: fewer output tokens, same technical content",
    },
    "ponytail": {
        "repo": "DietrichGebert/ponytail", "marketplace": "ponytail", "plugin": "ponytail",
        "agy": "plugin", "opencode": "plugin-file", "license": "MIT",
        "about": "the laziest working solution: less code, stdlib and platform first",
    },
    "ecc": {
        "repo": "affaan-m/everything-claude-code", "marketplace": "ecc", "plugin": "ecc",
        "agy": "ecc", "opencode": "ecc", "license": "MIT",
        "about": "Everything Claude Code: 68 agents, 292 skills, rules and hooks",
    },
    # The frontend set (`addons add frontend`): the frontend roles use these skills when present.
    "impeccable": {
        "repo": "pbakaus/impeccable", "marketplace": "impeccable", "plugin": "impeccable",
        "agy": "skills", "opencode": "skills", "skills_dir": ".agents/skills", "license": "Apache-2.0",
        "about": "design, critique, audit, polish and harden frontend interfaces",
    },
    "taste": {
        "repo": "Leonxlnx/taste-skill", "marketplace": "taste-skill", "plugin": "taste-skill",
        "agy": "skills", "opencode": "skills", "license": "MIT",
        "about": "anti-slop art direction for landing pages, sites and app screens",
    },
    "frontend-design": {
        "repo": "anthropics/claude-plugins-official", "marketplace": "claude-plugins-official",
        "plugin": "frontend-design", "agy": "skills", "opencode": "skills",
        "skills_dir": "plugins/frontend-design/skills", "license": "Apache-2.0",
        "about": "Anthropic's frontend-design skill: distinctive, non-templated visual design",
    },
    "solar-icons": {
        "repo": "saoudi-h/solar-icons", "claude": "skills", "agy": "skills", "opencode": "skills",
        "license": "MIT (icons by 480 Design, CC BY 4.0)",
        "about": "Solar icon set: exact icon names and framework imports",
    },
    "cloudflare": {
        "repo": "cloudflare/skills", "marketplace": "cloudflare", "plugin": "cloudflare",
        "agy": "skills", "opencode": "skills", "license": "Apache-2.0",
        "about": "Cloudflare skills: Workers best practices, Zero Trust (cloudflare-one), Turnstile, perf",
    },
}
BUNDLES = {"frontend": ("impeccable", "taste", "frontend-design", "solar-icons", "cloudflare")}
APPS = ("claude", "agy", "opencode")


def present(app):
    """Is the app on this machine (its command, or for OpenCode its config folder)?"""
    return bool(shutil.which(app)) or (app == "opencode" and os.path.isdir(opencode_dir()))


def opencode_dir():
    return home(".config", "opencode")
MARK = ".team-workflow-addon"


def home(*parts):
    return os.path.join(os.path.expanduser("~"), *parts)


def run(*cmd, cwd=None, timeout=600):
    """(ok, output) of a command; never raises."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, cwd=cwd)
    except (OSError, subprocess.SubprocessError) as e:
        return False, str(e)
    return out.returncode == 0, (out.stdout + out.stderr).strip()


def fetch_json(url):
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            return json.load(r)
    except (OSError, ValueError):
        return None


def resolve(spec):
    """(name, entry) for a catalog name, `owner/repo`, a GitHub URL or `plugin@marketplace`."""
    if spec in CATALOG:
        return spec, dict(CATALOG[spec])
    if re.fullmatch(r"[\w.-]+@[\w.-]+", spec):
        plugin, market = spec.split("@")
        return plugin, {"plugin": plugin, "marketplace": market, "agy": "plugin@marketplace",
                        "about": f"{spec} from a marketplace Claude Code already knows"}
    m = re.fullmatch(r"(?:https://github\.com/)?([\w.-]+/[\w.-]+?)(?:\.git)?/?", spec)
    if not m:
        raise ValueError(f"not a catalog name, owner/repo, GitHub URL or plugin@marketplace: {spec}")
    repo = m.group(1)
    raw = f"https://raw.githubusercontent.com/{repo}/HEAD/"
    market = fetch_json(raw + ".claude-plugin/marketplace.json") or {}
    plugins = market.get("plugins") or []
    if not plugins:
        raise ValueError(f"{repo} has no .claude-plugin/marketplace.json with a plugin")
    plugin = plugins[0]["name"]
    agy = "plugin" if fetch_json(raw + "plugin.json") else "skills"
    return plugin, {"repo": repo, "marketplace": market["name"], "plugin": plugin, "agy": agy,
                    "opencode": "plugin-file" if plugin_file_hint(repo) else "skills",
                    "about": (plugins[0].get("description") or market.get("description") or "")[:100]}


def plugin_file_hint(repo):
    """Does the repository ship an OpenCode plugin file (.opencode/plugins/*.js|mjs)?"""
    listing = fetch_json(f"https://api.github.com/repos/{repo}/contents/.opencode/plugins") or []
    return any(isinstance(x, dict) and re.search(r"\.(m?js|ts)$", x.get("name", "")) for x in listing)


def chosen(config=None):
    return (config or settings.load()).get("addons", {})


# --- Claude Code -------------------------------------------------------------------------

def claude_skills_dir():
    return home(".claude", "skills")


def claude_version(entry, name=None):
    if entry.get("claude") == "skills":  # a repository without a Claude Code marketplace
        return "skills" if name and agy_skill_dirs(name, claude_skills_dir()) else None
    try:
        with open(home(".claude", "plugins", "installed_plugins.json"), encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        return None
    rows = data.get("plugins", data).get(f"{entry['plugin']}@{entry['marketplace']}") or []
    return (rows[0].get("version") or "installed") if rows else None


def claude_markets():
    try:
        with open(home(".claude", "plugins", "known_marketplaces.json"), encoding="utf-8") as f:
            return set(json.load(f))
    except (OSError, ValueError):
        return set()


def claude_steps(action, entry):
    pid = f"{entry['plugin']}@{entry['marketplace']}"
    if action == "remove":
        return [("claude", "plugin", "uninstall", pid)]
    steps = []
    if entry["marketplace"] not in claude_markets():
        if not entry.get("repo"):
            raise ValueError(f"Claude Code does not know the marketplace {entry['marketplace']}")
        steps.append(("claude", "plugin", "marketplace", "add", entry["repo"]))
    else:
        steps.append(("claude", "plugin", "marketplace", "update", entry["marketplace"]))
    steps.append(("claude", "plugin", "update" if action == "update" else "install", pid))
    return steps


# --- agy ---------------------------------------------------------------------------------

def agy_plugins():
    ok, out = run("agy", "plugin", "list", timeout=30)
    try:
        return {p["name"] for p in json.loads(out[out.index("{"):]).get("imports", [])} if ok else set()
    except ValueError:
        return set()


def agy_skills_dir():
    return home(".gemini", "config", "skills")


def opencode_skills_dir():
    return os.path.join(opencode_dir(), "skills")


def agy_skill_dirs(name, root=None):
    """Skill folders this add-on copied into agy (or into root)."""
    root = root or agy_skills_dir()
    found = []
    for d in sorted(os.listdir(root)) if os.path.isdir(root) else []:
        try:
            with open(os.path.join(root, d, MARK), encoding="utf-8") as f:
                if f.read().strip() == name:
                    found.append(d)
        except OSError:
            continue
    return found


def clone_dir(name):
    return os.path.join(settings.home_dir(), "addons", name)


def agy_version(name, entry):
    kind = entry.get("agy")
    if kind in ("plugin", "plugin@marketplace"):
        return "installed" if entry["plugin"] in agy_plugins() else None
    if kind == "skills":
        if not agy_skill_dirs(name):
            return None
        ok, out = run("git", "-C", clone_dir(name), "rev-parse", "--short", "HEAD")
        return f"git {out}" if ok else "installed"
    if kind == "ecc":
        return "per project (ecc-universal)"
    return None


def fetch(name, entry):
    """Clone or pull the add-on's repository into ~/.team-workflow/addons/<name>."""
    src = clone_dir(name)
    if os.path.isdir(os.path.join(src, ".git")):
        ok, out = run("git", "-C", src, "pull", "--ff-only", "-q")
    else:
        os.makedirs(os.path.dirname(src), exist_ok=True)
        ok, out = run("git", "clone", "-q", "--depth", "1", f"https://github.com/{entry['repo']}", src)
    return ok, out, src


def copy_skills(name, entry, dest=None, also_seen=()):
    """Clone or pull the repository, then copy its skills into agy (or dest). Skills whose name
    exists in a folder of also_seen are skipped: the app already loads them. Returns (ok, log)."""
    ok, out, src = fetch(name, entry)
    if not ok:
        return False, out
    dest, copied, skipped = dest or agy_skills_dir(), [], []
    os.makedirs(dest, exist_ok=True)
    ours = set(agy_skill_dirs(name, dest))
    base = os.path.join(src, *entry.get("skills_dir", "skills").split("/"))
    for d in sorted(os.listdir(base)) if os.path.isdir(base) else []:
        skill = os.path.join(base, d)
        if not os.path.isfile(os.path.join(skill, "SKILL.md")):
            continue
        target = os.path.join(dest, d)
        if any(os.path.isfile(os.path.join(seen, d, "SKILL.md")) for seen in also_seen):
            continue  # already loaded from another skills folder
        if os.path.exists(target) and d not in ours:
            skipped.append(d)  # someone else's skill with the same name
            continue
        shutil.rmtree(target, ignore_errors=True)
        shutil.copytree(skill, target, ignore=shutil.ignore_patterns(".git"))
        with open(os.path.join(target, MARK), "w", encoding="utf-8") as f:
            f.write(name + "\n")
        copied.append(d)
    log = f"copied into {dest}: {', '.join(copied) or 'nothing (already available)'}"
    return True, log + (f"\nskipped, not ours: {', '.join(skipped)}" if skipped else "")


def opencode_config_path():
    return os.path.join(opencode_dir(), "opencode.json")


def edit_opencode_plugins(path_to_add=None, path_to_remove=None):
    """Add or remove one entry of the "plugin" array of ~/.config/opencode/opencode.json."""
    cfg = opencode_config_path()
    data = {"$schema": "https://opencode.ai/config.json"}
    if os.path.isfile(cfg):
        try:
            with open(cfg, encoding="utf-8") as f:
                data = json.load(f)
        except ValueError:
            raise ValueError(f"{cfg} is not plain JSON (comments?): add or remove the plugin by hand: "
                             f"{path_to_add or path_to_remove}")
    plugins = [p for p in data.get("plugin", []) if p != path_to_remove]
    if path_to_add and path_to_add not in plugins:
        plugins.append(path_to_add)
    data["plugin"] = plugins
    os.makedirs(os.path.dirname(cfg), exist_ok=True)
    with open(cfg, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        f.write("\n")
    return cfg


def opencode_plugin_file(name):
    folder = os.path.join(clone_dir(name), ".opencode", "plugins")
    files = sorted(f for f in os.listdir(folder) if re.search(r"\.(m?js|ts)$", f)) if os.path.isdir(folder) else []
    return os.path.join(folder, files[0]) if files else None


def opencode_version(name, entry):
    kind = entry.get("opencode")
    if kind == "skills":
        return f"{len(agy_skill_dirs(name, opencode_skills_dir()))} skills" if agy_skill_dirs(
            name, opencode_skills_dir()) else None
    if kind == "plugin-file":
        path = opencode_plugin_file(name)
        try:
            with open(opencode_config_path(), encoding="utf-8") as f:
                listed = path in json.load(f).get("plugin", [])
        except (OSError, ValueError, TypeError):
            listed = False
        return "plugin" if path and listed else None
    if kind == "ecc":
        state = os.path.join(opencode_dir(), "ecc-install-state.json")
        return "installed (ecc-universal)" if os.path.isfile(state) else None
    return None


def opencode_apply(action, name, entry, root):
    kind = entry.get("opencode", "skills")
    if kind == "skills":
        dest = opencode_skills_dir()
        if action == "remove":
            for d in agy_skill_dirs(name, dest):
                shutil.rmtree(os.path.join(dest, d), ignore_errors=True)
            return True, f"removed its skills from {dest}"
        return copy_skills(name, entry, dest, also_seen=(home(".claude", "skills"), home(".agents", "skills")))
    if kind == "plugin-file":
        if action == "remove":
            path = opencode_plugin_file(name)
            return True, f"removed from {edit_opencode_plugins(path_to_remove=path)}" if path else "not installed"
        ok, out, _ = fetch(name, entry)
        path = opencode_plugin_file(name)
        if not ok or not path:
            return False, out or f"{entry.get('repo')} has no .opencode/plugins file"
        try:
            return True, f"plugin {path} listed in {edit_opencode_plugins(path_to_add=path)}"
        except ValueError as e:
            return False, str(e)
    if kind == "ecc":
        if not root:
            return False, "run this inside a git repository (ECC's installer starts from a project)"
        version = ecc_version()
        if not version:
            return False, "npm view ecc-universal failed (needs Node.js and network)"
        verb = ["uninstall"] if action == "remove" else ["install", "--profile", "minimal",
                                                         "--target", "opencode"]
        ok, out = run("npx", "-y", f"ecc-universal@{version}", *verb, cwd=root)
        return ok, f"$ npx ecc-universal@{version} {' '.join(verb)}  (in {root})\n{out[-1500:]}"
    return False, f"no OpenCode install method for {name}"


def ecc_version():
    ok, out = run("npm", "view", "ecc-universal", "version", timeout=60)
    return out.strip() if ok and re.fullmatch(r"\d+\.\d+\.\d+", out.strip()) else None


def agy_apply(action, name, entry, root):
    kind = entry.get("agy")
    if kind == "skills":
        if action == "remove":
            for d in agy_skill_dirs(name):
                shutil.rmtree(os.path.join(agy_skills_dir(), d), ignore_errors=True)
            return True, f"removed its skills from {agy_skills_dir()}"
        return copy_skills(name, entry)
    if kind == "ecc":
        if not root:
            return False, "ECC installs into a project in agy: run this inside a git repository"
        version = ecc_version()
        if not version:
            return False, "npm view ecc-universal failed (needs Node.js and network)"
        verb = ["uninstall"] if action == "remove" else ["install", "--profile", "minimal",
                                                         "--target", "antigravity"]
        ok, out = run("npx", "-y", f"ecc-universal@{version}", *verb, cwd=root)
        log = f"$ npx ecc-universal@{version} {' '.join(verb)}  (in {root})\n{out}"
        import roles
        shadow = roles.shadowed("agy", root) if ok and action != "remove" else []
        if shadow:
            log += ("\nnote: in this project agy now uses ECC's agents instead of team-workflow's for: "
                    + ", ".join(shadow))
        return ok, log
    source = (f"https://github.com/{entry['repo']}" if kind == "plugin"
              else f"{entry['plugin']}@{entry['marketplace']}")
    log = []
    if action != "add" and entry["plugin"] in agy_plugins():
        ok, out = run("agy", "plugin", "uninstall", entry["plugin"])
        log.append(out)
        if not ok or action == "remove":
            return ok, "\n".join(log)
    elif action == "remove":
        return True, "not installed in agy"
    ok, out = run("agy", "plugin", "install", source)
    log.append(f"$ agy plugin install {source}\n{out}")
    if not ok and action == "update":
        log.append(f"the old version is uninstalled; retry: agy plugin install {source}")
    return ok, "\n".join(log)


# --- commands ----------------------------------------------------------------------------

def status_lines(root=None):
    config = settings.load(root)
    picked = chosen(config)
    names = list(CATALOG) + [n for n in picked if n not in CATALOG]
    lines = []
    for name in names:
        entry = picked.get(name) or CATALOG[name]
        claude = claude_version(entry, name) if present("claude") else None
        agy = agy_version(name, entry) if present("agy") else None
        oc = opencode_version(name, entry) if present("opencode") else None
        mark = "*" if name in picked else " "
        lines.append(f"{mark} {name:<16} claude: {claude or '-':<10} agy: {agy or '-':<16} "
                     f"opencode: {oc or '-':<16} {entry.get('about', '')[:60]}")
    return lines


def apply(action, spec, apps=APPS, root=None):
    """add, update or remove one add-on (or a bundle of them) in the chosen apps; returns (ok, log)."""
    if spec in BUNDLES:
        results = [(n, *apply(action, n, apps, root)) for n in BUNDLES[spec]]
        return (all(ok for _, ok, _ in results),
                "\n".join(f"== {n}\n{out}" for n, _, out in results))
    if action == "add":
        name, entry = resolve(spec)
    else:
        name = spec
        entry = chosen(settings.load(root)).get(name) or CATALOG.get(name)
        if not entry:
            raise ValueError(f"unknown add-on {name!r}")
    log, ok_all = [], True
    for app in apps:
        if not present(app):
            log.append(f"{app}: not installed, skipped")
            continue
        if app == "claude" and entry.get("claude") == "skills":
            if action == "remove":
                for d in agy_skill_dirs(name, claude_skills_dir()):
                    shutil.rmtree(os.path.join(claude_skills_dir(), d), ignore_errors=True)
                ok, out = True, f"removed its skills from {claude_skills_dir()}"
            else:
                ok, out = copy_skills(name, entry, claude_skills_dir())
            log.append(f"claude: {out}")
            ok_all &= ok
        elif app == "claude":
            try:
                steps = claude_steps(action, entry)
            except ValueError as e:
                log.append(f"claude: {e}")
                ok_all = False
                continue
            for cmd in steps:
                ok, out = run(*cmd)
                log.append(f"$ {' '.join(cmd)}\n{out}")
                if not ok:
                    ok_all = False
                    break
        elif app == "agy":
            ok, out = agy_apply(action, name, entry, root)
            log.append(f"agy: {out}")
            ok_all &= ok
        else:
            ok, out = opencode_apply(action, name, entry, root)
            log.append(f"opencode: {out}")
            ok_all &= ok
    if action == "add":
        settings.save(f"addons.{name}", dict(entry, apps=list(apps)))
    elif action == "remove":
        settings.save(f"addons.{name}", None)
    log.append("Restart the apps to load the change.")
    return ok_all, "\n".join(log)


def update_all(root=None):
    """Update every chosen add-on in the apps it was added to; returns (ok, log)."""
    picked = chosen(settings.load(root))
    if not picked:
        return True, "add-ons: none chosen"
    ok_all, log = True, []
    for name, entry in picked.items():
        ok, out = apply("update", name, tuple(entry.get("apps", APPS)), root)
        ok_all &= ok
        log.append(f"== {name}\n{out}")
    return ok_all, "\n".join(log)
