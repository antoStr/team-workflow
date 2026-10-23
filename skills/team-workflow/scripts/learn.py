"""Learn a repository's habits from its git history, locally and without limits (what ECC's
/skill-create and its hosted Pro analysis do): hotspots, bug-prone files, files that change
together, commit conventions, tests changed with code, reverts. The orchestrator turns the
facts into memory (Known traps, PLAYBOOKS conventions) or a project skill, with the user's yes.

    python3 learn.py --root . [--max 2000] [--json]
"""
import argparse
import collections
import itertools
import json
import os
import re
import subprocess

FIX = re.compile(r"\b(fix|fixes|fixed|bug|hotfix|regression|patch)\b", re.I)
REVERT = re.compile(r"^Revert\b|\brevert\b", re.I)
CONVENTIONAL = re.compile(r"^(\w+)(\([^)]*\))?!?:")
TEST = re.compile(r"(^|/)(tests?|spec|__tests__)/|[._-](test|spec)\.\w+$|_test\.go$|(^|/)test_")
NOISE = re.compile(r"(^|/)(package-lock\.json|yarn\.lock|pnpm-lock\.yaml|Cargo\.lock|go\.sum|poetry\.lock"
                   r"|uv\.lock|composer\.lock|Gemfile\.lock|CHANGELOG\.md)$|(^|/)(dist|build|vendor)/")


def commits(root, limit):
    """[(hash, subject, [files])], newest first."""
    out = subprocess.run(["git", "-C", root, "log", f"-n{limit}", "--no-merges", "--name-only",
                          "--format=%x00%h%x09%s"], capture_output=True, text=True, encoding="utf-8", errors="replace")
    result = []
    for block in out.stdout.split("\x00")[1:]:
        head, _, body = block.partition("\n")
        sha, _, subject = head.partition("\t")
        files = [f for f in body.splitlines() if f.strip() and not NOISE.search(f)]
        result.append((sha, subject, files))
    return result


def analyze(root, limit=2000):
    history = commits(root, limit)
    touched, fixes, pairs = collections.Counter(), collections.Counter(), collections.Counter()
    prefixes, reverts, sizes = collections.Counter(), [], []
    with_tests = code_commits = 0
    for sha, subject, files in history:
        sizes.append(len(files))
        touched.update(files)
        code = [f for f in files if not TEST.search(f)]
        if FIX.search(subject):
            fixes.update(code)
        if REVERT.search(subject):
            reverts.append(f"{sha} {subject}")
        m = CONVENTIONAL.match(subject)
        prefixes[m.group(1).lower() if m else "(none)"] += 1
        if code:
            code_commits += 1
            with_tests += any(TEST.search(f) for f in files)
        if 2 <= len(code) <= 12:  # big commits pair everything with everything
            pairs.update(itertools.combinations(sorted(code), 2))
    n = len(history) or 1
    return {
        "commits": len(history),
        "hotspots": touched.most_common(12),
        "bug_prone": [(f, c, touched[f]) for f, c in fixes.most_common(12) if c >= 2],
        "change_together": [(a, b, c) for (a, b), c in pairs.most_common(15) if c >= 3],
        "conventions": {"prefixes": prefixes.most_common(8),
                        "conventional_share": round(1 - prefixes["(none)"] / n, 2),
                        "median_files_per_commit": sorted(sizes)[len(sizes) // 2] if sizes else 0},
        "tests_with_code_share": round(with_tests / code_commits, 2) if code_commits else None,
        "reverts": reverts[:10],
    }


def report(data):
    if not data["commits"]:
        return "learn: no commits to analyze"
    lines = [f"learn: {data['commits']} commits analyzed", "", "Hotspots (commits touching the file):"]
    lines += [f"  {c:4}  {f}" for f, c in data["hotspots"]]
    if data["bug_prone"]:
        lines += ["", "Bug-prone files (fix commits / all commits): candidates for Known traps"]
        lines += [f"  {c:3}/{t:<4} {f}" for f, c, t in data["bug_prone"]]
    if data["change_together"]:
        lines += ["", "Files that change together (hidden coupling worth an area card note):"]
        lines += [f"  {c:3}x  {a}  <->  {b}" for a, b, c in data["change_together"]]
    conv = data["conventions"]
    lines += ["", f"Commit messages: {int(conv['conventional_share'] * 100)}% conventional; prefixes "
              + ", ".join(f"{p} {c}" for p, c in conv["prefixes"]),
              f"Median files per commit: {conv['median_files_per_commit']}"]
    if data["tests_with_code_share"] is not None:
        lines.append(f"Code commits that also change tests: {int(data['tests_with_code_share'] * 100)}%")
    if data["reverts"]:
        lines += ["", "Reverts (what went wrong before):"] + [f"  {r}" for r in data["reverts"]]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Learn a repository's habits from its git history.")
    ap.add_argument("--root", default=".")
    ap.add_argument("--max", type=int, default=2000, help="commits to read (default 2000)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    data = analyze(os.path.abspath(args.root), args.max)
    print(json.dumps(data, indent=2) if args.json else report(data))


if __name__ == "__main__":
    main()
