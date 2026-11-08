# Stato del Progetto

## Versione Corrente: v2.1.3 (Release Ufficiale)

### 1. Suite Malware Analysis & URL Threat Intelligence
- **43 nuove skill specializzate di sicurezza avanzata**:
  - `malware-analysis` (35 skill): triage binari (PE, ELF), payload deobfuscation, memory forensics, C2 protocol decoding, YARA e Sigma rule development, STIX 2.1 threat reporting, MITRE ATT&CK mapping, e tassonomie per APT, botnet, ransomware, wiper, rootkit, infostealer, RAT, macro/document payload e fileless memory malware.
  - `threat-intel-url` (8 skill): scansione e audit interattivo con URLScan.io API, analisi header email phishing (SPF, DKIM, DMARC), certificate transparency log hunting, C2 domain fronting detection, adversary infrastructure tracking, Zeek network analysis, TShark packet extraction e HTTP request proxy audit.
- **Nuovo ruolo specialista**: `malware-analyst` (`skills/team-workflow/roles/quality/malware-analyst.md`).
- **Totale libreria**: **512 voci di libreria** (396 skill, 94 comandi, 22 set di regole).
- **Totale agenti**: **130 specialisti** con catalogo e traduzioni bilingue sincronizzati.

### 2. Rinominazione Completa in `team` e Comandi `/team` & `/team:<comando>`
- Il plugin è stato rinominato ufficialmente in `team` (in `plugin.json` e `.claude-plugin/plugin.json`).
- Consolidamento: `skills/team-workflow` è stato unificato e fuso interamente in `skills/team/`, eliminando del tutto ogni riferimento e comando obsoleto con nome `team-workflow`.
- Tutte le 24 skill specialistiche sono attive in `skills/` e namespaciate nativamente sotto `/team:<comando>` in Antigravity (`agy`), ad esempio `/team:doctor`, `/team:audit`, `/team:fix-bug`, `/team:settings`, `/team:update-plugin`.
- Il comando universale `/team` è disponibile come skill di primo livello in `~/.gemini/config/skills/team/SKILL.md`.
- Zero duplicati e zero comandi con prefisso `team-workflow` residui nell'autocompletamento di agy.
- Router di fallback zero-token in `prompt_command.py` e in `tw.py` per gestire con compatibilità totale qualsiasi digitazione di comandi (`tw doctor`, `team doctor`, `/team doctor`, ecc.).

### 3. Live Execution & Smoke Test Gate (`tw.py smoke`) — Zero Fake-Solved
- Creato `skills/team-workflow/scripts/smoke.py`: esegue il processo reale per un intervallo controllato (es. 5-10s) con monitoraggio di exit code, stderr e stabilità di boot.
- Regola ferrea "Zero Fake-Solved" codificata in `rules/AGENTS.md`: nessun bug o funzione su app/giochi/UI può essere dichiarata risolta senza prova empirica di avvio reale.

### 4. Continuous Auto-Learning & Vaccini Preventivi (`tw.py learn`)
- Creato `skills/team-workflow/scripts/autolearn.py` collegato a `docs/brain/learnings/`.
- Registra gli anti-pattern identificati e inietta automaticamente "vaccini comportamentali" mirati nei prompt degli agenti a ogni avvio sessione (`session_start.py`).

### 5. Adversarial Gating Protocol (Builder ⚔️ Breaker)
- Creato `skills/team-workflow/scripts/gate.py`: separa categoricamente chi scrive il codice da chi lo valida, richiedendo controprove prima del merge.

### 6. Cybersecurity & Binary Reverse Engineering Ingestion
- **Strix Autonomous Pentesting** (`usestrix/strix`): 42 playbook di vulnerabilità e exploit verification (`strix-pentest`).
- **Cloudflare Security Audit** (`cloudflare/security-audit-skill`): 15 playbook di audit avanzato (`cloudflare-sec`).
- **Specialisti dedicati**: `pentester` (CVSS, PoC, counter-evidence), `reverse-engineer` (IDA Pro, Ghidra, x64dbg, Cutter, decompilazione MCP) e `malware-analyst`.

### 7. WSL Bridge (Supporto Linux Nativo su Windows)
- Integrato supporto WSL in `skills/team-workflow/scripts/smoke.py` (`tw.py smoke "<cmd>" --wsl`) con mapping automatico dei percorsi Windows/WSL (`C:\...` -> `/mnt/c/...`).
- Codificato in `rules/AGENTS.md`, `skills/team/SKILL.md` e configurazione globale: su host Windows, WSL2 (Ubuntu Linux) è sempre attivo e disponibile per utility POSIX, test di rete, binari ELF e tool di sicurezza/reversing Linux.

### 8. Brain Knowledge Graph & Compattazione Settimanale
- Nodi Markdown con frontmatter YAML e wikilink bidirezionali compatibili Obsidian (`docs/brain/`).
- `tw.py brain rollover`: compattazione e archiviazione dello stato delle settimane passate in journal dedicati (`docs/brain/journal/week-YYYY-WXX.md`), garantendo supporto per sessioni di settimane/mesi senza saturare il contesto.

### 9. Aggiornamenti a Zero Token, Wrapper Win32 & In-Place Git Update (v2.1.2)
- Risolto il supporto all'aggiornamento da terminale Windows: `tw.py install-cli` registra i wrapper `tw.cmd`, `tw.bat`, `team.cmd`, `team.bat`, `agy.cmd` e `agy.bat` in `~/.local/bin` e aggiunge la cartella alla variabile utente `PATH` nel registro di Windows (`HKCU\Environment\Path`).
- Riscritto il motore di aggiornamento `agy_update`: i plugin git vengono aggiornati in-place tramite `git pull/fetch`, evitando rimozioni premature, file locks e l'errore `FileExistsError [WinError 183]` su Windows.
- Gestione sicura dei permessi read-only nei file `.git` su Windows (`safe_rmtree`).
- Aggiunto supporto diretto al comando CLI `tw` (`tw update`, `tw doctor`, `tw settings`, `tw thermal`) e flag `--force`.

### 10. Documentazione Bilingue & Cataloghi
- `README.md` (Italiano) e `README.en.md` (Inglese) aggiornati con badge e dettagli v2.1.2.
- Catalogo completo sincronizzato in `docs/CATALOG.md` (130 agenti, 512 risorse).
- Suite di test: 102 test passati (100 ok, 2 skipped, 0 errori).
- Strict brain check: OK (0 problemi).
