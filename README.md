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

## Il team

| Agente | Modello | Quando interviene |
|---|---|---|
| architect | opus, effort alto | scelte strutturali: nuovi moduli, modello dati, API, refactor trasversali |
| backend-dev | sonnet | codice server, CLI, librerie e dati |
| frontend-dev | sonnet | interfaccia accessibile e responsive |
| tester | sonnet | ogni modifica non banale; per i bug scrive prima il test che fallisce |
| code-reviewer | sonnet | modifiche medie e grandi, prima del merge |
| security-reviewer | opus, effort alto | autenticazione, input, rete, segreti, crittografia, dipendenze |
| release-manager | sonnet | pipeline, versione, tag e note; pubblica solo dopo il tuo ok |
| doc-keeper | haiku | aggiorna memoria e documentazione dal diff |

L'orchestratore puo' alzare il modello per il singolo compito (opus per concorrenza,
sicurezza, rischio di perdita di dati) o abbassarlo (haiku per lavori meccanici).
Chi scrive il codice non lo approva mai da solo: lo verifica il tester.

## Comandi

| Comando | Cosa fa |
|---|---|
| `/team-workflow:init` | crea `docs/memory` e la compila leggendo il codice |
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
