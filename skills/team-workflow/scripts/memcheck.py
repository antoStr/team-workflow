#!/usr/bin/env python3
"""Check docs/memory: file sizes, secrets and path references that do not exist.

Size limits and secrets are errors; missing paths are warnings (errors with --strict).
Exit code 1 on errors, so it can run in CI:
    python3 memcheck.py --root . [--strict]
"""
import argparse
import os
import re
import subprocess
import sys

LIMITS = {"INDEX.md": 70, "STATE.md": 50, "MAP.md": 120, "DECISIONS.md": 70,
          "PLAYBOOKS.md": 90, "ACCESS.md": 70}
CARD_LIMIT = 70  # every file in areas/
SECRETS = {
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,})"),
    "Slack token": re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}"),
    "API key": re.compile(r"\bsk-(?:ant-|proj-)?[A-Za-z0-9_-]{32,}"),
    "Google API key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "Stripe live key": re.compile(r"\b[rs]k_live_[0-9A-Za-z]{20,}"),
    "npm token": re.compile(r"\bnpm_[A-Za-z0-9]{36}\b"),
}
PATH_REF = re.compile(r"`([^`\s]+/[^`\s]*)`")
DOMAIN = re.compile(r"^[a-z0-9-]+(?:\.[a-z0-9-]+)+$")


def repo_paths(root):
    """Tracked files and their folders: cards often write paths relative to a subfolder."""
    try:
        out = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return set()
    files = out.stdout.splitlines() if out.returncode == 0 else []
    paths = set(files)
    for f in files:
        parts = f.split("/")
        paths.update("/".join(parts[:i]) for i in range(1, len(parts)))
    return paths


def is_dead(ref, bases, known):
    ref = re.sub(r":\d+(?::\d+)?$", "", ref).rstrip("/")  # file:line, folder/
    if "://" in ref or ref.startswith(("~", "/", "$", "-")) or any(c in ref for c in "<>*{}"):
        return False
    if DOMAIN.match(ref.split("/", 1)[0]):  # module paths such as golang.org/x/net
        return False
    if any(os.path.exists(os.path.join(base, ref)) for base in bases):
        return False
    return not any(p == ref or p.endswith("/" + ref) for p in known)


def check(root, strict=False):
    mem = os.path.join(root, "docs", "memory")
    if not os.path.isdir(mem):
        return [f"{os.path.relpath(mem, root)}: missing (create it with init_memory.py)"], []
    errors, warnings = [], []
    known = repo_paths(root)
    for dirpath, _, files in os.walk(mem):
        for name in sorted(f for f in files if f.endswith(".md")):
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            with open(path, encoding="utf-8", errors="replace") as f:
                text = f.read()
            limit = CARD_LIMIT if os.path.basename(dirpath) == "areas" else LIMITS.get(name)
            lines = text.count("\n")
            if limit and lines > limit:
                errors.append(f"{rel}: {lines} lines, limit {limit}: summarize or archive history")
            for label, rx in SECRETS.items():
                if rx.search(text):
                    errors.append(f"{rel}: looks like a {label}: remove it")
            for ref in PATH_REF.findall(text):
                if is_dead(ref, (root, mem, dirpath), known):
                    (errors if strict else warnings).append(f"{rel}: `{ref}` not found in the repository")
    return errors, warnings


def main():
    ap = argparse.ArgumentParser(description="Check docs/memory: sizes, secrets, missing paths.")
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    ap.add_argument("--strict", action="store_true", help="treat missing paths as errors")
    args = ap.parse_args()
    errors, warnings = check(os.path.abspath(args.root), args.strict)
    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"error: {e}")
    print(f"memcheck: {len(errors)} errors, {len(warnings)} warnings")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
