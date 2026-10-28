#!/usr/bin/env python3
"""Import Everything Claude Code (ECC, MIT license) into team-workflow:

    python3 tools/import_ecc.py <path to an ECC checkout>

- ECC agents that team-workflow has no role for become roles in
  skills/team-workflow/roles/<pack>/<role>.md. ECC's model is dropped (the settings choose it)
  and so is its prompt-defense block (every role gets roles/_shared/untrusted-input.md).
  The agents team-workflow already covers are listed in COVERED and not imported.
- ECC skills, commands and rules become the library, skills/team-workflow/library/<id>/, each
  with MAIN.md instead of SKILL.md, so no app loads hundreds of skills by itself, and
  library/index.json; `tw.py library` searches them and installs the chosen ones as skills.

Rerun it after an ECC update: the library is rebuilt and the imported roles are rewritten; a
role file without the `source: "ECC ..."` line is never overwritten. An ECC agent that is in
neither IMPORT nor COVERED stops the import, so every new agent gets a decision.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.normpath(os.path.join(HERE, "..", "skills", "team-workflow"))
ROLES = os.path.join(SKILL, "roles")
LIBRARY = os.path.join(SKILL, "library")

# ECC agent -> (team-workflow role, pack)
IMPORT = {
    "build-error-resolver": ("build-fixer", "quality"),
    "code-simplifier": ("code-simplifier", "quality"),
    "comment-analyzer": ("comment-analyzer", "quality"),
    "commit-reviewer": ("commit-reviewer", "quality"),
    "database-reviewer": ("database-reviewer", "quality"),
    "code-architect": ("code-architect", "planning"),
    "spec-miner": ("spec-miner", "planning"),
    "docs-lookup": ("docs-lookup", "planning"),
    "django-reviewer": ("django-reviewer", "frameworks"),
    "django-build-resolver": ("django-build-fixer", "frameworks"),
    "fastapi-reviewer": ("fastapi-reviewer", "frameworks"),
    "flutter-reviewer": ("flutter-reviewer", "frameworks"),
    "react-reviewer": ("react-reviewer", "frameworks"),
    "react-build-resolver": ("react-build-fixer", "frameworks"),
    "vue-reviewer": ("vue-reviewer", "frameworks"),
    "harmonyos-app-resolver": ("harmonyos-specialist", "frameworks"),
    "pytorch-build-resolver": ("pytorch-build-fixer", "ml"),
    "agent-evaluator": ("agent-evaluator", "harness"),
    "conversation-analyzer": ("conversation-analyzer", "harness"),
    "loop-operator": ("loop-operator", "harness"),
    "gan-planner": ("gan-planner", "gan"),
    "gan-generator": ("gan-generator", "gan"),
    "gan-evaluator": ("gan-evaluator", "gan"),
    "opensource-forker": ("open-source-forker", "opensource"),
    "opensource-packager": ("open-source-packager", "opensource"),
    "network-architect": ("network-architect", "network"),
    "network-config-reviewer": ("network-config-reviewer", "network"),
    "network-troubleshooter": ("network-troubleshooter", "network"),
    "homelab-architect": ("homelab-architect", "network"),
    "healthcare-reviewer": ("healthcare-reviewer", "domains"),
    "bengali-reviewer": ("bengali-reviewer", "domains"),
    "chief-of-staff": ("chief-of-staff", "ops"),
}
# ECC agent -> the team-workflow role that already does its job
COVERED = {
    "a11y-architect": "accessibility-specialist", "architect": "architect",
    "code-explorer": "code-explorer", "code-reviewer": "code-reviewer",
    "doc-updater": "doc-keeper", "e2e-runner": "e2e-tester", "harness-optimizer": "harness-optimizer",
    "marketing-agent": "marketing-strategist", "mle-reviewer": "ml-reviewer",
    "opensource-sanitizer": "open-source-sanitizer", "performance-optimizer": "performance-engineer",
    "planner": "planner", "pr-test-analyzer": "test-coverage-reviewer",
    "rag-pipeline-reviewer": "rag-reviewer", "refactor-cleaner": "refactor-specialist",
    "security-reviewer": "security-reviewer", "seo-specialist": "seo-specialist",
    "silent-failure-hunter": "silent-failure-hunter", "tdd-guide": "tester",
    "type-design-analyzer": "type-design-reviewer", "typescript-reviewer": "typescript-reviewer",
    **{f"{lang}-reviewer": f"{lang}-reviewer" for lang in (
        "cpp", "csharp", "fsharp", "go", "java", "kotlin", "php", "python", "ruby", "rust", "swift")},
    **{f"{lang}-build-resolver": f"{lang}-build-fixer" for lang in (
        "cpp", "dart", "go", "java", "kotlin", "rust", "swift")},
}
COLORS = {"quality": "red", "planning": "blue", "frameworks": "cyan", "ml": "purple",
          "harness": "yellow", "gan": "orange", "opensource": "green", "network": "blue",
          "domains": "purple", "ops": "green"}
RUNTIME = "CLAUDE_PLUGIN_ROOT"  # an entry that calls ECC's own scripts needs ECC installed


def read(path):
    with open(path, encoding="utf-8", errors="replace") as f:
        return f.read().replace("\r\n", "\n")


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def front(text):
    """(simple frontmatter dict, body). Folded values (`>`, `|`) and indented lines are joined."""
    m = re.match(r"\A---\n(.*?)\n---\n?(.*)\Z", text, re.S)
    if not m:
        return {}, text
    meta, key = {}, None
    for line in m.group(1).splitlines():
        if re.match(r"^[A-Za-z][\w-]*:", line):
            key, _, value = line.partition(":")
            key, value = key.strip(), value.strip()
            meta[key] = "" if value in (">", "|", ">-", "|-") else value
        elif key and line.startswith((" ", "\t")):
            meta[key] = (meta[key] + " " + line.strip()).strip()
    for k, v in meta.items():
        if len(v) > 1 and v[0] == v[-1] and v[0] in "\"'":
            meta[k] = json.loads(v) if v[0] == '"' else v[1:-1]
    return meta, m.group(2)


def drop_defense(body):
    """ECC's "Prompt Defense Baseline" section: our untrusted-input block replaces it."""
    return re.sub(r"^## Prompt Defense Baseline\n.*?(?=^#)", "", body, flags=re.S | re.M).strip()


def import_agents(ecc):
    names = sorted(n[:-3] for n in os.listdir(os.path.join(ecc, "agents")) if n.endswith(".md"))
    unknown = [n for n in names if n not in IMPORT and n not in COVERED]
    if unknown:
        raise SystemExit(f"new ECC agents, add them to IMPORT or COVERED: {', '.join(unknown)}")
    written = []
    for name in names:
        if name not in IMPORT:
            continue
        role, pack = IMPORT[name]
        meta, body = front(read(os.path.join(ecc, "agents", name + ".md")))
        path = os.path.join(ROLES, pack, role + ".md")
        if os.path.exists(path) and 'source: "ECC' not in read(path):
            raise SystemExit(f"{path} is a team-workflow role, not an imported one: rename {name}")
        tools = [t.strip() for t in meta.get("tools", "Read, Grep, Glob").split(",") if t.strip()]
        lines = ["---", f"name: {role}", f"description: {json.dumps(meta.get('description', role))}",
                 f"tools: {json.dumps(tools)}", f"color: {COLORS[pack]}"]
        if role.endswith("-reviewer"):
            lines.append('includes: ["review-discipline"]')
        lines += [f'source: "ECC agents/{name}.md (MIT, affaan-m/everything-claude-code)"', "---", "", ""]
        write(path, "\n".join(lines) + drop_defense(body) + "\n")
        written.append(role)
    return written


def digest(folder):
    h = hashlib.sha1()
    for base, _, files in sorted(os.walk(folder)):
        for name in sorted(files):
            path = os.path.join(base, name)
            h.update(os.path.relpath(path, folder).replace(os.sep, "/").encode())
            with open(path, "rb") as f:
                h.update(f.read().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def one_line(text):
    return re.sub(r"\s+", " ", text or "").strip()


def entry(eid, kind, pack, description, folder, **extra):
    text = "".join(read(os.path.join(b, n)) for b, _, fs in os.walk(folder) for n in fs
                   if n.endswith((".md", ".sh", ".py", ".js", ".mjs", ".json")))
    e = {"id": eid, "kind": kind, "pack": pack, "description": one_line(description)}
    if RUNTIME in text:
        e["runtime"] = "ecc"
    e.update(extra)
    return e


def skill_packs(ecc):
    """{"skills/<name>": (pack, pack description)} from ECC's install modules."""
    with open(os.path.join(ecc, "manifests", "install-modules.json"), encoding="utf-8") as f:
        modules = json.load(f)["modules"]
    found = {}
    for mod in modules:
        for p in mod.get("paths", []):
            if p.startswith("skills/"):
                found.setdefault(p, (mod["id"], one_line(mod.get("description"))))
    return found


def import_library(ecc):
    shutil.rmtree(LIBRARY, ignore_errors=True)
    os.makedirs(LIBRARY)
    entries, packs = [], {}
    owner = skill_packs(ecc)
    names = sorted(os.listdir(os.path.join(ecc, "skills")))
    for name in names:
        src = os.path.join(ecc, "skills", name)
        if not os.path.isfile(os.path.join(src, "SKILL.md")):
            continue
        pack, about = owner.get(f"skills/{name}", ("misc", "Skills without an ECC module."))
        if pack in names:  # a pack named like a skill: keep the two names apart
            pack += "-pack"
        packs[pack] = about
        dest = os.path.join(LIBRARY, name)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        os.replace(os.path.join(dest, "SKILL.md"), os.path.join(dest, "MAIN.md"))
        meta, _ = front(read(os.path.join(dest, "MAIN.md")))
        entries.append(entry(name, "skill", pack, meta.get("description"), dest))
    skills = {e["id"] for e in entries}
    packs["commands"] = "ECC slash commands, installed as skills you call by name."
    for file in sorted(os.listdir(os.path.join(ecc, "commands"))):
        if not file.endswith(".md"):
            continue
        name = file[:-3]
        eid = name + "-command" if name in skills else name
        meta, body = front(read(os.path.join(ecc, "commands", file)))
        head = ["---", f"name: {eid}", f"description: {json.dumps(one_line(meta.get('description')) or name)}"]
        if meta.get("argument-hint"):
            head.append(f"argument-hint: {json.dumps(meta['argument-hint'])}")
        head += ["disable-model-invocation: true", "---", ""]
        dest = os.path.join(LIBRARY, eid)
        write(os.path.join(dest, "MAIN.md"), "\n".join(head) + body.strip() + "\n")
        entries.append(entry(eid, "command", "commands", meta.get("description"), dest))
    packs["rules"] = "ECC coding rules: the common set and one set per language or framework."
    rules = sorted(d for d in os.listdir(os.path.join(ecc, "rules"))
                   if os.path.isdir(os.path.join(ecc, "rules", d)))
    for lang in rules:
        eid, src, dest = f"rules-{lang}", os.path.join(ecc, "rules", lang), os.path.join(LIBRARY, f"rules-{lang}")
        listing = []
        for file in sorted(os.listdir(src)):
            if not file.endswith(".md"):
                continue
            text = re.sub(r"\]\(\.\./(" + "|".join(rules) + r")/", r"](../rules-\1/", read(os.path.join(src, file)))
            write(os.path.join(dest, file), text)
            meta, body = front(text)
            title = re.search(r"^# (.+)$", body, re.M)
            listing.append(f"- [{file}]({file}): {title.group(1) if title else file[:-3]}")
        what = "the rules every language follows" if lang == "common" else f"{lang} rules"
        description = (f"Coding rules from ECC, {what}: style, patterns, security, testing. Use when "
                       f"writing or reviewing {'any' if lang == 'common' else lang} code.")
        requires = [] if lang == "common" else ["rules-common"]
        body = (f"# {what.capitalize()}\n\nRead the files that match your work; "
                + ("they extend [rules-common](../rules-common/MAIN.md).\n\n" if requires else "\n\n")
                + "\n".join(listing) + "\n")
        write(os.path.join(dest, "MAIN.md"),
              f"---\nname: {eid}\ndescription: {json.dumps(description)}\n---\n\n{body}")
        extra = {"requires": requires} if requires else {}
        entries.append(entry(eid, "rule", "rules", description, dest, **extra))
    ids = [e["id"] for e in entries]
    clash = sorted({i for i in ids if ids.count(i) > 1} | (set(ids) & set(packs)))
    if clash:
        raise SystemExit(f"library ids clash: {', '.join(clash)}")
    for e in entries:
        e["hash"] = digest(os.path.join(LIBRARY, e["id"]))
    return entries, packs


def main(argv):
    if len(argv) != 1 or not os.path.isdir(os.path.join(argv[0], "agents")):
        raise SystemExit(__doc__)
    ecc = os.path.abspath(argv[0])
    commit = subprocess.run(["git", "-C", ecc, "rev-parse", "HEAD"], capture_output=True,
                            text=True).stdout.strip()
    version = read(os.path.join(ecc, "VERSION")).strip() if os.path.isfile(os.path.join(ecc, "VERSION")) else ""
    roles = import_agents(ecc)
    entries, packs = import_library(ecc)
    index = {"source": {"repo": "affaan-m/everything-claude-code", "version": version, "commit": commit,
                        "license": "MIT"},
             "packs": dict(sorted(packs.items())), "entries": entries}
    write(os.path.join(LIBRARY, "index.json"), json.dumps(index, indent=1, ensure_ascii=False) + "\n")
    write(os.path.join(LIBRARY, "NOTICE.md"),
          f"# Library\n\nImported from Everything Claude Code {version} ({commit[:12]}),\n"
          "https://github.com/affaan-m/everything-claude-code, by `tools/import_ecc.py`.\n"
          "Do not edit these files: rerun the import.\n\n"
          f"```\n{read(os.path.join(ecc, 'LICENSE')).strip()}\n```\n")
    kinds = {k: sum(e["kind"] == k for e in entries) for k in ("skill", "command", "rule")}
    print(f"roles imported: {len(roles)}; covered by existing roles: {len(COVERED)}")
    print(f"library: {kinds['skill']} skills, {kinds['command']} commands, {kinds['rule']} rule sets "
          f"in {len(packs)} packs; {sum('runtime' in e for e in entries)} need ECC's runtime")


if __name__ == "__main__":
    main(sys.argv[1:])
