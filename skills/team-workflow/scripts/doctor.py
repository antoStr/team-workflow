"""Health check, repair and clean uninstall of team-workflow in Claude Code and agy (the doctor,
repair and uninstall tools ECC keeps for Pro, here local and free).

    checks(root)            -> [(status, area, message)]   status: ok, warn, fail
    repair(root)            -> [message]                    what --fix changed
    uninstall(everything)   -> [message]                    remove what team-workflow wrote
"""
import json
import os
import shutil
import sys

import addons
import audit
import memcheck
import roles
import settings
import update_plugin


def launcher_path():
    return os.path.join(os.path.expanduser("~"), ".local", "bin", "team-workflow")


def invalid_settings(path):
    """Keys of a settings file that the current version rejects."""
    bad = []
    for key, value in settings.flatten(settings._read(path)):
        if key.startswith("addons."):
            continue
        try:
            settings.parse_value(key, str(value).lower() if isinstance(value, bool) else str(value))
        except ValueError:
            bad.append(key)
    return bad


def checks(root=None):
    out = []

    def add(status, area, message):
        out.append((status, area, message))

    if sys.version_info < (3, 9):
        add("fail", "python", f"Python {sys.version.split()[0]}: team-workflow needs 3.9 or newer")
    else:
        add("ok", "python", sys.version.split()[0])

    newer = update_plugin.newer_version()
    for app in ("claude", "agy", "opencode"):
        version = update_plugin.installed(app)
        if app == "opencode" and version is None:
            if shutil.which("opencode"):
                add("warn", app, "team-workflow is not installed in OpenCode: tw.py install-opencode")
            continue
        if not shutil.which(app):
            continue
        if version is None:
            add("warn", app, "team-workflow is not installed in this app")
        elif newer and version != newer:
            add("warn", app, f"team-workflow {version} installed, {newer} available: tw.py update")
        else:
            add("ok", app, f"team-workflow {version}")

    for path in [settings.user_file()] + ([settings.project_file(root)] if root else []):
        if not os.path.isfile(path):
            continue
        try:
            with open(path, encoding="utf-8") as f:
                json.load(f)
        except ValueError:
            add("fail", "settings", f"{path} is not valid JSON")
            continue
        bad = invalid_settings(path)
        add("warn" if bad else "ok", "settings",
            f"{path}: " + (f"invalid keys {', '.join(bad)} (tw.py doctor --fix)" if bad else "valid"))

    config = settings.load(root)
    for app in roles.installed_apps():
        r = roles.sync(app, config=config, root=root, dry_run=True)
        stale = r["written"] + r["removed"]
        if stale:
            add("warn", f"{app} agents", f"{len(stale)} out of date ({', '.join(stale[:4])}...): "
                                         "tw.py agents sync")
        else:
            add("ok", f"{app} agents", "native agents match the settings")
        if r["skipped"]:
            add("warn", f"{app} agents", "files not written by team-workflow shadow these roles: "
                                         + ", ".join(r["skipped"]))
        project = roles.shadowed(app, root, config)
        if project:
            add("warn", f"{app} agents", "in this repository, project agents with the same name "
                "replace these roles (for example ECC's): " + ", ".join(project))

    for name, entry in addons.chosen(config).items():
        for app in entry.get("apps", addons.APPS):
            if shutil.which(app):
                version = (addons.claude_version(entry) if app == "claude"
                           else addons.agy_version(name, entry))
                add("ok" if version else "warn", f"add-on {name}",
                    f"{app}: {version or 'chosen but not installed (tw.py addons update)'}")

    if shutil.which("agy") and not os.path.isfile(launcher_path()):
        add("warn", "agy commands", "no team-workflow launcher for !team-workflow in agy "
                                    "(tw.py install-cli)")

    if root and os.path.isfile(os.path.join(root, "docs", "memory", "INDEX.md")):
        errors, warnings = memcheck.check(root)
        add("fail" if errors else "warn" if warnings else "ok", "memory",
            f"{len(errors)} errors, {len(warnings)} warnings (memcheck)")

    findings, scanned = audit.audit(root)
    serious = [f for f in findings if f["severity"] in ("critical", "high")]
    add("fail" if serious else "warn" if findings else "ok", "audit",
        f"{len(findings)} findings, {len(serious)} critical or high, in {scanned} files (tw.py audit)")
    return out


def repair(root=None):
    done = []
    for path, target in [(settings.user_file(), None)] + ([(settings.project_file(root), root)] if root else []):
        for key in invalid_settings(path) if os.path.isfile(path) else []:
            settings.save(key, None, target)
            done.append(f"removed invalid setting {key} from {path}")
    for app in roles.installed_apps():
        r = roles.sync(app, root=root)
        if r["written"] or r["removed"]:
            done.append(f"{app}: {len(r['written'])} agents written, {len(r['removed'])} removed")
    return done or ["nothing to repair"]


def uninstall(everything=False):
    """Remove what team-workflow wrote outside the plugins: native agents, add-on skill copies in
    agy, the launcher; with everything also ~/.team-workflow (settings, ledger, clones)."""
    done = []
    for app in roles.APPS:
        folder = roles.native_dir(app)
        for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            path = os.path.join(folder, name)
            try:
                with open(path, encoding="utf-8") as f:
                    ours = roles.ours(f.read())
            except OSError:
                ours = False
            if ours:
                os.remove(path)
                done.append(f"removed {path}")
    for name in addons.chosen():
        for d in addons.agy_skill_dirs(name):
            shutil.rmtree(os.path.join(addons.agy_skills_dir(), d), ignore_errors=True)
            done.append(f"removed agy skill {d} (add-on {name})")
    if os.path.isfile(launcher_path()):
        os.remove(launcher_path())
        done.append(f"removed {launcher_path()}")
    if everything and os.path.isdir(settings.home_dir()):
        shutil.rmtree(settings.home_dir())
        done.append(f"removed {settings.home_dir()} (settings, usage ledger, add-on clones)")
    done.append("the plugins themselves stay: claude plugin uninstall team-workflow@team-workflow; "
                "agy plugin uninstall team-workflow")
    return done
