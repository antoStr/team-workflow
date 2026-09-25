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

NAME = "team-workflow"
REPO = "https://github.com/antoStr/team-workflow"
AGY_DIR = os.path.join(os.path.expanduser("~"), ".gemini", "config", "plugins", NAME)


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
        steps = [("agy", "plugin", "uninstall", NAME), ("agy", "plugin", "install", source)]
    log = []
    for cmd in steps:
        code, out = run(*cmd)
        log.append(f"$ {' '.join(cmd)}\n{out}")
        if code:
            if cmd[-2:] == ("install", source):
                log.append(f"agy install failed: the plugin is uninstalled. Retry: agy plugin install {source}")
            return False, "\n".join(log)
    return True, "\n".join(log)


def main():
    ap = argparse.ArgumentParser(description="Check and update the installed team-workflow plugin.")
    ap.add_argument("--check", action="store_true", help="only show installed and latest versions")
    ap.add_argument("--harness", choices=("claude", "agy", "all"), default="all")
    ap.add_argument("--source", default=REPO, help="what agy installs from (default: GitHub)")
    args = ap.parse_args()

    code, out = run("git", "ls-remote", "--tags", "--refs", REPO, timeout=30)
    latest = latest_tag(out) if code == 0 else None
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
