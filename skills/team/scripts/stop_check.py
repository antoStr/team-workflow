#!/usr/bin/env python3
"""Stop hook: ask for a memory update when files changed after docs/memory/STATE.md.

It looks at the changes of this session (working tree, and commits since SessionStart),
never blocks twice in a row (stop_hook_active) and is off with the setting stop_check=false
(or TEAM_WORKFLOW_STOP_CHECK=0), and with activation=manual.
"""
import json
import os
import sys

import settings

from common import (MEMORY_DIR, dirty_paths, git, is_agy, read_hook_input, repo_root, session_id,
                    snapshot_path)

STATE = f"{MEMORY_DIR}/STATE.md"
BRAIN_STATE = "docs/brain/STATE.md"
REASON = ("team-workflow: files changed after STATE.md was last updated. Before "
          "stopping, update STATE.md (and the area card, MAP.md, DECISIONS.md or Brain Graph when they are "
          "affected), then give the end-of-task report in the user's language.")


def locate_state(root):
    for candidate in (BRAIN_STATE, STATE):
        if os.path.isfile(os.path.join(root, candidate)):
            return candidate
    return STATE


def changed_this_session(root, snap):
    # ponytail: files already dirty at session start count only once committed; hash them at
    # SessionStart if later edits to them must be caught too.
    changed = dirty_paths(root) - set(snap.get("dirty", []))
    head = snap.get("head")
    if head:
        changed |= set((git(root, "diff", "--name-only", head, "HEAD") or "").splitlines())
    return changed


def change_times(root, paths, head):
    """{path: when it last changed}: the time of its newest commit since `head` for a committed file
    without local edits, else its mtime. A pull writes files in any order, so mtimes alone would say
    STATE.md is older than the code it came with."""
    committed, stamp = {}, 0
    for line in (git(root, "log", "--format=@%ct", "--name-only", f"{head}..HEAD") or "").splitlines() if head else []:
        if line.startswith("@"):
            stamp = int(line[1:])
        elif line.strip():
            committed.setdefault(line.strip(), stamp)  # newest commit first
    # shortcut: commit times have 1 s resolution, so code committed in the same second as STATE.md counts
    # as covered by it; compare commit order instead if that ever matters
    dirty = dirty_paths(root)
    times = {}
    for p in paths:
        full = os.path.join(root, p)
        if p in committed and p not in dirty:
            times[p] = float(committed[p])
        elif os.path.exists(full):
            times[p] = os.path.getmtime(full)
    return times


def read_mark(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None


def write_mark(path, text):
    try:
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
    except OSError:
        pass


def _auto_evolve_session(root, work):
    """Automatically update project genome, learned skills, and synaptic weights after code edits."""
    try:
        import autolearn
        import cortex
        import omniscience
        autolearn.auto_learn_from_talk(root)
        has_brain = os.path.isdir(os.path.join(root, "docs", "brain"))
        cortex.assimilate_project_knowledge(root, write_genome_md=has_brain)
        cortex.evolve_skills(root)
        tamper = omniscience.audit_anti_tamper(root)
        contracts = omniscience.check_ast_contracts(root)
        if not tamper.get("passed", True):
            first = (tamper.get("violations") or [{}])[0]
            autolearn.record_learning(
                root=root,
                title=f"Anti-Tamper violation in {first.get('file', 'diff')}",
                trigger=first.get("detail", "Anti-tamper shield caught violation"),
                anti_pattern=first.get("kind", "tampering"),
                solution="Fix implementation root cause without deleting tests, skipping assertions, or weakening security.",
                applies_to=["backend-dev", first.get("file", "*")],
                category="security",
            )
            omniscience.mutate_role_agent(
                root=root,
                role="backend-dev",
                lesson=first.get("detail", "Do not tamper with tests or security guards"),
                trigger="diff audit",
                anti_pattern=first.get("kind", "tampering"),
                solution="Keep test assertions and security guards intact.",
            )
        if not contracts.get("ok", True):
            brk = (contracts.get("breaking_changes") or [{}])[0]
            omniscience.mutate_role_agent(
                root=root,
                role="backend-dev",
                lesson=f"Preserve signature {brk.get('before', '')} in {brk.get('file', '')}",
                trigger="AST contract change",
                anti_pattern=brk.get("reason", "breaking signature"),
                solution="Preserve backward-compatible arguments/defaults or update all callers.",
            )
        cortex.record_feedback(root=root, outcome="pass", task_text=" ".join(work[:12]))
    except Exception as exc:  # noqa: BLE001 - auto-evolution never blocks stop check
        print(f"team-workflow auto-evolve warning: {exc}", file=sys.stderr)


def decide(data):
    """Claude Code: {"decision": "block"}; agy: {"decision": "continue"}; None lets it stop."""
    again = data.get("stop_hook_active") or (data.get("executionNum") or 0) > 0  # agy counts from 0
    if again or os.environ.get("TEAM_WORKFLOW_STOP_CHECK") == "0":
        return None
    root = repo_root(data)
    state_rel = locate_state(root) if root else STATE
    state_full = os.path.join(root, state_rel) if root else ""
    config = settings.load(root) if root else {}
    if (not root or not os.path.isfile(state_full) or not config["stop_check"]
            or config["activation"] == "manual"):
        return None
    try:
        with open(snapshot_path(session_id(data)), encoding="utf-8") as f:
            snap = json.load(f)
    except (OSError, ValueError):
        snap = {}
    changed = changed_this_session(root, snap)
    work = [p for p in changed if not p.startswith(MEMORY_DIR + "/") and not p.startswith("docs/brain/")]
    if not work:
        return None
    import autolearn  # lazy, as in _auto_evolve_session
    failed = autolearn.check_violations(root, sorted(work))
    checks_mark = snapshot_path(session_id(data)) + ".checks"
    if failed and read_mark(checks_mark) != "\n".join(failed):  # once per set of failures, not every turn
        write_mark(checks_mark, "\n".join(failed))
        return {"decision": "continue" if is_agy(data) else "block",
                "reason": "team-workflow: changed files fail recorded checks: " + "; ".join(failed[:5])
                          + ". Fix the root cause before stopping."}
    times = change_times(root, work + [state_rel], snap.get("head"))
    newest = max((times[p] for p in work if p in times), default=0.0)
    fingerprint = f"{sorted(work)}|{newest}"
    # Once per state of the files: every turn would add a "pass" to the cortex and rewrite the brain.
    evolved = snapshot_path(session_id(data)) + ".evolved"
    if read_mark(evolved) != fingerprint:
        _auto_evolve_session(root, work)
        write_mark(evolved, fingerprint)
    if state_rel in changed and times.get(state_rel, 0.0) >= newest:
        return None
    # Ask once per state of the files, whatever the tool's own loop counter does.
    mark = snapshot_path(session_id(data)) + ".asked"
    if read_mark(mark) == fingerprint:
        return None
    write_mark(mark, fingerprint)
    return {"decision": "continue" if is_agy(data) else "block", "reason": REASON}


def main():
    verdict = decide(read_hook_input())
    if verdict:
        print(json.dumps(verdict))


if __name__ == "__main__":
    main()
