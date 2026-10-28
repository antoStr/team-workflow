#!/usr/bin/env python3
"""Write docs/CATALOG.md: every agent (role) by pack and every library entry (skills, commands,
rules) by pack, from the plugin's own files, so the documentation never drifts from what ships.

    python3 tools/readme_catalog.py          rewrite docs/CATALOG.md
    python3 tools/readme_catalog.py --check  exit 1 when it is out of date (the tests run it)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(ROOT, "skills", "team-workflow", "scripts"))
import library  # noqa: E402
import roles  # noqa: E402

CATALOG = os.path.join(ROOT, "docs", "CATALOG.md")
# Italian one-liners for people; the agents' own instructions stay in English.
ITALIAN = os.path.join(ROOT, "docs", "catalog.it.json")


def italian():
    with open(ITALIAN, encoding="utf-8") as f:
        return json.load(f)


def it_text(table, key, it):
    """The Italian description; a missing one stops the build, so none slips through."""
    if key not in it[table]:
        raise SystemExit(f"docs/catalog.it.json: no Italian description for {table} {key!r}")
    return it[table][key].replace("|", "\\|")
PACK_ORDER = ("core", "frameworks", "quality", "planning", "ml", "harness", "gan", "opensource",
              "network", "domains", "ops", "growth", "alt")


def version():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as f:
        return json.load(f)["version"]


def agent_it(role, meta, it):
    alt = re.match(r"Alternative version of the ([\w-]+) role", meta.get("description", ""))
    if role.startswith("alt-") and alt:
        return f"Versione alternativa del ruolo `{alt.group(1)}`, per una seconda opinione."
    return it_text("agents", role, it)


def agents_block():
    it = italian()
    catalog = roles.catalog()
    packs = {}
    for role, info in catalog.items():
        packs.setdefault(info["pack"], []).append(role)
    languages = sorted(p for p in packs if p in roles.languages())
    order = [p for p in PACK_ORDER if p in packs] + sorted(
        p for p in packs if p not in PACK_ORDER and p not in languages)
    lang_count = sum(len(packs[p]) for p in languages)
    out = ["## Tutti gli agenti", "",
           f"**{len(catalog)} agenti**: {len(packs['core'])} nel core, {len(catalog) - len(packs['core']) - lang_count} negli altri "
           f"pack, {lang_count} nei pack dei linguaggi; il pack `alt` raccoglie versioni alternative "
           "di ruoli che esistono gia' (`alt-<nome>`). Accendi un pack con "
           "`/team-workflow:agents enable <pack>` (il core e' sempre acceso).", ""]
    for pack in order:
        out += [f"<details><summary><b>{pack}</b> ({len(packs[pack])})</summary>", "",
                "| Agente | Cosa fa |", "|---|---|"]
        for role in sorted(packs[pack]):
            meta, _ = roles.parse(roles.read(catalog[role]))
            out.append(f"| `{role}` | {agent_it(role, meta, it)} |")
        out += ["", "</details>", ""]
    out += [f"<details><summary><b>linguaggi</b> ({len(languages)} pack, {lang_count} agenti)</summary>", "",
            "| Agente | Pack | Cosa fa |", "|---|---|---|"]
    for slug in languages:
        meta, _ = roles.languages()[slug]
        name = meta.get("language", slug)
        out.append(f"| `{slug}-reviewer` | `{slug}` | Rivede il codice {name}: correttezza, sicurezza e "
                   "idiomi del linguaggio, con i suoi strumenti. |")
        out.append(f"| `{slug}-build-fixer` | `{slug}` | Ripara build, type check e dipendenze {name} "
                   "con la modifica più piccola. |")
    return out + ["", "</details>", ""]


def library_it(e, it):
    if e["kind"] == "rule":
        lang = e["id"][len("rules-"):]
        return ("Regole comuni a tutti i linguaggi: stile, pattern, sicurezza, test." if lang == "common"
                else f"Regole di stile per {lang}: stile, pattern, sicurezza, test.")
    return it_text("library", e["id"], it)


def library_block():
    it = italian()
    data, found = library.index(), library.entries()
    kinds = {k: sum(e["kind"] == k for e in found.values()) for k in ("skill", "command", "rule")}
    out = ["## Tutta la libreria", "",
           f"**{len(found)} voci**: {kinds['skill']} skill, {kinds['command']} comandi, "
           f"{kinds['rule']} set di regole. Licenza MIT (`skills/team-workflow/library/NOTICE.md`). Cerca con "
           "`/team-workflow:library search <parole>`, installa con `library enable <id|pack>`.", ""]
    for pack, about in data["packs"].items():
        mine = sorted((e for e in found.values() if e["pack"] == pack), key=lambda e: e["id"])
        out += [f"<details><summary><b>{pack}</b> ({len(mine)}): {it_text('packs', pack, it)}</summary>", "",
                "| Voce | Tipo | Cosa fa |", "|---|---|---|"]
        for e in mine:
            kind = {"skill": "skill", "command": "comando", "rule": "regole"}[e["kind"]]
            out.append(f"| `{e['id']}` | {kind} | {library_it(e, it)} |")
        out += ["", "</details>", ""]
    return out


def render():
    lines = [f"# Catalogo completo (versione {version()})", "",
             "<!-- generated by tools/readme_catalog.py: do not edit by hand -->", "",
             "Tutti gli agenti e tutta la libreria di team-workflow. Per iniziare leggi il "
             "[README](../README.md); per usare, cambiare o creare agenti la "
             "[guida agli agenti](AGENTS.md); i dettagli sono nel [manuale](REFERENCE.md).", "",
             "> [!TIP]",
             "> **Come usare un agente di questa pagina:** chiedilo per nome (\"fai controllare al "
             "tester\"), oppure `/team-workflow:call-team <compito>`. Se e' in un pack spento, "
             "accendilo prima: `/team-workflow:agents enable <pack>`. Le sue istruzioni complete: "
             "`/team-workflow:agents show <agente>`. Una voce della libreria: "
             "`/team-workflow:library show <voce>`.", "",
             "- [Tutti gli agenti](#tutti-gli-agenti)", "- [Tutta la libreria](#tutta-la-libreria)", ""]
    lines += agents_block() + library_block()
    return "\n".join(lines).rstrip() + "\n"


def main(argv):
    try:
        with open(CATALOG, encoding="utf-8") as f:
            text = f.read()
    except OSError:
        text = ""
    new = render()
    if "--check" in argv:
        if new != text:
            raise SystemExit("docs/CATALOG.md is out of date: python3 tools/readme_catalog.py")
        return
    os.makedirs(os.path.dirname(CATALOG), exist_ok=True)
    with open(CATALOG, "w", encoding="utf-8", newline="\n") as f:
        f.write(new)
    print("docs/CATALOG.md written")


if __name__ == "__main__":
    main(sys.argv[1:])
