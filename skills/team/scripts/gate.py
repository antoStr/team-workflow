#!/usr/bin/env python3
"""Adversarial Gating Protocol (Builder ⚔️ Breaker) for team-workflow.

Enforces strict verification where code written by a Builder role (e.g. backend-dev)
must survive attack attempts by an adversarial Breaker role (e.g. pentester, tester,
or performance-engineer) before it can pass the gate into main/production.

When a flaw is proven via PoC, the gate BLOCKS until fixed, and the lesson is
automatically fed into autolearn.py so the team never repeats the mistake.
"""
from datetime import datetime, timezone
import json
import os
import re
import sys

VAULT_DIR = "docs/brain"
GATES_DIR = os.path.join(VAULT_DIR, "gates")


def _ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def _slug(text):
    clean = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return clean[:40] or "gate"


def gates_path(root="."):
    return os.path.join(root, GATES_DIR)


GATE_ID_PATTERN = re.compile(r"^gate-[a-z0-9_-]{1,80}$")


def _validate_gate_id(gate_id):
    if not gate_id or not GATE_ID_PATTERN.match(gate_id):
        raise ValueError(f"Invalid gate id: {gate_id!r} (must match 'gate-[a-z0-9_-]+')")


def load_gate(gate_id, root="."):
    _validate_gate_id(gate_id)
    gp = os.path.join(gates_path(root), f"{gate_id}.json")
    if os.path.isfile(gp):
        try:
            with open(gp, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            pass
    return None


def save_gate(gate, root="."):
    _validate_gate_id(gate.get("id"))
    gp = gates_path(root)
    _ensure_dir(gp)
    path = os.path.join(gp, f"{gate['id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(gate, f, indent=2, ensure_ascii=False)


def create_gate(
    root=".",
    target="",
    builder="backend-dev",
    breaker="pentester",
    topic="",
    hypothesis=""
):
    """Create a new Adversarial Verification Gate."""
    if not target:
        raise ValueError("Gate requires a target file or feature description.")

    now_iso = datetime.now(timezone.utc).isoformat()
    gid = f"gate-{_slug(target)}-{int(datetime.now().timestamp()) % 10000}"

    gate = {
        "id": gid,
        "target": target,
        "builder": builder,
        "breaker": breaker,
        "topic": topic or "general",
        "status": "PENDING_BREAKER",
        "hypothesis": hypothesis or f"Breaker {breaker} must attempt to exploit/break changes in {target}",
        "poc": None,
        "evidence": None,
        "blocks_count": 0,
        "created_at": now_iso,
        "updated_at": now_iso
    }

    save_gate(gate, root)

    # If talk is available and topic provided, notify channel
    if topic:
        try:
            import talk
            talk.post(
                topic=topic,
                sender="orchestrator",
                text=f"Adversarial Gate [{gid}] OPEN on target '{target}'. Builder: {builder}. "
                     f"Breaker ({breaker}), attempt to find exploit/failing edge case with working PoC.",
                kind="question",
                to=breaker,
                cwd=root
            )
        except Exception:
            pass

    return gate


def block_gate(root=".", gate_id="", poc="", challenger=None):
    """Mark a gate as BLOCKED by a successful breaker exploit/test PoC."""
    gate = load_gate(gate_id, root)
    if not gate:
        raise ValueError(f"Gate {gate_id} not found.")

    now_iso = datetime.now(timezone.utc).isoformat()
    gate["status"] = "BLOCKED"
    gate["poc"] = poc
    gate["blocks_count"] = gate.get("blocks_count", 0) + 1
    gate["updated_at"] = now_iso

    save_gate(gate, root)

    topic = gate.get("topic")
    if topic:
        try:
            import talk
            talk.post(
                topic=topic,
                sender=challenger or gate["breaker"],
                text=f"Gate [{gate_id}] BLOCKED on '{gate['target']}'. PoC found:\n{poc}\n"
                     f"Builder ({gate['builder']}), patch this flaw with verification.",
                kind="challenge",
                to=gate["builder"],
                cwd=root
            )
        except Exception:
            pass

    return gate


def pass_gate(root=".", gate_id="", evidence="", verifier=None):
    """Mark a gate as PASSED after verifying counter-evidence or patch."""
    gate = load_gate(gate_id, root)
    if not gate:
        raise ValueError(f"Gate {gate_id} not found.")

    now_iso = datetime.now(timezone.utc).isoformat()
    was_blocked = (gate["status"] == "BLOCKED" or gate.get("blocks_count", 0) > 0)
    gate["status"] = "PASSED"
    gate["evidence"] = evidence
    gate["updated_at"] = now_iso

    save_gate(gate, root)

    # If it was blocked and now resolved, automatically record a learning!
    if was_blocked:
        try:
            import autolearn
            autolearn.record_learning(
                root=root,
                title=f"Gate Fix: {gate['target']}",
                trigger=f"Breaker {gate['breaker']} blocked gate with PoC: {gate.get('poc', '')[:100]}",
                anti_pattern=gate.get("poc", "Unchecked boundary condition or vulnerability"),
                solution=evidence or "Applied verified patch with counter-evidence validation",
                applies_to=[gate["builder"], gate["target"]],
                category="bug" if "test" in gate["breaker"] else "security",
                source=f"gate:{gate_id}"
            )
        except Exception:
            pass

    topic = gate.get("topic")
    if topic:
        try:
            import talk
            talk.post(
                topic=topic,
                sender=verifier or gate["breaker"],
                text=f"Gate [{gate_id}] PASSED on '{gate['target']}'. Evidence: {evidence or 'Verified clean.'}",
                kind="decision",
                to=None,
                cwd=root
            )
        except Exception:
            pass

    return gate


def list_gates(root=".", topic=None):
    gp = gates_path(root)
    if not os.path.isdir(gp):
        return []
    gates = []
    for f in os.listdir(gp):
        if f.endswith(".json"):
            gate = load_gate(os.path.splitext(f)[0], root)
            if gate:
                if not topic or gate.get("topic") == topic:
                    gates.append(gate)
    gates.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return gates


def active_blocking_gates(root=".", topic=None):
    all_gates = list_gates(root, topic)
    return [g for g in all_gates if g.get("status") in ("PENDING_BREAKER", "BLOCKED")]
