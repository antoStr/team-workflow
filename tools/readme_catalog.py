#!/usr/bin/env python3
"""Write docs/CATALOG.md (English) and docs/CATALOG.it.md (Italian): every agent (role) by pack
and every library entry (skills, commands, rules) by pack, from the plugin's own files, so the
documentation never drifts from what ships.

    python3 tools/readme_catalog.py          rewrite both catalogs
    python3 tools/readme_catalog.py --check  exit 1 when one is out of date (the tests run it)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
scripts_dir = os.path.join(ROOT, "skills", "team", "scripts")
if not os.path.isdir(scripts_dir):
    scripts_dir = os.path.join(ROOT, "skills", "team-workflow", "scripts")
sys.path.insert(0, scripts_dir)
import library  # noqa: E402
import roles  # noqa: E402

CATALOG = {"en": os.path.join(ROOT, "docs", "CATALOG.md"), "it": os.path.join(ROOT, "docs", "CATALOG.it.md")}
# Italian one-liners for people; the English ones come from the agents' and entries' own descriptions.
ITALIAN = os.path.join(ROOT, "docs", "catalog.it.json")
PACK_ORDER = ("core", "frameworks", "quality", "planning", "pm", "ml", "harness", "gan", "opensource",
              "network", "domains", "ops", "growth", "alt")

TEXT = {
    "en": dict(
        title="Full catalog (version {v})",
        intro="Every agent and the whole library of team. To get started read the [README](../README.md); "
              "to use, change or create agents the [agent guide](AGENTS.md); details are in the "
              "[reference manual](REFERENCE.md). [Versione italiana](CATALOG.it.md).",
        tip="> **How to use an agent from this page:** ask for it by name (\"have the tester check "
            "it\"), or `/team:call-team <task>`. When its pack is off, switch it on first: "
            "`/team:agents enable <pack>`. Its full instructions: `/team:agents show <agent>`. A "
            "library entry: `/team:library show <entry>`.",
        agents="All agents", library="The whole library",
        agents_intro="**{n} agents**: {core} in the core, {other} in the other packs, {lang} in the language "
                     "packs; the `alt` pack holds alternative versions of existing roles (`alt-<name>`). "
                     "Switch a pack on with `/team:agents enable <pack>` (the core is always on).",
        agent_cols="| Agent | What it does |", lang_cols="| Agent | Pack | What it does |",
        languages="languages", lang_summary="{p} packs, {n} agents",
        reviewer="Reviews {name} code: correctness, safety and language idiom, with its own tools.",
        fixer="Fixes {name} builds, type checks and dependencies with the smallest change.",
        alt="Alternative version of the `{role}` role, for a second opinion.",
        library_intro="**{n} entries**: {s} skills, {c} commands, {r} rule sets. MIT license "
                      "(`skills/team/library/NOTICE.md`). Search with `/team:library search <words>`, "
                      "install with `library enable <id|pack>`.",
        entry_cols="| Entry | Type | What it does |",
        kinds={"skill": "skill", "command": "command", "rule": "rules"},
        rules_common="Rules shared by every language: style, patterns, security, testing.",
        rules_lang="Rules for {lang}: style, patterns, security, testing."),
    "it": dict(
        title="Catalogo completo (versione {v})",
        intro="Tutti gli agenti e tutta la libreria di team. Per iniziare leggi il "
              "[README](../README.it.md); per usare, cambiare o creare agenti la "
              "[guida agli agenti](AGENTS.it.md); i dettagli sono nel [manuale](REFERENCE.it.md). "
              "[English version](CATALOG.md).",
        tip="> **Come usare un agente di questa pagina:** chiedilo per nome (\"fai controllare al "
            "tester\"), oppure `/team:call-team <compito>`. Se è in un pack spento, accendilo prima: "
            "`/team:agents enable <pack>`. Le sue istruzioni complete: `/team:agents show <agente>`. "
            "Una voce della libreria: `/team:library show <voce>`.",
        agents="Tutti gli agenti", library="Tutta la libreria",
        agents_intro="**{n} agenti**: {core} nel core, {other} negli altri pack, {lang} nei pack dei "
                     "linguaggi; il pack `alt` raccoglie versioni alternative di ruoli che esistono già "
                     "(`alt-<nome>`). Accendi un pack con `/team:agents enable <pack>` (il core è sempre "
                     "acceso).",
        agent_cols="| Agente | Cosa fa |", lang_cols="| Agente | Pack | Cosa fa |",
        languages="linguaggi", lang_summary="{p} pack, {n} agenti",
        reviewer="Rivede il codice {name}: correttezza, sicurezza e idiomi del linguaggio, con i suoi strumenti.",
        fixer="Ripara build, type check e dipendenze {name} con la modifica più piccola.",
        alt="Versione alternativa del ruolo `{role}`, per una seconda opinione.",
        library_intro="**{n} voci**: {s} skill, {c} comandi, {r} set di regole. Licenza MIT "
                      "(`skills/team/library/NOTICE.md`). Cerca con `/team:library search <parole>`, "
                      "installa con `library enable <id|pack>`.",
        entry_cols="| Voce | Tipo | Cosa fa |",
        kinds={"skill": "skill", "command": "comando", "rule": "regole"},
        rules_common="Regole comuni a tutti i linguaggi: stile, pattern, sicurezza, test.",
        rules_lang="Regole di stile per {lang}: stile, pattern, sicurezza, test."),
}


def italian():
    with open(ITALIAN, encoding="utf-8") as f:
        return json.load(f)


def it_text(table, key, it):
    """The Italian description; a missing one stops the build, so none slips through."""
    if key not in it[table]:
        raise SystemExit(f"docs/catalog.it.json: no Italian description for {table} {key!r}")
    return it[table][key].replace("|", "\\|")


def first_sentence(text):
    """The summary of an English description: up to its first colon or full stop."""
    text = " ".join(text.split())
    cut = min([i for i in (text.find(": "), text.find(". ")) if i > 0] or [len(text)])
    return (text[:cut].rstrip(".") + ".").replace("|", "\\|")


def text_for(table, key, english, it, lang):
    return first_sentence(english) if lang == "en" else it_text(table, key, it)


def version():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def agent_text(role, meta, it, lang):
    alt = re.match(r"Alternative version of the ([\w-]+) role", meta.get("description", ""))
    if role.startswith("alt-") and alt:
        return TEXT[lang]["alt"].format(role=alt.group(1))
    return text_for("agents", role, meta.get("description", ""), it, lang)


def agents_block(lang, it):
    T = TEXT[lang]
    catalog = roles.catalog()
    packs = {}
    for role, info in catalog.items():
        packs.setdefault(info["pack"], []).append(role)
    languages = sorted(p for p in packs if p in roles.languages())
    order = [p for p in PACK_ORDER if p in packs] + sorted(
        p for p in packs if p not in PACK_ORDER and p not in languages)
    lang_count = sum(len(packs[p]) for p in languages)
    out = [f"## {T['agents']}", "",
           T["agents_intro"].format(n=len(catalog), core=len(packs["core"]),
                                    other=len(catalog) - len(packs["core"]) - lang_count, lang=lang_count), ""]
    for pack in order:
        out += [f"<details><summary><b>{pack}</b> ({len(packs[pack])})</summary>", "",
                T["agent_cols"], "|---|---|"]
        for role in sorted(packs[pack]):
            meta, _ = roles.parse(roles.read(catalog[role]))
            out.append(f"| `{role}` | {agent_text(role, meta, it, lang)} |")
        out += ["", "</details>", ""]
    out += [f"<details><summary><b>{T['languages']}</b> "
            f"({T['lang_summary'].format(p=len(languages), n=lang_count)})</summary>", "",
            T["lang_cols"], "|---|---|---|"]
    for slug in languages:
        meta, _ = roles.languages()[slug]
        name = meta.get("language", slug)
        out.append(f"| `{slug}-reviewer` | `{slug}` | {T['reviewer'].format(name=name)} |")
        out.append(f"| `{slug}-build-fixer` | `{slug}` | {T['fixer'].format(name=name)} |")
    return out + ["", "</details>", ""]


def library_text(e, it, lang):
    if e["kind"] == "rule":
        rules = e["id"][len("rules-"):]
        return TEXT[lang]["rules_common"] if rules == "common" else TEXT[lang]["rules_lang"].format(lang=rules)
    return text_for("library", e["id"], e.get("description", ""), it, lang)


def library_block(lang, it):
    T = TEXT[lang]
    data, found = library.index(), library.entries()
    kinds = {k: sum(e["kind"] == k for e in found.values()) for k in ("skill", "command", "rule")}
    out = [f"## {T['library']}", "",
           T["library_intro"].format(n=len(found), s=kinds["skill"], c=kinds["command"], r=kinds["rule"]), ""]
    for pack, about in data["packs"].items():
        mine = sorted((e for e in found.values() if e["pack"] == pack), key=lambda e: e["id"])
        summary = text_for("packs", pack, about, it, lang)
        out += [f"<details><summary><b>{pack}</b> ({len(mine)}): {summary}</summary>", "",
                T["entry_cols"], "|---|---|---|"]
        for e in mine:
            out.append(f"| `{e['id']}` | {T['kinds'][e['kind']]} | {library_text(e, it, lang)} |")
        out += ["", "</details>", ""]
    return out


def anchor(title):
    return re.sub(r"[^\w\- ]", "", title.lower()).replace(" ", "-")


def render(lang="en"):
    T, it = TEXT[lang], italian()
    lines = [f"# {T['title'].format(v=version())}", "",
             "<!-- generated by tools/readme_catalog.py: do not edit by hand -->", "",
             T["intro"], "", "> [!TIP]", T["tip"], "",
             f"- [{T['agents']}](#{anchor(T['agents'])})", f"- [{T['library']}](#{anchor(T['library'])})", ""]
    lines += agents_block(lang, it) + library_block(lang, it)
    return "\n".join(lines).rstrip() + "\n"


def main(argv):
    stale = []
    for lang, path in CATALOG.items():
        try:
            with open(path, encoding="utf-8") as f:
                text = f.read()
        except OSError:
            text = ""
        new = render(lang)
        if "--check" in argv:
            if new != text:
                stale.append(os.path.relpath(path, ROOT).replace(os.sep, "/"))
            continue
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(new)
        print(f"{os.path.relpath(path, ROOT)} written")
    if stale:
        raise SystemExit(f"{', '.join(stale)} out of date: python3 tools/readme_catalog.py")


if __name__ == "__main__":
    main(sys.argv[1:])
