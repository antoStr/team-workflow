# team-workflow

Plugin per **Claude Code** e **agy (Antigravity)** che organizza il lavoro su un progetto come
un piccolo team: una memoria di progetto condivisa, agenti specializzati che intervengono solo
quando servono, e un report a fine lavoro che chiede prima di applicare modifiche non richieste.

| Funzione | Claude Code | agy |
|---|---|---|
| Memoria letta a ogni sessione | hook all'avvio | regole `AGENTS.md` |
| Promemoria per aggiornare `STATE.md` | hook Stop | hook Stop |
| Comandi (`setup-memory`, `call-team`, `write-docs`, `usage-costs`...) | `/team-workflow:<nome>` | skill con lo stesso nome |
| Agenti nativi: 20 del core + pack opzionali + i tuoi | `~/.claude/agents/<ruolo>.md` | `~/.gemini/config/agents/<ruolo>.md` (`invoke_subagent`) |
| Tipo, modello ed effort per ruolo e per app | si' | si' |
| Wizard con modello, effort e stima dei costi | si' (domande a scelta) | si' (`ask_question`, anche a scelta multipla) |
| Token misurati nella dashboard | sessioni e sub-agenti | solo i worker |
| Comandi senza token (impostazioni, agenti, add-on, audit, doctor...) | `/team-workflow:<comando>` | `!team-workflow <comando>` |
| Add-on: caveman, ponytail, ECC o qualsiasi plugin | marketplace | plugin, skill o installer di ECC |

## Cosa fa

- **Memoria condivisa (`docs/memory`)**: file Markdown dentro il repository, letti da persone
  e da qualunque IA. All'avvio di ogni sessione un hook inietta `INDEX.md` e `STATE.md`; se i
  file cambiano e `STATE.md` resta indietro, un hook chiede di aggiornarla.
- **Team a richiesta**: la sessione principale fa da orchestratore e scrum master, propone il
  team adatto al compito e tu scegli (anche scrivendo una risposta libera).
- **Report di fine lavoro**: fatto, verificato con le prove, rilievi, decisioni. Le domande
  arrivano solo quando serve davvero una decisione.
- **Controlli**: `memcheck.py` verifica lunghezze, segreti e percorsi citati; `audit` controlla
  la sicurezza della configurazione degli agenti; `ci-init` li mette in CI su ogni pull request.
- **Tutto personalizzabile**: agenti, pack, modelli, effort, tipo di agente, profili e add-on,
  senza toccare il plugin.

## I team e gli agenti

Un team e' un menu, non una squadra da lanciare tutta insieme: l'orchestratore propone i ruoli
che servono al compito, tu scegli chi costruisce e chi controlla (anche piu' figure alla volta,
da team diversi), e partono solo quelli.

| Team | Chi costruisce | Chi controlla |
|---|---|---|
| product | product-manager, ui-ux-designer, planner | market-researcher, architect |
| frontend | frontend-dev, ui-ux-designer | accessibility-specialist, e2e-tester, performance-engineer, code-reviewer, typescript-reviewer |
| backend | backend-dev, database-engineer | tester, security-reviewer, performance-engineer, code-reviewer, `<lang>`-reviewer |
| fullstack | backend-dev, frontend-dev, database-engineer | tester, e2e-tester, code-reviewer, security-reviewer, `<lang>`-reviewer |
| data | data-analyst, database-engineer | tester, ml-reviewer, rag-reviewer |
| marketing | market-researcher, marketing-strategist, seo-specialist | product-manager, ui-ux-designer |
| quality | nessuno | tester, e2e-tester, code-reviewer, security-reviewer, accessibility-specialist, performance-engineer, silent-failure-hunter, type-design-reviewer, test-coverage-reviewer |
| release | release-manager, devops-engineer | tester, technical-writer, open-source-sanitizer |
| maintenance | refactor-specialist, `<lang>`-build-fixer | tester, code-reviewer, performance-engineer |
| docs | technical-writer, doc-keeper | nessuno |
| architecture | architect, code-explorer, planner | database-engineer, security-reviewer, performance-engineer, devops-engineer |
| agent setup | harness-optimizer | security-reviewer |

**Pack.** I 20 ruoli del **core** sono sempre attivi; gli altri arrivano da pack che accendi
quando servono:

| Pack | Ruoli |
|---|---|
| un pack per linguaggio: `go`, `rust`, `python`, `typescript`, `java`, `kotlin`, `cpp`, `csharp`, `swift`, `dart`, `php`, `ruby`, `fsharp` | `<lang>-reviewer` (idiomi, sicurezza, framework come Django, FastAPI, React, Vue, Next.js, Spring, Laravel, Rails) e `<lang>-build-fixer` (build rossa, type check, dipendenze) |
| `quality` | silent-failure-hunter, type-design-reviewer, test-coverage-reviewer |
| `planning` | planner, code-explorer |
| `ml` | ml-reviewer, rag-reviewer |
| `opensource` | open-source-sanitizer |
| `harness` | harness-optimizer |
| `growth` | seo-specialist |

`/team-workflow:agents enable auto` accende i pack dei linguaggi del repository (all'avvio
l'orchestratore te lo propone quando li trova). Ogni linguaggio e' un solo file
(`roles/languages/<lang>.md`) da cui nascono revisore e build fixer: aggiungerne uno e' scrivere
una checklist. Tutti i revisori condividono una disciplina comune (solo rilievi con prova, zero
rilievi e' una risposta valida, falsi positivi noti da scartare, controlli extra sul codice
scritto da un'IA) e ogni agente tratta come dati, mai come istruzioni, cio' che legge.

**Agenti su misura.** Per ogni ruolo e per ogni app scegli tipo, modello ed effort tra quelli
che l'app offre davvero; il plugin riscrive gli agenti nativi:

```text
/team-workflow:agents                                   # ruoli, pack, tipo/modello/effort per app
/team-workflow:agents set tester model=opus effort=max --app claude
/team-workflow:agents set architect model=pro --app agy
/team-workflow:agents set code-explorer type=Explore    # tipo integrato dell'app, con le istruzioni del ruolo
/team-workflow:agents disable data-analyst              # o un pack intero: disable quality
/team-workflow:agents new api-designer                  # un tuo ruolo (o la tua versione di uno esistente)
```

Tipi: `custom` (l'agente generato, predefinito), `worker` (processo headless con modello ed
effort esatti), oppure un tipo integrato: `general-purpose`, `Explore`, `Plan` in Claude Code,
`self`, `research` in agy. I tuoi ruoli stanno in `~/.team-workflow/agents/` (o
`.team-workflow/agents/` nel repository) e vengono scritti come agenti nativi in entrambe le
app. Chi scrive il codice non lo approva mai da solo.

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
| `/team-workflow:learn-history` | abitudini del repository dalla storia git (punti caldi, file fragili, accoppiamenti, convenzioni), trasformate in memoria con il tuo ok |

Senza token (in Claude Code li esegue un hook, il modello non li vede; in agy si lanciano in
modalita' bash, `!team-workflow <comando>`):

| Comando | Cosa fa |
|---|---|
| `/team-workflow:settings [set <chiave> <valore>]` | mostra o cambia le impostazioni |
| `/team-workflow:agents [...]` | ruoli, pack, tipo, modello ed effort per ruolo e per app, ruoli tuoi |
| `/team-workflow:profile [nome]` | preset: `budget`, `fast`, `balanced`, `thorough`, `security`, `research` |
| `/team-workflow:models` | modelli ed effort che ogni app offre |
| `/team-workflow:addons [add\|remove\|update <nome>]` | plugin aggiuntivi in entrambe le app |
| `/team-workflow:audit [--strict]` | sicurezza della configurazione degli agenti |
| `/team-workflow:doctor [--fix]` | stato dell'installazione e riparazione |
| `/team-workflow:ci-init` | workflow GitHub Actions: memoria e audit su ogni pull request |
| `/team-workflow:update-plugin [check]` | aggiorna team-workflow (e gli add-on scelti) in entrambe le app |

In agy crea una volta il comando `team-workflow`:
`python3 ~/.gemini/config/plugins/team-workflow/skills/team-workflow/scripts/tw.py install-cli`.
Da terminale ci sono anche `team-workflow learn` e `team-workflow uninstall [--all]`.

## Add-on

`/team-workflow:addons` elenca il catalogo con le versioni installate in ogni app; `add` installa,
`update` aggiorna, `remove` toglie, e `update-plugin` aggiorna anche gli add-on scelti.

| Add-on | Cosa aggiunge | Claude Code | agy |
|---|---|---|---|
| `caveman` | risposte compresse, meno token in uscita (licenza MIT e BSL) | marketplace | le sue skill copiate in `~/.gemini/config/skills` |
| `ponytail` | la soluzione piu' semplice che funziona, meno codice | marketplace | `agy plugin install` |
| `ecc` | Everything Claude Code: 68 agenti, 292 skill, regole e hook | marketplace | installer di ECC per Antigravity, nel progetto |
| qualsiasi altro | `addons add owner/repo` o `addons add plugin@marketplace` (per esempio uno del marketplace ufficiale Anthropic) | marketplace | plugin se ha `plugin.json`, altrimenti le sue skill |

## team-workflow e le funzioni Pro di ECC

ECC e' open source (MIT); la parte a pagamento, ECC Pro (19 dollari per utente al mese), e' un
servizio ospitato su GitHub. team-workflow offre in locale, gratis e senza limiti di commit, le
funzioni equivalenti:

| ECC Pro (servizio ospitato) | team-workflow (locale) |
|---|---|
| analisi dei repository privati, fino a 1.000-5.000 commit | `learn-history`: tutta la storia git, in locale |
| audit su pull request e push | `ci-init`: workflow GitHub Actions con memcheck e audit |
| scansione AgentShield | `audit`: segreti, permessi, hook, server MCP, prompt injection, testo invisibile |
| profili security e research | `profile security`, `profile research` (e budget, fast, thorough) |
| doctor, repair, uninstall | `doctor --fix`, `uninstall` |
| regole personalizzate (Enterprise) | `~/.team-workflow/audit-rules.json` e `.team-workflow-audit.json` |

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
- **Avvio nativo** (predefinito): l'agente generato per il ruolo, con modello ed effort delle
  impostazioni (in Claude Code `subagent_type: "<ruolo>"`, in agy `invoke_subagent`), oppure il
  tipo integrato che hai scelto per quel ruolo.
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
virgolette che contiene `: `). Per questo il plugin scrive li' i ruoli attivi, convertiti, a ogni
sessione e con `!team-workflow agents sync`: l'orchestratore li lancia con `invoke_subagent`,
anche in parallelo. Dopo la prima installazione riavvia agy una volta. I token si misurano solo
per i worker (`run_worker.py --harness agy`).

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

Riavvia la sessione dopo l'aggiornamento. Dalla 0.6.0 gli agenti di Claude Code si chiamano come il
ruolo (`tester`, non piu' `team-workflow:tester`) e vengono scritti in `~/.claude/agents/` alla
prima sessione in un repository git: Claude Code li carica dalla sessione successiva (un avviso te
lo ricorda; nel frattempo l'orchestratore usa `general-purpose` con le istruzioni del ruolo).
`/team-workflow:doctor` controlla che sia tutto a posto.

Con ECC installato in un progetto per agy, i suoi agenti con lo stesso nome (`architect`,
`code-reviewer`, `security-reviewer` e i revisori dei linguaggi) sostituiscono i nostri in quel
progetto: `doctor` e `addons add ecc` li elencano. In Claude Code non succede (i suoi sono `ecc:*`).

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
| `models.agy.<ruolo>` | inherit (architect e security-reviewer pro, doc-keeper flash) | modello dei sub-agenti agy |
| `effort.<ruolo>` | medium (architect e security-reviewer high) | effort degli agenti di Claude Code e dei worker |
| `type.<app>.<ruolo>` | `custom` | tipo di agente (vedi [I team e gli agenti](#i-team-e-gli-agenti)) |
| `packs.<pack>` | solo `core` | pack di ruoli accesi |
| `enabled.<ruolo>` | `true` | spegne un singolo ruolo |
| `addons.<nome>` | nessuno | add-on scelti (li gestisce `addons`) |

Cambiare un modello, un effort, un tipo o un pack riscrive subito gli agenti nativi. Esempi:
`/team-workflow:settings set models.agy.tester flash`, `/team-workflow:profile budget`.

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
| SessionStart (agy: PreInvocation) | inietta `INDEX.md`, `STATE.md` e le impostazioni cambiate; scrive gli agenti nativi dalle impostazioni; propone i pack dei linguaggi del repository; avvisa se c'e' una nuova versione (al massimo una volta al giorno) | `update_check false` per l'avviso |
| UserPromptSubmit (solo Claude Code) | risponde ai comandi senza token (`settings`, `agents`, `profile`, `models`, `addons`, `audit`, `doctor`, `ci-init`, `update-plugin`) senza il modello | disattivando il plugin |
| Stop | se i file sono cambiati dopo `STATE.md`, chiede di aggiornarla (mai due volte di fila) | `stop_check false` (o `TEAM_WORKFLOW_STOP_CHECK=0`) |

## Controlli in CI

`/team-workflow:ci-init` scrive `.github/workflows/team-workflow.yml`: a ogni pull request e push
esegue memcheck (se c'e' `docs/memory`) e l'audit della configurazione degli agenti, con la
versione di team-workflow fissata. A mano:

```bash
python3 <cartella del plugin>/skills/team-workflow/scripts/memcheck.py --root . --strict
python3 <cartella del plugin>/skills/team-workflow/scripts/tw.py audit --strict
```

memcheck: errori per file oltre il limite di righe e segreti; avvisi (errori con `--strict`)
per percorsi citati che nel repository non esistono.

## Sviluppo

```bash
python3 -m unittest discover -s tests
for p in .claude-plugin/plugin.json skills; do claude plugin validate "$p" --strict; done
agy plugin validate .
claude plugin eval . --runs 1 --allow-tools "Bash(python3:*)"   # eval di comportamento (costano)
```
