"""The session setup questions, ready for the app's question tool (`tw.py questions`).

The model used to pick which roles and skills to offer and dropped most of them; agy and
Claude Code also asked different things. These calls are the same in every app: every enabled
role, the library skills for the task, model and effort for every chosen role. Claude Code's
AskUserQuestion takes 2-4 options per question and 4 questions per call, so long lists are
split; the tool's free-text "Other" takes any role or library id not shown.
"""
import re

import cortex
import library
import roles

PER_QUESTION, PER_CALL = 4, 4
EFFORT_ORDER = ["none", "minimal", "low", "medium", "high", "xhigh", "max"]


def chunks(items, size=PER_QUESTION):
    """Groups of 2..size: a single leftover joins the group before it (the tool needs 2 options)."""
    groups = [items[i:i + size] for i in range(0, len(items), size)]
    if len(groups) > 1 and len(groups[-1]) == 1:
        groups[-2], groups[-1] = groups[-2][:-1], [groups[-2][-1], groups[-1][0]]
    return groups


def calls(questions):
    return [{"questions": questions[i:i + PER_CALL]} for i in range(0, len(questions), PER_CALL)]


def short(text, size=110):
    text = re.split(r"(?<=[.!?])\s", " ".join(str(text or "").split()), maxsplit=1)[0]
    return text if len(text) <= size else text[:size - 1].rstrip() + "…"


def role_text(role, root):
    try:
        meta, _ = roles.load(role, root)
    except (OSError, ValueError):
        return ""
    return re.sub(r"^Use this agent (to|when|for)\s+", "", short(meta.get("description", ""), 300))


def setup_calls(data, task_words, config, root):
    """Scope and preset, every enabled role, the skills for the task, add-ons and team talk."""
    out = [{"step": "scope and preset", "questions": [
        {"question": "Where do the choices of this setup go?", "header": "Scope", "multiSelect": False,
         "options": [{"label": "This conversation only", "description": "Nothing is saved (Recommended)"},
                     {"label": "My defaults", "description": f"User file {data['scope']['user_file']}"}]
         + ([{"label": "This project's defaults", "description": f"Project file {data['scope']['project_file']}"}]
            if data["scope"].get("project_file") else [])},
        {"question": "Which preset for the team?", "header": "Preset", "multiSelect": False,
         "options": [{"label": "Keep my settings", "description": "The models and efforts shown above (Recommended)"}]
         + [{"label": p, "description": f"tw.py profile {p}"} for p in data["presets"] if p != "balanced"][:3]}]}]
    texts = {r: role_text(r, root) for r in data["roles"]}
    task_text = " ".join(task_words or [])
    plan = cortex.route_and_orchestrate(task_text, root=root or ".", app=data.get("app", "claude")) if task_text.strip() else None
    activated = {n["role"] for n in (plan or {}).get("activated_neurons") or []}
    ranked = cortex.rank_roles_for_wizard(data, task_words, config, root=root or ".", plan=plan)
    groups = chunks(ranked)
    role_qs = [{"question": f"Which roles does this conversation use? ({i}/{len(groups)}, pick any, also none here)",
                "header": f"Roles {i}/{len(groups)}", "multiSelect": True,
                "options": [{"label": r, "description": ("[★ Cortex] " if r in activated else "")
                             + f"{data['roles'][r]['model']}/{data['roles'][r]['effort']}"
                             + (f" - {texts[r]}" if texts[r] else "")} for r in group]}
               for i, group in enumerate(groups, 1)]
    for c in calls(role_qs):
        out.append({"step": "roles", **c})
    found, langs = library.entries(), data["languages_here"]
    learned = cortex.load_learned_skills(root or ".")
    merged_skills = dict(found)
    for sid, linfo in learned.items():
        merged_skills.setdefault(sid, linfo)
    words = [w for w in re.findall(r"\w+", " ".join(task_words)) if len(w) >= 4]  # short words match anything
    chosen = list(learned)[:4] + [f"rules-{lang}" for lang in langs]
    chosen += [e["id"] for e in library.search(words + langs, limit=12)] if words or langs else []
    chosen += sorted(library.wanted(config)) + ["rules-common"]
    ids = [i for n, i in enumerate(chosen) if i in merged_skills and i not in chosen[:n]][:16]
    on = library.wanted(config)
    skill_groups = chunks(ids) if len(ids) >= 2 else []  # the tool needs 2 options
    skill_qs = [{"question": f"Which library skills do the agents get? ({i}/{len(skill_groups)}; all {len(merged_skills)} "
                             "entries are available by path, none needs installing; Other: any id from "
                             "`tw.py library search WORDS`)",
                 "header": f"Skills {i}/{len(skill_groups)}", "multiSelect": True,
                 "options": [{"label": s, "description": f"{merged_skills[s]['pack']}"
                              + (", installed" if s in on else "") + f" - {short(merged_skills[s]['description'], 90)}"}
                             for s in group]}
                for i, group in enumerate(skill_groups, 1)]
    for c in calls(skill_qs):
        out.append({"step": "skills", **c})
    bundles = [b for b in data["addons"]["bundles"] if not set(data["addons"]["bundles"][b]) <= set(data["addons"]["chosen"])]
    last = []
    if len(bundles) >= 2:
        last.append({"question": "Which add-on bundles to add? (installing downloads them; a restart loads them)",
                     "header": "Add-ons", "multiSelect": True,
                     "options": [{"label": b, "description": ", ".join(data["addons"]["bundles"][b])} for b in bundles[:4]]})
    last.append({"question": "Team talk between the agents (two or more roles)?", "header": "Team talk",
                 "multiSelect": False,
                 "options": [{"label": "Up to 3 rounds", "description": "Recommended"},
                             {"label": "1 round", "description": "Cheaper"},
                             {"label": "5 rounds", "description": "Hard problems"}]})
    out.append({"step": "add-ons and team talk", "questions": last})
    return out


def model_options(data, current):
    models = list(data["native"].get("models") or [])
    if data["app"] in ("opencode", "codex") and current not in models:
        models.insert(0, current)
    models = [current] + [m for m in models if m != current]
    return [{"label": f"{m} (current)" if m == current else m,
             "description": ("the session model " + data["native"]["session_model"]
                             if m == "inherit" and data["native"].get("session_model") else "native")}
            for m in models[:PER_QUESTION]]


def effort_options(data, model, current):
    """The model's efforts, the current first; agy: session effort or a worker id (its suffix)."""
    if data["app"] == "agy":
        session = data["native"].get("session_effort") or "-"
        family = re.sub(r"-(low|medium|high|xhigh)$", "", data["native"].get("session_model") or "")
        workers = [w for w in data["worker"]["models"] if family and w.startswith(family + "-")
                   and w != data["native"].get("session_model")]
        return [{"label": f"session effort {session} (current)", "description": "native, with any native model"}] + \
               [{"label": w, "description": "runs as a worker with this effort"} for w in workers[:PER_QUESTION - 1]]
    efforts = data["native"].get("efforts")
    efforts = efforts.get(model, []) if isinstance(efforts, dict) else efforts if isinstance(efforts, list) else []
    if not efforts:
        return []
    near = sorted((e for e in efforts if e != current),
                  key=lambda e: abs(EFFORT_ORDER.index(e) - EFFORT_ORDER.index(current))
                  if e in EFFORT_ORDER and current in EFFORT_ORDER else 0)
    shown = ([current] if current in efforts else []) + near[:PER_QUESTION - (current in efforts)]
    shown.sort(key=lambda e: EFFORT_ORDER.index(e) if e in EFFORT_ORDER else 0)
    return [{"label": f"{e} (current)" if e == current else e, "description": "for this role"} for e in shown]


def model_calls(data, chosen):
    """Model and effort of every chosen role, never merged: two roles per call."""
    qs = []
    for role in chosen:
        info = data["roles"].get(role)
        if not info:
            continue
        head = role[:12]
        qs.append({"question": f"Model for {role}?", "header": head, "multiSelect": False,
                   "options": model_options(data, info["model"])})
        effort = effort_options(data, info["model"], info["effort"])
        if len(effort) >= 2:
            hidden = [e for e in (data["native"].get("efforts") or {}).get(info["model"], [])
                      if e not in {o["label"].split(" ")[0] for o in effort}] \
                if isinstance(data["native"].get("efforts"), dict) else []
            qs.append({"question": f"Effort for {role}?" + (f" (Other: {', '.join(hidden)})" if hidden else ""),
                       "header": head, "multiSelect": False, "options": effort})
    return [{"step": "model and effort", **c} for c in calls(qs)]
