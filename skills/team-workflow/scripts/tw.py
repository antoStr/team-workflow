#!/usr/bin/env python3
"""team-workflow commands that run without the model, so they spend no tokens.

    tw.py update [--check]                 update the plugin in Claude Code and agy
    tw.py settings                         show every setting and where it comes from
    tw.py settings set KEY VALUE [--project]
    tw.py settings reset KEY [--project]
    tw.py models                           models and efforts each app offers
    tw.py agents [list]                    roles with pack, on/off, type, model, effort per app
    tw.py agents set ROLE model=M effort=E type=T [--app claude|agy] [--project]
    tw.py agents enable|disable ROLE|PACK  switch a role or a whole pack
    tw.py agents show ROLE                 the full instructions of a role
    tw.py agents new ROLE                  your own role (or an override) to edit
    tw.py agents sync                      rewrite the native agents of both apps
    tw.py addons [list]                    add-on plugins (caveman, ponytail, ecc, any other)
    tw.py addons add NAME|owner/repo|plugin@marketplace [--app claude|agy]
    tw.py addons remove NAME
    tw.py addons update [NAME]
    tw.py profile [NAME] [--project]       presets: budget, fast, balanced, thorough, security, research
    tw.py audit [--strict] [--json]        security scan of settings, hooks, MCP, agents, skills
    tw.py doctor [--fix]                   health check and repair of the installation
    tw.py uninstall [--all]                remove what team-workflow wrote outside the plugins
    tw.py learn [--max N] [--json]         habits of this repository from its git history
    tw.py ci-init                          GitHub Actions workflow: memory and audit on every PR
    tw.py agy-update [NAME...]             what `agy plugin update` would be: reinstall from source
    tw.py install-cli [--no-shell]         `team-workflow` command, and `agy plugin update` in the shell

In Claude Code, /team-workflow:<command> for update-plugin, settings, models, agents, addons,
profile, audit and doctor is answered by a hook that runs this script, with no tokens. In agy,
use its bash mode: !team-workflow <command>.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys

import addons
import audit
import doctor
import learn
import roles
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
        if args.key.split(".")[0] in settings.ROLE_TABLES:
            for app in roles.installed_apps():
                roles.sync(app, root=root)
            print("agents rewritten in " + ", ".join(roles.installed_apps()))
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
    root = repo_root()
    config = settings.load(root)
    action, rest = args.action, args.rest
    if action == "list":
        rows = [("role", "pack", "on", "Claude Code: type model effort", "agy: type model",
                 "OpenCode: type model variant")]
        rows += roles.table(config, root)
        widths = [max(len(r[i]) for r in rows) for i in range(5)]
        for r in rows:
            print("  ".join(c.ljust(w) for c, w in zip(r, widths)) + "  " + r[5])
        packs = sorted({i["pack"] for i in roles.catalog(root).values()})
        on = [p for p in packs if roles.is_enabled(config, "", p)]
        print(f"\npacks on: {', '.join(on)}")
        print(f"packs off: {', '.join(p for p in packs if p not in on)}")
        if root:
            print(f"languages of this repository: {', '.join(roles.detect(root)) or 'none detected'}")
        print("\nchange: agents set ROLE model=opus effort=high type=custom [--app claude|agy]")
        print("         agents enable|disable ROLE|PACK|auto|languages, agents new ROLE, agents sync")
        print("types: " + "; ".join(f"{app} " + " | ".join(settings.CHOICES[f"type.{app}"])
                                    for app in roles.APPS))
        return
    if action == "sync":
        for app in roles.installed_apps() if not args.workspace else roles.APPS:
            dest = roles.native_dir(app, args.workspace)
            r = roles.sync(app, root=root, dest=dest)
            print(f"{app} ({dest}): written {len(r['written'])}, removed {len(r['removed'])}"
                  + (f", not ours so left alone: {', '.join(r['skipped'])}" if r["skipped"] else ""))
        print("Restart the app to load new or changed agents.")
        return
    if not rest:
        raise SystemExit(f"usage: agents {action} ROLE ...")
    name, target = rest[0], (root if args.project else None)
    try:
        if action == "new":
            print(f"edit {roles.new_role(name, target)}, then: agents sync")
            return
        if action == "show":
            meta, body = roles.load(name, root)
            print(f"# {name}\n\n{meta.get('description', '')}\n\n{body}")
            return
        catalog = roles.catalog(root)
        packs = {i["pack"] for i in catalog.values()}
        if action in ("enable", "disable"):
            on = "true" if action == "enable" else "false"
            if name in ("auto", "languages"):
                slugs = roles.detect(root or os.getcwd()) if name == "auto" else list(roles.languages())
                if not slugs:
                    raise ValueError("no language of this repository has a pack")
                changes = [(f"packs.{s}", settings.parse_value(f"packs.{s}", on)) for s in slugs]
            elif name in packs and name not in catalog:
                changes = [(f"packs.{name}", settings.parse_value(f"packs.{name}", on))]
            elif name in catalog:
                changes = [(f"enabled.{name}", settings.parse_value(f"enabled.{name}", on))]
            else:
                raise ValueError(f"no role or pack named {name!r}; packs: {', '.join(sorted(packs))}")
        else:  # set
            if name not in catalog:
                raise ValueError(f"unknown role {name!r}")
            changes = []
            apps = (args.app,) if args.app else roles.APPS
            for pair in rest[1:]:
                field, _, value = pair.partition("=")
                if field == "effort":
                    changes.append((f"effort.{name}", settings.parse_value(f"effort.{name}", value)))
                elif field in ("model", "type"):
                    # without --app, the value goes to every app that accepts it (a Claude
                    # model name is not an agy tier nor an OpenCode provider/model)
                    table = "models" if field == "model" else "type"
                    accepted, errors = [], []
                    for app in apps:
                        key = f"{table}.{app}.{name}"
                        try:
                            accepted.append((key, settings.parse_value(key, value)))
                        except ValueError as err:
                            errors.append(str(err))
                    if not accepted or (args.app and errors):
                        raise ValueError("; ".join(errors))
                    changes += accepted
                else:
                    raise ValueError(f"unknown field {field!r}: use model=, effort=, type=")
            if not changes:
                raise ValueError("nothing to set: agents set ROLE model=... effort=... type=...")
    except ValueError as e:
        raise SystemExit(str(e))
    for key, value in changes:
        print(f"{key} = {json.dumps(value)}  ->  {settings.save(key, value, target)}")
    for app in roles.installed_apps():
        roles.sync(app, root=root)
    print("agents rewritten in " + ", ".join(roles.installed_apps()) + "; restart the app to load them.")


def cmd_profile(args):
    root = repo_root()
    if not args.name:
        for name, values in settings.PROFILES.items():
            print(f"{name:<9} " + (", ".join(f"{k}={json.dumps(v)}" for k, v in values.items())
                                  or "the defaults of every key the other profiles change"))
        print("\napply: profile NAME [--project]")
        return
    try:
        changes = settings.apply_profile(args.name, root if args.project else None)
    except ValueError as e:
        raise SystemExit(str(e))
    for key, value in changes:
        print(f"{key} = {json.dumps(value) if value is not None else '(default)'}")
    for app in roles.installed_apps():
        roles.sync(app, root=root)
    print(f"profile {args.name} applied" + (" to this repository" if args.project else ""))


def cmd_audit(args):
    findings, scanned = audit.audit(repo_root())
    print(json.dumps(findings, indent=2) if args.json else audit.report(findings, scanned))
    if args.strict and any(f["severity"] in ("critical", "high") for f in findings):
        raise SystemExit(1)


def cmd_doctor(args):
    root = repo_root()
    if args.fix:
        print("\n".join(doctor.repair(root)) + "\n")
    results = doctor.checks(root)
    for status, area, message in results:
        print(f"[{status.upper():4}] {area}: {message}")
    if any(s == "fail" for s, _, _ in results):
        raise SystemExit(1)


def cmd_uninstall(args):
    print("\n".join(doctor.uninstall(args.all)))


def cmd_learn(args):
    data = learn.analyze(repo_root() or os.getcwd(), args.max)
    print(json.dumps(data, indent=2) if args.json else learn.report(data))


CI_WORKFLOW = """name: team-workflow

on:
  pull_request:
  push:
    branches: [{branch}]

jobs:
  checks:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      # The checks come from team-workflow {version}, copied into .github/team-workflow/.
      - name: Project memory (docs/memory)
        if: hashFiles('docs/memory/INDEX.md') != ''
        run: python3 .github/team-workflow/memcheck.py --root . --strict
      - name: Agent configuration audit (settings, hooks, MCP, agents, skills)
        run: python3 .github/team-workflow/audit.py --root . --strict
      # Add the project's own checks from docs/memory/PLAYBOOKS.md here (build, lint, tests).
"""


def cmd_ci_init(_args):
    root = repo_root()
    if not root:
        raise SystemExit("ci-init needs a git repository")
    path = os.path.join(root, ".github", "workflows", "team-workflow.yml")
    if os.path.exists(path):
        raise SystemExit(f"{path} exists: edit it or remove it first")
    head = subprocess.run(["git", "-C", root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
                          capture_output=True, text=True).stdout.strip()
    branch = head.split("/", 1)[1] if "/" in head else "main"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    vendor = os.path.join(root, ".github", "team-workflow")
    os.makedirs(vendor, exist_ok=True)
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("memcheck.py", "audit.py", "settings.py"):  # what the two checks import
        shutil.copy(os.path.join(here, name), vendor)
    with open(path, "w", encoding="utf-8") as f:
        f.write(CI_WORKFLOW.format(branch=branch, version=update_plugin.own_version() or "0.0.0"))
    print(f"written {path} and .github/team-workflow/ (the check scripts): memory and agent-config "
          f"audit on every pull request and push to {branch}")
    print("add the project's build and tests from PLAYBOOKS.md, then commit it")


SHELL_START, SHELL_END = "# >>> team-workflow: agy plugin update >>>", "# <<< team-workflow <<<"
SHELL_HOOK = f"""{SHELL_START}
# agy has no `plugin update`: this adds it (any plugin, reinstalled from its source) and passes
# every other command to agy unchanged. Remove the block to undo.
agy() {{
  if [ "$1" = plugin -o "$1" = plugins ] && [ "$2" = update ]; then
    shift 2; team-workflow agy-update "$@"
  else
    command agy "$@"
  fi
}}
{SHELL_END}
"""


def add_shell_hook(rc):
    """Add (or refresh) the agy function in a shell rc file; returns True when it changed."""
    try:
        with open(rc, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        return False
    if SHELL_START in text:
        start, end = text.index(SHELL_START), text.index(SHELL_END) + len(SHELL_END)
        new = text[:start] + SHELL_HOOK.rstrip("\n") + text[end:]
    else:
        new = text.rstrip("\n") + "\n\n" + SHELL_HOOK
    if new == text:
        return False
    with open(rc, "w", encoding="utf-8") as f:
        f.write(new)
    return True


def cmd_install_cli(args):
    path = os.path.join(os.path.expanduser("~"), ".local", "bin", "team-workflow")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(LAUNCHER)
    os.chmod(path, 0o755)
    print(f"written {path}: run `team-workflow update`, `team-workflow settings`...")
    if os.path.dirname(path) not in os.environ.get("PATH", "").split(os.pathsep):
        print(f"{os.path.dirname(path)} is not in PATH: add it to your shell profile")
    if getattr(args, "no_shell", False):
        return
    for rc in (".zshrc", ".bashrc"):
        full = os.path.join(os.path.expanduser("~"), rc)
        if add_shell_hook(full):
            print(f"added `agy plugin update [name...]` to {full} (open a new terminal to use it)")


def cmd_agy_update(args):
    ok, log = update_plugin.agy_update(args.names)
    names = args.names or []
    if not names or any(n in addons.chosen() for n in names):  # add-ons copied as skills
        for name, entry in addons.chosen().items():
            if entry.get("agy") == "skills" and (not names or name in names):
                done, out = addons.copy_skills(name, entry)
                log += f"\n{name} (skills): {out}"
                ok &= done
    print(log)
    if not ok:
        raise SystemExit(1)


def cmd_addons(args):
    root = repo_root()
    if args.action == "list":
        print("\n".join(addons.status_lines(root)))
        print("\n* = chosen, updated with `update`. add: addons add caveman | owner/repo | plugin@marketplace")
        return
    if not args.name and args.action != "update":
        raise SystemExit(f"usage: addons {args.action} NAME")
    try:
        if args.action == "update" and not args.name:
            ok, log = addons.update_all(root)
        else:
            apps = (args.app,) if args.app else addons.APPS
            ok, log = addons.apply(args.action, args.name, apps, root)
    except ValueError as e:
        raise SystemExit(str(e))
    print(log)
    if not ok:
        raise SystemExit(1)


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
    ag = sub.add_parser("agents", help="roles: list, set type/model/effort, enable, new, sync")
    ag.add_argument("action", nargs="?", default="list",
                    choices=("list", "show", "set", "enable", "disable", "new", "sync"))
    ag.add_argument("rest", nargs="*", help="ROLE [model=... effort=... type=...]")
    ag.add_argument("--app", choices=roles.APPS, help="set: only this app")
    ag.add_argument("--project", action="store_true", help="this repository only")
    ag.add_argument("--workspace", help="sync: write into <repository>/.claude and .agents")
    ad = sub.add_parser("addons", help="add-on plugins in Claude Code and agy")
    ad.add_argument("action", nargs="?", choices=("list", "add", "remove", "update"), default="list")
    ad.add_argument("name", nargs="?")
    ad.add_argument("--app", choices=addons.APPS, help="only this app")
    pr = sub.add_parser("profile", help="presets that change several settings")
    pr.add_argument("name", nargs="?")
    pr.add_argument("--project", action="store_true", help="this repository only")
    au = sub.add_parser("audit", help="security scan of the agent setup")
    au.add_argument("--strict", action="store_true", help="exit 1 on critical or high findings")
    au.add_argument("--json", action="store_true")
    do = sub.add_parser("doctor", help="health check of the installation")
    do.add_argument("--fix", action="store_true", help="repair what can be repaired")
    un = sub.add_parser("uninstall", help="remove what team-workflow wrote outside the plugins")
    un.add_argument("--all", action="store_true", help="also ~/.team-workflow (settings, ledger)")
    le = sub.add_parser("learn", help="habits of this repository from its git history")
    le.add_argument("--max", type=int, default=2000)
    le.add_argument("--json", action="store_true")
    sub.add_parser("ci-init", help="GitHub Actions workflow for memory and audit checks")
    au2 = sub.add_parser("agy-update", help="agy plugin update: reinstall agy plugins from their source")
    au2.add_argument("names", nargs="*", help="plugins to update (default: all)")
    ic = sub.add_parser("install-cli", help="add team-workflow to ~/.local/bin and `agy plugin update`")
    ic.add_argument("--no-shell", action="store_true", help="do not add the agy function to .zshrc/.bashrc")
    args = ap.parse_args(argv)
    if args.command == "update":
        check = args.check or args.check_word
        try:
            update_plugin.main(["--check"] if check else [])
        except SystemExit as e:
            if e.code:
                print("team-workflow update failed")
        if not check:
            print(addons.update_all(repo_root())[1])
    elif args.command == "settings":
        cmd_settings(args)
    elif args.command == "models":
        cmd_models(args)
    elif args.command == "addons":
        cmd_addons(args)
    elif args.command == "agents":
        cmd_agents(args)
    else:
        {"profile": cmd_profile, "audit": cmd_audit, "doctor": cmd_doctor, "uninstall": cmd_uninstall,
         "learn": cmd_learn, "ci-init": cmd_ci_init, "install-cli": cmd_install_cli,
         "agy-update": cmd_agy_update}[args.command](args)


if __name__ == "__main__":
    main(sys.argv[1:])
