# team-workflow

Plugin per **Claude Code** e **agy (Antigravity)** che organizza il lavoro su un progetto come
un piccolo team: una memoria di progetto condivisa, agenti specializzati che intervengono solo
quando servono, e un report a fine lavoro che chiede prima di applicare modifiche non richieste.

| Funzione | Claude Code | agy |
|---|---|---|
| Memoria letta a ogni sessione | hook all'avvio | regole `AGENTS.md` |
| Promemoria per aggiornare `STATE.md` | hook Stop | hook Stop |
| Comandi (`setup-memory`, `call-team`, `write-docs`, `usage-costs`...) | `/team-workflow:<nome>` | skill con lo stesso nome |
| 20 agenti come sub-agenti nativi | si' | si' (`invoke_subagent`, scritti in `~/.gemini/config/agents/`) |
| Wizard con modello, effort e stima dei costi | si' (domande a scelta) | si' (`ask_question`, anche a scelta multipla) |
| Token misurati nella dashboard | sessioni e sub-agenti | solo i worker |
| Impostazioni, modelli, aggiornamento senza token | `/team-workflow:settings`, `:models`, `:update-plugin` | `!team-workflow settings`, `models`, `update` |

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
| `/team-workflow:setup-memory` | crea `docs/memory` e la compila leggendo il codice |
| `/team-workflow:call-team [team] <compito>` | descrivi il compito e scegli le figure (anche piu' di una); il team (frontend, backend, data...) e' facoltativo |
| `/team-workflow:new-feature <cosa>` | nuova funzionalita' con il team |
| `/team-workflow:fix-bug <bug>` | test che fallisce, correzione della causa, verifica |
| `/team-workflow:review-changes [range]` | test, review del codice e della sicurezza, un solo verdetto |
| `/team-workflow:release [versione]` | rilascio, solo dopo la tua approvazione |
| `/team-workflow:end-session` | chiude la sessione: memoria, lezioni apprese, punto di ripresa |
| `/team-workflow:usage-costs [giorni\|latest]` | token e costi per agente, modello e sessione |
| `/team-workflow:write-docs [architettura\|onboarding\|changelog\|readme]` | documentazione per le persone ricavata dalla memoria, verificata sul codice |
| `/team-workflow:update-plugin [check]` | aggiorna il plugin in Claude Code e in agy; con `check` mostra solo la versione installata e l'ultima |
| `/team-workflow:settings [set <chiave> <valore>]` | mostra o cambia le impostazioni |
| `/team-workflow:models` | modelli ed effort che ogni app offre agli agenti |

Gli ultimi tre non passano dal modello e non consumano token: in Claude Code li esegue un hook,
in agy si lanciano in modalita' bash (`!team-workflow update`, `!team-workflow settings`,
`!team-workflow models`) dopo aver creato il comando una volta:
`python3 ~/.gemini/config/plugins/team-workflow/skills/team-workflow/scripts/tw.py install-cli`.

## Wizard di assegnazione

Ogni volta che partono degli agenti (team, feature, fix, review, rilascio) scegli i ruoli
(anche piu' di uno alla volta), poi un riepilogo con un blocco per agente mostra su cosa lavora,
come, modello, effort, stima di token e costo, e il totale; parte solo con il tuo ok. Con
`wizard: quick` (predefinito) le domande arrivano solo per gli agenti che vuoi cambiare; con
`full` per tutti; con `off` nessuna. I modelli proposti sono solo quelli che l'app offre:
haiku, sonnet, opus, fable in Claude Code; `inherit`, `flash`, `pro` per i sub-agenti di agy e
gli id di `agy models` (es. `gemini-3.8-flash-high`) per i worker.

- **Stime**: `scripts/estimate.py`, tarate su esecuzioni reali; dopo due esecuzioni di un ruolo
  nel progetto usa la mediana della sua storia.
- **Avvio nativo** (predefinito): sub-agente di Claude Code con il modello scelto (l'effort e'
  quello della definizione dell'agente), oppure sub-agente di agy (`invoke_subagent`) con il
  modello impostato per il ruolo.
- **Avvio worker**: `scripts/run_worker.py` esegue `claude -p` o `agy -p` con modello ed effort
  esatti e registra i token in `~/.team-workflow/ledger/`. Sola lettura, salvo tuo consenso.

## Dashboard dei consumi

`/team-workflow:usage-costs` (o `scripts/dashboard.py --root . --html`) mostra costo ai prezzi di
listino API, token, quota letta dalla cache, consumi per agente, modello e sessione, salute della
memoria e catalogo degli agenti; la pagina HTML e' autonoma, anche in tema scuro. I prezzi stanno
in `skills/team-workflow/pricing.json` (data e fonte indicate, modificabili). Con un abbonamento
i costi indicano consumo, non una fattura.

## agy (Antigravity)

```bash
agy plugin install https://github.com/antoStr/team-workflow   # oppure il percorso locale del repo
agy plugin uninstall team-workflow                            # prima di reinstallare una nuova versione
python3 skills/team-workflow/scripts/install_agy.py --workspace /percorso/repo   # un solo progetto
```

Il repository e' anche un plugin agy (`plugin.json`, `hooks.json` e `rules/` nella radice, che
Claude Code ignora). agy lo installa in `~/.gemini/config/plugins/team-workflow/` con le skill
(`team-workflow` e un workflow per skill in `skills/<nome>/`: `setup-memory`, `call-team`,
`new-feature`, ...), le regole che portano la memoria e gli hook nel formato di agy.

agy non usa gli agenti di un plugin come sub-agenti: li prende da `~/.gemini/config/agents/`,
nel suo formato (e scarta in silenzio un file con `model: sonnet` o con una descrizione senza
virgolette che contiene `: `). Per questo il plugin scrive li' i 20 ruoli convertiti a ogni
sessione, e con `!team-workflow agents`: l'orchestratore li lancia con `invoke_subagent`, anche
in parallelo. Dopo la prima installazione riavvia agy una volta. I token si misurano solo per
i worker (`run_worker.py --harness agy`).

Non e' obbligatorio usarli: basta chiedere normalmente, la skill si attiva sul lavoro di
sviluppo.

## Installazione

Requisiti: Claude Code e/o agy, `git` e `python3`. Claude Code:

```bash
claude plugin marketplace add antoStr/team-workflow   # oppure il percorso locale del repo
claude plugin install team-workflow@team-workflow
```

Per provarlo senza installarlo: `claude --plugin-dir ~/Workspace/team-workflow`. Per agy vedi la
sezione [agy (Antigravity)](#agy-antigravity).

### Aggiornare

La versione installata si vede con `claude plugin list` (o `/plugin`) e in agy con
`agy plugin list`; l'ultima e' in `.claude-plugin/plugin.json` e nei tag `vX.Y.Z` del repository
(su GitHub: Watch → Custom → Releases per ricevere un avviso).

Il modo piu' semplice e' `/team-workflow:update-plugin` in Claude Code, o `!team-workflow update`
in agy: aggiorna entrambi dove il plugin e' installato, senza consumare token; `check` mostra
solo le versioni. All'avvio di Claude Code un avviso dice quando esce una nuova versione.
Da terminale: `python3 skills/team-workflow/scripts/tw.py update [check]`. A mano:

```bash
# Claude Code (oppure attiva l'auto-update del marketplace in /plugin → Marketplaces)
claude plugin marketplace update team-workflow
claude plugin update team-workflow@team-workflow
# agy (non ha un comando update)
agy plugin uninstall team-workflow
agy plugin install https://github.com/antoStr/team-workflow
```

Riavvia la sessione dopo l'aggiornamento. Dalla 0.4.0 i comandi hanno nomi nuovi (`setup-memory`,
`call-team`, `new-feature`, `fix-bug`, `review-changes`, `release`, `end-session`, `usage-costs`,
`write-docs`).

## Impostazioni

Tutti i comportamenti si cambiano senza toccare il plugin: `/team-workflow:settings` (in agy
`!team-workflow settings`) li mostra con la loro origine, `settings set <chiave> <valore>` li
cambia per tutti i progetti (`~/.team-workflow/settings.json`), con `--project` solo per il
repository (`.team-workflow.json`); `settings reset <chiave>` torna al valore predefinito.

| Chiave | Predefinito | Cosa decide |
|---|---|---|
| `wizard` | `quick` | `quick`: riepilogo con le scelte consigliate, domande solo per chi vuoi cambiare; `full`: tutte le domande; `off`: nessuna |
| `max_agents` | `4` | quanti agenti propone al massimo senza chiedere |
| `launch` | `native` | `native` (sub-agenti dell'app) o `worker` (processi headless con modello ed effort esatti) |
| `worker_edits` | `false` | se i worker possono modificare file senza chiedere ogni volta |
| `auto_security_review` | `true` | aggiunge `security-reviewer` quando la modifica tocca codice sensibile |
| `end_report` | `full` | `short`: solo fatto, verificato, decisioni |
| `update_check` | `true` | avviso di nuova versione all'avvio |
| `stop_check` | `true` | promemoria per aggiornare `STATE.md` |
| `models.claude.<ruolo>` | sonnet (architect e security-reviewer opus, doc-keeper haiku) | modello in Claude Code |
| `models.agy.<ruolo>` | inherit (architect e security-reviewer pro, doc-keeper flash) | modello dei sub-agenti agy; cambiarlo riscrive i sub-agenti |
| `effort.<ruolo>` | medium (architect e security-reviewer high) | effort per i worker |

Esempio: `/team-workflow:settings set models.agy.tester flash`.

## Primo uso in un progetto

1. Apri Claude Code nel repository e lancia `/team-workflow:setup-memory` (in agy: chiedi la skill
   `setup-memory`).
2. Il comando crea `docs/memory`, rileva i comandi di build e test (Go, Node, Rust, Python,
   Maven, Gradle) e aggiunge un rimando in `AGENTS.md` (e in `GEMINI.md` o `CLAUDE.md` se ci
   sono), cosi' anche Gemini, Codex e Cursor leggono la stessa memoria.
3. Controlla cosa ha scritto: ogni file, funzione e comando citato deve esistere.

Le istruzioni per gli agenti sono in inglese; le risposte arrivano nella lingua in cui scrivi.
Una memoria gia' esistente mantiene la sua lingua.

## Hook

| Hook | Cosa fa | Come spegnerlo |
|---|---|---|
| SessionStart (agy: PreInvocation) | inietta `INDEX.md`, `STATE.md` e le impostazioni cambiate; avvisa se c'e' una nuova versione (al massimo una volta al giorno); in agy aggiorna i sub-agenti | `update_check false` per l'avviso |
| UserPromptSubmit (solo Claude Code) | risponde a `settings`, `models`, `update-plugin` senza il modello | disattivando il plugin |
| Stop | se i file sono cambiati dopo `STATE.md`, chiede di aggiornarla (mai due volte di fila) | `stop_check false` (o `TEAM_WORKFLOW_STOP_CHECK=0`) |

## memcheck in CI

```bash
python3 <cartella del plugin>/skills/team-workflow/scripts/memcheck.py --root . --strict
```

Errori: file oltre il limite di righe, segreti. Avvisi (errori con `--strict`): percorsi
citati che nel repository non esistono.

## Sviluppo

```bash
python3 -m unittest discover -s tests
for p in .claude-plugin/plugin.json agents skills; do claude plugin validate "$p" --strict; done
```
