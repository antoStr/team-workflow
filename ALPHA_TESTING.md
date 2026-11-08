# team-workflow v2.0.0-alpha.1 — Guida Alpha Testing

Benvenuto nella release Alpha **v2.0.0-alpha.1** di `team-workflow`!
Questa versione introduce il nuovo motore **Brain** (Obsidian-compatible Knowledge Vault), il **Dual Loader**, il **Rolling Digest** nei canali team talk e la portabilità cross-platform Windows.

---

## 1. Funzionalità Chiave

### 🧠 Motore Brain (Obsidian Vault in `docs/brain/`)
- **Struttura Vault**: Cartella `docs/brain/` con sottocartelle `nodes/`, `areas/`, `decisions/`.
- **Obsidian Graph View**: Configurazione automatica `.obsidian/graph.json` con color-coding per layer (core, area, decision, interface).
- **Wikilinks Bidirezionali**: Connessioni `[[slug]]` generate automaticamente tra nodi upstream e downstream.
- **Token Efficiency (~85-90%)**: `tw.py brain query` espande il contesto via BFS a 1-hop (o 2-hop) fornendo solo contratti, interfacce e topologia essenziale anziché interi file sorgente.
- **Integrità Vault**: `tw.py brain check` verifica wikilink orfani o rotti, file mancanti e frontmatter.

### 🔄 Dual Loader
- Compatibilità retroattiva completa: se `memory_engine` è impostato su `"brain"` e `docs/brain` esiste, inietta il grafo Brain; in caso contrario effettua fallback trasparente sul formato classico `docs/memory/INDEX.md` e `STATE.md`.

### 💬 Rolling Digest (Team Talk)
- Compattazione automatica quando i messaggi superano la soglia (default: 20).
- Archiviazione sicura in `<topic>.archive.jsonl`.
- Riscrittura atomica di `<topic>.jsonl` con:
  1. Messaggio `[digest]` riassuntivo dei thread chiusi.
  2. TUTTI i thread ancora aperti (`open_threads()` non perde mai una domanda o contestazione aperta).
  3. Sliding window dei messaggi recenti.

### 🪟 Windows Portability
- Risoluzione dinamica di `python_executable()` che esclude i puntatori a 0-byte del Microsoft Store su Windows.

---

## 2. Quickstart per Tester

### Test 1: Inizializzazione e Mappatura del Brain
```bash
# Inizializza il vault Obsidian in docs/brain/
python skills/team-workflow/scripts/tw.py brain init

# Scansiona la codebase e genera i nodi
python skills/team-workflow/scripts/tw.py brain map

# Verifica l'integrità del grafo
python skills/team-workflow/scripts/tw.py brain check
```

### Test 2: Query di Contesto (Token-Saving BFS)
```bash
# Esegui una query a 1-hop su un modulo
python skills/team-workflow/scripts/tw.py brain query talk --hops 1

# Esegui una query in formato JSON
python skills/team-workflow/scripts/tw.py brain query talk --format json
```

### Test 3: Obsidian Graph View
1. Apri **Obsidian**.
2. Seleziona **Open folder as vault** e scegli la cartella `docs/brain/`.
3. Premi `Ctrl + G` (o apri la vista Graph View).
4. Osserva i nodi colorati per tag (`#core`, `#area`, `#decision`, `#interface`) e i collegamenti interattivi tra i moduli.

### Test 4: Rolling Digest nei Canali Talk
```bash
# Entra in un canale di test
python skills/team-workflow/scripts/tw.py talk join test-digest --as tester "Verifica rolling digest"

# Genera compattazione manuale del canale
python skills/team-workflow/scripts/tw.py talk digest test-digest

# Verifica thread aperti
python skills/team-workflow/scripts/tw.py talk open test-digest
```

---

## 3. Feedback e Segnalazioni
Segnala eventuali anomalie, wikilink non risolti o problemi di esecuzione aprendo una issue o condividendo il log di `tw.py doctor`.
