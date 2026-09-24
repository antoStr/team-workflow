# team-workflow

Plugin per Claude Code che organizza il lavoro su un progetto come un piccolo team: una
memoria di progetto condivisa, agenti specializzati che intervengono solo quando servono, e un
report a fine lavoro che chiede prima di applicare modifiche non richieste.

## Cosa fa

- **Memoria condivisa (`docs/memory`)**: file Markdown dentro il repository, letti da persone
  e da qualunque IA. All'avvio di ogni sessione un hook inietta `INDEX.md` e `STATE.md`; se i
  file cambiano e `STATE.md` resta indietro, un hook chiede di aggiornarla.
- **Team a richiesta**: la sessione principale fa da orchestratore e scrum master, propone il
  team adatto al compito e tu scegli (anche scrivendo una risposta libera).
- **Report di fine lavoro**: fatto, verificato con le prove, rilievi, decisioni. Le domande
  arrivano solo quando serve davvero una decisione.
- **Controlli**: `memcheck.py` verifica lunghezze, segreti e percorsi citati, anche in CI.

## I team

Venti agenti specializzati, organizzati in team. Un team e' un menu, non una squadra da
lanciare tutta insieme: l'orchestratore propone i ruoli che servono al compito, tu scegli chi
costruisce e chi controlla, e partono solo quelli.

| Team | Chi costruisce | Chi controlla |
|---|---|---|
| product | product-manager, ui-ux-designer | market-researcher, architect |
| frontend | frontend-dev, ui-ux-designer | accessibility-specialist, e2e-tester, performance-engineer, code-reviewer |
| backend | backend-dev, database-engineer | tester, security-reviewer, performance-engineer, code-reviewer |
| fullstack | backend-dev, frontend-dev, database-engineer | tester, e2e-tester, code-reviewer, security-reviewer |
| data | data-analyst, database-engineer | tester |
| marketing | market-researcher, marketing-strategist | product-manager, ui-ux-designer |
| quality | nessuno | tester, e2e-tester, code-reviewer, security-reviewer, accessibility-specialist, performance-engineer |
| release | release-manager, devops-engineer | tester, technical-writer |
| maintenance | refactor-specialist | tester, code-reviewer, performance-engineer |
| docs | technical-writer, doc-keeper | nessuno |
| architecture | architect | database-engineer, security-reviewer, performance-engineer, devops-engineer |

Modelli: architect e security-reviewer su opus con effort alto (dove un errore costa caro),
doc-keeper su haiku (lavoro meccanico), tutti gli altri su sonnet. L'orchestratore puo'
alzare o abbassare il modello per il singolo compito. Chi scrive il codice non lo approva mai
da solo. Ruoli, modelli e permessi di ogni agente: `skills/team-workflow/TEAMS.md`.

## Comandi

| Comando | Cosa fa |
|---|---|
| `/team-workflow:init` | crea `docs/memory` e la compila leggendo il codice |
| `/team-workflow:team <team> <compito>` | chiama un team (frontend, backend, data, marketing...) |
| `/team-workflow:feature <cosa>` | nuova funzionalita' con il team |
| `/team-workflow:fix <bug>` | test che fallisce, correzione della causa, verifica |
| `/team-workflow:review [range]` | test, review del codice e della sicurezza, un solo verdetto |
| `/team-workflow:ship [versione]` | rilascio, solo dopo la tua approvazione |
| `/team-workflow:wrap-up` | chiude la sessione: memoria, lezioni apprese, punto di ripresa |

Non e' obbligatorio usarli: basta chiedere normalmente, la skill si attiva sul lavoro di
sviluppo.

## Installazione

Requisiti: Claude Code, `git` e `python3`.

```bash
claude plugin marketplace add ~/Workspace/team-workflow
claude plugin install team-workflow@team-workflow
```

Per provarlo senza installarlo: `claude --plugin-dir ~/Workspace/team-workflow`.

## Primo uso in un progetto

1. Apri Claude Code nel repository e lancia `/team-workflow:init`.
2. Il comando crea `docs/memory`, rileva i comandi di build e test (Go, Node, Rust, Python,
   Maven, Gradle) e aggiunge un rimando in `AGENTS.md` (e in `GEMINI.md` o `CLAUDE.md` se ci
   sono), cosi' anche Gemini, Codex e Cursor leggono la stessa memoria.
3. Controlla cosa ha scritto: ogni file, funzione e comando citato deve esistere.

Le istruzioni per gli agenti sono in inglese; le risposte arrivano nella lingua in cui scrivi.
Una memoria gia' esistente mantiene la sua lingua.

## Hook

| Hook | Cosa fa | Come spegnerlo |
|---|---|---|
| SessionStart | inietta `INDEX.md` e `STATE.md`; senza memoria suggerisce `init` | disattivando il plugin |
| Stop | se i file sono cambiati dopo `STATE.md`, chiede di aggiornarla (mai due volte di fila) | `TEAM_WORKFLOW_STOP_CHECK=0` |

## memcheck in CI

```bash
python3 <cartella del plugin>/skills/team-workflow/scripts/memcheck.py --root . --strict
```

Errori: file oltre il limite di righe, segreti. Avvisi (errori con `--strict`): percorsi
citati che nel repository non esistono.

## Sviluppo

```bash
python3 -m unittest discover -s tests
for p in .claude-plugin/plugin.json agents commands skills; do claude plugin validate "$p" --strict; done
```
