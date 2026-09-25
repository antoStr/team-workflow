#!/usr/bin/env python3
"""Show the installed team-workflow versions and update them, in Claude Code and in agy.

Latest version: the highest vX.Y.Z tag of the repository. Claude Code updates through its
marketplace; agy has no update command, so the plugin is uninstalled and installed again.

    python3 update_plugin.py [--check] [--harness claude|agy|all] [--source URL_OR_PATH]
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import time

NAME = "team-workflow"
REPO = "https://github.com/antoStr/team-workflow"
AGY_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins", NAME)
PLUGIN = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))


def run(*cmd, timeout=180):
    """(returncode, output) of a command; never raises."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as e:
        return 1, str(e)
    return out.returncode, (out.stdout + out.stderr).strip()


def vkey(v):
    return tuple(int(x) for x in v.split("."))


def latest_tag(ls_remote):
    """Highest X.Y.Z among the vX.Y.Z tags printed by `git ls-remote --tags`."""
    tags = re.findall(r"refs/tags/v(\d+\.\d+\.\d+)$", ls_remote, re.M)
    return max(tags, key=vkey) if tags else None


def fetch_latest(timeout=30):
    code, out = run("git", "ls-remote", "--tags", "--refs", REPO, timeout=timeout)
    return latest_tag(out) if code == 0 else None


def own_version():
    """Version of the plugin this script belongs to."""
    for rel in (os.path.join(".claude-plugin", "plugin.json"), "plugin.json"):
        try:
            with open(os.path.join(PLUGIN, rel), encoding="utf-8") as f:
                version = json.load(f).get("version")
        except (OSError, ValueError):
            continue
        if version:
            return version
    return None


def newer_version(max_age=86400):
    """The latest version when it is newer than this plugin, asking GitHub at most once a day
    (~/.team-workflow/update-check.json); None otherwise or on any error."""
    cache = os.path.join(os.path.expanduser("~"), ".team-workflow", "update-check.json")
    try:
        with open(cache, encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, ValueError):
        data = {}
    if time.time() - data.get("checked", 0) > max_age:
        data = {"checked": time.time(), "latest": fetch_latest(timeout=3)}
        try:
            os.makedirs(os.path.dirname(cache), exist_ok=True)
            with open(cache, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            pass
    latest, mine = data.get("latest"), own_version()
    try:
        return latest if latest and mine and vkey(latest) > vkey(mine) else None
    except ValueError:
        return None


def claude_version(plugin_list):
    """Version of team-workflow in the output of `claude plugin list`."""
    m = re.search(rf"{NAME}@\S+\s+Version:\s*(\S+)", plugin_list)
    return m.group(1) if m else None


def agy_version():
    try:
        with open(os.path.join(AGY_DIR, "plugin.json"), encoding="utf-8") as f:
            return json.load(f).get("version", "older than 0.4.0")
    except (OSError, ValueError):
        return None


def installed(harness):
    if not shutil.which(harness):
        return None
    if harness == "claude":
        return claude_version(run("claude", "plugin", "list")[1])
    return agy_version()


def update(harness, source):
    """Run the update steps; (ok, log)."""
    if harness == "claude":
        steps = [("claude", "plugin", "marketplace", "update", NAME),
                 ("claude", "plugin", "update", f"{NAME}@{NAME}")]
    else:
        steps = [("agy", "plugin", "uninstall", NAME), ("agy", "plugin", "install", source),
                 ("python3", os.path.join(AGY_DIR, "skills", NAME, "scripts", "install_agy.py"),
                  "--agents-only")]  # the new version's roles, as agy subagents
    log = []
    for cmd in steps:
        code, out = run(*cmd)
        log.append(f"$ {' '.join(cmd)}\n{out}")
        if code:
            if cmd[-2:] == ("install", source):
                log.append(f"agy install failed: the plugin is uninstalled. Retry: agy plugin install {source}")
            return False, "\n".join(log)
    return True, "\n".join(log)


def agy_plugins_dir():
    return os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins")


def agy_source(name):
    """Where agy installed a plugin from: the origin of its clone, or None."""
    code, out = run("git", "-C", os.path.join(agy_plugins_dir(), name), "remote", "get-url", "origin",
                    timeout=10)
    return out.strip() if code == 0 and out.strip() else None


def agy_update(names=None):
    """`agy plugin update`: reinstall each plugin from where it came from. Returns (ok, log)."""
    folder = agy_plugins_dir()
    installed_names = sorted(n for n in os.listdir(folder) if os.path.isdir(os.path.join(folder, n))) \
        if os.path.isdir(folder) else []
    names = names or installed_names
    ok_all, log = True, []
    for name in names:
        if name not in installed_names:
            log.append(f"{name}: not installed in agy ({', '.join(installed_names) or 'none'})")
            ok_all = False
            continue
        source = agy_source(name)
        if not source:
            log.append(f"{name}: agy did not keep its source; reinstall it once with "
                       f"agy plugin install <url or path>")
            ok_all = False
            continue
        if not os.path.isdir(source):  # check the source answers before removing anything
            code, out = run("git", "ls-remote", "--heads", source, timeout=60)
            if code:
                log.append(f"{name}: {source} cannot be reached, nothing changed\n{out.splitlines()[-1] if out else ''}")
                ok_all = False
                continue
        backup = os.path.join(os.path.expanduser("~"), ".team-workflow", "agy-backup", name)
        shutil.rmtree(backup, ignore_errors=True)
        shutil.copytree(os.path.join(folder, name), backup, symlinks=True)
        code, out = run("agy", "plugin", "uninstall", name)
        if code:
            log.append(f"{name}: uninstall failed, nothing changed\n{out}")
            ok_all = False
            continue
        code, out = run("agy", "plugin", "install", source)
        if code:
            restored, _ = run("agy", "plugin", "install", backup)
            log.append(f"{name}: install from {source} failed; "
                       + ("the previous version is back" if restored == 0 else
                          f"restore it with: agy plugin install {backup}") + f"\n{out}")
            ok_all = False
            continue
        shutil.rmtree(backup, ignore_errors=True)
        log.append(f"{name}: reinstalled from {source}")
        if name == NAME:  # the new version's roles, as agy subagents
            script = os.path.join(folder, NAME, "skills", NAME, "scripts", "install_agy.py")
            code, out = run("python3", script, "--agents-only")
            log.append(out if out else "agents refreshed")
    log.append("Restart agy to load the updates.")
    return ok_all, "\n".join(log)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Check and update the installed team-workflow plugin.")
    ap.add_argument("--check", action="store_true", help="only show installed and latest versions")
    ap.add_argument("--harness", choices=("claude", "agy", "all"), default="all")
    ap.add_argument("--source", default=REPO, help="what agy installs from (default: GitHub)")
    args = ap.parse_args(argv)

    latest = fetch_latest()
    print(f"latest: {latest or 'unknown (no network?)'}")
    failed = False
    for harness in (("claude", "agy") if args.harness == "all" else (args.harness,)):
        before = installed(harness)
        if before is None:
            print(f"{harness}: not installed")
            continue
        current = latest and re.fullmatch(r"\d+\.\d+\.\d+", before) and vkey(before) >= vkey(latest)
        print(f"{harness}: {before}" + (" (up to date)" if current else ""))
        if args.check or current:
            continue
        ok, log = update(harness, args.source)
        print(log)
        print(f"{harness}: {before} -> {installed(harness)}" if ok else f"{harness}: update FAILED")
        failed |= not ok
    if not args.check:
        print("Restart the session to load the new version.")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
