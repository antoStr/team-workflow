#!/usr/bin/env python3
"""team-workflow commands that run without the model, so they spend no tokens.

    tw.py update [--check]                 update the plugin in Claude Code and agy
    tw.py settings                         show every setting and where it comes from
    tw.py settings set KEY VALUE [--project]
    tw.py settings reset KEY [--project]
    tw.py models                           models and efforts each app offers
    tw.py models --app opencode [--provider P] [--search TEXT] [--json]
                                           OpenCode: providers, favorite and recent models, search
    tw.py agents [list]                    roles with pack, on/off, type, model, effort per app
    tw.py agents set ROLE model=M effort=E type=T [--app claude|agy] [--project]
    tw.py agents enable|disable ROLE|PACK  switch a role or a whole pack
    tw.py agents show ROLE                 the full instructions of a role
    tw.py agents new ROLE                  your own role (or an override) to edit
    tw.py agents sync                      rewrite the native agents of both apps
    tw.py addons [list]                    add-on plugins, MCP servers and bundles
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
    tw.py options [--app A|all] [--json]   models, efforts and roles the session wizard can offer
    tw.py install-opencode [--workspace R] install team-workflow into OpenCode
    tw.py install-cli [--no-shell]         `team-workflow` command, and `agy plugin update` in the shell
    tw.py setup                            everything in one place: activation, wizard, team, talk,
                                           checks, roles, library, add-ons, and how to change them
    tw.py library [list [PACK...]]         the library: packs, or the entries of some packs
    tw.py library search WORDS...          entries for a task, best first, with their path
    tw.py library show ID                  one entry's instructions
    tw.py library enable|disable ID|PACK [--project]   install it as a native skill, or remove it
    tw.py library sync                     rewrite the installed library skills of every app
    tw.py talk [list]                      team talk channels of this repository
    tw.py talk post TOPIC --from ROLE [--to ROLE] [--kind K] [--re ID] [--wait SECONDS] TEXT...
    tw.py talk read TOPIC [--for ROLE] [--since ID] [--wait SECONDS]   --for: only unread ones
    tw.py talk open TOPIC [--strict]       open questions and challenges, unread messages per role
    tw.py talk clear TOPIC

In Claude Code, /team-workflow:<command> for update-plugin, settings, models, agents, addons,
profile, audit, doctor, library and talk is answered by a hook that runs this script, with no
tokens. In agy, use its bash mode: !team-workflow <command>.
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
import library
import opencode_cli
import roles
import settings
import talk
import update_plugin
from common import utf8_output
from usage import load_pricing

EFFORTS = ("low", "medium", "high", "xhigh", "max")
LAUNCHER = '''#!/usr/bin/env python3
"""team-workflow launcher: runs tw.py from the installed plugin (Claude Code, agy, OpenCode)."""
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
paths.append(os.path.join(home, ".config", "opencode"))  # skills/team-workflow lives there
for p in paths:
    tw = os.path.join(p, "skills", "team-workflow", "scripts", "tw.py")
    if os.path.isfile(tw):
        os.execv(sys.executable, [sys.executable, tw, *sys.argv[1:]])
sys.exit("team-workflow: plugin not found in Claude Code, agy or OpenCode")
'''


def output(cmd, timeout=60):
    """stdout of a command, or "" when it cannot run or fails."""
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, stdin=subprocess.DEVNULL)
    except (OSError, subprocess.SubprocessError):
        return ""
    return out.stdout if out.returncode == 0 else ""


def repo_root():
    """The git repository around the working folder, or None (no git, not a repository)."""
    try:
        out = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                             timeout=10)
    except (OSError, subprocess.SubprocessError):
        return None
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


def cmd_models(args):
    if isinstance(args.search, list):
        args.search = " ".join(args.search)
    if args.app == "opencode" or args.provider or args.search:
        data = opencode_models()
        if args.json:
            found = opencode_cli.search(data["models"], args.provider, args.search) if data else []
            print(json.dumps(found if (args.provider or args.search) else data, indent=1))
            return
        print_opencode_models(data, args.provider, args.search)
        return
    pricing = load_pricing()
    print("Claude Code (native subagents and workers; a native subagent keeps its file's effort):")
    for alias, mid in pricing.get("aliases", {}).items():
        efforts = pricing["models"].get(mid, {}).get("effort", EFFORTS)
        print(f"  {alias:<7} {mid:<18} effort: {', '.join(efforts) or 'none'}")
    print("agy native subagents: model inherit (the session's model), flash or pro")
    if shutil.which("agy"):
        ids = [line.split("\t")[0] for line in output(["agy", "models"]).splitlines() if "\t" in line]
        print("agy workers (exact model, effort in the name): " + (", ".join(ids) or "agy models failed"))
    else:
        print("agy: not installed")
    print_opencode_models(opencode_models())


def opencode_models():
    """What OpenCode offers now: the providers the user connected, their models with names and
    variants, and the models used most. None when OpenCode is not installed."""
    if not opencode_cli.binary():
        return None
    models = opencode_cli.catalog()
    by_id = {m["id"]: m for m in models}
    recent = [dict(by_id.get(mid) or {"id": mid, "name": mid, "variants": []}, sessions=n)
              for mid, n in opencode_cli.recent()]
    return {"version": ".".join(map(str, opencode_cli.version() or ())) or None,
            "providers": opencode_cli.providers(models), "recent": recent, "models": models}


def model_line(m):
    variants = ", ".join(m["variants"]) or "none"
    return f"  {m['id']:<52} {m['name']:<34} variants: {variants}"


def print_opencode_models(data, provider=None, text=None):
    if data is None:
        print("OpenCode: not installed (or its CLI is not found: set TEAM_WORKFLOW_OPENCODE_BIN)")
        return
    if provider or text:
        found = opencode_cli.search(data["models"], provider, text)
        print(f"OpenCode models{' of ' + provider if provider else ''}"
              f"{' matching ' + repr(text) if text else ''}: {len(found)}")
        for m in found:
            print(model_line(m))
        return
    print(f"OpenCode {data['version'] or ''} subagents and workers: inherit (the calling agent's model) "
          "or any provider/model below; the effort is the model's variant")
    for pid, p in data["providers"].items():
        print(f"  provider {pid} ({p['name']}): {p['models']} models")
    if data["recent"]:
        print("  favorites and recent:")
        for m in data["recent"]:
            print("  " + model_line(m))
    print("  find one: models --app opencode --provider <id> --search <text>   (for example --search glm 5.3)")


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


def app_options(app, root=None):
    """What the session wizard may offer in one app, right now."""
    config = settings.load(root)
    pricing = load_pricing()
    catalog = roles.catalog(root)
    enabled = [r for r, i in catalog.items() if roles.is_enabled(config, r, i["pack"])]
    lib = library.pack_rows(config)
    out = {"app": app, "settings": {k: config[k] for k in ("activation", "wizard", "max_agents", "launch",
                                                            "talk", "talk_rounds", "end_report")},
           "scope": {"user_file": settings.user_file(),
                     "project_file": settings.project_file(root) if root else None},
           "library": {"entries": sum(r[1] for r in lib), "packs": {r[0]: r[1] for r in lib},
                       "installed": {r[0]: r[2] for r in lib if r[2]},
                       "search": "tw.py library search <words> --json"},
           "addons": {"chosen": sorted(config.get("addons") or {}),
                      "catalog": {n: e.get("about", "") for n, e in addons.CATALOG.items()},
                      "bundles": {b: list(n) for b, n in addons.BUNDLES.items()}},
           "presets": {k: v for k, v in settings.PROFILES.items()},
           "types": list(settings.CHOICES[f"type.{app}"]),
           "roles": {r: dict(roles.plan(config, r, app), pack=catalog[r]["pack"]) for r in enabled},
           "packs_off": sorted({i["pack"] for r, i in catalog.items() if r not in enabled}),
           "languages_here": roles.detect(root) if root else []}
    if app == "claude":
        out["native"] = {"models": list(pricing.get("aliases", {})),
                         "efforts": {a: pricing["models"].get(m, {}).get("effort", []) for a, m in
                                     pricing.get("aliases", {}).items()},
                         "per_launch": "the Agent tool's model parameter changes the model for one "
                                       "launch; the effort is fixed in the agent file"}
        out["worker"] = {"models": list(pricing.get("aliases", {})) + ["<full model id>"],
                         "efforts": ["low", "medium", "high", "xhigh", "max"]}
    elif app == "agy":
        session = effort = None
        if shutil.which("agy"):
            session = output(["agy", "-p", "/model"]).split("\t")[0].strip() or None
            effort = output(["agy", "-p", "/effort"]).strip() or None
        ids = [line.split("\t")[0] for line in output(["agy", "models"]).splitlines() if "\t" in line] \
            if shutil.which("agy") else []
        out["native"] = {"models": ["inherit", "flash", "pro"], "session_model": session,
                         "session_effort": effort,
                         "per_launch": "invoke_subagent has no model: a subagent uses its file's tier; "
                                       "inherit = the session model (change it with /model)"}
        out["worker"] = {"models": ids, "efforts": "part of the model id (-low, -medium, -high)"}
    else:  # hundreds of models: the providers and the most used, the rest by search
        data = opencode_models() or {"version": None, "providers": {}, "recent": [], "models": []}
        brief = lambda m: {k: m[k] for k in ("id", "name", "variants") if k in m}
        out["native"] = {"models": ["inherit"] + [m["id"] for m in data["recent"]],
                         "version": data["version"], "providers": data["providers"],
                         "recent": [brief(m) for m in data["recent"]],
                         "find": "tw.py models --app opencode --provider <id> --search <text> --json",
                         "efforts": "the model's variants (listed per model; none = no effort)",
                         "per_launch": "the subagent tool has no model: a subagent uses its file's model "
                                       "and variant; inherit = the model of the calling agent"}
        out["worker"] = {"models": "any provider/model of the providers above",
                         "efforts": "the model's variants (run as provider/model#variant)"}
    for p in out["roles"].values():
        p["runs"] = runs_as(app, p, out["native"])
    return out


def runs_as(app, p, native):
    """How a role really runs in an app, in words: native or worker, and what the effort does."""
    if p["type"] == "worker":
        return "worker: exact model and effort"
    if p["type"] != "custom":
        return f"built-in {p['type']}, with the role's instructions in the prompt"
    model, effort = p["model"], p["effort"]
    if app == "claude":
        if model in native["efforts"] and not native["efforts"][model]:
            return f"native; {model} has no effort, so it is ignored"
        return f"native: effort {effort} (agent file)"
    if app == "agy":
        if model == "inherit":
            return (f"native: {native.get('session_model') or 'session model'}, "
                    f"session effort {native.get('session_effort') or '-'}")
        return f"native: tier {model}, no effort"
    who = "the calling agent's model" if model == "inherit" else model
    return f"native: {who}, " + ("default variant" if effort == "medium" else f"variant {effort}")


def print_options(data):
    app, native, worker = data["app"], data["native"], data["worker"]
    name = {"claude": "Claude Code", "agy": "agy", "opencode": "OpenCode"}[app]
    print(f"== {name}")
    print("Models for native agents (the agent file):")
    if app == "claude":
        for m in native["models"]:
            print(f"  {m:<8} effort: {' | '.join(native['efforts'][m]) or 'none'}")
    elif app == "agy":
        print(f"  inherit  = session model {native.get('session_model') or '(agy not found)'}, "
              f"effort {native.get('session_effort') or '-'} (change with /model, /effort)")
        print("  flash    = Gemini flash tier, no effort")
        print("  pro      = Gemini 3.1 Pro, older than the 3.8 flash models, no effort")
        print("  a native agy agent ignores the role's effort; for another effort pick a worker id")
    else:
        print("  inherit  = the calling agent's model")
        if not native["providers"]:
            print("  (OpenCode not found: install it, or set TEAM_WORKFLOW_OPENCODE_BIN to its CLI)")
        for pid, p in native["providers"].items():
            print(f"  provider {pid} ({p['name']}): {p['models']} models")
        if native["recent"]:
            print("  favorites and recent:")
            for m in native["recent"]:
                print("  " + model_line(m))
        print(f"  find one: {native['find'].replace(' --json', '')}")
        print(f"  effort: {native['efforts']}")
    print("Models for workers (any exact model, for one run):")
    models = worker["models"]
    print("  " + (", ".join(models) if isinstance(models, list) else models or "-"))
    efforts = worker["efforts"]
    print(f"  effort: {' | '.join(efforts) if isinstance(efforts, list) else efforts}")
    print("Roles now (type, model, effort -> how it runs):")
    for role, p in data["roles"].items():
        print(f"  {role:<26} {p['type']:<8} {p['model']:<10} {p['effort']:<7} -> {p['runs']}")
    print()


def cmd_options(args):
    app = args.app or os.environ.get("TEAM_WORKFLOW_APP") or "claude"
    root = repo_root()
    apps = roles.APPS if app == "all" else (app,)
    every = [app_options(a, root) for a in apps]
    if args.json:
        print(json.dumps(every if app == "all" else every[0], indent=1))
        return
    for data in every:
        print_options(data)
    print("presets: " + ", ".join(settings.PROFILES))
    print("When you can change model and effort:")
    print("  - at the first task of a conversation, in the session setup (per role)")
    print("  - before every launch: \"Change an agent\" on the assignment board (this run only)")
    print("  - for good: tw.py agents set ROLE model=M effort=E [--app A] [--project], then restart the app")
    print("  - a whole preset: tw.py profile NAME")
    data = every[0]
    st, lib, add = data["settings"], data["library"], data["addons"]
    print(f"Session: activation {st['activation']}, team talk {'on' if st['talk'] else 'off'} "
          f"({st['talk_rounds']} rounds), wizard {st['wizard']}, up to {st['max_agents']} agents")
    print(f"Skills: library of {lib['entries']} entries in {len(lib['packs'])} packs; installed: "
          + (", ".join(f"{p} ({n})" for p, n in lib["installed"].items()) or "none")
          + "; find: library search WORDS")
    print("Add-ons chosen: " + (", ".join(add["chosen"]) or "none") + "; bundles: "
          + "; ".join(f"{b} = {', '.join(n)}" for b, n in add["bundles"].items()))
    print(f"Saving choices: user file {data['scope']['user_file']}"
          + (f", project file {data['scope']['project_file']}" if data["scope"]["project_file"] else ""))
    if app != "all":
        print("Other apps: options --app all")


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
    head = output(["git", "-C", root, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"]).strip()
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


def cmd_install_opencode(args):
    import install_opencode
    result = install_opencode.install(args.workspace)
    print(f"installed in OpenCode: {result['payload']}; {result['commands']} commands, the plugin, "
          f"{len(result['agents'])} agents written or refreshed. Restart OpenCode.")


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
        for bundle, names in addons.BUNDLES.items():
            print(f"bundle: addons add {bundle} = {', '.join(names)}")
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


def sync_library(root):
    for app in roles.installed_apps():
        r = library.sync(app, root=root)
        print(f"{app}: library skills written {len(r['written'])}, removed {len(r['removed'])}"
              + (f", not ours so left alone: {', '.join(r['skipped'])}" if r["skipped"] else ""))


def entry_line(e, config):
    return (f"{'*' if library.is_on(config, e) else ' '} {e['id']:<38} {e['kind']:<7} {e['pack']:<26} "
            f"{e['description'][:100]}")


def cmd_library(args):
    root = repo_root()
    config = settings.load(root)
    found, rest = library.entries(), args.rest
    if not found:
        raise SystemExit("the library is missing: reinstall team-workflow (tools/import_upstream.py builds it)")
    if args.action == "list":
        if rest:
            for e in sorted(found.values(), key=lambda e: (e["pack"], e["id"])):
                if e["pack"] in rest:
                    print(entry_line(e, config))
            return
        print(f"{'pack':<28} {'entries':>7} {'on':>4}  about")
        for pack, count, on, about in library.pack_rows(config):
            print(f"{pack:<28} {count:>7} {on:>4}  {about[:90]}")
        print(f"\n{len(found)} entries (MIT, see NOTICE.md) in {library.LIBRARY}")
        print("library PACK... lists entries; library search WORDS; library show ID")
        print("library enable|disable ID|PACK [--project] installs or removes native skills (* = on)")
        return
    if args.action == "sync":
        sync_library(root)
        return
    if not rest:
        raise SystemExit(f"usage: library {args.action} " + ("WORDS..." if args.action == "search" else "ID|PACK"))
    if args.action == "search":
        hits = library.search(rest)
        for e in hits:
            print(entry_line(e, config) + f"\n    {library.main_file(e['id'])}")
        print(f"{len(hits)} found" if hits else "nothing found: try other words, or `library` for the packs")
        return
    name = rest[0]
    if args.action == "show":
        if name not in found:
            raise SystemExit(f"no entry {name!r}: library search WORDS")
        with open(library.main_file(name), encoding="utf-8") as f:
            print(f"{library.main_file(name)}\n\n{f.read()}")
        return
    if args.project and not root:
        raise SystemExit("--project needs a git repository")
    packs = library.index()["packs"]
    if name in packs:
        key = f"library.packs.{name}"
    elif name in found:
        key = f"library.skills.{name}"
    else:
        raise SystemExit(f"no entry or pack {name!r}: library search WORDS, or library for the packs")
    value = settings.parse_value(key, "true" if args.action == "enable" else "false")
    print(f"{key} = {json.dumps(value)}  ->  {settings.save(key, value, root if args.project else None)}")
    sync_library(root)
    print("Restart the app to load the skills.")


def cmd_talk(args):
    try:
        if args.action == "list":
            channels = talk.topics()
            for name, msgs in channels:
                print(f"{name:<32} {len(msgs):>4} messages  {len(talk.open_threads(msgs))} open")
            print(("" if channels else "no channels yet\n") + f"channels: {talk.channel_dir()}")
            return
        if not args.topic:
            raise ValueError(f"usage: talk {args.action} TOPIC")
        if args.action == "post":
            print(talk.line(talk.post(args.topic, args.sender, " ".join(args.text), args.kind,
                                      args.to, args.re)))
            if args.wait:  # post, then wait for the reply in the same call
                args.role, args.action = args.sender, "read"
        if args.action == "read":
            if args.wait:
                msgs, waited = talk.wait(args.topic, args.role, args.since, args.wait)
            elif args.role:
                msgs, waited = talk.unread(args.topic, args.role, args.since), None
            else:
                msgs, waited = [m for m in talk.read(args.topic) if m["id"] > (args.since or 0)], None
            if args.json:
                print(json.dumps(msgs, indent=1, ensure_ascii=False))
                return
            print("\n".join(talk.line(m) for m in msgs) or "(no new messages)")
            if waited is not None:
                print(f"({len(msgs)} new after {waited}s)" if msgs else
                      f"(nothing new after waiting {waited}s)")
            if not args.role:
                last = max([m["id"] for m in talk.read(args.topic)] or [0])
                print(f"(last message #{last}; read --for ROLE shows only what is new for a role)")
        elif args.action == "open":
            threads = talk.open_threads(talk.read(args.topic))
            print("\n".join(talk.line(m) for m in threads) or "nothing open")
            for role, ids in talk.unread_by_role(args.topic).items():
                print(f"unread by {role}: " + ", ".join(f"#{i}" for i in ids))
            if threads and args.strict:
                raise SystemExit(1)
        elif args.action == "clear":
            print("cleared" if talk.clear(args.topic) else "no such channel")
    except (ValueError, TimeoutError) as e:
        raise SystemExit(str(e))


SETUP_GROUPS = (
    ("Activation", ("activation",),
     "auto: every session in a repository loads the memory, the protocol and the Stop check. "
     "manual: team-workflow stays quiet until you call /team-workflow:<name>. Manual everywhere and "
     "auto in some projects: settings set activation manual, then in those projects "
     "settings set activation auto --project."),
    ("Session setup and questions", ("session_wizard", "wizard", "end_report"),
     "session_wizard: at the first task, scope, preset, roles, models, skills, add-ons, talk; "
     "wizard: quick | full | off."),
    ("Team", ("max_agents", "launch", "worker_edits", "auto_security_review"),
     "launch native subagents or headless workers (exact model and effort)."),
    ("Agents talk to each other", ("talk", "talk_rounds"),
     "shared channel where agents debug together, challenge and verify each other (TALK.md)."),
    ("Checks", ("stop_check", "update_check"), "memory reminder at the end of a turn; daily update check."),
    ("Default models", ("models.claude.default", "models.agy.default", "models.opencode.default",
                        "effort.default"), "per role: tw.py agents set ROLE model=M effort=E."),
)


def cmd_setup(_args):
    root = repo_root()
    config = settings.load(root)
    user = dict(settings.flatten(settings._read(settings.user_file())))
    project = dict(settings.flatten(settings._read(settings.project_file(root)))) if root else {}
    values = dict(settings.flatten(config))
    print("team-workflow setup" + (f" for {root}" if root else " (outside a repository: user settings only)"))
    for title, keys, about in SETUP_GROUPS:
        print(f"\n{title}: {about}")
        for key in keys:
            source = "project" if key in project else "user" if key in user else "default"
            choices = settings.CHOICES.get(key)
            print(f"  {key:<26} {json.dumps(values.get(key)):<12} {source}"
                  + (f"   ({' | '.join(choices)})" if choices else ""))
    catalog = roles.catalog(root)
    packs = sorted({i["pack"] for i in catalog.values()})
    on = [p for p in packs if roles.is_enabled(config, "", p)]
    print(f"\nRoles: {sum(roles.is_enabled(config, r, i['pack']) for r, i in catalog.items())} of "
          f"{len(catalog)} on. Packs on: {', '.join(on)}. Off: {', '.join(p for p in packs if p not in on)}.")
    print("  change: agents enable|disable ROLE|PACK|auto, agents set ROLE ..., agents new ROLE")
    lib = library.pack_rows(config)
    lib_on = [f"{p} ({n})" for p, _, n, _ in lib if n]
    print(f"\nLibrary (skills, commands, rules): {sum(r[1] for r in lib)} entries in {len(lib)} packs; "
          f"installed: {', '.join(lib_on) or 'none'}.")
    print("  change: library, library search WORDS, library enable|disable ID|PACK [--project]")
    chosen = config.get("addons") or {}
    print(f"\nAdd-ons: {', '.join(chosen) or 'none'}.  change: addons, addons add NAME")
    print(f"Presets: {', '.join(settings.PROFILES)}.  apply: profile NAME [--project]")
    print(f"\nuser file:    {settings.user_file()}" + (f"\nproject file: {settings.project_file(root)}" if root else ""))
    print("change one value: settings set KEY VALUE [--project] | settings reset KEY [--project]")


def main(argv=None):
    utf8_output()
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
    mo = sub.add_parser("models", help="models and efforts each app offers")
    mo.add_argument("--app", choices=roles.APPS, help="opencode: its providers and models")
    mo.add_argument("--provider", help="OpenCode: the models of this provider (for example nano-gpt)")
    mo.add_argument("--search", nargs="+", help="OpenCode: the models whose id or name has these words")
    mo.add_argument("--json", action="store_true")
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
    op = sub.add_parser("options", help="what the session wizard can offer in an app")
    op.add_argument("--app", choices=(*roles.APPS, "all"))
    op.add_argument("--json", action="store_true")
    io = sub.add_parser("install-opencode", help="install team-workflow into OpenCode")
    io.add_argument("--workspace", help="this repository only (.opencode)")
    au2 = sub.add_parser("agy-update", help="agy plugin update: reinstall agy plugins from their source")
    au2.add_argument("names", nargs="*", help="plugins to update (default: all)")
    ic = sub.add_parser("install-cli", help="add team-workflow to ~/.local/bin and `agy plugin update`")
    ic.add_argument("--no-shell", action="store_true", help="do not add the agy function to .zshrc/.bashrc")
    sub.add_parser("setup", help="every setting in one place, with how to change it")
    li = sub.add_parser("library", help="skills, commands and rules: list, search, show, enable")
    li.add_argument("action", nargs="?", default="list",
                    choices=("list", "search", "show", "enable", "disable", "sync"))
    li.add_argument("rest", nargs="*", help="PACK..., WORDS..., ID or PACK")
    li.add_argument("--project", action="store_true", help="enable/disable: this repository only")
    tk = sub.add_parser("talk", help="team talk: the channel where agents talk to each other")
    tk.add_argument("action", nargs="?", default="list", choices=("list", "post", "read", "open", "clear"))
    tk.add_argument("topic", nargs="?")
    tk.add_argument("text", nargs="*")
    tk.add_argument("--from", dest="sender", help="post: your role")
    tk.add_argument("--to", help="post: one role (default: everyone)")
    tk.add_argument("--kind", default="note", choices=talk.KINDS)
    tk.add_argument("--re", type=int, help="post: the id of the message this answers")
    tk.add_argument("--for", dest="role", help="read: only messages for this role")
    tk.add_argument("--since", type=int, help="read: after this message id (default with --for: "
                                                "what that role has not read yet)")
    tk.add_argument("--wait", type=int, default=0, help="read, or post then read: wait up to SECONDS "
                                                        "for a new message")
    tk.add_argument("--strict", action="store_true", help="open: exit 1 when something is open")
    tk.add_argument("--json", action="store_true")
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
         "agy-update": cmd_agy_update, "install-opencode": cmd_install_opencode,
         "options": cmd_options, "setup": cmd_setup, "library": cmd_library,
         "talk": cmd_talk}[args.command](args)


if __name__ == "__main__":
    main(sys.argv[1:])
