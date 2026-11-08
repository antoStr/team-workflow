#!/usr/bin/env python3
"""team-workflow Brain: Obsidian-compatible graph memory engine (standard library only).

Manages an interconnected knowledge vault in docs/brain/ with bi-directional wikilinks [[...]],
AST-based repository mapping, fast BFS-expanded context queries, and vault health checks.
"""
import ast
import collections
import json
import os
import re
import sys
import time

VAULT_DIR = "docs/brain"
IGNORE_DIRS = {
    ".git", ".obsidian", "__pycache__", "node_modules", "venv", ".venv",
    "env", ".env", "dist", "build", ".pytest_cache", ".mypy_cache", ".cache", "library"
}
CODE_EXTENSIONS = {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs"}


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _validate_vault_path(root, vault_dir):
    root_abs = os.path.abspath(root)
    target_abs = os.path.abspath(os.path.join(root, vault_dir))
    if not (target_abs == root_abs or target_abs.startswith(root_abs + os.sep)):
        raise ValueError(f"Security: vault_dir '{vault_dir}' must stay within repository root '{root}'.")
    return target_abs


def init_vault(vault_dir=VAULT_DIR, root=".", force=False):
    """Initialize a new Obsidian-compatible vault directory structure."""
    target = _validate_vault_path(root, vault_dir)
    if os.path.exists(target) and not force and os.listdir(target):
        return {"status": "exists", "path": target, "message": "Vault already exists. Use force=True to overwrite."}

    _ensure_dir(target)
    for sub in ("nodes", "areas", "decisions", "learnings", "journal", ".obsidian"):
        _ensure_dir(os.path.join(target, sub))

    # Obsidian app settings
    app_json = {
        "useMarkdownLinks": False,
        "newFileFolderPath": "nodes",
        "attachmentFolderPath": "attachments"
    }
    with open(os.path.join(target, ".obsidian", "app.json"), "w", encoding="utf-8") as f:
        json.dump(app_json, f, indent=2)

    # Obsidian graph settings with color groups
    graph_json = {
        "collapse-filter": False,
        "search": "",
        "localJumps": 1,
        "localBacklinks": True,
        "localForelinks": True,
        "localInterlinks": True,
        "showTags": True,
        "showAttachments": False,
        "hideUnresolved": False,
        "showOrphans": True,
        "colorGroups": [
            {"query": "tag:#area", "color": {"a": 1, "rgb": 14725376}},
            {"query": "tag:#core", "color": {"a": 1, "rgb": 39168}},
            {"query": "tag:#decision", "color": {"a": 1, "rgb": 16744448}},
            {"query": "tag:#interface", "color": {"a": 1, "rgb": 255}}
        ]
    }
    with open(os.path.join(target, ".obsidian", "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph_json, f, indent=2)

    # Vault root index
    index_md = """# Project Brain Index

Welcome to the project Brain vault (Obsidian-compatible).
This graph-based memory replaces static documentation with interconnected nodes and contracts.

## Vault Structure
- [[nodes/]]: Fine-grained architecture and module nodes
- [[areas/]]: High-level domain areas and subsystems
- [[decisions/]]: Architecture Decision Records (ADRs)

## Navigation & Commands
- Query context: `tw.py brain query <target>`
- Validate vault integrity: `tw.py brain check`
- Map codebase changes: `tw.py brain map`
"""
    with open(os.path.join(target, "INDEX.md"), "w", encoding="utf-8") as f:
        f.write(index_md)

    return {"status": "created", "path": target, "subdirs": ["nodes", "areas", "decisions", ".obsidian"]}


def _slugify(text):
    slug = re.sub(r"[^a-zA-Z0-9_-]", "-", text).strip("-").lower()
    return re.sub(r"-+", "-", slug)


def _extract_py_contracts(filepath):
    """Extract classes, functions, and imports using AST."""
    contracts = {"imports": [], "classes": [], "functions": [], "docstring": ""}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            source = f.read()
        tree = ast.parse(source, filename=filepath)
    except (SyntaxError, OSError):
        return contracts

    contracts["docstring"] = ast.get_docstring(tree) or ""

    for node in tree.body:
        if isinstance(node, ast.Import):
            for alias in node.names:
                contracts["imports"].append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            for alias in node.names:
                contracts["imports"].append(f"{mod}.{alias.name}" if mod else alias.name)
        elif isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
            contracts["classes"].append({"name": node.name, "methods": methods})
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            args = [a.arg for a in node.args.args]
            contracts["functions"].append(f"{node.name}({', '.join(args)})")

    return contracts


def _extract_regex_contracts(filepath, ext):
    """Extract imports and symbols for JS, TS, Go, Rust using regex."""
    contracts = {"imports": [], "classes": [], "functions": [], "docstring": ""}
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return contracts

    if ext in (".js", ".jsx", ".ts", ".tsx"):
        for m in re.finditer(r'''(?:import|from|require\()\s*['"]([^'"]+)['"]''', content):
            contracts["imports"].append(m.group(1))
        for m in re.finditer(r'''(?:class|interface)\s+([A-Za-z0-9_]+)''', content):
            contracts["classes"].append({"name": m.group(1), "methods": []})
        for m in re.finditer(r'''function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)''', content):
            contracts["functions"].append(f"{m.group(1)}({m.group(2).strip()})")
    elif ext == ".go":
        for m in re.finditer(r'''import\s+(?:\(\s*([^)]+)\s*\)|"([^"]+)")''', content):
            block = m.group(1) or m.group(2) or ""
            for line in block.splitlines():
                clean = line.strip().strip('"')
                if clean:
                    contracts["imports"].append(clean)
        for m in re.finditer(r'''func\s+(?:\([^)]+\)\s+)?([A-Za-z0-9_]+)\s*\(([^)]*)\)''', content):
            contracts["functions"].append(f"{m.group(1)}({m.group(2).strip()})")
    elif ext == ".rs":
        for m in re.finditer(r'''use\s+([^;]+);''', content):
            contracts["imports"].append(m.group(1).strip())
        for m in re.finditer(r'''(?:fn|struct|enum)\s+([A-Za-z0-9_]+)''', content):
            contracts["functions"].append(m.group(1))

    return contracts


def map_repo(root=".", vault_dir=VAULT_DIR, incremental=False):
    """Scan the codebase, extract contracts, and generate/update nodes in vault_dir/nodes."""
    vault_path = _validate_vault_path(root, vault_dir)
    nodes_dir = os.path.join(vault_path, "nodes")
    _ensure_dir(nodes_dir)

    file_to_node = {}
    code_files = []

    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in CODE_EXTENSIONS:
                full = os.path.join(dirpath, f)
                rel = os.path.relpath(full, root).replace("\\", "/")
                # Skip files inside the vault itself
                if rel.startswith(vault_dir.replace("\\", "/")):
                    continue
                code_files.append((rel, full, ext))
                slug = _slugify(os.path.splitext(rel)[0])
                file_to_node[rel] = slug

    # Pass 1: Parse contracts
    nodes_data = {}
    for rel, full, ext in code_files:
        slug = file_to_node[rel]
        if ext == ".py":
            contracts = _extract_py_contracts(full)
        else:
            contracts = _extract_regex_contracts(full, ext)

        layer = rel.split("/")[0] if "/" in rel else "root"
        nodes_data[slug] = {
            "id": slug,
            "title": os.path.basename(rel),
            "layer": layer,
            "tags": ["code", ext.lstrip(".")],
            "aliases": [rel, os.path.basename(rel)],
            "files": [rel],
            "raw_imports": contracts["imports"],
            "classes": contracts["classes"],
            "functions": contracts["functions"],
            "docstring": contracts["docstring"],
            "upstream": set(),
            "downstream": set(),
            "mtime": os.path.getmtime(full)
        }

    # Pass 2: Resolve internal dependencies (upstream & downstream) via O(1) suffix index
    suffix_to_slug = {}
    for other_rel, other_slug in file_to_node.items():
        base = os.path.splitext(other_rel)[0].replace("\\", "/")
        parts = base.split("/")
        for i in range(len(parts)):
            sub = "/".join(parts[i:])
            suffix_to_slug.setdefault(sub, []).append(other_slug)

    for slug, data in nodes_data.items():
        for imp in data["raw_imports"]:
            imp_norm = imp.replace(".", "/").replace("\\", "/")
            candidates = suffix_to_slug.get(imp_norm, [])
            for target_slug in candidates:
                if target_slug != slug:
                    data["upstream"].add(target_slug)
                    nodes_data[target_slug]["downstream"].add(slug)

    # Pass 3: Write markdown files
    now_iso = time.strftime("%Y-%m-%dT%H:%M:%S")
    written = 0

    for slug, data in nodes_data.items():
        node_file = os.path.join(nodes_dir, f"{slug}.md")
        if incremental and os.path.isfile(node_file):
            if os.path.getmtime(node_file) >= data["mtime"]:
                continue

        frontmatter = [
            "---",
            f"id: {data['id']}",
            f"title: {data['title']}",
            f"layer: {data['layer']}",
            f"tags: [{', '.join(data['tags'])}]",
            f"aliases: [{', '.join(data['aliases'])}]",
            "upstream:",
            *(f"  - \"[[{u}]]\"" for u in sorted(data["upstream"])),
            "downstream:",
            *(f"  - \"[[{d}]]\"" for d in sorted(data["downstream"])),
            f"files: [{', '.join(data['files'])}]",
            "status: active",
            f"last_updated: {now_iso}",
            "---"
        ]

        content = [
            "\n".join(frontmatter),
            f"\n# {data['title']}\n",
            data["docstring"].strip() if data["docstring"] else "No module docstring.",
            "\n## Contracts\n"
        ]

        if data["classes"]:
            content.append("### Classes")
            for c in data["classes"]:
                methods_str = f" (methods: {', '.join(c['methods'])})" if c["methods"] else ""
                content.append(f"- `{c['name']}`{methods_str}")
        if data["functions"]:
            content.append("\n### Functions")
            for fn in data["functions"][:15]:
                content.append(f"- `{fn}`")
            if len(data["functions"]) > 15:
                content.append(f"- ... and {len(data['functions']) - 15} more functions")

        content.append("\n## Dependencies")
        content.append("### Upstream")
        if data["upstream"]:
            content.extend(f"- [[{u}]]" for u in sorted(data["upstream"]))
        else:
            content.append("- None")
        content.append("### Downstream")
        if data["downstream"]:
            content.extend(f"- [[{d}]]" for d in sorted(data["downstream"]))
        else:
            content.append("- None")

        with open(node_file, "w", encoding="utf-8") as f:
            f.write("\n".join(content) + "\n")
        written += 1

    return {"files_scanned": len(code_files), "nodes_written": written, "vault": nodes_dir}


def _parse_frontmatter(text):
    """Extract YAML frontmatter dictionary and body text."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    yaml_text = parts[1]
    body = parts[2]
    data = {}
    for line in yaml_text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip()
            if v.startswith("[") and v.endswith("]"):
                data[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            else:
                data[k] = v.strip("'\"")
    return data, body


def _load_all_nodes(vault_path):
    """Load all nodes from nodes/, areas/, decisions/, learnings/, journal/ in the vault."""
    nodes = {}
    for folder in ("nodes", "areas", "decisions", "learnings", "journal"):
        p = os.path.join(vault_path, folder)
        if not os.path.isdir(p):
            continue
        for fname in os.listdir(p):
            if fname.endswith(".md"):
                full = os.path.join(p, fname)
                try:
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        meta, body = _parse_frontmatter(f.read())
                    slug = meta.get("id") or os.path.splitext(fname)[0]
                    # Extract wikilinks from body (ignoring placeholder examples like [[...]])
                    raw_links = re.findall(r"\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]", body)
                    wikilinks = [w for w in raw_links if w not in ("...", "slug", "Nota", "target", "node", "id")]
                    nodes[slug] = {
                        "slug": slug,
                        "file": full,
                        "meta": meta,
                        "body": body,
                        "wikilinks": wikilinks
                    }
                except OSError:
                    continue
    return nodes


def query_context(target_or_query, vault_dir=VAULT_DIR, root=".", hops=1, format="prompt"):
    """Query seed node(s) and expand 1-hop / 2-hop BFS. Returns dense, token-saving context."""
    vault_path = os.path.join(root, vault_dir)
    nodes = _load_all_nodes(vault_path)
    if not nodes:
        return f"No brain vault found at {vault_path}. Run `tw.py brain init` and `map` first."

    # 1. Match seed node(s)
    query = (target_or_query or "").strip().lower()
    seeds = []
    for slug, n in nodes.items():
        if query == slug or query in [a.lower() for a in n["meta"].get("aliases", [])]:
            seeds.append(slug)
            break
        for f in n["meta"].get("files", []):
            if query in f.lower() or os.path.basename(f).lower() == query:
                seeds.append(slug)
                break

    if not seeds:
        for slug, n in nodes.items():
            if query in slug or query in n["meta"].get("title", "").lower():
                seeds.append(slug)
            elif query in n["body"].lower():
                seeds.append(slug)

    if not seeds:
        return f"No brain node matching '{target_or_query}' found."

    # 2. BFS expansion with pre-indexed inverted links and deque O(1)
    backlinks = collections.defaultdict(set)
    for other_slug, other_node in nodes.items():
        for wl in other_node["wikilinks"]:
            backlinks[_slugify(wl)].add(other_slug)

    visited = {}
    queue = collections.deque((s, 0) for s in seeds[:3])
    for s in seeds[:3]:
        visited[s] = 0

    while queue:
        curr, dist = queue.popleft()
        if dist >= hops:
            continue
        node = nodes.get(curr)
        if not node:
            continue
        # Neighbors: explicit body wikilinks + pre-indexed backlinks
        neighbors = set(node["wikilinks"]) | backlinks.get(curr, set())
        for nb in neighbors:
            clean_nb = _slugify(nb)
            if clean_nb in nodes and clean_nb not in visited:
                visited[clean_nb] = dist + 1
                queue.append((clean_nb, dist + 1))

    # 3. Format output
    if format == "json":
        res = []
        for s, d in visited.items():
            res.append({"node": s, "depth": d, "meta": nodes[s]["meta"]})
        return json.dumps(res, indent=2)

    lines = [f"[BRAIN CONTEXT | seed: '{target_or_query}' | hops: {hops} | nodes: {len(visited)}]"]
    for slug, dist in sorted(visited.items(), key=lambda x: (x[1], x[0])):
        n = nodes[slug]
        meta = n["meta"]
        title = meta.get("title", slug)
        layer = meta.get("layer", "unknown")
        files = ", ".join(meta.get("files", [])) or "-"
        # Extract contracts snippet
        contracts_match = re.search(r"## Contracts\s*(.*?)(?=\n## |\Z)", n["body"], re.DOTALL)
        contracts = contracts_match.group(1).strip() if contracts_match else ""
        contracts_short = "\n    ".join(contracts.splitlines()[:8]) if contracts else "no contracts listed"

        lines.append(f"\n@node {slug} (layer: {layer}, depth: {dist})")
        lines.append(f"  title: {title}")
        lines.append(f"  files: {files}")
        lines.append(f"  contracts:\n    {contracts_short}")
        links_str = ", ".join(f"[[{w}]]" for w in n["wikilinks"][:8]) or "none"
        lines.append(f"  links: {links_str}")

    return "\n".join(lines)


def context_briefing(target_or_query, vault_dir=VAULT_DIR, root=".", hops=1, role=None):
    """Combine sub-graph topology context with active vaccines from autolearn."""
    base_context = query_context(target_or_query, vault_dir=vault_dir, root=root, hops=hops)
    try:
        import autolearn
        vaccines = autolearn.get_vaccines(root=root, file_path=target_or_query, role=role)
        if vaccines:
            return base_context + "\n\n" + autolearn.format_vaccine_prompt(vaccines)
    except Exception:
        pass
    return base_context


def check_vault(vault_dir=VAULT_DIR, root=".", strict=False):
    """Verify broken wikilinks, orphan nodes, missing files, and invalid frontmatter."""
    vault_path = _validate_vault_path(root, vault_dir)
    nodes = _load_all_nodes(vault_path)

    findings = {
        "broken_wikilinks": [],
        "orphan_nodes": [],
        "missing_files": [],
        "invalid_frontmatter": []
    }

    all_slugs = set(nodes.keys())
    # Add aliases
    for n in nodes.values():
        for a in n["meta"].get("aliases", []):
            all_slugs.add(_slugify(a))

    incoming_links = {slug: 0 for slug in nodes}

    for slug, n in nodes.items():
        meta = n["meta"]
        # Check frontmatter
        if not meta or "id" not in meta or "title" not in meta:
            findings["invalid_frontmatter"].append({"file": n["file"], "issue": "Missing id or title"})

        # Check missing files
        for f in meta.get("files", []):
            if not os.path.exists(os.path.join(root, f)):
                findings["missing_files"].append({"node": slug, "missing_file": f})

        # Check wikilinks
        for link in n["wikilinks"]:
            link_slug = _slugify(link)
            if link_slug in nodes:
                incoming_links[link_slug] = incoming_links.get(link_slug, 0) + 1
            elif link_slug not in all_slugs:
                findings["broken_wikilinks"].append({"from_node": slug, "target": link})

    # Check orphans (nodes with no incoming and no outgoing links)
    for slug, n in nodes.items():
        if n["meta"].get("type") in ("learning", "journal"):
            continue
        if incoming_links.get(slug, 0) == 0 and len(n["wikilinks"]) == 0:
            findings["orphan_nodes"].append(slug)

    total_issues = (len(findings["broken_wikilinks"]) +
                    len(findings["missing_files"]) + len(findings["invalid_frontmatter"]))

    return {
        "ok": total_issues == 0,
        "total_nodes": len(nodes),
        "total_issues": total_issues,
        "findings": findings
    }


def rollover_state(root=".", vault_dir=VAULT_DIR):
    """Archive past achievements from STATE.md into a weekly journal note and keep STATE lean."""
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)
    week_str = now.strftime("%Y-W%W")

    vault_path = _validate_vault_path(root, vault_dir)
    journal_dir = os.path.join(vault_path, "journal")
    _ensure_dir(journal_dir)

    # Locate active STATE.md
    state_file = os.path.join(vault_path, "STATE.md")
    if not os.path.isfile(state_file):
        state_file = os.path.join(root, "docs", "memory", "STATE.md")
    if not os.path.isfile(state_file):
        return {"status": "no_state", "message": "No active STATE.md found to rollover."}

    with open(state_file, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    archive_file = os.path.join(journal_dir, f"week-{week_str}.md")

    journal_content = [
        "---",
        f"id: journal-week-{week_str}",
        f"title: \"Weekly Archive: {week_str}\"",
        "type: journal",
        "tags: [\"#journal\", \"#sprint\"]",
        f"date: \"{now.strftime('%Y-%m-%d')}\"",
        "---",
        "",
        f"# Weekly Retrospective: {week_str}",
        "",
        content
    ]
    with open(archive_file, "w", encoding="utf-8") as f:
        f.write("\n".join(journal_content))

    lean_state = [
        f"# Stato del Progetto ({week_str})",
        "",
        f"> [!NOTE] Cronologia precedente archiviata in [[journal-week-{week_str}]].",
        "",
        "## Obiettivi Attivi della Settimana",
        "- [ ] Definire nuovi task o riprendere dal backlog.",
        "",
        "## Cosa Verificare",
        "- Test suite: `pytest tests`.",
        "- Integrità Brain: `tw.py brain check --strict`.",
        "",
        "## Punto di Ripresa",
        f"- Inizio nuovo sprint/ciclo ({week_str}). Consultare le schede d'area (`docs/brain/areas/`) per lo stato dei singoli moduli."
    ]
    with open(state_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lean_state))

    return {
        "status": "archived",
        "week": week_str,
        "archive_path": archive_file,
        "state_path": state_file
    }
