#!/usr/bin/env python3
"""Neural Cortex Router, Project Genome Assimilation & Meta-Skill Evolution Engine.

Evolves team-workflow beyond prompt-based multi-agent orchestration into a
resource-aware neural routing & self-evolving system:
1. Sensory Layer: perceives available resources (hardware thermal/RAM headroom,
   app models/efforts, roles, library + learned skills, Brain graph, vaccines)
   and required task resources (14-domain activation, Brain blast radius, risk,
   complexity, verification gates).
2. Hidden/Output Layer: propagates excitatory & inhibitory synaptic activations
   across specialist roles, allocates optimal models/efforts, binds library &
   learned skills, and selects execution topology.
3. Project Knowledge Assimilation: extracts Brain architectural hubs, git
   co-change coupling clusters, fragility hotspots, and verification commands
   into .team-workflow/project_knowledge.json and docs/brain/PROJECT_GENOME.md.
4. Hebbian Plasticity & Meta-Skill Evolution: learns from task outcomes via
   synaptic weight updates and synthesizes reusable SKILL.md modules (including
   `team-meta-cortex`) in .team-workflow/skills/.
"""
import ast
import collections
from datetime import datetime, timezone
import json
import os
import re
import shutil
import subprocess

import autolearn
import brain
import library
import omniscience
import roles
import scan
import settings
import talk
from usage import load_pricing

CORTEX_DIR = ".team-workflow"
WEIGHTS_FILE = "cortex_weights.json"
KNOWLEDGE_FILE = "project_knowledge.json"
GENOME_MD = os.path.join("docs", "brain", "PROJECT_GENOME.md")
LEARNED_SKILLS_REL = os.path.join(".team-workflow", "skills")

WEIGHT_MIN = -0.5
WEIGHT_MAX = 1.0

DOMAIN_RECEPTORS = {
    "frontend": {
        "keywords": ("ui", "ux", "frontend", "react", "next", "nextjs", "vue", "svelte",
                     "tailwind", "css", "html", "component", "layout", "modal", "dialog",
                     "button", "responsive", "accessibility", "a11y", "wcag", "animation",
                     "shadcn", "radix", "design", "browser", "dom", "canvas", "style"),
        "roles": ("frontend-dev", "design-engineer", "ui-ux-designer", "accessibility-specialist",
                  "react-reviewer", "vue-reviewer", "e2e-tester", "flutter-reviewer"),
        "skill_hints": ("frontend-components", "shadcn-ui", "base-ui", "radix-ui", "ui-styling",
                        "frontend-design", "impeccable", "ui-ux-pro-max", "solar-icons"),
        "gates": ("smoke", "visual-check", "verify-docs"),
    },
    "backend": {
        "keywords": ("api", "backend", "server", "endpoint", "route", "rest", "graphql",
                     "grpc", "auth", "oauth", "jwt", "session", "worker", "queue", "cli",
                     "script", "service", "webhook", "fastapi", "django", "python", "node",
                     "go", "rust", "cortex", "router", "orchestrate"),
        "roles": ("backend-dev", "code-architect", "build-fixer", "fastapi-reviewer",
                  "django-reviewer", "python-reviewer", "go-reviewer", "rust-reviewer"),
        "skill_hints": ("backend", "api", "rules-", "dotnet-patterns", "workers-", "mcp-builder"),
        "gates": ("smoke", "verify-docs"),
    },
    "architecture": {
        "keywords": ("architect", "architecture", "design", "system", "module", "boundary",
                     "interface", "contract", "schema", "protocol", "pattern", "plugin",
                     "monolith", "microservice", "neural", "evolve", "orchestration", "spec"),
        "roles": ("architect", "code-architect", "code-explorer", "spec-miner", "planner",
                  "type-design-reviewer"),
        "skill_hints": ("brainstorming", "writing-plans", "agentic-patterns", "orchestration",
                        "lean-build"),
        "gates": ("smoke", "verify-docs"),
    },
    "security": {
        "keywords": ("security", "auth", "authentication", "authorization", "xss", "sqli",
                     "sql injection", "csrf", "ssrf", "idor", "pentest", "vulnerability",
                     "exploit", "cve", "token", "secret", "password", "encrypt", "crypto",
                     "tls", "oauth", "rbac", "permission", "audit", "sanitize", "strix"),
        "roles": ("security-reviewer", "pentester", "code-reviewer", "open-source-sanitizer"),
        "skill_hints": ("security", "strix-pentest", "cloudflare-sec", "security-audit",
                        "owasp-top-10-testing", "penetration-testing-with-strix"),
        "gates": ("smoke", "gate", "verify-docs"),
    },
    "reverse_engineering": {
        "keywords": ("reverse", "reversing", "decompile", "disassemble", "binary", "elf",
                     "pe", "mach-o", "firmware", "ida", "ghidra", "x64dbg", "cutter",
                     "assembly", "asm", "rop", "shellcode", "protocol", "patch binary"),
        "roles": ("reverse-engineer", "malware-analyst", "security-reviewer"),
        "skill_hints": ("malware-reverse-engineering-disassembly", "malware-pe-binary-exploration",
                        "malware-exploit-payload-analysis"),
        "gates": ("smoke", "gate", "wsl", "verify-docs"),
    },
    "malware": {
        "keywords": ("malware", "ransomware", "rat", "trojan", "infostealer", "yara", "sigma",
                     "ioc", "c2", "beacon", "pcap", "sandbox", "obfuscate", "deobfuscate",
                     "macro", "vba", "stix", "mitre", "forensics", "rootkit", "wiper"),
        "roles": ("malware-analyst", "reverse-engineer", "pentester", "security-reviewer"),
        "skill_hints": ("malware-analysis", "threat-intel-url", "malware-initial-triage",
                        "malware-yara-rule-development", "malware-sigma-rule-development"),
        "gates": ("smoke", "gate", "wsl", "verify-docs"),
    },
    "database": {
        "keywords": ("sql", "postgres", "postgresql", "mysql", "sqlite", "database", "db",
                     "migration", "schema", "index", "query", "transaction", "orm", "prisma",
                     "drizzle", "supabase", "rls", "backup", "restore", "table"),
        "roles": ("database-engineer", "database-reviewer", "backend-dev"),
        "skill_hints": ("database", "postgres-patterns", "database-migrations"),
        "gates": ("smoke", "gate", "verify-docs"),
    },
    "devops": {
        "keywords": ("ci", "cd", "pipeline", "github actions", "docker", "container", "k8s",
                     "kubernetes", "deploy", "terraform", "cloudflare", "wrangler", "env",
                     "release", "tag", "changelog", "monitor", "linux", "wsl", "systemd"),
        "roles": ("devops-engineer", "release-manager", "build-fixer", "network-architect"),
        "skill_hints": ("devops-infra", "cloudflare", "wrangler", "workers-"),
        "gates": ("smoke", "verify-docs"),
    },
    "testing": {
        "keywords": ("test", "tests", "pytest", "unittest", "vitest", "jest", "playwright",
                     "e2e", "coverage", "regression", "assert", "mock", "smoke", "verify",
                     "verification", "qa", "bug", "crash", "fix", "debug", "broken"),
        "roles": ("tester", "e2e-tester", "test-coverage-reviewer", "code-reviewer",
                  "silent-failure-hunter"),
        "skill_hints": ("test-driven-development", "webapp-testing", "systematic-debugging",
                        "verification-before-completion", "csharp-testing"),
        "gates": ("smoke", "verify-docs"),
    },
    "performance": {
        "keywords": ("slow", "performance", "latency", "memory", "leak", "cpu", "gpu",
                     "benchmark", "profile", "optimize", "cache", "bundle", "vitals",
                     "lighthouse", "bottleneck", "throughput", "scale"),
        "roles": ("performance-engineer", "code-reviewer", "database-reviewer"),
        "skill_hints": ("web-perf", "workers-profiling", "optimization-workflows"),
        "gates": ("smoke", "verify-docs"),
    },
    "pm": {
        "keywords": ("roadmap", "schedule", "gantt", "milestone", "budget", "risk",
                     "stakeholder", "sprint", "agile", "scrum", "charter", "wbs",
                     "project plan", "estimate", "requirements", "backlog", "scope"),
        "roles": ("project-manager", "product-manager", "project-scheduler",
                  "project-controller", "risk-manager", "stakeholder-manager", "agile-coach"),
        "skill_hints": ("project-management", "doc-coauthoring"),
        "gates": ("verify-docs",),
    },
    "documentation": {
        "keywords": ("doc", "docs", "documentation", "readme", "changelog", "guide",
                     "tutorial", "comment", "docstring", "memory", "brain", "state.md",
                     "catalog", "wiki"),
        "roles": ("doc-keeper", "technical-writer", "comment-analyzer"),
        "skill_hints": ("documentation-context", "documentation-change-impact", "doc-coauthoring"),
        "gates": ("verify-docs",),
    },
    "refactoring": {
        "keywords": ("refactor", "cleanup", "simplify", "deduplicate", "extract",
                     "technical debt", "dead code", "modularize", "split", "rename",
                     "lint", "types", "typing"),
        "roles": ("refactor-specialist", "code-simplifier", "code-reviewer",
                  "type-design-reviewer"),
        "skill_hints": ("safe-refactor", "karpathy-guidelines", "code-quality"),
        "gates": ("smoke", "verify-docs"),
    },
    "ml": {
        "keywords": ("ml", "ai", "llm", "model", "neural", "pytorch", "tensorflow", "rag",
                     "embedding", "vector", "agent", "prompt", "eval", "benchmark", "train",
                     "inference", "weights", "synapse", "fine-tune"),
        "roles": ("ml-reviewer", "pytorch-build-fixer", "rag-reviewer", "agent-evaluator",
                  "harness-optimizer", "data-analyst"),
        "skill_hints": ("machine-learning", "agentic-patterns", "skill-creator"),
        "gates": ("smoke", "verify-docs"),
    },
}

EXCITATORY_SYNAPSES = {
    "frontend-dev": [("tester", 0.24), ("design-engineer", 0.22), ("accessibility-specialist", 0.16)],
    "design-engineer": [("frontend-dev", 0.22), ("accessibility-specialist", 0.20), ("ui-ux-designer", 0.18)],
    "backend-dev": [("tester", 0.26), ("code-reviewer", 0.20), ("security-reviewer", 0.14)],
    "database-engineer": [("database-reviewer", 0.26), ("backend-dev", 0.18), ("tester", 0.18)],
    "architect": [("code-reviewer", 0.18), ("tester", 0.18), ("doc-keeper", 0.14)],
    "code-architect": [("code-explorer", 0.20), ("tester", 0.18)],
    "security-reviewer": [("pentester", 0.24), ("code-reviewer", 0.16)],
    "pentester": [("security-reviewer", 0.22), ("backend-dev", 0.14)],
    "reverse-engineer": [("malware-analyst", 0.22), ("security-reviewer", 0.16)],
    "malware-analyst": [("reverse-engineer", 0.22), ("security-reviewer", 0.16)],
    "project-manager": [("project-scheduler", 0.22), ("risk-manager", 0.20), ("project-controller", 0.16)],
    "refactor-specialist": [("code-reviewer", 0.22), ("tester", 0.22), ("code-simplifier", 0.16)],
    "devops-engineer": [("security-reviewer", 0.16), ("tester", 0.16)],
    "performance-engineer": [("tester", 0.20), ("code-reviewer", 0.16)],
}

INHIBITORY_GROUPS = (
    ("architect", "code-architect", "alt-architect"),
    ("code-reviewer", "alt-code-reviewer"),
    ("security-reviewer", "alt-security-reviewer"),
    ("accessibility-specialist", "alt-a11y-architect"),
    ("refactor-specialist", "alt-refactor-cleaner", "code-simplifier"),
    ("code-explorer", "alt-code-explorer"),
    ("e2e-tester", "alt-e2e-runner"),
    ("doc-keeper", "alt-doc-updater", "technical-writer"),
    ("performance-engineer", "alt-performance-optimizer"),
    ("python-reviewer", "alt-python-reviewer"),
    ("typescript-reviewer", "alt-typescript-reviewer"),
    ("rust-reviewer", "alt-rust-reviewer"),
    ("go-reviewer", "alt-go-reviewer"),
)

HIGH_COGNITIVE_ROLES = {
    "architect", "code-architect", "security-reviewer", "pentester", "reverse-engineer",
    "malware-analyst", "database-engineer", "performance-engineer", "harness-optimizer",
}

VERIFIER_ROLES = {
    "tester", "e2e-tester", "code-reviewer", "security-reviewer", "pentester",
    "database-reviewer", "test-coverage-reviewer", "silent-failure-hunter",
    "type-design-reviewer", "accessibility-specialist",
}

BUILDER_ROLES = {
    "backend-dev", "frontend-dev", "design-engineer", "database-engineer",
    "devops-engineer", "refactor-specialist", "build-fixer", "doc-keeper",
}

STACK_ROLE_MAP = {
    "python": ("python-reviewer", "python-build-fixer", "django-reviewer", "fastapi-reviewer"),
    "javascript/typescript": ("typescript-reviewer", "react-reviewer", "react-build-fixer", "vue-reviewer"),
    "rust": ("rust-reviewer", "rust-build-fixer"),
    "go": ("go-reviewer", "go-build-fixer"),
    "c# / .net": ("csharp-reviewer", "csharp-build-fixer"),
}

EXT_DOMAIN_MAP = {
    ".tsx": "frontend", ".jsx": "frontend", ".css": "frontend", ".scss": "frontend", ".html": "frontend",
    ".py": "backend", ".go": "backend", ".rs": "backend", ".ts": "backend", ".js": "backend",
    ".sql": "database", ".prisma": "database",
    ".yml": "devops", ".yaml": "devops", ".dockerfile": "devops", ".tf": "devops",
    ".md": "documentation",
    ".yar": "malware", ".yara": "malware",
}


def _clamp(val, lo=WEIGHT_MIN, hi=WEIGHT_MAX):
    return max(lo, min(hi, round(float(val), 4)))


def _slug(text):
    clean = re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")
    return clean[:50] or "skill"


def _tokenize(text):
    return re.findall(r"[a-z0-9_+#.-]+", str(text or "").lower())


def _cortex_dir(root="."):
    return os.path.join(os.path.abspath(root), CORTEX_DIR)


def _weights_path(root="."):
    return os.path.join(_cortex_dir(root), WEIGHTS_FILE)


def _global_weights_path():
    return os.path.join(settings.home_dir(), WEIGHTS_FILE)


def _knowledge_path(root="."):
    return os.path.join(_cortex_dir(root), KNOWLEDGE_FILE)


def _read_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except (OSError, ValueError):
        return default


def _ensure_cortex_gitignore(cortex_dir):
    """Keep auto-assimilated .team-workflow artifacts invisible to git status."""
    os.makedirs(cortex_dir, exist_ok=True)
    gi = os.path.join(cortex_dir, ".gitignore")
    if not os.path.isfile(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("*\n")


def _write_json(path, data):
    parent = os.path.dirname(path)
    os.makedirs(parent, exist_ok=True)
    if os.path.basename(parent) == CORTEX_DIR:
        _ensure_cortex_gitignore(parent)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _empty_weights():
    return {
        "version": 1,
        "updated_at": None,
        "roles": {},
        "skills": {},
        "domain_roles": {},
        "role_skills": {},
        "stats": {"passes": 0, "failures": 0, "total_runs": 0},
        "history": [],
    }


def load_weights(root="."):
    """Load project synaptic weights merged over global user weights."""
    global_w = _read_json(_global_weights_path(), {})
    local_w = _read_json(_weights_path(root), {})
    out = _empty_weights()
    for bucket in ("roles", "skills", "domain_roles", "role_skills"):
        merged = dict(global_w.get(bucket) or {})
        for k, v in (local_w.get(bucket) or {}).items():
            merged[k] = _clamp(merged.get(k, 0.0) * 0.4 + float(v)) if k in merged else _clamp(v)
        out[bucket] = merged
    if local_w.get("stats"):
        out["stats"] = dict(local_w["stats"])
    elif global_w.get("stats"):
        out["stats"] = dict(global_w["stats"])
    out["history"] = list(local_w.get("history") or global_w.get("history") or [])
    out["updated_at"] = local_w.get("updated_at") or global_w.get("updated_at")
    return out


def _parse_frontmatter(text):
    """Parse lightweight YAML frontmatter from SKILL.md files."""
    m = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n?(.*)\Z", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            try:
                parsed = json.loads(v)
                meta[k] = [str(x) for x in parsed] if isinstance(parsed, list) else []
            except ValueError:
                meta[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            meta[k] = v.strip("'\"")
    return meta, m.group(2)


def load_learned_skills(root="."):
    """Discover learned and meta-skills in <root>/.team-workflow/skills and ~/.team-workflow/skills."""
    found = {}
    roots = [
        (os.path.join(settings.home_dir(), "skills"), "user"),
        (os.path.join(os.path.abspath(root), LEARNED_SKILLS_REL), "project"),
    ]
    for folder, origin in roots:
        if not os.path.isdir(folder):
            continue
        for entry in sorted(os.listdir(folder)):
            skill_md = os.path.join(folder, entry, "SKILL.md")
            if not os.path.isfile(skill_md):
                continue
            try:
                with open(skill_md, encoding="utf-8", errors="replace") as f:
                    text = f.read()
            except OSError:
                continue
            meta, body = _parse_frontmatter(text)
            sid = meta.get("name") or entry
            triggers = meta.get("triggers") or []
            if isinstance(triggers, str):
                triggers = [x.strip() for x in triggers.split(",") if x.strip()]
            target_roles = meta.get("roles") or []
            if isinstance(target_roles, str):
                target_roles = [x.strip() for x in target_roles.split(",") if x.strip()]
            found[sid] = {
                "id": sid,
                "pack": meta.get("pack") or "learned",
                "kind": "skill",
                "description": meta.get("description") or f"Learned project skill ({sid})",
                "path": skill_md,
                "triggers": triggers,
                "roles": target_roles,
                "origin": origin,
                "learned": True,
                "body_preview": " ".join(body.split())[:220],
            }
    return found


def _hardware_profile(config):
    """Perceive host CPU/GPU thermal and RAM headroom via settings.hardware_status()."""
    hw_data, age = settings.hardware_status()
    stale = bool(hw_data) and age is not None and age > settings.HARDWARE_STALE_SECONDS
    if not hw_data or stale:
        return {
            "telemetry_active": False,
            "stale": stale,
            "status": "UNKNOWN" if not hw_data else "STALE",
            "cpu_temp_c": None,
            "gpu_temp_c": None,
            "ram_percent": None,
            "capacity_factor": 1.0,
            "effective_max_agents": max(1, int(config.get("max_agents", 4))),
        }
    cpu_temp = (hw_data.get("CPU") or {}).get("Temp_C")
    gpu_temp = (hw_data.get("GPU") or {}).get("Temp_C")
    ram_pct = (hw_data.get("RAM") or {}).get("PercentUsed")
    status = str(hw_data.get("Status") or "OK").upper()

    is_critical = (
        status == "CRITICAL"
        or (isinstance(cpu_temp, (int, float)) and cpu_temp > 85)
        or (isinstance(gpu_temp, (int, float)) and gpu_temp > 80)
        or (isinstance(ram_pct, (int, float)) and ram_pct > 93)
    )
    is_warning = (
        status == "WARNING"
        or (isinstance(ram_pct, (int, float)) and ram_pct > 85)
        or (isinstance(cpu_temp, (int, float)) and cpu_temp > 75)
        or (isinstance(gpu_temp, (int, float)) and gpu_temp > 72)
    )
    factor = 0.35 if is_critical else (0.65 if is_warning else 1.0)
    max_agents = max(1, int(config.get("max_agents", 4)))
    eff_max = max(1, round(max_agents * factor))
    return {
        "telemetry_active": True,
        "stale": False,
        "status": "CRITICAL" if is_critical else ("WARNING" if is_warning else "OK"),
        "cpu_temp_c": cpu_temp,
        "gpu_temp_c": gpu_temp,
        "ram_percent": ram_pct,
        "capacity_factor": factor,
        "effective_max_agents": eff_max,
    }


def _available_models(app, pricing):
    """Collect available models and efforts for the active host app."""
    if app == "claude":
        aliases = list((pricing.get("aliases") or {}).keys()) or ["haiku", "sonnet", "opus", "fable"]
        efforts = {
            a: (pricing.get("models") or {}).get(m, {}).get("effort", ["low", "medium", "high"])
            for a, m in (pricing.get("aliases") or {}).items()
        }
        return {"native": aliases, "efforts": efforts}
    if app == "agy":
        return {"native": ["inherit", "flash_lite", "flash", "pro"], "efforts": {}}
    if app == "codex":
        try:
            import install_codex
            found = install_codex.models()
            return {
                "native": ["inherit"] + [m["id"] for m in found],
                "efforts": {m["id"]: m.get("efforts", []) for m in found},
            }
        except Exception:
            return {"native": ["inherit"], "efforts": {}}
    return {"native": ["inherit"], "efforts": {}}


def perceive_resources(root=".", app="agy"):
    """Sensory Layer 1: inventory all available compute, model, role, skill, and memory resources."""
    root = os.path.abspath(root)
    config = settings.load(root)
    pricing = load_pricing()
    catalog = roles.catalog(root)
    enabled_roles = sorted(r for r, i in catalog.items() if roles.is_enabled(config, r, i["pack"]))
    disabled_packs = sorted({i["pack"] for r, i in catalog.items() if r not in enabled_roles})
    lib_entries = library.entries()
    learned_skills = load_learned_skills(root)
    hw = _hardware_profile(config)
    knowledge = _read_json(_knowledge_path(root), {})
    weights = load_weights(root)
    vaccines = autolearn.list_learnings(root)

    brain_dir = os.path.join(root, config.get("brain_dir", "docs/brain"))
    brain_nodes = brain._load_all_nodes(brain_dir) if os.path.isdir(brain_dir) else {}

    return {
        "app": app,
        "root": root,
        "hardware_health": hw,
        "models": _available_models(app, pricing),
        "config": {
            "max_agents": int(config.get("max_agents", 4)),
            "effective_max_agents": hw["effective_max_agents"],
            "talk": bool(config.get("talk", True)),
            "talk_rounds": int(config.get("talk_rounds", 3)),
            "auto_security_review": bool(config.get("auto_security_review", True)),
            "launch": config.get("launch", "native"),
        },
        "roles": {
            "total": len(catalog),
            "enabled": enabled_roles,
            "enabled_count": len(enabled_roles),
            "disabled_packs": disabled_packs,
        },
        "skills": {
            "library_count": len(lib_entries),
            "learned_count": len(learned_skills),
            "learned_ids": sorted(learned_skills),
        },
        "memory": {
            "brain_nodes": len(brain_nodes),
            "active_vaccines": len(vaccines),
            "project_knowledge_assimilated": bool(knowledge),
            "co_change_rules": len(knowledge.get("co_change_clusters") or []),
            "fragility_hotspots": len(knowledge.get("fragility_hotspots") or []),
        },
        "plasticity": {
            "learned_role_weights": len(weights.get("roles") or {}),
            "learned_skill_weights": len(weights.get("skills") or {}),
            "total_feedback_runs": (weights.get("stats") or {}).get("total_runs", 0),
        },
    }


def _match_brain_nodes(task_text, files, nodes):
    """Find Brain nodes referenced by the task or file paths and measure 1-hop blast radius."""
    if not nodes:
        return [], 0
    tokens = set(_tokenize(task_text))
    norm_files = [f.replace("\\", "/").lower() for f in (files or [])]
    matched = []
    neighbors = set()
    for slug, node in nodes.items():
        meta = node.get("meta") or {}
        node_files = [str(f).replace("\\", "/").lower() for f in (meta.get("files") or [])]
        title = str(meta.get("title") or slug).lower()
        base_name = os.path.splitext(title)[0]
        hit = (
            slug in tokens
            or title in tokens
            or (len(base_name) >= 3 and base_name in tokens)
            or any(nf in fp or fp in nf or os.path.basename(nf) == os.path.basename(fp)
                   for nf in node_files for fp in norm_files)
            or any(any(part == t for part in re.split(r"[^a-z0-9]+", nf) if len(part) >= 4)
                   for nf in node_files for t in tokens)
        )
        if hit:
            matched.append(slug)
            for wl in node.get("wikilinks") or []:
                neighbors.add(brain._slugify(wl))
            for other_slug, other in nodes.items():
                if slug in {brain._slugify(w) for w in (other.get("wikilinks") or [])}:
                    neighbors.add(other_slug)
    blast = len(neighbors - set(matched))
    return matched[:12], blast


def perceive_requirements(task_text, root=".", files=None):
    """Sensory Layer 2: parse task domain tensor, Brain blast radius, risk, complexity, and gates."""
    root = os.path.abspath(root)
    files = list(files or [])
    scan_report = scan.scan_repository(root, include_cortex=False)
    stack = scan_report.get("stack") or {}
    config = settings.load(root)
    knowledge = _read_json(_knowledge_path(root), {})

    text_lower = str(task_text or "").lower()
    tokens = set(_tokenize(task_text))
    file_tokens = set()
    file_domains = collections.Counter()
    for f in files:
        norm = f.replace("\\", "/").lower()
        file_tokens.update(_tokenize(norm))
        ext = os.path.splitext(norm)[1]
        if ext in EXT_DOMAIN_MAP:
            file_domains[EXT_DOMAIN_MAP[ext]] += 1
        if "test" in norm:
            file_domains["testing"] += 1

    all_tokens = tokens | file_tokens
    langs_lower = {l.lower() for l in stack.get("languages") or []}
    ui_comps = stack.get("ui_components") or []
    fws_lower = " ".join(stack.get("frameworks") or []).lower()

    domain_scores = {}
    for domain, cfg in DOMAIN_RECEPTORS.items():
        score = 0.0
        for kw in cfg["keywords"]:
            if " " in kw:
                if kw in text_lower:
                    score += 0.32
            elif kw in all_tokens:
                score += 0.25
        if file_domains.get(domain):
            score += min(0.45, 0.22 * file_domains[domain])
        if domain == "frontend" and (ui_comps or any(w in fws_lower for w in ("react", "next", "vue", "svelte", "tailwind"))):
            if score > 0 or not task_text.strip():
                score += 0.15
        if domain == "testing" and (stack.get("testing") and any(k in all_tokens for k in ("fix", "bug", "feature", "add", "implement", "build"))):
            score += 0.15
        domain_scores[domain] = round(min(1.0, score), 3)

    if not any(v > 0 for v in domain_scores.values()):
        if "python" in langs_lower or "go" in langs_lower or "rust" in langs_lower:
            domain_scores["backend"] = 0.4
        elif ui_comps:
            domain_scores["frontend"] = 0.4
        else:
            domain_scores["architecture"] = 0.35

    brain_dir = os.path.join(root, config.get("brain_dir", "docs/brain"))
    brain_nodes = brain._load_all_nodes(brain_dir) if os.path.isdir(brain_dir) else {}
    matched_nodes, blast_radius = _match_brain_nodes(task_text, files, brain_nodes)

    co_change_alerts = []
    norm_files = {f.replace("\\", "/") for f in files}
    for rule in knowledge.get("co_change_clusters") or []:
        fa, fb = rule.get("file_a", ""), rule.get("file_b", "")
        if (fa in norm_files or fb in norm_files
                or (fa and os.path.basename(fa).lower() in text_lower)
                or (fb and os.path.basename(fb).lower() in text_lower)):
            co_change_alerts.append(rule)

    hotspot_hits = []
    for hs in knowledge.get("fragility_hotspots") or []:
        fp = hs.get("file", "")
        if fp in norm_files or (fp and os.path.basename(fp).lower() in text_lower):
            hotspot_hits.append(hs)

    vaccines = []
    seen_vid = set()
    for fp in (files or [""]):
        for v in autolearn.get_vaccines(root=root, file_path=fp or None, limit=5):
            if v["id"] not in seen_vid:
                seen_vid.add(v["id"])
                vaccines.append(v)
    if not vaccines:
        for v in autolearn.list_learnings(root):
            text_v = (v.get("title", "") + " " + v.get("trigger", "") + " " + v.get("anti_pattern", "")).lower()
            if any(t in text_v for t in all_tokens if len(t) >= 4):
                if v["id"] not in seen_vid:
                    seen_vid.add(v["id"])
                    vaccines.append(v)

    active_domains = [d for d, s in sorted(domain_scores.items(), key=lambda x: -x[1]) if s >= 0.2]
    complex_words = {"architect", "architecture", "system", "evolve", "neural", "orchestrate",
                     "migrate", "migration", "redesign", "full", "end-to-end", "parallel", "audit"}
    complexity = min(
        1.0,
        0.18 * len(active_domains[:4])
        + min(0.30, 0.06 * blast_radius)
        + min(0.22, 0.06 * len(files))
        + (0.20 if tokens & complex_words else 0.0)
        + (0.10 if len(text_lower.split()) >= 14 else 0.0),
    )

    risk = min(
        1.0,
        0.60 * max(domain_scores["security"], domain_scores["malware"], domain_scores["reverse_engineering"])
        + 0.35 * domain_scores["database"]
        + min(0.25, 0.12 * len(hotspot_hits))
        + min(0.20, 0.08 * len(vaccines))
        + (0.15 if blast_radius >= 5 else 0.0),
    )

    gates = ["smoke"]
    if domain_scores["frontend"] >= 0.25:
        gates.append("visual-check")
    if risk >= 0.55 or max(domain_scores["security"], domain_scores["malware"]) >= 0.35:
        gates.append("gate")
    if max(domain_scores["reverse_engineering"], domain_scores["malware"]) >= 0.35 or "wsl" in all_tokens or "linux" in all_tokens:
        gates.append("wsl")
    gates.append("verify-docs")

    return {
        "task": task_text,
        "files": files,
        "scan": stack,
        "domain_activations": {k: v for k, v in sorted(domain_scores.items(), key=lambda x: -x[1]) if v > 0},
        "top_domains": active_domains or [max(domain_scores, key=domain_scores.get)],
        "matched_brain_nodes": matched_nodes,
        "blast_radius": blast_radius,
        "co_change_alerts": co_change_alerts[:6],
        "fragility_hotspots": hotspot_hits[:5],
        "vaccines": vaccines[:6],
        "complexity": round(complexity, 3),
        "risk": round(risk, 3),
        "required_gates": list(dict.fromkeys(gates)),
    }


def _allocate_model_and_effort(role, app, preset, capacity_factor, complexity, risk, config, available_models):
    """Choose optimal model and reasoning effort given app capabilities, thermal/RAM capacity, and role load."""
    base = roles.plan(config, role, app)
    model = base["model"]
    effort = base["effort"]
    high_load = role in HIGH_COGNITIVE_ROLES or complexity >= 0.65 or risk >= 0.60
    native = available_models.get("native") or []

    if app == "claude":
        if preset == "budget" or capacity_factor <= 0.4:
            model = "sonnet" if high_load else "haiku"
            effort = "medium" if high_load else "low"
        elif capacity_factor < 0.8 or preset == "fast":
            model = "sonnet" if model == "opus" and not high_load else model
            effort = "medium" if high_load else "low"
        elif preset in ("thorough", "security") or (high_load and complexity >= 0.75):
            model = "opus" if role in HIGH_COGNITIVE_ROLES and "opus" in native else model
            effort = "high" if role not in ("security-reviewer", "pentester") else "max"
        else:
            if role in VERIFIER_ROLES and complexity < 0.45:
                effort = "low" if role == "doc-keeper" else "medium"
            elif high_load:
                effort = "high"
        allowed = (available_models.get("efforts") or {}).get(model)
        if allowed and effort not in allowed:
            effort = allowed[-1] if high_load else allowed[0]
        rationale = f"capacity={capacity_factor:.2f}, load={'high' if high_load else 'standard'}, preset={preset}"
        return model, effort, rationale

    if app == "agy":
        if capacity_factor <= 0.4 or preset == "budget":
            model = "flash" if high_load else "flash_lite"
        elif preset == "fast":
            model = "flash"
        elif preset in ("thorough", "security") and high_load:
            model = "inherit"
        else:
            model = "inherit" if high_load else (model if model in native else "inherit")
        effort = "low" if capacity_factor < 0.7 else ("high" if high_load else base["effort"])
        rationale = f"agy tier={model} (capacity={capacity_factor:.2f}, load={'high' if high_load else 'standard'})"
        return model, effort, rationale

    # OpenCode / Codex
    if capacity_factor <= 0.4 or preset == "budget":
        effort = "low"
    elif high_load and complexity >= 0.65:
        effort = "high"
    rationale = f"{app} plan={model}/{effort} (capacity={capacity_factor:.2f})"
    return model, effort, rationale


def _score_skills_for_task(task_text, role, top_domains, lib_entries, learned_skills, weights, langs):
    """Dendritic skill binding: score built-in library + learned skills for a role and task."""
    tokens = set(_tokenize(task_text))
    domain_hints = set()
    for d in top_domains[:3]:
        domain_hints.update(DOMAIN_RECEPTORS.get(d, {}).get("skill_hints", ()))

    all_entries = dict(lib_entries)
    all_entries.update(learned_skills)

    scored = []
    role_skills_w = weights.get("role_skills") or {}
    skill_w = weights.get("skills") or {}
    for sid, entry in all_entries.items():
        desc = str(entry.get("description") or "").lower()
        pack = str(entry.get("pack") or "").lower()
        sid_l = sid.lower()
        score = 0.0

        # Direct task token overlap
        for t in tokens:
            if len(t) < 3:
                continue
            if t in sid_l:
                score += 0.32
            elif t in desc or t in pack:
                score += 0.14

        # Domain hint affinity
        for hint in domain_hints:
            if hint in sid_l or hint in pack:
                score += 0.25

        # Learned skill triggers & role bindings
        if entry.get("learned"):
            score += 0.22  # prior project-specific synthesized skills get baseline resonance
            for trig in entry.get("triggers") or []:
                if trig.lower() in task_text.lower():
                    score += 0.35
            if role in (entry.get("roles") or []) or "*" in (entry.get("roles") or []):
                score += 0.30

        # Language rules boost
        for lang in langs:
            if sid_l == f"rules-{lang.lower()}" and role in (BUILDER_ROLES | VERIFIER_ROLES):
                score += 0.35
        if sid_l == "rules-common" and score > 0:
            score += 0.15

        # Hebbian weights
        score += float(skill_w.get(sid, 0.0)) * 0.45
        score += float(role_skills_w.get(f"{role}:{sid}", 0.0)) * 0.55

        if score >= 0.22:
            path = entry.get("path") or library.main_file(sid)
            scored.append({
                "id": sid,
                "pack": entry.get("pack", "library"),
                "score": round(score, 3),
                "learned": bool(entry.get("learned", False)),
                "path": path,
            })

    scored.sort(key=lambda x: (-x["score"], -int(x["learned"]), x["id"]))
    return scored[:4]


def route_and_orchestrate(task_text, root=".", app="agy", files=None, budget_override=None):
    """Hidden & Output Layer: compute neural role activations, model allocation, skill bindings & topology."""
    root = os.path.abspath(root)
    config = settings.load(root)
    resources = perceive_resources(root, app=app)
    req = perceive_requirements(task_text, root=root, files=files)
    weights = load_weights(root)
    catalog = roles.catalog(root)
    lib_entries = library.entries()
    learned_skills = load_learned_skills(root)
    detected_langs = roles.detect(root)

    top_domains = req["top_domains"]
    domain_scores = req["domain_activations"]
    tokens = set(_tokenize(task_text))
    preset = budget_override or ("security" if req["risk"] >= 0.7 else "balanced")
    capacity = resources["hardware_health"]["capacity_factor"]
    effective_max = resources["config"]["effective_max_agents"]
    if budget_override == "budget":
        effective_max = min(effective_max, 2)
    elif budget_override == "thorough":
        effective_max = max(effective_max, 4)

    raw_scores = collections.defaultdict(float)
    reasons = collections.defaultdict(list)

    # 1. Input -> Hidden Layer: Receptor excitation + stack + vaccines + Hebbian weights
    for role, info in catalog.items():
        score = 0.0
        for d, d_val in domain_scores.items():
            d_roles = DOMAIN_RECEPTORS[d]["roles"]
            if role in d_roles:
                idx = d_roles.index(role)
                pos_weight = 0.65 if idx == 0 else (0.48 if idx == 1 else max(0.24, 0.42 - idx * 0.04))
                contrib = d_val * pos_weight
                score += contrib
                if contrib >= 0.15:
                    reasons[role].append(f"domain:{d}({contrib:.2f})")

        # Direct role name / description match
        role_parts = set(_tokenize(role.replace("-", " ")))
        if role_parts & tokens:
            hit = 0.28 * len(role_parts & tokens) / max(1, len(role_parts))
            score += hit
            reasons[role].append(f"name-match({hit:.2f})")

        # Stack language specialist boost
        for lang_name in req["scan"].get("languages") or []:
            mapped = STACK_ROLE_MAP.get(lang_name.lower(), ())
            if role in mapped:
                score += 0.18
                reasons[role].append(f"stack:{lang_name}(0.18)")
        for slug in detected_langs:
            if role in (f"{slug}-reviewer", f"{slug}-build-fixer"):
                score += 0.16
                reasons[role].append(f"lang-pack:{slug}(0.16)")

        # Active vaccine / hotspot boost
        for v in req["vaccines"]:
            if role in (v.get("applies_to") or []):
                score += 0.22
                reasons[role].append("vaccine-affinity(0.22)")
                break
        if req["fragility_hotspots"] and role in ("tester", "code-reviewer"):
            score += 0.16
            reasons[role].append("hotspot-guard(0.16)")

        # Learned skill role bindings
        for ls in learned_skills.values():
            if role in (ls.get("roles") or []):
                score += 0.12

        # Hebbian synaptic weights
        w_role = float((weights.get("roles") or {}).get(role, 0.0))
        w_dom = max([float((weights.get("domain_roles") or {}).get(f"{d}:{role}", 0.0)) for d in top_domains[:2]] or [0.0])
        if w_role or w_dom:
            hw_boost = w_role * 0.4 + w_dom * 0.5
            score += hw_boost
            reasons[role].append(f"hebbian({hw_boost:+.2f})")

        if not roles.is_enabled(config, role, info["pack"]) and info["pack"] != "core":
            score *= 0.88  # slight prior bias toward already-enabled packs while keeping dormant specialists reachable

        raw_scores[role] = max(0.0, score)

    # 2. Excitatory lateral synapses from primary activated neurons
    top_primaries = sorted(raw_scores.items(), key=lambda x: -x[1])[:3]
    for parent, p_score in top_primaries:
        if p_score < 0.28:
            continue
        for target, edge_w in EXCITATORY_SYNAPSES.get(parent, ()):
            if target in catalog:
                boost = p_score * edge_w
                raw_scores[target] += boost
                reasons[target].append(f"synapse<-{parent}({boost:.2f})")

    if config.get("auto_security_review", True) and req["risk"] >= 0.55:
        for sec_role in ("security-reviewer", "pentester"):
            if sec_role in catalog:
                raw_scores[sec_role] += 0.26
                reasons[sec_role].append("risk-reflex(0.26)")

    # 3. Lateral inhibition across overlapping specialist groups
    if req["complexity"] <= 0.75:
        for group in INHIBITORY_GROUPS:
            present = [(r, raw_scores[r]) for r in group if r in raw_scores and raw_scores[r] > 0]
            if len(present) > 1:
                present.sort(key=lambda x: -x[1])
                for loser, _ in present[1:]:
                    raw_scores[loser] = max(0.0, raw_scores[loser] - 0.25)

    # 4. Threshold & Capacity Selection
    ranked = sorted(
        [(r, round(s, 3)) for r, s in raw_scores.items() if s >= 0.28],
        key=lambda x: (-x[1], x[0]),
    )
    if not ranked:
        fallback = "backend-dev" if "backend" in top_domains else ("frontend-dev" if "frontend" in top_domains else "architect")
        if fallback in catalog:
            ranked = [(fallback, 0.35)]
            reasons[fallback].append("default-prior(0.35)")

    selected = ranked[:effective_max]
    selected_names = {r for r, _ in selected}

    # Ensure builder + verifier equilibrium for non-trivial work when capacity allows
    if req["complexity"] >= 0.25 and effective_max >= 2:
        has_verifier = bool(selected_names & VERIFIER_ROLES)
        if not has_verifier and "tester" in catalog:
            t_score = round(max(raw_scores.get("tester", 0.0), 0.34), 3)
            if len(selected) >= effective_max:
                selected[-1] = ("tester", t_score)
            else:
                selected.append(("tester", t_score))
            reasons["tester"].append("verifier-equilibrium")

    # 5. Output Layer: Model/effort allocation + Dendritic skill binding
    activated_neurons = []
    dormant_packs = set()
    all_bound_skills = {}
    learned_triggered = []

    for role, activation in selected:
        info = catalog[role]
        pack = info["pack"]
        enabled = roles.is_enabled(config, role, pack)
        if not enabled:
            dormant_packs.add(pack)
        model, effort, rationale = _allocate_model_and_effort(
            role, app, preset, capacity, req["complexity"], req["risk"], config, resources["models"]
        )
        bound = _score_skills_for_task(
            task_text, role, top_domains, lib_entries, learned_skills, weights, detected_langs
        )
        for sk in bound:
            all_bound_skills[sk["id"]] = sk
            if sk["learned"] and sk["id"] not in learned_triggered:
                learned_triggered.append(sk["id"])

        activated_neurons.append({
            "role": role,
            "pack": pack,
            "enabled": enabled,
            "activation": activation,
            "model": model,
            "effort": effort,
            "allocation_rationale": rationale,
            "reasons": reasons[role][:4],
            "bound_skills": bound,
        })

    # 6. Execution Topology selection
    n_active = len(activated_neurons)
    active_set = {n["role"] for n in activated_neurons}
    if n_active <= 1 and req["complexity"] < 0.35:
        topology = "solo-direct"
    elif req["risk"] >= 0.60 or bool(active_set & {"pentester", "security-reviewer"}):
        topology = "adversarial-gate"
    elif n_active >= 3:
        topology = "parallel-wave"
    else:
        topology = "duo-verified"

    summary = (
        f"Topology={topology} | Capacity={capacity:.2f} ({resources['hardware_health']['status']}) | "
        f"Complexity={req['complexity']:.2f} | Risk={req['risk']:.2f} | "
        f"Neurons=[{', '.join(n['role'] + ':' + n['model'] for n in activated_neurons)}]"
    )

    booster = build_agent_booster(req, activated_neurons, root=root, files=files)

    return {
        "task": task_text,
        "app": app,
        "summary": summary,
        "topology": topology,
        "resources_available": resources,
        "resources_required": req,
        "activated_neurons": activated_neurons,
        "bound_skills": sorted(all_bound_skills.values(), key=lambda x: -x["score"]),
        "learned_skills_triggered": learned_triggered,
        "co_change_alerts": req["co_change_alerts"],
        "vaccines_injected": [
            {"id": v["id"], "title": v["title"], "anti_pattern": v.get("anti_pattern", ""), "solution": v.get("solution", "")}
            for v in req["vaccines"]
        ],
        "verification_gates": req["required_gates"],
        "dormant_packs_to_enable": sorted(dormant_packs),
        "agent_booster": booster,
    }


def _in_memory_nodes(root):
    """Analyze codebase files in-memory when docs/brain/nodes does not exist yet."""
    nodes = {}
    file_to_slug = {}
    code_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in brain.IGNORE_DIRS and not d.startswith(".")]
        for fname in filenames:
            ext = os.path.splitext(fname)[1].lower()
            if ext in brain.CODE_EXTENSIONS:
                full = os.path.join(dirpath, fname)
                rel = os.path.relpath(full, root).replace("\\", "/")
                slug = brain._slugify(os.path.splitext(rel)[0])
                code_files.append((rel, full, ext))
                file_to_slug[rel] = slug
    for rel, full, ext in code_files:
        contracts = brain._extract_py_contracts(full) if ext == ".py" else brain._extract_regex_contracts(full, ext)
        slug = file_to_slug[rel]
        nodes[slug] = {
            "slug": slug,
            "meta": {"files": [rel], "title": os.path.basename(rel)},
            "imports": contracts["imports"],
            "upstream": set(),
            "downstream": set(),
        }
    suffix = {}
    for rel, slug in file_to_slug.items():
        parts = os.path.splitext(rel)[0].split("/")
        for i in range(len(parts)):
            suffix.setdefault("/".join(parts[i:]), []).append(slug)
    for slug, data in nodes.items():
        for imp in data["imports"]:
            for target in suffix.get(imp.replace(".", "/"), []):
                if target != slug:
                    data["upstream"].add(target)
                    nodes[target]["downstream"].add(slug)
    return nodes


def _mine_git_history(root, limit=200):
    """Extract co-change clusters and fragility hotspots from recent git commits."""
    if not os.path.isdir(os.path.join(root, ".git")):
        return [], [], 0
    try:
        out = subprocess.run(
            ["git", "-C", root, "log", f"-n{limit}", "--name-only", "--pretty=format:__COMMIT__%s"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30,
        )
        if out.returncode != 0:
            return [], [], 0
    except (OSError, subprocess.SubprocessError):
        return [], [], 0

    commits = []
    curr_msg, curr_files = None, []
    for raw in out.stdout.splitlines():
        line = raw.strip()
        if line.startswith("__COMMIT__"):
            if curr_msg is not None:
                commits.append((curr_msg, curr_files))
            curr_msg = line[len("__COMMIT__"):]
            curr_files = []
        elif line:
            curr_files.append(line.replace("\\", "/"))
    if curr_msg is not None:
        commits.append((curr_msg, curr_files))

    fix_rx = re.compile(r"\b(fix|bug|revert|crash|hotfix|regression|patch)\b", re.I)
    file_counts = collections.Counter()
    pair_counts = collections.Counter()
    fix_counts = collections.Counter()

    for msg, files in commits:
        unique = sorted(set(files))
        is_fix = bool(fix_rx.search(msg))
        for f in unique:
            if is_fix:
                fix_counts[f] += 1
        if 1 <= len(unique) <= 15:
            for f in unique:
                file_counts[f] += 1
            for i in range(len(unique)):
                for j in range(i + 1, len(unique)):
                    pair_counts[(unique[i], unique[j])] += 1

    clusters = []
    for (fa, fb), count in pair_counts.most_common(40):
        if count < 2:
            continue
        denom = max(file_counts[fa], file_counts[fb], 1)
        conf = round(count / denom, 3)
        if conf >= 0.4:
            clusters.append({
                "file_a": fa,
                "file_b": fb,
                "co_changes": count,
                "confidence": conf,
            })

    hotspots = [
        {"file": f, "fix_commits": c}
        for f, c in fix_counts.most_common(12)
    ]
    return clusters[:15], hotspots, len(commits)


def _detect_verification_commands(root, stack):
    """Infer deterministic test/check commands from repository layout."""
    cmds = []
    langs = {l.lower() for l in stack.get("languages") or []}
    testing = stack.get("testing") or []
    if "python" in langs:
        if "pytest" in testing:
            cmds.append("pytest")
        elif os.path.isdir(os.path.join(root, "tests")):
            cmds.append("python -m unittest discover -s tests")
    pkg = _read_json(os.path.join(root, "package.json"), {})
    scripts = pkg.get("scripts") or {}
    for key in ("test", "lint", "typecheck", "build"):
        if key in scripts:
            cmds.append(f"npm run {key}")
    if os.path.isfile(os.path.join(root, "Cargo.toml")):
        cmds.append("cargo test")
    if os.path.isfile(os.path.join(root, "go.mod")):
        cmds.append("go test ./...")
    return list(dict.fromkeys(cmds))


def assimilate_project_knowledge(root=".", write_genome_md=True, scan_report=None):
    """Pillar 2: extract architectural hubs, co-change rules, hotspots, and verification invariants."""
    root = os.path.abspath(root)
    config = settings.load(root)
    scan_report = scan_report or scan.scan_repository(root, include_cortex=False)
    stack = scan_report.get("stack") or {}
    brain_rel = config.get("brain_dir", "docs/brain")
    brain_dir = os.path.join(root, brain_rel)
    nodes_dir = os.path.join(brain_dir, "nodes")

    if os.path.isdir(nodes_dir):
        brain.map_repo(root=root, vault_dir=brain_rel, incremental=True)
        loaded = brain._load_all_nodes(brain_dir)
        hub_rows = []
        backlinks = collections.Counter()
        for slug, node in loaded.items():
            for wl in node.get("wikilinks") or []:
                backlinks[brain._slugify(wl)] += 1
        for slug, node in loaded.items():
            meta = node.get("meta") or {}
            files = meta.get("files") or []
            if not files:
                continue
            out_deg = len(node.get("wikilinks") or [])
            in_deg = backlinks.get(slug, 0)
            centrality = out_deg + 2 * in_deg
            hub_rows.append({
                "node": slug,
                "file": files[0],
                "in_degree": in_deg,
                "out_degree": out_deg,
                "centrality": centrality,
            })
    else:
        mem_nodes = _in_memory_nodes(root)
        hub_rows = [
            {
                "node": slug,
                "file": data["meta"]["files"][0],
                "in_degree": len(data["downstream"]),
                "out_degree": len(data["upstream"]),
                "centrality": len(data["upstream"]) + 2 * len(data["downstream"]),
            }
            for slug, data in mem_nodes.items()
        ]

    hub_rows.sort(key=lambda x: (-x["centrality"], x["file"]))
    co_changes, hotspots, commits_scanned = _mine_git_history(root)
    verify_cmds = _detect_verification_commands(root, stack)
    vaccines = autolearn.list_learnings(root)

    knowledge = {
        "version": 1,
        "assimilated_at": datetime.now(timezone.utc).isoformat(),
        "root": root,
        "stack": stack,
        "commits_scanned": commits_scanned,
        "architectural_hubs": hub_rows[:12],
        "co_change_clusters": co_changes,
        "fragility_hotspots": hotspots,
        "verification_commands": verify_cmds,
        "active_vaccines_count": len(vaccines),
    }
    _write_json(_knowledge_path(root), knowledge)

    genome_path = None
    if write_genome_md:
        genome_path = os.path.join(root, GENOME_MD)
        os.makedirs(os.path.dirname(genome_path), exist_ok=True)
        lines = [
            "---",
            "id: project-genome",
            "title: Project Architectural Genome",
            "type: genome",
            f"updated: \"{knowledge['assimilated_at']}\"",
            "---",
            "",
            "# Project Architectural Genome",
            "",
            f"Assimilated from codebase AST/regex contracts, `{commits_scanned}` git commits, and `{len(vaccines)}` active vaccines.",
            "",
            "## Stack & Verification Commands",
            f"- Languages: {', '.join(stack.get('languages') or ['none'])}",
            f"- Frameworks: {', '.join(stack.get('frameworks') or ['none'])}",
            f"- Test Suites: {', '.join(stack.get('testing') or ['none'])}",
            f"- Commands: {', '.join(f'`{c}`' for c in verify_cmds) or 'none detected'}",
            "",
            "## Architectural Hubs (Centrality)",
        ]
        if hub_rows[:10]:
            lines += ["| Module | File | In | Out | Centrality |", "|---|---|---:|---:|---:|"]
            for h in hub_rows[:10]:
                lines.append(f"| `{h['node']}` | `{h['file']}` | {h['in_degree']} | {h['out_degree']} | {h['centrality']} |")
        else:
            lines.append("- No code module hubs mapped yet.")

        lines += ["", "## Co-Change Coupling Rules"]
        if co_changes:
            for r in co_changes[:10]:
                lines.append(f"- `{r['file_a']}` <-> `{r['file_b']}` ({r['co_changes']} co-changes, conf={r['confidence']:.2f})")
        else:
            lines.append("- No recurring co-change clusters detected yet.")

        lines += ["", "## Fragility Hotspots (Fix/Revert Density)"]
        if hotspots:
            for hs in hotspots[:8]:
                lines.append(f"- `{hs['file']}` ({hs['fix_commits']} fix/revert commits)")
        else:
            lines.append("- No fix hotspots detected in git history.")

        with open(genome_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    knowledge["genome_md"] = genome_path
    knowledge["knowledge_json"] = _knowledge_path(root)
    return knowledge


def record_feedback(root=".", outcome="pass", roles_used=(), skills_used=(), task_text="", notes=""):
    """Pillar 3a: Hebbian synaptic plasticity from task outcome ('pass', 'fail', 'blocked')."""
    root = os.path.abspath(root)
    norm_outcome = str(outcome or "pass").lower()
    if norm_outcome not in ("pass", "fail", "blocked"):
        raise ValueError("outcome must be 'pass', 'fail', or 'blocked'")

    weights = _read_json(_weights_path(root), _empty_weights())
    for bucket in ("roles", "skills", "domain_roles", "role_skills"):
        weights.setdefault(bucket, {})
    stats = weights.setdefault("stats", {"passes": 0, "failures": 0, "total_runs": 0})
    history = weights.setdefault("history", [])

    req = perceive_requirements(task_text, root=root) if task_text else {"top_domains": ["backend"]}
    top_domain = (req.get("top_domains") or ["backend"])[0]
    delta = 0.15 if norm_outcome == "pass" else -0.10

    roles_list = [r.strip() for r in (roles_used.split(",") if isinstance(roles_used, str) else roles_used) if r.strip()]
    skills_list = [s.strip() for s in (skills_used.split(",") if isinstance(skills_used, str) else skills_used) if s.strip()]

    for role in roles_list:
        weights["roles"][role] = _clamp(weights["roles"].get(role, 0.0) + delta)
        dk = f"{top_domain}:{role}"
        weights["domain_roles"][dk] = _clamp(weights["domain_roles"].get(dk, 0.0) + delta)

    for skill in skills_list:
        weights["skills"][skill] = _clamp(weights["skills"].get(skill, 0.0) + delta)
        for role in roles_list:
            rk = f"{role}:{skill}"
            weights["role_skills"][rk] = _clamp(weights["role_skills"].get(rk, 0.0) + delta)

    # Compensatory homeostatic plasticity: failures reinforce verifiers
    if norm_outcome in ("fail", "blocked"):
        stats["failures"] = stats.get("failures", 0) + 1
        for guard in ("tester", "code-reviewer"):
            weights["roles"][guard] = _clamp(weights["roles"].get(guard, 0.0) + 0.10)
            dk = f"{top_domain}:{guard}"
            weights["domain_roles"][dk] = _clamp(weights["domain_roles"].get(dk, 0.0) + 0.10)
    else:
        stats["passes"] = stats.get("passes", 0) + 1

    stats["total_runs"] = stats.get("total_runs", 0) + 1
    now_iso = datetime.now(timezone.utc).isoformat()
    weights["updated_at"] = now_iso
    mutated = []
    if norm_outcome in ("fail", "blocked") and roles_list:
        for role in roles_list:
            mres = omniscience.mutate_role_agent(
                root=root,
                role=role,
                lesson=notes or f"Failed on {top_domain} task: {task_text}",
                trigger=task_text or top_domain,
                anti_pattern="Unverified edit or broken invariant",
                solution="Verify AST contracts, co-change files, and run targeted smoke/unit test before completion",
            )
            if mres.get("mutated"):
                mutated.append(mres)
    if mutated:
        weights["mutated_roles"] = mutated
    history.append({
        "at": now_iso,
        "outcome": norm_outcome,
        "domain": top_domain,
        "roles": roles_list,
        "skills": skills_list,
        "notes": notes[:200] if notes else "",
    })
    weights["history"] = history[-100:]
    _write_json(_weights_path(root), weights)
    return weights


def _write_skill_file(skills_dir, skill_id, description, triggers, target_roles, sections):
    """Write a learned SKILL.md module under .team-workflow/skills/<skill_id>/SKILL.md."""
    cortex_parent = os.path.dirname(skills_dir)
    if os.path.basename(cortex_parent) == CORTEX_DIR:
        _ensure_cortex_gitignore(cortex_parent)
    dest = os.path.join(skills_dir, skill_id)
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, "SKILL.md")
    lines = [
        "---",
        f"name: {skill_id}",
        f"description: {json.dumps(description)}",
        "pack: learned",
        f"triggers: {json.dumps(triggers)}",
        f"roles: {json.dumps(target_roles)}",
        "---",
        "",
        f"# {skill_id}",
        "",
        description,
        "",
    ]
    for heading, body_lines in sections:
        lines.append(f"## {heading}")
        lines.extend(body_lines)
        lines.append("")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines).rstrip() + "\n")
    return path


def evolve_skills(root=".", custom_name=None):
    """Pillar 3b: synthesize team-meta-cortex and domain skills from project genome, vaccines & talk."""
    root = os.path.abspath(root)
    knowledge = _read_json(_knowledge_path(root), {})
    if not knowledge:
        knowledge = assimilate_project_knowledge(root, write_genome_md=os.path.isdir(os.path.join(root, "docs", "brain")))

    weights = load_weights(root)
    learnings = autolearn.list_learnings(root)
    topics = talk.topics(cwd=root)
    skills_dir = os.path.join(root, LEARNED_SKILLS_REL)
    synthesized = []

    # 1. Always synthesize `team-meta-cortex`: evolving the skill of the `team` skill itself
    top_roles = sorted((weights.get("roles") or {}).items(), key=lambda x: -x[1])[:8]
    top_skills = sorted((weights.get("skills") or {}).items(), key=lambda x: -x[1])[:8]
    co_changes = knowledge.get("co_change_clusters") or []
    hotspots = knowledge.get("fragility_hotspots") or []
    verify_cmds = knowledge.get("verification_commands") or []

    meta_sections = [
        ("Learned Synaptic Affinities", [
            "- Top performing roles: " + (", ".join(f"`{r}` ({w:+.2f})" for r, w in top_roles) or "baseline defaults (awaiting feedback runs)"),
            "- Top effective skills: " + (", ".join(f"`{s}` ({w:+.2f})" for s, w in top_skills) or "baseline library defaults"),
            f"- Recorded outcomes: {weights.get('stats', {}).get('passes', 0)} passes, {weights.get('stats', {}).get('failures', 0)} failures.",
        ]),
        ("Mandatory Co-Change Guards", [
            f"- Whenever `{r['file_a']}` changes, check `{r['file_b']}` (co-changes={r['co_changes']}, conf={r['confidence']:.2f})."
            for r in co_changes[:8]
        ] or ["- No mandatory co-change couplings extracted yet."]),
        ("Fragility Hotspot Protections", [
            f"- `{h['file']}` ({h['fix_commits']} prior fix commits) -> require `tester` + `code-reviewer` gate."
            for h in hotspots[:6]
        ] or ["- No fragility hotspots detected yet."]),
        ("Deterministic Verification Loop", [
            f"- Run `{cmd}` before declaring done." for cmd in verify_cmds
        ] or ["- Run `tw.py smoke` and `tw.py verify-docs --strict` before declaring done."]),
    ]
    meta_triggers = ["team", "cortex", "orchestrate", "route"] + [os.path.basename(h["file"]) for h in hotspots[:4]]
    meta_path = _write_skill_file(
        skills_dir,
        "team-meta-cortex",
        "Self-evolved meta-orchestration playbook for this repository: synaptic affinities, co-change rules, hotspot guards, and verification loop.",
        list(dict.fromkeys(meta_triggers)),
        ["*"],
        meta_sections,
    )
    synthesized.append({"id": "team-meta-cortex", "path": meta_path, "kind": "meta-skill"})

    # 2. Group learnings/vaccines + resolved talk challenges into reusable domain skills
    resolved_verdicts = []
    for t_name, msgs in topics:
        challenges = {m["id"]: m for m in msgs if m.get("kind") == "challenge"}
        for m in msgs:
            if m.get("kind") == "verdict" and m.get("re") in challenges:
                resolved_verdicts.append({
                    "topic": t_name,
                    "challenge": challenges[m["re"]].get("text", ""),
                    "verdict": m.get("text", ""),
                    "from": m.get("from", "reviewer"),
                })

    groups = collections.defaultdict(list)
    for item in learnings:
        cat = _slug(custom_name or item.get("category") or "general")
        groups[cat].append(item)

    if not groups and resolved_verdicts:
        groups[_slug(custom_name or "talk-lessons")] = []

    for cat, items in groups.items():
        skill_id = _slug(custom_name) if custom_name and len(groups) == 1 else f"project-{cat}-guard"
        triggers = [cat]
        target_roles = set()
        anti_lines, sol_lines = [], []
        for it in items:
            triggers.extend(_tokenize(it.get("title", ""))[:3])
            for ap in it.get("applies_to") or []:
                if ap != "*" and "." not in ap:
                    target_roles.add(ap)
                elif "." in ap:
                    triggers.append(os.path.basename(ap))
            if it.get("anti_pattern"):
                anti_lines.append(f"- **{it['title']}**: Avoid `{it['anti_pattern'][:140]}`")
            if it.get("solution"):
                sol_lines.append(f"- **{it['title']}**: Require `{it['solution'][:160]}`")
        for rv in resolved_verdicts[:5]:
            sol_lines.append(f"- **Talk `{rv['topic']}` ({rv['from']})**: {rv['verdict'][:140]}")

        sections = [
            ("Trigger Conditions", [f"- Activate when modifying files or tasks matching: {', '.join(f'`{t}`' for t in list(dict.fromkeys(triggers))[:10])}."]),
            ("Anti-Patterns & Vaccines", anti_lines or ["- Prevent regressions captured in project history."]),
            ("Required Implementation Pattern", sol_lines or ["- Follow verified patterns and project invariants."]),
            ("Co-Change & Verification Gate", [f"- Verify with `{cmd}`." for cmd in verify_cmds] or ["- Run `tw.py smoke` and `tw.py verify-docs --strict`."]),
        ]
        spath = _write_skill_file(
            skills_dir,
            skill_id,
            f"Auto-evolved project skill from {len(items)} vaccine(s) and {len(resolved_verdicts)} talk resolution(s) for category '{cat}'.",
            list(dict.fromkeys(t for t in triggers if len(t) >= 2))[:12],
            sorted(target_roles) or ["*"],
            sections,
        )
        synthesized.append({"id": skill_id, "path": spath, "kind": "learned-skill", "vaccines": len(items)})

    return {"skills_dir": skills_dir, "synthesized": synthesized}


def rank_roles_for_wizard(data, task_words, config, root=".", plan=None):
    """Rank enabled roles for `tw.py questions` using neural activation scores."""
    task_text = " ".join(task_words or [])
    if not task_text.strip():
        return list(data["roles"])
    plan = plan or route_and_orchestrate(task_text, root=root or ".", app=data.get("app", "claude"))
    activated_order = {n["role"]: idx for idx, n in enumerate(plan["activated_neurons"])}
    domain_scores = plan["resources_required"]["domain_activations"]
    weights = load_weights(root or ".")
    words = set(_tokenize(task_text))

    def sort_key(r):
        if r in activated_order:
            return (0, activated_order[r], r)
        score = float((weights.get("roles") or {}).get(r, 0.0)) * 0.4
        for d, dv in domain_scores.items():
            if r in DOMAIN_RECEPTORS.get(d, {}).get("roles", ()):
                score += dv * 0.5
        if set(_tokenize(r.replace("-", " "))) & words:
            score += 0.3
        return (1, -round(score, 4), r)

    return sorted(data["roles"], key=sort_key)


def status_report(root=".", app="agy"):
    """Summarize Neural Cortex resources, assimilated genome, synaptic weights, and learned skills."""
    root = os.path.abspath(root)
    resources = perceive_resources(root, app=app)
    weights = load_weights(root)
    knowledge = _read_json(_knowledge_path(root), {})
    learned = load_learned_skills(root)
    return {
        "resources": resources,
        "knowledge": {
            "assimilated": bool(knowledge),
            "assimilated_at": knowledge.get("assimilated_at"),
            "hubs_count": len(knowledge.get("architectural_hubs") or []),
            "co_change_rules": len(knowledge.get("co_change_clusters") or []),
            "hotspots_count": len(knowledge.get("fragility_hotspots") or []),
            "verification_commands": knowledge.get("verification_commands") or [],
        },
        "weights": {
            "stats": weights.get("stats") or {},
            "top_roles": sorted((weights.get("roles") or {}).items(), key=lambda x: -x[1])[:8],
            "top_skills": sorted((weights.get("skills") or {}).items(), key=lambda x: -x[1])[:8],
        },
        "learned_skills": [
            {"id": sid, "origin": info["origin"], "path": info["path"], "triggers": info["triggers"]}
            for sid, info in sorted(learned.items())
        ],
    }


def format_route_report(plan):
    """Human-readable neural routing report."""
    hw = plan["resources_available"]["hardware_health"]
    req = plan["resources_required"]
    lines = [
        "=" * 64,
        "🧠 NEURAL CORTEX ROUTING & ORCHESTRATION PLAN",
        "=" * 64,
        f"🎯 Task:       {plan['task'] or '(general)'}",
        f"🕸️ Topology:   {plan['topology']} | Complexity: {req['complexity']:.2f} | Risk: {req['risk']:.2f}",
        f"⚡ Hardware:   {hw['status']} (capacity={hw['capacity_factor']:.2f}, max_agents={plan['resources_available']['config']['effective_max_agents']})",
        f"📡 Domains:    {', '.join(f'{k}={v:.2f}' for k, v in list(req['domain_activations'].items())[:5])}",
        f"💥 Blast rad.: {req['blast_radius']} node(s) | Gates: {', '.join(plan['verification_gates'])}",
        "",
        "Activated Neurons (Roles -> Model / Effort -> Bound Skills):",
    ]
    for n in plan["activated_neurons"]:
        flag = "" if n["enabled"] else " [DORMANT PACK]"
        skills_str = ", ".join(f"{s['id']}{'*' if s['learned'] else ''}" for s in n["bound_skills"]) or "none"
        lines.append(f"  • {n['role']:<24} act={n['activation']:.2f}  {n['model']}/{n['effort']}{flag}")
        lines.append(f"      reasons: {', '.join(n['reasons']) or '-'}")
        lines.append(f"      skills:  {skills_str}")
    if plan["learned_skills_triggered"]:
        lines.append(f"\n🧬 Learned / Meta Skills Triggered: {', '.join(plan['learned_skills_triggered'])}")
    if plan["co_change_alerts"]:
        lines.append("\n🔗 Co-Change Alerts:")
        for c in plan["co_change_alerts"]:
            lines.append(f"  • {c['file_a']} <-> {c['file_b']} (conf={c['confidence']:.2f})")
    if plan["vaccines_injected"]:
        lines.append(f"\n🛡️ Active Vaccines Injected ({len(plan['vaccines_injected'])}):")
        for v in plan["vaccines_injected"]:
            lines.append(f"  • [{v['id']}] {v['title']}")
    if plan["dormant_packs_to_enable"]:
        lines.append(f"\n💡 Dormant packs needed: {', '.join(plan['dormant_packs_to_enable'])} (enable via `tw.py agents enable <pack>`)")
    if plan.get("agent_booster"):
        co = plan["agent_booster"]["cost_optimization"]
        lines.append(
            f"\n⚡ Vibecode Booster: ~{co['total_estimated_cost_savings_pct']}% est. token/cost cut "
            f"(in -{co['input_token_reduction_pct']}%, out -{co['output_token_reduction_pct']}%, "
            f"retries -{co['retry_loop_reduction_pct']}%)"
        )
    lines.append("=" * 64)
    return "\n".join(lines)


VIBECODE_DIRECTIVES = (
    {
        "id": "caveman-telemetry",
        "role": "Output Token Compressor",
        "rule": "Use terse technical telemetry (`file:line -> change -> proof`); zero conversational fluff (~65% output token cut).",
    },
    {
        "id": "ponytail-yagni",
        "role": "Lazy Senior Dev / Zero-Bloat",
        "rule": "Write the smallest working diff using stdlib and existing repo helpers first; zero speculative abstractions.",
    },
    {
        "id": "karpathy-surgical",
        "role": "Surgical Line-Targeted Edits",
        "rule": "Read/edit only exact AST skeleton ranges (`file:L<line>`); check coupled co-change files before finishing.",
    },
    {
        "id": "context-mode-diet",
        "role": "Context Window Shield",
        "rule": "Never dump full files or >40 lines of raw command output; filter test runs to failing assertions only.",
    },
)


def _extract_py_skeleton(filepath):
    """Extract classes (with line & methods) and top-level functions with line numbers."""
    symbols = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, OSError):
        return symbols

    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            methods = [
                f"{n.name}@L{n.lineno}"
                for n in node.body
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
            ]
            m_str = f" [{', '.join(methods[:8])}]" if methods else ""
            symbols.append(f"L{node.lineno}: class {node.name}{m_str}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            prefix = "async def" if isinstance(node, ast.AsyncFunctionDef) else "def"
            args = [a.arg for a in node.args.args]
            symbols.append(f"L{node.lineno}: {prefix} {node.name}({', '.join(args)})")
    return symbols


def _extract_regex_skeleton(filepath):
    """Extract JS/TS/Go/Rust symbol declarations with line numbers."""
    symbols = []
    rx = re.compile(
        r"^\s*(?:export\s+(?:default\s+)?(?:async\s+)?)?"
        r"(?:class|interface|function|async\s+function|func|fn|struct|enum)\s+([A-Za-z0-9_]+)"
        r"|^\s*(?:export\s+)?const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\("
    )
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for lineno, line in enumerate(f, 1):
                m = rx.match(line)
                if m:
                    name = m.group(1) or m.group(2)
                    symbols.append(f"L{lineno}: {line.strip()[:72]}")
                    if not name:
                        continue
    except OSError:
        return symbols
    return symbols


def extract_skeleton_map(root=".", files=None, matched_nodes=None, max_files=6):
    """Zero-token RepoMap / AST Symbol Skeleton so agents read exact lines instead of whole files."""
    root = os.path.abspath(root)
    config = settings.load(root)
    knowledge = _read_json(_knowledge_path(root), {})
    candidates = []

    for f in (files or []):
        candidates.append(f.replace("\\", "/"))

    if matched_nodes:
        brain_dir = os.path.join(root, config.get("brain_dir", "docs/brain"))
        if os.path.isdir(brain_dir):
            loaded = brain._load_all_nodes(brain_dir)
            for slug in matched_nodes:
                node = loaded.get(slug)
                if node:
                    for mf in (node.get("meta") or {}).get("files") or []:
                        candidates.append(str(mf).replace("\\", "/"))

    for hub in knowledge.get("architectural_hubs") or []:
        if hub.get("file"):
            candidates.append(str(hub["file"]).replace("\\", "/"))

    if not candidates:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in brain.IGNORE_DIRS and not d.startswith(".")]
            for fname in sorted(filenames):
                if os.path.splitext(fname)[1].lower() in brain.CODE_EXTENSIONS:
                    rel = os.path.relpath(os.path.join(dirpath, fname), root).replace("\\", "/")
                    candidates.append(rel)
                    if len(candidates) >= max_files:
                        break
            if len(candidates) >= max_files:
                break

    seen = set()
    skeleton = []
    for rel in candidates:
        if not rel or rel in seen:
            continue
        seen.add(rel)
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(rel)[1].lower()
        syms = _extract_py_skeleton(full) if ext == ".py" else _extract_regex_skeleton(full)
        skeleton.append({"file": rel, "symbols": syms[:18]})
        if len(skeleton) >= max_files:
            break
    return skeleton


def build_agent_booster(req, activated_neurons, root=".", files=None):
    """Build default Vibecode Agent Booster & Cost-Reduction Pack for every agent brief."""
    skeleton = extract_skeleton_map(
        root=root,
        files=files,
        matched_nodes=req.get("matched_brain_nodes"),
    )
    target_files = list(files or [s["file"] for s in skeleton])
    env_sense = omniscience.sense_environment(root)
    shadow_spec = omniscience.synthesize_shadow_spec(
        req.get("task", ""), root=root, files=target_files, domains=req.get("top_domains")
    )
    anti_tamper = omniscience.audit_anti_tamper(root)
    ast_contracts = omniscience.check_ast_contracts(root, files=target_files)

    has_skeleton = any(item["symbols"] for item in skeleton) or bool(req.get("matched_brain_nodes"))
    has_guards = bool(req.get("co_change_alerts") or req.get("vaccines"))

    inp_cut = 62 if has_skeleton else 45
    out_cut = 65
    retry_cut = 55 if has_guards else 45
    total_cut = round(0.45 * inp_cut + 0.35 * out_cut + 0.20 * retry_cut)

    cost_opt = {
        "input_token_reduction_pct": inp_cut,
        "output_token_reduction_pct": out_cut,
        "retry_loop_reduction_pct": retry_cut,
        "total_estimated_cost_savings_pct": total_cut,
    }

    block = [
        "[VIBECODE AGENT BOOSTER — DEFAULT COST & QUALITY SHIELD]",
        f"Estimated savings: ~{total_cut}% (input -{inp_cut}%, output -{out_cut}%, retries -{retry_cut}%)",
        "Default Reflexes:",
    ]
    for d in VIBECODE_DIRECTIVES:
        block.append(f"- {d['id']}: {d['rule']}")

    if shadow_spec.get("invariants"):
        block.append("Shadow Spec Invariants (Non-Negotiable):")
        for inv in shadow_spec["invariants"][:4]:
            block.append(f"- {inv}")

    if shadow_spec.get("preserved_signatures"):
        block.append("Preserved Call-Site Signatures:")
        for sig in shadow_spec["preserved_signatures"][:6]:
            block.append(f"- {sig}")

    env_alerts = []
    if env_sense.get("missing_env_keys"):
        env_alerts.append(f"Missing .env keys: {', '.join(env_sense['missing_env_keys'][:8])}")
    if env_sense.get("dependency_warnings"):
        env_alerts.extend(env_sense["dependency_warnings"])
    if env_sense.get("conflict_files"):
        env_alerts.append(f"Merge conflicts: {', '.join(env_sense['conflict_files'][:5])}")
    if env_sense.get("active_ports"):
        env_alerts.append(f"Occupied local ports: {', '.join(str(p) for p in env_sense['active_ports'])}")
    if env_alerts:
        block.append("Environment Alerts:")
        for al in env_alerts:
            block.append(f"- {al}")

    if skeleton:
        block.append("AST Symbol Skeleton (jump straight to lines):")
        for entry in skeleton:
            sym_line = "; ".join(entry["symbols"][:8]) if entry["symbols"] else "(no symbols parsed)"
            block.append(f"- {entry['file']}: {sym_line}")

    if req.get("co_change_alerts"):
        block.append("Co-Change Guards:")
        for c in req["co_change_alerts"][:4]:
            block.append(f"- {c['file_a']} <-> {c['file_b']} (conf={c['confidence']:.2f})")

    block.append("Zero-Entropy Telemetry Schema: " + omniscience.zero_entropy_schema())
    block.append("Required Gates: " + ", ".join(req.get("required_gates") or ["smoke", "verify-docs"]))

    return {
        "directives": list(VIBECODE_DIRECTIVES),
        "skeleton_map": skeleton,
        "cost_optimization": cost_opt,
        "environment_sense": env_sense,
        "shadow_spec": shadow_spec,
        "anti_tamper": anti_tamper,
        "ast_contracts": ast_contracts,
        "zero_entropy_schema": omniscience.zero_entropy_schema(),
        "prompt_block": "\n".join(block),
    }


def vibecode_boost(task_text, root=".", app="agy", files=None):
    """Expand a lazy/vibe prompt into cost-optimized agent briefs plus the Vibecoding Arsenal."""
    import addons

    root = os.path.abspath(root)
    plan = route_and_orchestrate(task_text, root=root, app=app, files=files)
    booster = plan["agent_booster"]
    skeleton_files = [s["file"] for s in booster["skeleton_map"]]
    gates = ", ".join(plan["verification_gates"])

    expanded_briefs = []
    for neuron in plan["activated_neurons"]:
        skills_str = ", ".join(f"{s['id']} ({s['path']})" for s in neuron["bound_skills"]) or "none"
        brief_lines = [
            f"Role: {neuron['role']} ({neuron['model']}/{neuron['effort']}, topology={plan['topology']})",
            f"Goal: {task_text or 'Execute task cleanly'}",
            f"Target Files: {', '.join(files or skeleton_files) or 'discover via skeleton/brain'}",
            f"Bound Skills: {skills_str}",
            f"Verification Gates: {gates}",
            booster["prompt_block"],
        ]
        expanded_briefs.append({
            "role": neuron["role"],
            "model": neuron["model"],
            "effort": neuron["effort"],
            "bound_skills": [s["id"] for s in neuron["bound_skills"]],
            "target_files": list(files or skeleton_files),
            "verification_gates": list(plan["verification_gates"]),
            "brief_text": "\n".join(brief_lines),
        })

    installed = set(addons.chosen(settings.load(root)))
    arsenal_ids = list(addons.BUNDLES.get("vibecoding", ())) + ["task-master", "magic-21st"]
    arsenal = []
    for aid in dict.fromkeys(arsenal_ids):
        entry = addons.CATALOG.get(aid)
        if entry:
            arsenal.append({
                "id": aid,
                "installed": aid in installed,
                "about": entry.get("about", ""),
                "install_cmd": f"tw.py addons add {aid}",
            })

    return {
        "task": task_text,
        "app": app,
        "route": plan,
        "agent_booster": booster,
        "cost_optimization": booster["cost_optimization"],
        "expanded_briefs": expanded_briefs,
        "vibecoding_arsenal": {
            "bundle_cmd": "tw.py addons add vibecoding",
            "tools": arsenal,
        },
    }


def format_boost_report(boost_data):
    """Human-readable Vibecode Booster report with cost savings, skeleton map, and tool arsenal."""
    co = boost_data["cost_optimization"]
    booster = boost_data["agent_booster"]
    plan = boost_data["route"]
    lines = [
        "=" * 64,
        "🚀 VIBECODE LAZY BOOSTER & COST OPTIMIZER",
        "=" * 64,
        f"🎯 Vibe Prompt: {boost_data['task'] or '(general)'}",
        f"🕸️ Topology:    {plan['topology']} | Agents: {len(boost_data['expanded_briefs'])}",
        f"💸 Est. Savings: ~{co['total_estimated_cost_savings_pct']}% total "
        f"(input -{co['input_token_reduction_pct']}%, output -{co['output_token_reduction_pct']}%, "
        f"retries -{co['retry_loop_reduction_pct']}%)",
        "",
        "Injected Default Reflexes (Zero-Bloat & Token Diet):",
    ]
    for d in booster["directives"]:
        lines.append(f"  • {d['id']:<20} ({d['role']}): {d['rule']}")

    if booster["skeleton_map"]:
        lines.append("\nAST Symbol Skeleton Map (No Full-File Reads):")
        for entry in booster["skeleton_map"]:
            lines.append(f"  • {entry['file']}: {', '.join(entry['symbols'][:5]) or '(raw file)'}")

    lines.append("\nExpanded Agent Briefs:")
    for b in boost_data["expanded_briefs"]:
        lines.append(f"  • {b['role']:<22} {b['model']}/{b['effort']} -> skills: {', '.join(b['bound_skills']) or 'none'}")

    arsenal = boost_data["vibecoding_arsenal"]
    lines.append(f"\n🧰 Cult Vibecoding Arsenal (1-command install: `{arsenal['bundle_cmd']}`):")
    for t in arsenal["tools"]:
        mark = "✅" if t["installed"] else "➕"
        lines.append(f"  {mark} {t['id']:<16} {t['about']}")
    lines.append("=" * 64)
    return "\n".join(lines)
