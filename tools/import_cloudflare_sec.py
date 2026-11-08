#!/usr/bin/env python3
"""Import Cloudflare security audit skills, binary analysis and vulnerability hunting playbooks into team-workflow library."""
import hashlib
import json
import os
import re

CLOUDFLARE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "cloudflare_sec_skill", "skills", "security-audit"))
LIBRARY_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "skills", "team-workflow", "library"))
INDEX_FILE = os.path.join(LIBRARY_DIR, "index.json")
CATALOG_IT = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "docs", "catalog.it.json"))


def _hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _slug(name):
    clean = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return clean


MD_MAP = {
    "SKILL.md": ("cloudflare-security-audit", "Comprehensive multi-phase security audit methodology: reconnaissance, hunting, validation and reporting."),
    "MEMORY-SAFETY-AND-BINARY.md": ("cloudflare-sec-memory-safety-binary", "Memory safety, binary reverse engineering, buffer overflows, and native vulnerability hunting."),
    "AI-AND-LLM.md": ("cloudflare-sec-ai-and-llm", "Security auditing for LLM and agentic systems, prompt injection, tool abuse, and data leakage."),
    "ATTACK-CLASSES.md": ("cloudflare-sec-attack-classes", "Taxonomy of core web, protocol, logic, and infrastructure attack classes for systematic audits."),
    "CLIENT-SIDE.md": ("cloudflare-sec-client-side", "Client-side vulnerability hunting: DOM injection, messaging trust, UI redress, and prototype pollution."),
    "CLOUD-AND-DEPLOYMENT.md": ("cloudflare-sec-cloud-and-deployment", "Cloud security audit: IAM, infrastructure-as-code, containers, serverless ingress, and misconfigurations."),
    "DATA-ISOLATION-AND-LIFECYCLE.md": ("cloudflare-sec-data-isolation-lifecycle", "Multi-tenant data isolation, cache leaks, search index boundaries, and data lifecycle auditing."),
    "DESKTOP-MOBILE-AND-LOCAL-IPC.md": ("cloudflare-sec-desktop-mobile-ipc", "Desktop, mobile and local IPC security: deep-links, webviews, exported components, and daemons."),
    "HUNTING.md": ("cloudflare-sec-hunting", "Coverage-led vulnerability hunting methodology, hypothesis generation, and candidate validation."),
    "PROTOCOLS-RPC-AND-MESSAGING.md": ("cloudflare-sec-protocols-rpc-messaging", "RPC, serialization, queue brokers, webhooks, and streaming protocol security testing."),
    "RECONNAISSANCE.md": ("cloudflare-sec-reconnaissance", "Systematic reconnaissance, architecture mapping, trust boundary discovery, and input surface analysis."),
    "RESOURCE-EXHAUSTION-AND-AVAILABILITY.md": ("cloudflare-sec-resource-exhaustion", "Denial-of-service, algorithmic complexity, queue worker starvation, and operator-spend exhaustion."),
    "SUPPLY-CHAIN-AND-RELEASE.md": ("cloudflare-sec-supply-chain-release", "Software supply chain security: dependency pinning, build pipeline integrity, signing, and extensions."),
    "VALIDATION-AND-REPORTING.md": ("cloudflare-sec-validation-reporting", "Candidate validation discipline, falsification criteria, and structured security reporting."),
    "WEB-PROTOCOL-AND-AUTH.md": ("cloudflare-sec-web-protocol-auth", "HTTP request framing, cache poisoning, session hijacking, and authentication protocol testing.")
}

IT_DESC = {
    "cloudflare-security-audit": "Metodologia completa di audit di sicurezza a 6 fasi: ricognizione, caccia a copertura, validazione e report.",
    "cloudflare-sec-memory-safety-binary": "Sicurezza della memoria, reverse engineering di binari, buffer overflow e analisi di codice nativo.",
    "cloudflare-sec-ai-and-llm": "Audit di sicurezza per sistemi LLM e agenti: prompt injection, abuso di tool ed esfiltrazione.",
    "cloudflare-sec-attack-classes": "Tassonomia delle classi di attacco web, logica di business e infrastruttura per audit sistematici.",
    "cloudflare-sec-client-side": "Vulnerabilità client-side: iniezione DOM, postMessage, UI redressing e inquinamento del prototipo.",
    "cloudflare-sec-cloud-and-deployment": "Audit cloud: policy IAM, infrastruttura come codice, container, serverless e ingress.",
    "cloudflare-sec-data-isolation-lifecycle": "Isolamento dati multi-tenant, leak nella cache, confini di ricerca e ciclo di vita dei dati.",
    "cloudflare-sec-desktop-mobile-ipc": "Sicurezza app desktop e mobile: deep-link, webview, IPC locale e daemon di sistema.",
    "cloudflare-sec-hunting": "Metodologia di caccia alle vulnerabilità guidata da copertura, ipotesi e validazione.",
    "cloudflare-sec-protocols-rpc-messaging": "Sicurezza di protocolli RPC, serializzazione, code di messaggi, broker e webhook.",
    "cloudflare-sec-reconnaissance": "Ricognizione sistematica: mappatura dell'architettura, confini di fiducia e superfici di input.",
    "cloudflare-sec-resource-exhaustion": "Attacchi di esaurimento risorse (DoS), complessità algoritmica e saturazione worker.",
    "cloudflare-sec-supply-chain-release": "Sicurezza della supply chain: dipendenze, pipeline CI, firma digitale e integrità del rilascio.",
    "cloudflare-sec-validation-reporting": "Disciplina di validazione dei candidati, falsificazione e reportistica strutturata di sicurezza.",
    "cloudflare-sec-web-protocol-auth": "Framing HTTP, cache poisoning, hijacking di sessione e protocolli di autenticazione."
}


def main():
    if not os.path.isdir(CLOUDFLARE_DIR):
        raise SystemExit(f"Directory not found: {CLOUDFLARE_DIR}")

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog["packs"]["cloudflare-sec"] = (
        "Enterprise vulnerability discovery, coverage-led hunting, binary analysis, and security auditing from Cloudflare."
    )

    existing_ids = {e["id"] for e in catalog["entries"]}
    imported_count = 0

    for fname, (entry_id, desc) in MD_MAP.items():
        src_path = os.path.join(CLOUDFLARE_DIR, fname)
        if not os.path.isfile(src_path):
            continue

        with open(src_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        target_dir = os.path.join(LIBRARY_DIR, entry_id)
        os.makedirs(target_dir, exist_ok=True)
        main_file = os.path.join(target_dir, "MAIN.md")

        header = (
            f"<!-- Imported from cloudflare/security-audit-skill (BSD-3-Clause) -->\n"
            f"# Cloudflare Security Audit: {fname.replace('.md', '')}\n\n"
        )
        with open(main_file, "w", encoding="utf-8") as f:
            f.write(header + content)

        found = False
        for e in catalog["entries"]:
            if e["id"] == entry_id:
                e["description"] = desc
                e["hash"] = _hash(header + content)
                found = True
                break
        if not found:
            catalog["entries"].append({
                "id": entry_id,
                "kind": "skill",
                "pack": "cloudflare-sec",
                "description": desc,
                "hash": _hash(header + content)
            })
            existing_ids.add(entry_id)
        imported_count += 1

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)

    # Update docs/catalog.it.json
    with open(CATALOG_IT, "r", encoding="utf-8") as f:
        it = json.load(f)

    it["packs"]["cloudflare-sec"] = "Audit di sicurezza enterprise, caccia alle vulnerabilità guidata da copertura e analisi binaria di Cloudflare."
    it["library"].update(IT_DESC)

    with open(CATALOG_IT, "w", encoding="utf-8") as f:
        json.dump(it, f, indent=1, ensure_ascii=False)

    print(f"Imported {imported_count} Cloudflare security audit skills into pack 'cloudflare-sec'.")
    print(f"Total entries in library index: {len(catalog['entries'])}")


if __name__ == "__main__":
    main()
