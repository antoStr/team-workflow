#!/usr/bin/env python3
"""team-workflow commands that run without the model, so they spend no tokens.

    tw.py update [--check]                 update the plugin in Claude Code and agy
    tw.py settings                         show every setting and where it comes from
    tw.py settings set KEY VALUE [--project]
    tw.py settings reset KEY [--project]
    tw.py models                           models and efforts each app offers
    tw.py agents                           rewrite the agy subagents from the plugin's roles
    tw.py install-cli                      add a `team-workflow` command to ~/.local/bin

In Claude Code, /team-workflow:update-plugin, /team-workflow:settings and /team-workflow:models
are answered by a hook that runs this script. In agy, use its bash mode: !team-workflow update.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import install_agy
import settings
import update_plugin
from usage import load_pricing

EFFORTS = ("low", "medium", "high", "xhigh", "max")
LAUNCHER = '''#!/usr/bin/env python3
"""team-workflow launcher: runs tw.py from the installed plugin (Claude Code first, then agy)."""
import json, os, sys
home = os.path.expanduser("~")
paths = []
try:
    with open(os.path.join(home, ".claude", "plugins", "installed_plugins.json")) as f:
        data = json.load(f)
    paths += [e["installPath"] for e in data.get("plugins", data).get("team-workflow@team-workflow", [])]
except (OSError, ValueError, KeyError, AttributeError):
    pass
paths.append(os.path.join(home, ".gemini", "config", "plugins", "team-workflow"))
for p in paths:
    tw = os.path.join(p, "skills", "team-workflow", "scripts", "tw.py")
    if os.path.isfile(tw):
        os.execv(sys.executable, [sys.executable, tw, *sys.argv[1:]])
sys.exit("team-workflow: plugin not found in Claude Code or agy")
'''


def repo_root():
    out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def cmd_settings(args):
    root = repo_root()
    if args.action in ("set", "reset"):
        if not args.key or (args.action == "set" and args.value is None):
            raise SystemExit("usage: settings set KEY VALUE | settings reset KEY")
        if args.project and not root:
            raise SystemExit("--project needs a git repository")
        try:
            value = settings.parse_value(args.key, args.value) if args.action == "set" else None
        except ValueError as e:
            raise SystemExit(str(e))
        path = settings.save(args.key, value, root if args.project else None)
        print(f"{args.key} = {json.dumps(value) if value is not None else '(default)'}  ->  {path}")
        if args.key.startswith("models.agy") and shutil.which("agy"):
            changed = install_agy.sync_agents(install_agy.agents_dir())
            print(f"agy subagents refreshed: {', '.join(changed) or 'none changed'}")
        return
    user = dict(settings.flatten(settings._read(settings.user_file())))
    project = dict(settings.flatten(settings._read(settings.project_file(root)))) if root else {}
    data = settings.load(root)
    if args.json:
        print(json.dumps(data, indent=2))
        return
    rows = list(settings.flatten(data))
    width = max(len(k) for k, _ in rows)
    for key, value in rows:
        source = "project" if key in project else "user" if key in user else "default"
        print(f"{key:<{width}}  {json.dumps(value):<10}  {source}")
    print(f"\nuser file:    {settings.user_file()}")
    if root:
        print(f"project file: {settings.project_file(root)}")
    print("change: settings set KEY VALUE [--project] | settings reset KEY [--project]")
    for key, allowed in settings.CHOICES.items():
        print(f"  {key}: {' | '.join(allowed)}")


def cmd_models(_args):
    pricing = load_pricing()
    print("Claude Code (native subagents and workers; a native subagent keeps its file's effort):")
    for alias, mid in pricing.get("aliases", {}).items():
        efforts = pricing["models"].get(mid, {}).get("effort", EFFORTS)
        print(f"  {alias:<7} {mid:<18} effort: {', '.join(efforts) or 'none'}")
    print("agy native subagents: model inherit (the session's model), flash or pro")
    if shutil.which("agy"):
        out = subprocess.run(["agy", "models"], capture_output=True, text=True, timeout=30)
        ids = [line.split("\t")[0] for line in out.stdout.splitlines() if "\t" in line]
        print("agy workers (exact model, effort in the name): " + (", ".join(ids) or "agy models failed"))
    else:
        print("agy: not installed")


def cmd_agents(args):
    dest = install_agy.agents_dir(args.workspace)
    changed = install_agy.sync_agents(dest)
    print(f"{dest}: {', '.join(changed) or 'all roles already current'}")
    print("Restart agy to load new subagents.")


def cmd_install_cli(_args):
    path = os.path.join(os.path.expanduser("~"), ".local", "bin", "team-workflow")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(LAUNCHER)
    os.chmod(path, 0o755)
    print(f"written {path}: run `team-workflow update`, `team-workflow settings`...")
    if os.path.dirname(path) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"{os.path.dirname(path)} is not in PATH: add it to your shell profile")


def main(argv=None):
    ap = argparse.ArgumentParser(prog="team-workflow", description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="command", required=True)
    up = sub.add_parser("update", help="update the plugin in Claude Code and agy")
    up.add_argument("--check", action="store_true", help="only show the versions")
    up.add_argument("check_word", nargs="?", choices=("check",), help=argparse.SUPPRESS)
    st = sub.add_parser("settings", help="show or change the settings")
    st.add_argument("action", nargs="?", choices=("show", "set", "reset"), default="show")
    st.add_argument("key", nargs="?")
    st.add_argument("value", nargs="?")
    st.add_argument("--project", action="store_true", help="this repository only")
    st.add_argument("--json", action="store_true")
    sub.add_parser("models", help="models and efforts each app offers")
    ag = sub.add_parser("agents", help="rewrite the agy subagents")
    ag.add_argument("--workspace", help="write them into <repository>/.agents/agents instead")
    sub.add_parser("install-cli", help="add a team-workflow command to ~/.local/bin")
    args = ap.parse_args(argv)
    if args.command == "update":
        update_plugin.main(["--check"] if args.check or args.check_word else [])
    elif args.command == "settings":
        cmd_settings(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "agents":
        cmd_agents(args)
    else:
        cmd_install_cli(args)


if __name__ == "__main__":
    main(sys.argv[1:])
