#!/usr/bin/env python3
"""Omniscient & Neuro-Symbolic Cortex v3 Engines for team-workflow.

Addresses the 2025-2026 documented failure modes of coding agents:
1. Environment & Runtime Sensor: safe .env key drift, dependency drift, occupied ports, git conflicts.
2. Shadow Spec & Latent Intent Synthesizer: unwritten invariants + AST call-site signature contracts.
3. Anti-Tamper Test & Security Shield: detects test assertion deletions/skips, silent excepts, RLS/TLS weakening.
4. Pre-Flight AST Contract Diff Simulator: detects breaking signature/arity mutations before commit.
5. Loop Circuit-Breaker & Counterfactual Recovery: trips at >=2 repeated error fingerprints (MAST loops).
6. Darwin-Godel Role Auto-Mutation (TextGrad): evolves project-local .team-workflow/agents/<role>.md overrides.
7. Zero-Entropy Telemetry Protocol: high-density claim/diff/contract/proof inter-agent schema.
"""
import ast
from datetime import datetime, timezone
import hashlib
import json
import os
import re
import socket
import subprocess

import roles

CORTEX_DIR = ".team-workflow"
CIRCUIT_FILE = "circuit_breaker.json"
DEV_PORTS = (3000, 5173, 8000, 8080, 5000, 4200)

ENV_KEY_RX = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=")
ASSERT_RX = re.compile(r"\bassert\b|self\.assert|\bexpect\s*\(|\bshould\.")
SKIP_RX = re.compile(r"@unittest\.skip|@pytest\.mark\.skip|pytest\.skip\s*\(|\.skip\s*\(|\bxit\s*\(|\bxdescribe\s*\(|@pytest\.mark\.xfail")
SILENT_EXCEPT_HEADER_RX = re.compile(r"^\s*except(?:\s+(?:BaseException|Exception))?(?:\s+as\s+\w+)?\s*:\s*(?:#.*)?$")
SILENT_EXCEPT_INLINE_RX = re.compile(r"^\s*except(?:\s+(?:BaseException|Exception))?(?:\s+as\s+\w+)?\s*:\s*(?:pass|\.\.\.)\s*(?:#.*)?$")
SECURITY_WEAKEN_RX = (
    ("rls_open_policy", re.compile(r"USING\s*\(\s*true\s*\)", re.I), "RLS USING (true) exposes all tenant rows"),
    ("tls_verify_disabled", re.compile(r"verify\s*=\s*False|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0"), "TLS certificate verification disabled"),
    ("unsafe_html_injection", re.compile(r"dangerouslySetInnerHTML"), "dangerouslySetInnerHTML added without verified sanitization"),
    ("wildcard_cors", re.compile(r"Access-Control-Allow-Origin['\"]?\s*[:=]\s*['\"]\*['\"]", re.I), "Wildcard CORS origin '*' weakened boundary"),
)
TEST_FILE_RX = re.compile(r"(?:^|/)(?:tests?|__tests__|spec)/|(?:^|/)test_[^/]+\.py$|[^/]+(?:_test\.py|\.test\.[jt]sx?|\.spec\.[jt]sx?)$", re.I)


def _ensure_cortex_gitignore(root):
    cdir = os.path.join(os.path.abspath(root), CORTEX_DIR)
    os.makedirs(cdir, exist_ok=True)
    gi = os.path.join(cdir, ".gitignore")
    if not os.path.isfile(gi):
        with open(gi, "w", encoding="utf-8") as f:
            f.write("*\n")
    return cdir


def _read_env_keys(path):
    """Read ONLY variable names from an env file; values are never read or stored."""
    keys = []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            for line in f:
                if line.lstrip().startswith("#"):
                    continue
                m = ENV_KEY_RX.match(line)
                if m:
                    keys.append(m.group(1))
    except OSError:
        return []
    return list(dict.fromkeys(keys))


def _probe_local_ports(ports=DEV_PORTS):
    active = []
    for port in ports:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.015):
                active.append(port)
        except OSError:
            pass
    return active


def _find_conflict_files(root):
    if not os.path.isdir(os.path.join(root, ".git")):
        return []
    try:
        out = subprocess.run(
            ["git", "-C", root, "status", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
        )
        if out.returncode != 0:
            return []
    except (OSError, subprocess.SubprocessError):
        return []

    conflicts = []
    for raw in out.stdout.splitlines()[:40]:
        if len(raw) < 4:
            continue
        code, rel = raw[:2], raw[3:].strip().strip('"')
        if code in ("UU", "AA", "DD", "AU", "UA", "DU", "UD"):
            conflicts.append(rel)
            continue
        full = os.path.join(root, rel)
        if os.path.isfile(full) and os.path.getsize(full) < 256_000:
            try:
                with open(full, encoding="utf-8", errors="replace") as f:
                    txt = f.read()
                if "<<<<<<< " in txt and "=======" in txt and ">>>>>>> " in txt:
                    conflicts.append(rel)
            except OSError:
                pass
    return list(dict.fromkeys(conflicts))


def sense_environment(root="."):
    """Engine 1: safe .env key drift, dependency drift, occupied localhost ports, and merge conflicts."""
    root = os.path.abspath(root)

    template_keys = []
    for name in (".env.example", ".env.sample", ".env.template"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            template_keys.extend(_read_env_keys(p))
    template_keys = list(dict.fromkeys(template_keys))

    actual_keys = set()
    for name in (".env", ".env.local"):
        p = os.path.join(root, name)
        if os.path.isfile(p):
            actual_keys.update(_read_env_keys(p))
    missing_env_keys = [k for k in template_keys if k not in actual_keys]

    dep_warnings = []
    pkg_path = os.path.join(root, "package.json")
    if os.path.isfile(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8", errors="replace") as f:
                pkg = json.load(f)
            if (pkg.get("dependencies") or pkg.get("devDependencies")) and not os.path.isdir(os.path.join(root, "node_modules")):
                dep_warnings.append("package.json has dependencies but node_modules/ is missing")
        except (OSError, ValueError):
            pass
    if os.path.isfile(os.path.join(root, "Pipfile")) and not any(
        os.path.isdir(os.path.join(root, d)) for d in (".venv", "venv")
    ):
        dep_warnings.append("Pipfile present without local .venv/ or venv/")

    active_ports = _probe_local_ports()
    conflicts = _find_conflict_files(root)

    return {
        "missing_env_keys": missing_env_keys,
        "dependency_warnings": dep_warnings,
        "active_ports": active_ports,
        "conflict_files": conflicts,
        "healthy": not missing_env_keys and not conflicts,
    }


def _extract_py_signatures(source):
    """Extract public function and class method signatures with argument arity."""
    sigs = {}
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return sigs

    def add_fn(qualname, fn_node):
        pos_args = list(getattr(fn_node.args, "posonlyargs", [])) + list(fn_node.args.args)
        # Drop self/cls for instance/class methods when computing caller-facing arity
        if "." in qualname and pos_args and pos_args[0].arg in ("self", "cls"):
            pos_args = pos_args[1:]
        defaults = fn_node.args.defaults or []
        min_args = max(0, len(pos_args) - len(defaults))
        sigs[qualname] = {
            "symbol": qualname,
            "min_args": min_args,
            "total_args": len(pos_args),
            "has_varargs": fn_node.args.vararg is not None,
            "has_kw": fn_node.args.kwarg is not None or bool(fn_node.args.kwonlyargs),
            "args": [a.arg for a in pos_args],
            "lineno": fn_node.lineno,
        }

    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                add_fn(node.name, node)
        elif isinstance(node, ast.ClassDef) and not node.name.startswith("_"):
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if not item.name.startswith("_") or item.name == "__init__":
                        add_fn(f"{node.name}.{item.name}", item)
    return sigs


def _extract_js_signatures(source):
    sigs = {}
    rx = re.compile(
        r"^\s*(?:export\s+(?:default\s+)?(?:async\s+)?)?"
        r"(?:function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)|"
        r"const\s+([A-Za-z0-9_]+)\s*=\s*(?:async\s*)?\(([^)]*)\)\s*=>)"
    )
    for lineno, line in enumerate(source.splitlines(), 1):
        m = rx.match(line)
        if m:
            name = m.group(1) or m.group(3)
            raw_args = (m.group(2) if m.group(1) else m.group(4)) or ""
            args = [a.strip().split("=")[0].split(":")[0].strip() for a in raw_args.split(",") if a.strip()]
            if name and not name.startswith("_"):
                sigs[name] = {
                    "symbol": name,
                    "min_args": len([a for a in raw_args.split(",") if a.strip() and "=" not in a and "?" not in a]),
                    "total_args": len(args),
                    "has_varargs": "..." in raw_args,
                    "has_kw": False,
                    "args": args,
                    "lineno": lineno,
                }
    return sigs


def synthesize_shadow_spec(task_text, root=".", files=None, domains=None):
    """Engine 2: infer unwritten non-negotiable invariants and preserve call-site contracts."""
    root = os.path.abspath(root)
    text_l = str(task_text or "").lower()
    dom_set = set(domains or [])

    invariants = [
        "Preserve existing test assertions; never delete or @skip failing tests to force green status.",
        "Use explicit error handling and timeouts; never swallow exceptions with bare `except: pass`.",
    ]
    edge_cases = ["Empty, null, or malformed inputs", "Subprocess/network timeout or non-zero exit"]

    if dom_set & {"security", "backend", "database"} or any(
        w in text_l for w in ("auth", "login", "jwt", "token", "oauth", "api", "db", "sql", "rls", "cors", "permission")
    ):
        invariants.append("Never weaken auth, CORS, TLS verification, or RLS policies to bypass an error; parameterize queries and validate inputs.")
        edge_cases.extend(["Unauthorized / cross-tenant access attempt", "Expired or missing credentials/tokens"])

    if dom_set & {"database"} or any(w in text_l for w in ("checkout", "payment", "billing", "order", "migration", "schema")):
        invariants.append("Keep database migrations backward-compatible and state mutations idempotent under retries.")
        edge_cases.extend(["Duplicate retry / concurrent race condition", "Rollback on mid-transaction failure"])

    if dom_set & {"frontend"} or any(w in text_l for w in ("ui", "modal", "form", "react", "next", "css", "button", "page")):
        invariants.append("Preserve keyboard navigation, responsive viewport integrity, and zero browser console errors.")
        edge_cases.extend(["Mobile 375px viewport overflow", "Loading, empty, and error UI states"])

    preserved = []
    for rel in (files or [])[:6]:
        clean_rel = rel.replace("\\", "/")
        full = os.path.join(root, clean_rel)
        if not os.path.isfile(full):
            continue
        ext = os.path.splitext(clean_rel)[1].lower()
        try:
            with open(full, encoding="utf-8", errors="replace") as f:
                src = f.read()
        except OSError:
            continue
        sigs = _extract_py_signatures(src) if ext == ".py" else (
            _extract_js_signatures(src) if ext in (".js", ".jsx", ".ts", ".tsx") else {}
        )
        for qual, info in list(sigs.items())[:8]:
            preserved.append(f"{clean_rel}:L{info['lineno']} {qual}({', '.join(info['args'])})")

    return {
        "invariants": list(dict.fromkeys(invariants)),
        "preserved_signatures": preserved[:15],
        "unwritten_edge_cases": list(dict.fromkeys(edge_cases))[:6],
    }


def _git_diff_text(root):
    if not os.path.isdir(os.path.join(root, ".git")):
        return ""
    chunks = []
    for cmd in (["git", "-C", root, "diff"], ["git", "-C", root, "diff", "--cached"]):
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15)
            if out.returncode == 0 and out.stdout.strip():
                chunks.append(out.stdout)
        except (OSError, subprocess.SubprocessError):
            pass
    return "\n".join(chunks)


def audit_anti_tamper(root=".", diff_text=None):
    """Engine 3: detect test assertion deletion/skips, silent except swallowing, and security bypasses."""
    root = os.path.abspath(root)
    raw = _git_diff_text(root) if diff_text is None else diff_text
    violations = []

    current_file = None
    removed = []
    added = []

    def flush_file():
        if not current_file:
            return
        is_test = bool(TEST_FILE_RX.search(current_file))
        if is_test:
            rem_asserts = sum(1 for ln in removed if ASSERT_RX.search(ln))
            add_asserts = sum(1 for ln in added if ASSERT_RX.search(ln))
            if rem_asserts > add_asserts:
                violations.append({
                    "kind": "test_assertion_tampering",
                    "file": current_file,
                    "detail": f"Removed {rem_asserts} test assertion(s) vs added {add_asserts}",
                })
            for ln in added:
                if SKIP_RX.search(ln):
                    violations.append({
                        "kind": "test_assertion_tampering",
                        "file": current_file,
                        "detail": f"Added test skip/xfail marker: {ln.strip()[:80]}",
                    })
                    break
        else:
            for idx, ln in enumerate(added):
                if SILENT_EXCEPT_INLINE_RX.match(ln):
                    violations.append({
                        "kind": "silent_exception_swallow",
                        "file": current_file,
                        "detail": f"Inline silent exception swallow: {ln.strip()[:80]}",
                    })
                elif SILENT_EXCEPT_HEADER_RX.match(ln) and idx + 1 < len(added):
                    nxt = added[idx + 1].strip()
                    if nxt in ("pass", "...") or nxt.startswith(("pass ", "pass#")):
                        violations.append({
                            "kind": "silent_exception_swallow",
                            "file": current_file,
                            "detail": f"Silent exception block: {ln.strip()} -> {nxt}",
                        })
                for kind, rx, msg in SECURITY_WEAKEN_RX:
                    if rx.search(ln):
                        violations.append({
                            "kind": "security_guard_weakening",
                            "subkind": kind,
                            "file": current_file,
                            "detail": f"{msg}: {ln.strip()[:80]}",
                        })

    for line in (raw or "").splitlines():
        if line.startswith("diff --git "):
            flush_file()
            current_file = line.split(" b/", 1)[-1].replace("\\", "/") if " b/" in line else None
            removed, added = [], []
        elif line.startswith("--- ") or line.startswith("+++ "):
            if line.startswith("+++ b/") and not current_file:
                current_file = line[6:].replace("\\", "/")
        elif line.startswith("-"):
            removed.append(line[1:])
        elif line.startswith("+"):
            added.append(line[1:])
    flush_file()

    return {
        "passed": len(violations) == 0,
        "tamper_score": min(1.0, round(0.35 * len(violations), 2)),
        "violations": violations,
    }


def _compare_sources(before_src, after_src, file_label):
    before_sigs = _extract_py_signatures(before_src)
    after_sigs = _extract_py_signatures(after_src)
    breaks = []
    for sym, b in before_sigs.items():
        if sym not in after_sigs:
            breaks.append({
                "file": file_label,
                "symbol": sym,
                "before": f"{sym}({', '.join(b['args'])})",
                "after": "(removed)",
                "reason": "Public symbol removed",
            })
            continue
        a = after_sigs[sym]
        if a["min_args"] > b["min_args"]:
            breaks.append({
                "file": file_label,
                "symbol": sym,
                "before": f"{sym}({', '.join(b['args'])})",
                "after": f"{sym}({', '.join(a['args'])})",
                "reason": f"Required arguments increased from {b['min_args']} to {a['min_args']} without defaults",
            })
        elif a["total_args"] < b["total_args"] and not a["has_varargs"]:
            breaks.append({
                "file": file_label,
                "symbol": sym,
                "before": f"{sym}({', '.join(b['args'])})",
                "after": f"{sym}({', '.join(a['args'])})",
                "reason": f"Accepted positional arguments reduced from {b['total_args']} to {a['total_args']}",
            })
    return breaks


def check_ast_contracts(root=".", files=None, before_source=None, after_source=None, file_label="module.py"):
    """Engine 4: pre-flight AST contract diff simulator detecting breaking public signature mutations."""
    if before_source is not None and after_source is not None:
        breaks = _compare_sources(before_source, after_source, file_label)
        return {"ok": len(breaks) == 0, "breaking_changes": breaks}

    root = os.path.abspath(root)
    if not os.path.isdir(os.path.join(root, ".git")):
        return {"ok": True, "breaking_changes": []}

    target_files = [f.replace("\\", "/") for f in (files or []) if f.endswith(".py")]
    if not target_files:
        try:
            out = subprocess.run(
                ["git", "-C", root, "diff", "--name-only"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=15,
            )
            if out.returncode == 0:
                target_files = [ln.strip().replace("\\", "/") for ln in out.stdout.splitlines() if ln.strip().endswith(".py")]
        except (OSError, subprocess.SubprocessError):
            target_files = []

    all_breaks = []
    for rel in target_files[:12]:
        if TEST_FILE_RX.search(rel):
            continue
        full = os.path.join(root, rel)
        if not os.path.isfile(full):
            continue
        try:
            head_out = subprocess.run(
                ["git", "-C", root, "show", f"HEAD:{rel}"],
                capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10,
            )
            if head_out.returncode != 0:
                continue
            with open(full, encoding="utf-8", errors="replace") as f:
                after_src = f.read()
            all_breaks.extend(_compare_sources(head_out.stdout, after_src, rel))
        except (OSError, subprocess.SubprocessError):
            continue

    return {"ok": len(all_breaks) == 0, "breaking_changes": all_breaks}


def _normalize_error(error_text):
    norm = str(error_text or "").lower()
    norm = re.sub(r"0x[0-9a-f]+", "<hex>", norm)
    norm = re.sub(r"[a-z]:[\\/][^\s:]+|(?:/[\w.-]+)+", "<path>", norm)
    norm = re.sub(r"\d+", "<n>", norm)
    norm = " ".join(norm.split())
    return hashlib.sha256(norm.encode("utf-8")).hexdigest()[:12]


def record_attempt_and_check_circuit(root=".", command="", error_text="", reset=False):
    """Engine 5: loop circuit-breaker detecting >=2 repeated identical failure fingerprints."""
    root = os.path.abspath(root)
    cdir = _ensure_cortex_gitignore(root)
    path = os.path.join(cdir, CIRCUIT_FILE)
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}

    if reset or not str(error_text or "").strip():
        state = {
            "state": "CLOSED",
            "tripped": False,
            "consecutive_failures": 0,
            "last_fingerprint": None,
            "last_command": command,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "counterfactual_prescription": None,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
        return state

    fp = _normalize_error(error_text)
    consecutive = int(data.get("consecutive_failures") or 0) + 1 if data.get("last_fingerprint") == fp else 1
    tripped = consecutive >= 2
    prescription = None
    if tripped:
        prescription = (
            f"CIRCUIT OPEN (fingerprint={fp} repeated {consecutive}x): stop repeating the identical strategy. "
            "Rollback the last hunk or isolate alternatives in a git worktree, inspect AST contracts (`tw.py cortex contracts`), "
            "and switch approach or assign `code-explorer`/`architect` before another edit."
        )

    state = {
        "state": "OPEN" if tripped else "CLOSED",
        "tripped": tripped,
        "consecutive_failures": consecutive,
        "last_fingerprint": fp,
        "last_command": command,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "counterfactual_prescription": prescription,
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return state


MAX_MUTATIONS = 10  # prose budget: older lessons drop off; one that must always hold belongs in a check


def mutate_role_agent(root=".", role="", lesson="", trigger="", anti_pattern="", solution=""):
    """Engine 6: Darwin-Godel project-local TextGrad mutation in .team-workflow/agents/<role>.md."""
    role = (role or "").strip()
    if not role or not re.fullmatch(r"[a-z0-9][a-z0-9-]*", role):
        return {"role": role, "mutated": False, "reason": "invalid role name"}

    root = os.path.abspath(root)
    _ensure_cortex_gitignore(root)
    agents_dir = os.path.join(root, CORTEX_DIR, "agents")
    os.makedirs(agents_dir, exist_ok=True)
    target_path = os.path.join(agents_dir, f"{role}.md")

    cat = roles.catalog(root)
    if os.path.isfile(target_path):
        with open(target_path, encoding="utf-8", errors="replace") as f:
            text = f.read()
    elif role in cat:
        text = roles.read(cat[role])
    else:
        text = roles.TEMPLATE.format(role=role)

    heading = "## Darwin-Godel Learned Mutations (Project TextGrad)"
    if heading not in text:
        text = text.rstrip() + f"\n\n{heading}\n"

    summary = " ".join(str(lesson or solution or trigger or "Enforce verification").split())[:160]
    trig_s = " ".join(str(trigger or "project regression").split())[:100]
    avoid_s = " ".join(str(anti_pattern or "repeating unverified edits").split())[:100]
    req_s = " ".join(str(solution or summary).split())[:140]
    bullet = f"- **{summary}** (Trigger: `{trig_s}` | Avoid: `{avoid_s}` | Require: `{req_s}`)"

    if bullet not in text:
        head, _, tail = text.partition(heading)
        section, nxt, rest = tail.partition("\n## ")  # keep any later section as it is
        kept = [ln for ln in section.splitlines() if ln.strip().startswith("- ")][-(MAX_MUTATIONS - 1):]
        text = head + heading + "\n" + "\n".join(kept + [bullet]) + "\n" + (("\n## " + rest) if nxt else "")
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(text)

    mutations_count = sum(1 for ln in text.split(heading, 1)[-1].splitlines() if ln.strip().startswith("- "))
    return {
        "role": role,
        "path": target_path,
        "mutated": True,
        "mutations_count": mutations_count,
    }


def zero_entropy_schema():
    """Engine 7: fixed high-density inter-agent telemetry schema."""
    return "[CLAIM] file:L<line> | [DIFF] symbol | [CONTRACT] preserved | [PROOF] cmd -> exit 0"
