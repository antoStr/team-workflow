#!/usr/bin/env python3
"""Import the upstream agent collection (Everything Claude Code, MIT license, see
library/NOTICE.md) into team-workflow:

    python3 tools/import_upstream.py <path to the upstream checkout>

- Upstream agents that team-workflow has no role for become roles in
  skills/team-workflow/roles/<pack>/<role>.md. Their model is dropped (the settings choose it)
  and so is their prompt-defense block (every role gets roles/_shared/untrusted-input.md).
  The agents team-workflow already covers (COVERED) are imported too, as alternative versions:
  alt-<name> in the alt pack (off by default).
- Upstream skills, commands and rules become the library, skills/team-workflow/library/<id>/,
  each with MAIN.md instead of SKILL.md, so no app loads hundreds of skills by itself, and
  library/index.json; `tw.py library` searches them and installs the chosen ones as skills.
  Entries that only serve the upstream project itself (its installer, its repository, its
  scripts) are left out: everything in the library works on its own.
- Role text names neither the upstream project nor its paths: `skills/<id>/SKILL.md` becomes
  the library entry.

Rerun it after an upstream update: the library is rebuilt and the imported roles are rewritten;
a role file without the `source: "imported` line is never overwritten. An upstream agent that
is in neither IMPORT nor COVERED stops the import, so every new agent gets a decision.
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
    # Codex variants in .codex/agents
    "docs-researcher": "docs-lookup", "explorer": "code-explorer", "reviewer": "code-reviewer",
    **{f"{lang}-reviewer": f"{lang}-reviewer" for lang in (
        "cpp", "csharp", "fsharp", "go", "java", "kotlin", "php", "python", "ruby", "rust", "swift")},
    **{f"{lang}-build-resolver": f"{lang}-build-fixer" for lang in (
        "cpp", "dart", "go", "java", "kotlin", "rust", "swift")},
}
COLORS = {"quality": "red", "planning": "blue", "frameworks": "cyan", "ml": "purple",
          "harness": "yellow", "gan": "orange", "opensource": "green", "network": "blue",
          "domains": "purple", "ops": "green", "alt": "yellow"}
COMMAND_DIRS = ("commands", ".claude/commands", "legacy-command-shims/commands", ".opencode/commands")
RUNTIME = "CLAUDE_PLUGIN_ROOT"  # an entry that calls the upstream project's own scripts
# Entries that exist only for the upstream project itself: its setup, repository and tools.
UPSTREAM_ONLY = {
    "agent-sort", "auto-update", "configure-ecc", "cost-report", "deepseek-harness-setup",
    "ecc-conventions", "ecc-council", "ecc-guide", "ecc-guide-command", "ecc-recipes",
    "ecc-tools-cost-audit", "hermes-imports", "nanoclaw-repl", "nasiko-control-plane",
    "project-init", "quality-gate", "skill-host-compat", "skill-host-compat-command",
    "add-language-rules", "database-migration", "feature-development",
    "cost-tracking", "unified-memory", "workspace-surface-audit", "docs-governance",
}
SOURCE = 'source: "imported (MIT, see library/NOTICE.md)"'



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


def neutral(text, ids):
    """Role text without the upstream name or paths: a skill path becomes the library entry."""
    def entry_ref(m):
        return (f"the `{m.group(1)}` library entry (`tw.py library show {m.group(1)}`)"
                if m.group(1) in ids else m.group(0))
    text = re.sub(r"`?(?:~/\.claude/)?skills/([a-z0-9-]+)(?:/SKILL\.md)?`?", entry_ref, text)
    text = re.sub(r"\s+(?:for|through|in|with|of) (?:the )?(?:Everything Claude Code|ECC)\b(?:'s)?", "", text)
    text = re.sub(r"\ban (?:Everything Claude Code|ECC)(?:-native|-specific)? ", "a ", text)
    text = re.sub(r"\b(?:Everything Claude Code|ECC)'s\b", "the", text)
    text = re.sub(r"\b(?:Everything Claude Code|ECC)(?:-native|-specific)?\b[ -]?", "", text)
    return re.sub(r"  +", " ", text)


def neutral_main(path, ids):
    """The description in a library entry's frontmatter, without the upstream name."""
    text = read(path)
    m = re.match(r"\A(---\n.*?\n---\n)", text, re.S)
    if m:
        write(path, neutral(m.group(1), ids) + text[m.end():])


def drop_defense(body):
    """ECC's "Prompt Defense Baseline" section: our untrusted-input block replaces it."""
    return re.sub(r"^## Prompt Defense Baseline\n.*?(?=^#)", "", body, flags=re.S | re.M).strip()


def import_agents(ecc):
    names = sorted(n[:-3] for n in os.listdir(os.path.join(ecc, "agents")) if n.endswith(".md"))
    codex = os.path.join(ecc, ".codex", "agents")
    others = sorted(os.path.splitext(n)[0] for n in os.listdir(codex)) if os.path.isdir(codex) else []
    unknown = [n for n in names + others if n not in IMPORT and n not in COVERED]
    if unknown:
        raise SystemExit(f"new ECC agents, add them to IMPORT or COVERED: {', '.join(unknown)}")
    written = []
    for old in ("ecc", "alt"):  # rebuilt below
        shutil.rmtree(os.path.join(ROLES, old), ignore_errors=True)
    ids = set(os.listdir(os.path.join(ecc, "skills"))) - UPSTREAM_ONLY
    for name in names:
        meta, body = front(read(os.path.join(ecc, "agents", name + ".md")))
        if name in IMPORT:
            role, pack = IMPORT[name]
        else:  # an alternative version of a role we have, in the alt pack (off)
            role, pack = "alt-" + name, "alt"
            meta["description"] = (f"Alternative version of the {COVERED[name]} role. "
                                   + meta.get("description", ""))
        path = os.path.join(ROLES, pack, role + ".md")
        if os.path.exists(path) and not re.search(r'^source: "(?:imported|ECC)', read(path), re.M):
            raise SystemExit(f"{path} is a team-workflow role, not an imported one: rename {name}")
        tools = [t.strip() for t in meta.get("tools", "Read, Grep, Glob").split(",") if t.strip()]
        lines = ["---", f"name: {role}",
                 f"description: {json.dumps(neutral(meta.get('description', role), ids))}",
                 f"tools: {json.dumps(tools)}", f"color: {COLORS[pack]}"]
        if role.endswith("-reviewer") or name.endswith(("-reviewer", "-analyzer")):
            lines.append('includes: ["review-discipline"]')
        lines += [SOURCE, "---", "", ""]
        write(path, "\n".join(lines) + neutral(drop_defense(body), ids) + "\n")
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


LIBRARY_IDS = set()  # filled by import_library: the ids neutral() may point to


def entry(eid, kind, pack, description, folder, **extra):
    text = "".join(read(os.path.join(b, n)) for b, _, fs in os.walk(folder) for n in fs
                   if n.endswith((".md", ".sh", ".py", ".js", ".mjs", ".json")))
    if eid in UPSTREAM_ONLY or RUNTIME in text:  # works only inside the upstream project
        shutil.rmtree(folder)
        return None
    neutral_main(os.path.join(folder, "MAIN.md"), LIBRARY_IDS)
    e = {"id": eid, "kind": kind, "pack": pack, "description": one_line(neutral(description or "", LIBRARY_IDS))}
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
                about = " ".join(t for t in re.split(r"(?<=\.)\s+", one_line(mod.get("description")))
                                 if "ecc" not in t.lower())  # sentences about the upstream runtime
                found.setdefault(p, (mod["id"], about))
    return found


def extra_skills(ecc):
    """Skill folders outside skills/, first path first (translated docs only when no other)."""
    found = []
    for base, dirs, files in os.walk(ecc):
        dirs[:] = sorted(d for d in dirs if d not in (".git", "node_modules"))
        rel = os.path.relpath(base, ecc).replace(os.sep, "/")
        if "SKILL.md" in files and not rel.startswith("skills/"):
            found.append(base)
    return sorted(found, key=lambda p: ("/docs/" in p.replace(os.sep, "/"), p))


def command_files(ecc):
    """(folder, file.md) of every command, in order of precedence: commands/, then the ones ECC
    keeps for Claude Code projects, the legacy shims and OpenCode."""
    for rel in COMMAND_DIRS:
        folder = os.path.join(ecc, *rel.split("/"))
        for file in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
            if file.endswith(".md") and file != "README.md":
                yield folder, file


def import_library(ecc):
    shutil.rmtree(LIBRARY, ignore_errors=True)
    os.makedirs(LIBRARY)
    entries, packs = [], {}
    owner = skill_packs(ecc)
    names = sorted(os.listdir(os.path.join(ecc, "skills")))
    LIBRARY_IDS.update(set(names) - UPSTREAM_ONLY)
    sources = [(n, os.path.join(ecc, "skills", n)) for n in names]
    for folder in extra_skills(ecc):  # skills kept outside skills/ (.agents, pi, docs)
        name = os.path.basename(folder)
        if name not in names and name not in {n for n, _ in sources}:
            sources.append((name, folder))
    for name, src in sources:
        if not os.path.isfile(os.path.join(src, "SKILL.md")):
            continue
        pack, about = owner.get(f"skills/{name}", ("misc", "Skills kept outside the main skills "
                                                   "folder upstream."))
        if pack in names:  # a pack named like a skill: keep the two names apart
            pack += "-pack"
        packs[pack] = about
        dest = os.path.join(LIBRARY, name)
        shutil.copytree(src, dest, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".DS_Store"))
        os.replace(os.path.join(dest, "SKILL.md"), os.path.join(dest, "MAIN.md"))
        meta, _ = front(read(os.path.join(dest, "MAIN.md")))
        entries.append(entry(name, "skill", pack, meta.get("description"), dest))
    entries = [e for e in entries if e]
    skills = {e["id"] for e in entries}
    packs["commands"] = "Slash commands, installed as skills you call by name."
    seen = set()
    for folder, file in command_files(ecc):
        name = file[:-3]
        if name in seen:
            continue
        seen.add(name)
        eid = name + "-command" if name in skills or name in packs else name
        meta, body = front(read(os.path.join(folder, file)))
        head = ["---", f"name: {eid}", f"description: {json.dumps(one_line(meta.get('description')) or name)}"]
        if meta.get("argument-hint"):
            head.append(f"argument-hint: {json.dumps(meta['argument-hint'])}")
        head += ["disable-model-invocation: true", "---", ""]
        dest = os.path.join(LIBRARY, eid)
        write(os.path.join(dest, "MAIN.md"), "\n".join(head) + body.strip() + "\n")
        entries.append(entry(eid, "command", "commands", meta.get("description"), dest))
    packs["rules"] = "Coding rules: the common set and one set per language or framework."
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
        description = (f"Coding rules, {what}: style, patterns, security, testing. Use when "
                       f"writing or reviewing {'any' if lang == 'common' else lang} code.")
        requires = [] if lang == "common" else ["rules-common"]
        body = (f"# {what.capitalize()}\n\nRead the files that match your work; "
                + ("they extend [rules-common](../rules-common/MAIN.md).\n\n" if requires else "\n\n")
                + "\n".join(listing) + "\n")
        write(os.path.join(dest, "MAIN.md"),
              f"---\nname: {eid}\ndescription: {json.dumps(description)}\n---\n\n{body}")
        extra = {"requires": requires} if requires else {}
        entries.append(entry(eid, "rule", "rules", description, dest, **extra))
    entries = [e for e in entries if e]
    packs = {k: v for k, v in packs.items() if any(e["pack"] == k for e in entries)}
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
          "https://github.com/affaan-m/everything-claude-code, by `tools/import_upstream.py`.\n"
          "Do not edit these files: rerun the import.\n\n"
          f"```\n{read(os.path.join(ecc, 'LICENSE')).strip()}\n```\n")
    kinds = {k: sum(e["kind"] == k for e in entries) for k in ("skill", "command", "rule")}
    print(f"roles imported: {len(roles)} ({sum(r.startswith('alt-') for r in roles)} in the alt pack, "
          f"next to the team-workflow role that covers them)")
    print(f"library: {kinds['skill']} skills, {kinds['command']} commands, {kinds['rule']} rule sets "
          f"in {len(packs)} packs")


if __name__ == "__main__":
    main(sys.argv[1:])
