"""Security audit of the AI agent setup, local and free (the kind of scan AgentShield and ECC Pro
sell as a hosted service): Claude Code and agy settings, permissions, hooks, MCP servers,
instruction files, agents and skills of the user and of the repository.

Findings: {"severity", "file", "what", "fix"}; severities: critical, high, medium, low.
Custom rules (your own policy pack): ~/.team-workflow/audit-rules.json and
<repository>/.team-workflow-audit.json, a list of
    {"id": "no-prod-urls", "severity": "high", "pattern": "prod\\\\.example\\\\.com",
     "files": ["*.md", "*.json"], "message": "production host in agent config", "fix": "..."}
"""
import fnmatch
import glob
import json
import os
import re

import settings
from memcheck import SECRETS

SEVERITY = ("critical", "high", "medium", "low")
BROAD_ALLOW = re.compile(r"^(Bash|Write|Edit|MultiEdit|WebFetch|mcp__\w+)(\(\s*\*{1,2}\s*\))?$")
PIPE_TO_SHELL = re.compile(r"\b(curl|wget|iwr|Invoke-WebRequest)\b[^|;&]*\|\s*(ba|z|fi)?sh\b"
                           r"|base64\s+-d[^|]*\|\s*(ba)?sh")
DESTRUCTIVE = re.compile(r"\brm\s+-[a-z]*r[a-z]*\s+(/|~|\$HOME)(\s|$)|\bmkfs\b|\bdd\s+if=.*of=/dev/")
EXFIL = re.compile(r"\b(curl|wget|nc|ncat)\b[^\n]*\$\{?[A-Z_]*(KEY|TOKEN|SECRET|PASS)[A-Z_]*")
INJECTION = re.compile(
    r"ignore (all |any )?(previous|prior|above) (instructions|rules)|disregard (the )?(system|previous) prompt"
    r"|do not (tell|inform|show) the user|without (telling|asking) the user|exfiltrat"
    r"|you are now (in )?(developer|dan|jailbreak) mode", re.I)
HIDDEN = re.compile("[​-‏‪-‮⁠-⁤⁦-⁩﻿]")
UNPINNED = re.compile(r"^(@[\w.-]+/)?[\w.-]+(@latest)?$")
SECRET_KEY = re.compile(r"KEY|TOKEN|SECRET|PASSWORD")


def finding(severity, path, what, fix):
    return {"severity": severity, "file": path, "what": what, "fix": fix}


def read(path, limit=2_000_000):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read(limit)
    except OSError:
        return None


def load_json(path):
    text = read(path)
    if text is None:
        return None
    try:
        return json.loads(text)
    except ValueError:
        return {"__invalid__": True}


def mask(value):
    return value[:4] + "..." + value[-2:] if len(value) > 8 else "***"


def scan_text(path, text, instructions=False):
    out = []
    for label, rx in SECRETS.items():
        for m in rx.finditer(text):
            out.append(finding("critical", path, f"{label} in plain text ({mask(m.group(0))})",
                               "remove it, rotate it, load it from the environment or a keychain"))
    if HIDDEN.search(text):
        out.append(finding("high", path, "invisible or bidirectional Unicode characters",
                           "remove them: they can hide instructions from reviewers"))
    if instructions:
        for m in INJECTION.finditer(text):
            out.append(finding("high", path, f"prompt-injection phrase: {m.group(0)!r}",
                               "delete it or rewrite the instruction plainly"))
        if EXFIL.search(text):
            out.append(finding("high", path, "instruction that sends a secret-like variable over the network",
                               "remove it; agents must never send credentials anywhere"))
    return out


def scan_command(path, where, command):
    out = []
    if PIPE_TO_SHELL.search(command):
        out.append(finding("critical", path, f"{where} downloads and runs code: {command[:100]}",
                           "vendor or pin the script and run it from a reviewed file"))
    if DESTRUCTIVE.search(command):
        out.append(finding("critical", path, f"{where} runs a destructive command: {command[:100]}",
                           "remove it or scope it to a project folder"))
    if EXFIL.search(command):
        out.append(finding("high", path, f"{where} sends a secret-like variable over the network", "remove it"))
    return out


def plain_secrets(path, where, table):
    return [finding("high", path, f"{where} holds {key} in plain text", "pass it from the environment")
            for key, value in (table or {}).items()
            if SECRET_KEY.search(key) and value and not str(value).startswith("$")]


def scan_settings(path):
    data = load_json(path)
    if data is None:
        return []
    if data.get("__invalid__"):
        return [finding("medium", path, "not valid JSON: the app ignores it", "fix the syntax")]
    out = []
    perms = data.get("permissions") or {}
    for rule in perms.get("allow") or []:
        if BROAD_ALLOW.match(str(rule).strip()):
            out.append(finding("high", path, f"permission allows every call: {rule}",
                               "allow specific commands, e.g. Bash(npm test:*)"))
    if perms.get("defaultMode") == "bypassPermissions" or data.get("skipDangerousModePermissionPrompt"):
        out.append(finding("high", path, "permission prompts are bypassed for every tool",
                           "use acceptEdits or an allow list instead"))
    if perms.get("allow") and ".env" not in " ".join(map(str, perms.get("deny") or [])):
        out.append(finding("low", path, "no deny rule for secret files (.env, keys)",
                           'add "Read(./.env*)" and "Read(**/*.pem)" to permissions.deny'))
    for event, groups in (data.get("hooks") or {}).items():
        for group in groups if isinstance(groups, list) else []:
            for hook in group.get("hooks", []) if isinstance(group, dict) else []:
                out += scan_command(path, f"{event} hook", str(hook.get("command", "")))
    out += plain_secrets(path, "settings env", data.get("env"))
    return out + scan_text(path, json.dumps(data))


def scan_mcp(path, servers):
    out = []
    for name, cfg in (servers or {}).items():
        if not isinstance(cfg, dict):
            continue
        cmd = [str(cfg.get("command", ""))] + [str(a) for a in cfg.get("args", [])]
        if cmd[0] in ("npx", "bunx", "uvx", "pnpm"):
            pkgs = [a for a in cmd[1:] if not a.startswith("-") and a not in ("dlx", "exec")]
            if pkgs and UNPINNED.match(pkgs[0]):
                out.append(finding("medium", path, f"MCP server {name} runs an unpinned package: {pkgs[0]}",
                                   "pin a reviewed version (name@1.2.3)"))
        out += scan_command(path, f"MCP server {name}", " ".join(cmd))
        url = str(cfg.get("url") or cfg.get("serverUrl") or "")
        if url.startswith("http://") and not re.match(r"http://(localhost|127\.0\.0\.1)", url):
            out.append(finding("high", path, f"MCP server {name} over plain http: {url}", "use https"))
        out += plain_secrets(path, f"MCP server {name}", cfg.get("env"))
        auth = {k: v for k, v in (cfg.get("headers") or {}).items() if k.lower() == "authorization"}
        out += [finding("high", path, f"MCP server {name} has a literal Authorization header",
                        "pass it from the environment") for v in auth.values() if not str(v).startswith("$")]
    return out


def targets(root):
    """(kind, path) of every file the audit reads."""
    home = os.path.expanduser("~")
    found = [("settings", os.path.join(home, ".claude", "settings.json")),
             ("mcp-claude", os.path.join(home, ".claude.json")),
             ("mcp", os.path.join(home, ".gemini", "config", "mcp_config.json"))]
    for pattern in ("~/.claude/agents/*.md", "~/.gemini/config/agents/*.md", "~/.claude/CLAUDE.md",
                    "~/.gemini/GEMINI.md", "~/.gemini/config/skills/*/SKILL.md"):
        found += [("instructions", p) for p in glob.glob(os.path.expanduser(pattern))]
    if root:
        found += [("settings", os.path.join(root, ".claude", rel))
                  for rel in ("settings.json", "settings.local.json")]
        found.append(("mcp", os.path.join(root, ".mcp.json")))
        for pattern in ("CLAUDE.md", "AGENTS.md", "GEMINI.md", ".claude/agents/*.md",
                        ".claude/skills/*/SKILL.md", ".agents/agents/*.md", ".agents/skills/*/SKILL.md",
                        ".agents/rules/*.md", ".cursor/rules/*", "docs/memory/*.md"):
            found += [("instructions", p) for p in glob.glob(os.path.join(root, pattern))]
    return [(k, p) for k, p in found if os.path.isfile(p)]


def custom_rules(root):
    rules = []
    for path in [os.path.join(settings.home_dir(), "audit-rules.json")] + (
            [os.path.join(root, ".team-workflow-audit.json")] if root else []):
        data = load_json(path)
        if isinstance(data, list):
            rules += data
    return rules


def from_library(path, text):
    """A SKILL.md that tw.py library installed and that still equals its library entry."""
    try:
        import library  # absent where ci-init copied this file alone
    except ImportError:
        return False
    folder = os.path.dirname(path)
    if not os.path.isfile(os.path.join(folder, library.MARK)):
        return False
    return read(library.main_file(os.path.basename(folder))) == text


def audit(root=None):
    """(findings sorted by severity, number of files scanned)."""
    files, out = targets(root), []
    for kind, path in files:
        if kind == "settings":
            out += scan_settings(path)
        elif kind == "mcp-claude":  # ~/.claude.json: only the MCP servers, it holds much more
            data = load_json(path) or {}
            out += scan_mcp(path, data.get("mcpServers"))
            for proj, cfg in (data.get("projects") or {}).items():
                if root and os.path.abspath(proj) == os.path.abspath(root):
                    out += scan_mcp(path, (cfg or {}).get("mcpServers"))
        elif kind == "mcp":
            data = load_json(path) or {}
            out += scan_mcp(path, data.get("mcpServers")) + scan_text(path, json.dumps(data))
        else:
            text = read(path) or ""
            found = scan_text(path, text, instructions=True)
            if found and from_library(path, text):  # ECC's own warnings quote these phrases
                for f in found:
                    if f["what"].startswith("prompt-injection phrase"):
                        f["severity"] = "low"
                        f["what"] += " (team-workflow library entry from ECC, unchanged: check the context)"
            out += found
    for rule in custom_rules(root):
        try:
            rx = re.compile(rule["pattern"])
        except (KeyError, TypeError, re.error):
            continue
        for _, path in files:
            globs = rule.get("files")
            if globs and not any(fnmatch.fnmatch(os.path.basename(path), g) for g in globs):
                continue
            if rx.search(read(path) or ""):
                out.append(finding(rule.get("severity", "medium"), path,
                                   f"[{rule.get('id', 'custom')}] {rule.get('message', rule['pattern'])}",
                                   rule.get("fix", "see your policy")))
    home = os.path.expanduser("~")
    seen, unique = set(), []
    for f in sorted(out, key=lambda f: SEVERITY.index(f["severity"]) if f["severity"] in SEVERITY else 9):
        if (f["file"], f["what"]) not in seen:
            seen.add((f["file"], f["what"]))
            unique.append(dict(f, file=f["file"].replace(home, "~", 1)))
    return unique, len(files)


def main():
    import argparse
    import sys
    ap = argparse.ArgumentParser(description="Security audit of the AI agent setup.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--strict", action="store_true", help="exit 1 on critical or high findings")
    args = ap.parse_args()
    findings, scanned = audit(os.path.abspath(args.root))
    print(report(findings, scanned))
    if args.strict and any(f["severity"] in ("critical", "high") for f in findings):
        sys.exit(1)


def report(findings, scanned):
    if not findings:
        return f"audit: {scanned} files scanned, no findings"
    lines = [f"audit: {scanned} files scanned, {len(findings)} findings"]
    for f in findings:
        lines.append(f"[{f['severity'].upper()}] {f['file']}: {f['what']}\n    fix: {f['fix']}")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
