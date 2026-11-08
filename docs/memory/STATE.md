# Stato del Progetto

## Versione Corrente: v2.0.0-alpha.2 (Pre-release)

### 1. Comando Universale Semplificato `/team`
- Creato in `skills/team/SKILL.md` (e sincronizzato nella directory di configurazione utente): basta digitare `/team <compito>` o `/team upgrade`.
- Elimina la necessità di ricordare 25 comandi diversi: l'orchestratore capisce l'intento, interroga il Brain Graph, sceglie le skill e coordina gli agenti.

### 2. Live Execution & Smoke Test Gate (`tw.py smoke`) — Zero Fake-Solved
- Creato `skills/team-workflow/scripts/smoke.py`: esegue il processo reale per un intervallo controllato (es. 5-10s) con monitoraggio di exit code, stderr e stabilità di boot.
- Regola ferrea "Zero Fake-Solved" codificata in `rules/AGENTS.md`: nessun bug o funzione su app/giochi/UI può essere dichiarata risolta senza prova empirica di avvio reale.

### 3. Continuous Auto-Learning & Vaccini Preventivi (`tw.py learn`)
- Creato `skills/team-workflow/scripts/autolearn.py` collegato a `docs/brain/learnings/`.
- Registra gli anti-pattern identificati e inietta automaticamente "vaccini comportamentali" mirati nei prompt degli agenti a ogni avvio sessione (`session_start.py`).

### 4. Adversarial Gating Protocol (Builder ⚔️ Breaker)
- Creato `skills/team-workflow/scripts/gate.py`: separa categoricamente chi scrive il codice da chi lo valida, richiedendo controprove prima del merge.

### 5. Cybersecurity & Binary Reverse Engineering Ingestion
- **Strix Autonomous Pentesting** (`usestrix/strix`): 42 playbook di vulnerabilità e exploit verification (`strix-pentest`).
- **Cloudflare Security Audit** (`cloudflare/security-audit-skill`): 15 playbook di audit avanzato (`cloudflare-sec`), portando la libreria a **469 risorse**.
- **Specialisti dedicati**: `pentester` (CVSS, PoC, counter-evidence) e `reverse-engineer` (IDA Pro, Ghidra, x64dbg, Cutter, decompilazione MCP, analisi memoria e assembly).

### 6. WSL Bridge (Supporto Linux Nativo su Windows)
- Integrato supporto WSL in `skills/team-workflow/scripts/smoke.py` (`tw.py smoke "<cmd>" --wsl`) con mapping automatico dei percorsi Windows/WSL (`C:\...` -> `/mnt/c/...`).
- Codificato in `rules/AGENTS.md`, `skills/team/SKILL.md` e configurazione globale: su host Windows, WSL2 (Ubuntu Linux) è sempre attivo e disponibile per utility POSIX, test di rete, binari ELF e tool di sicurezza/reversing Linux.
- Aggiunto test `test_wsl_smoke_execution` in `tests/test_autolearn_gate_smoke.py`.

### 7. Brain Knowledge Graph & Compattazione Settimanale
- 155 nodi Markdown con frontmatter YAML e wikilink bidirezionali compatibili Obsidian (`docs/brain/`).
- `tw.py brain rollover`: compattazione e archiviazione dello stato delle settimane passate in journal dedicati (`docs/brain/journal/week-YYYY-WXX.md`), garantendo supporto per sessioni di settimane/mesi senza saturare il contesto.

### 8. Aggiornamenti a Zero Token & Notifiche
- All'avvio di ogni sessione, verifica non invasiva di nuovi rilasci.
- Comando `/team upgrade` (o `tw.py upgrade`) per allineare file e cataloghi a costo zero token senza passare da inferenze LLM.

### 9. Documentazione Bilingue & Cataloghi
- `README.md` (Italiano) e `README.en.md` (Inglese) con toggle linguistico in cima: `[English](README.en.md) | [Italiano](README.md)`.
- Catalogo completo aggiornato in `docs/CATALOG.md` (129 agenti, 469 skill).
- Versione sincronizzata a `2.0.0-alpha.2` in `plugin.json` e `.claude-plugin/plugin.json`.
- Suite di test: 100 passati, 2 saltati, 0 errori. Strict brain check: 0 problemi.
