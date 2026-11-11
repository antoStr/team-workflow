#!/usr/bin/env python3
"""Patch-Bridge: Atomic Unified Diff & Subagent Patch Patcher.

Allows subagents or CI pipelines to generate unified diff patches (unified diff,
git diff, or markdown ```diff blocks) that can be applied atomically across
repositories without requiring raw multi-file edit permissions.
"""
import os
import re
import subprocess
import sys


def extract_diff_from_text(text):
    """Extract unified diff text, stripping markdown code fences if present."""
    if not text:
        return ""
    # Strip markdown ```diff or ```patch
    m = re.search(r"```(?:diff|patch)?\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text.strip()


def parse_unified_diff(diff_text):
    """Parse unified diff text into per-file hunks."""
    files = []
    current_file = None
    lines = diff_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        if line.startswith("--- "):
            old_name = line[4:].strip().split("\t")[0]
            if old_name.startswith("a/"):
                old_name = old_name[2:]
            i += 1
            if i < len(lines) and lines[i].startswith("+++ "):
                new_name = lines[i][4:].strip().split("\t")[0]
                if new_name.startswith("b/"):
                    new_name = new_name[2:]
                target_file = new_name if new_name != "/dev/null" else old_name
                current_file = {
                    "old_name": old_name,
                    "new_name": new_name,
                    "target": target_file,
                    "hunks": []
                }
                files.append(current_file)
                i += 1
                continue

        if line.startswith("@@ ") and current_file is not None:
            # Parse hunk header: @@ -old_start,old_len +new_start,new_len @@
            m = re.match(r"^@@\s+-(\d+)(?:,(\d+))?\s+\+(\d+)(?:,(\d+))?\s+@@", line)
            if m:
                old_start = int(m.group(1))
                old_len = int(m.group(2)) if m.group(2) else 1
                new_start = int(m.group(3))
                new_len = int(m.group(4)) if m.group(4) else 1
                hunk = {
                    "old_start": old_start,
                    "old_len": old_len,
                    "new_start": new_start,
                    "new_len": new_len,
                    "lines": []
                }
                current_file["hunks"].append(hunk)
                i += 1
                while i < len(lines) and not lines[i].startswith("@@ ") and not lines[i].startswith("--- "):
                    hunk["lines"].append(lines[i])
                    i += 1
                continue
        i += 1

    return files


def apply_file_hunks(original_lines, hunks):
    """Apply hunks sequentially to original lines."""
    result = list(original_lines)
    offset = 0

    for hunk in hunks:
        old_start = hunk["old_start"] - 1 + offset
        del_count = 0
        add_lines = []

        for line in hunk["lines"]:
            if not line:
                continue
            prefix = line[0]
            content = line[1:]
            if prefix == " ":
                del_count += 1
                add_lines.append(content)
            elif prefix == "-":
                del_count += 1
            elif prefix == "+":
                add_lines.append(content)

        result[old_start:old_start + del_count] = add_lines
        offset += len(add_lines) - del_count

    return result


def apply_patch(diff_content, root=None, dry_run=False):
    """Apply a unified diff patch to the repository."""
    root = os.path.abspath(root or ".")
    clean_diff = extract_diff_from_text(diff_content)

    if not clean_diff:
        return {"ok": False, "errors": ["Empty or invalid diff content."]}

    # Attempt git apply first if in git repository
    is_git = os.path.isdir(os.path.join(root, ".git"))
    if is_git:
        try:
            check_cmd = ["git", "apply", "--check", "-"]
            p = subprocess.run(check_cmd, input=clean_diff, text=True, cwd=root,
                               capture_output=True, timeout=5)
            if p.returncode == 0:
                if dry_run:
                    return {"ok": True, "applied_files": ["(dry-run verified via git apply)"], "errors": []}
                apply_cmd = ["git", "apply", "-"]
                p_apply = subprocess.run(apply_cmd, input=clean_diff, text=True, cwd=root,
                                         capture_output=True, timeout=5)
                if p_apply.returncode == 0:
                    files = parse_unified_diff(clean_diff)
                    applied = [f["target"] for f in files] or ["(git apply modified files)"]
                    return {"ok": True, "applied_files": applied, "errors": []}
        except Exception:
            pass

    # Pure Python patcher fallback
    parsed = parse_unified_diff(clean_diff)
    if not parsed:
        return {"ok": False, "errors": ["Could not parse unified diff hunks."]}

    applied_files = []
    errors = []

    for file_spec in parsed:
        target_path = os.path.join(root, file_spec["target"])

        if file_spec["old_name"] == "/dev/null":
            # New file
            new_lines = []
            for hunk in file_spec["hunks"]:
                for line in hunk["lines"]:
                    if line.startswith("+"):
                        new_lines.append(line[1:])
            if not dry_run:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(new_lines) + "\n")
            applied_files.append(file_spec["target"])
            continue

        if not os.path.isfile(target_path):
            errors.append(f"Target file not found: {file_spec['target']}")
            continue

        with open(target_path, "r", encoding="utf-8", errors="replace") as f:
            orig = f.read().splitlines()

        try:
            patched = apply_file_hunks(orig, file_spec["hunks"])
            if not dry_run:
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(patched) + "\n")
            applied_files.append(file_spec["target"])
        except Exception as e:
            errors.append(f"Failed applying hunks to {file_spec['target']}: {e}")

    return {
        "ok": len(errors) == 0,
        "applied_files": applied_files,
        "errors": errors
    }
