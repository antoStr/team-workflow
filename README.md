# team-workflow

Plugin per **Claude Code**, **agy (Antigravity)** e **OpenCode** che organizza il lavoro su un progetto come
un piccolo team: una memoria di progetto condivisa, agenti specializzati che intervengono solo
quando servono, e un report a fine lavoro che chiede prima di applicare modifiche non richieste.

| Funzione | Claude Code | agy | OpenCode |
|---|---|---|---|
| Memoria letta a ogni sessione | hook all'avvio | regole `AGENTS.md` | 2.x: blocco in `AGENTS.md`; 1.x: plugin (prompt di sistema) |
| Promemoria per aggiornare `STATE.md` | hook Stop | hook Stop | 2.x: nelle istruzioni; 1.x: plugin (`session.idle`) |
| Comandi (`setup-memory`, `call-team`, `write-docs`, `usage-costs`...) | `/team-workflow:<nome>` | skill con lo stesso nome | `/team-workflow/<nome>` |
| Agenti nativi: 20 del core + pack opzionali + i tuoi | `~/.claude/agents/` | `~/.gemini/config/agents/` (`invoke_subagent`) | `~/.config/opencode/agents/` (strumento subagent) |
| Wizard a inizio conversazione: preset, agenti, modello ed effort tra quelli offerti | si' | si' | si' |
| Token misurati nella dashboard | sessioni e sub-agenti | solo i worker | sessioni, sub-agenti e worker |
| Comandi senza token (impostazioni, agenti, add-on, audit, doctor...) | `/team-workflow:<comando>` | `!team-workflow <comando>` | `/team-workflow/<comando>` (1.x: 0 token; 2.x: il modello mostra solo l'output) e `!team-workflow <comando>` |
| Add-on: caveman, ponytail, ECC, il set frontend o qualsiasi plugin | marketplace (o skill copiate) | plugin, skill o installer di ECC | skill, plugin in `opencode.json` o installer di ECC |
| Agenti che parlano tra loro (team talk) | si' | si' | si' |
| Libreria ECC: 311 skill, 97 comandi, 22 set di regole | ricerca + skill native a scelta | ricerca + skill native a scelta | ricerca + skill native a scelta |
| Attivazione automatica o solo quando la chiami | si' | solo il controllo Stop | si' |

## Novita' della 0.9.0

- **Tutto Everything Claude Code dentro team-workflow**: 88 agenti (32 nuovi da ECC in nuovi
  pack: frameworks, gan, network, domains, ops, e in quality, planning, harness, ml,
  opensource) e una libreria di 430 voci (311 skill, 97 comandi, 22 set di regole) che
  l'orchestratore cerca per ogni compito. Elenco completo nel
  [Catalogo completo](#catalogo-completo-versione-090).
- **Agenti che parlano tra loro**: canale condiviso per fare debug insieme, contestarsi le
  affermazioni con le prove e verificarsi a vicenda (`/team-workflow:talk`, `TALK.md`).
- **`/team-workflow:setup`**: tutte le impostazioni in un posto, compresa l'attivazione
  (automatica in ogni progetto, solo in alcuni, o solo quando la chiami).
- **Set frontend**: `addons add frontend` installa impeccable, taste, frontend-design,
  solar-icons e le skill Cloudflare, usate dagli agenti frontend e di sicurezza.

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
  senza toccare il plugin. `/team-workflow:setup` raccoglie tutto in un posto solo, compresa
  l'attivazione: da sola in ogni progetto, solo in alcuni progetti, o solo quando la chiami.
- **Agenti che parlano tra loro (team talk)**: gli agenti di un compito condividono un canale
  (`tw.py talk`, anche tra worktree diversi). Si fanno domande, mettono in dubbio le
  affermazioni degli altri con le prove, verificano le correzioni e danno un verdetto; il
  lavoro non e' finito finche' resta aperta una sfida. Tre modi: debug insieme, review
  incrociata, confronto su una decisione (`TALK.md`). Leggi la conversazione con
  `/team-workflow:talk read <topic>`.
- **Tutto ECC dentro team-workflow**: i 32 agenti di Everything Claude Code che mancavano sono
  ruoli nei pack (frameworks, quality, planning, harness, gan, network, domains, ops...); gli
  altri 39 erano gia' coperti dai ruoli esistenti. Le 311 skill, i 97 comandi e le 22 serie di
  regole sono una libreria che l'orchestratore cerca per ogni compito e passa agli agenti, e
  che puoi installare come skill native a pacchetti o una alla volta (`/team-workflow:library`).

## I team e gli agenti

Un team e' un menu, non una squadra da lanciare tutta insieme: l'orchestratore propone i ruoli
che servono al compito, tu scegli chi costruisce e chi controlla (anche piu' figure alla volta,
da team diversi), e partono solo quelli.

| Team | Chi costruisce | Chi controlla |
|---|---|---|
| product | product-manager, ui-ux-designer, planner | market-researcher, architect |
| frontend | frontend-dev, ui-ux-designer (con le skill del set frontend) | accessibility-specialist, e2e-tester, performance-engineer, code-reviewer, typescript-reviewer, react-reviewer, vue-reviewer, flutter-reviewer |
| backend | backend-dev, database-engineer | tester, security-reviewer, performance-engineer, code-reviewer, `<lang>`-reviewer, database-reviewer, django-reviewer, fastapi-reviewer |
| fullstack | backend-dev, frontend-dev, database-engineer | tester, e2e-tester, code-reviewer, security-reviewer, `<lang>`-reviewer |
| data | data-analyst, database-engineer | tester, ml-reviewer, rag-reviewer |
| marketing | market-researcher, marketing-strategist, seo-specialist | product-manager, ui-ux-designer |
| quality | nessuno | tester, e2e-tester, code-reviewer, security-reviewer, accessibility-specialist, performance-engineer, silent-failure-hunter, type-design-reviewer, test-coverage-reviewer, database-reviewer, comment-analyzer, commit-reviewer |
| release | release-manager, devops-engineer | tester, technical-writer, open-source-sanitizer |
| maintenance | refactor-specialist, code-simplifier, build-fixer, `<lang>`-build-fixer | tester, code-reviewer, performance-engineer |
| docs | technical-writer, doc-keeper | nessuno |
| architecture | architect, code-architect, code-explorer, spec-miner, planner, docs-lookup | database-engineer, security-reviewer, performance-engineer, devops-engineer |
| agent setup | harness-optimizer, loop-operator | security-reviewer, agent-evaluator, conversation-analyzer |
| build loop | gan-planner, gan-generator | gan-evaluator |
| network | network-architect, homelab-architect | network-config-reviewer, network-troubleshooter, security-reviewer |
| domain | chi costruisce il compito | healthcare-reviewer, bengali-reviewer |
| operations | chief-of-staff | nessuno |

**Pack.** I 20 ruoli del **core** sono sempre attivi; gli altri arrivano da pack che accendi
quando servono:

| Pack | Ruoli |
|---|---|
| un pack per linguaggio: `go`, `rust`, `python`, `typescript`, `java`, `kotlin`, `cpp`, `csharp`, `swift`, `dart`, `php`, `ruby`, `fsharp` | `<lang>-reviewer` (idiomi, sicurezza, framework come Django, FastAPI, React, Vue, Next.js, Spring, Laravel, Rails) e `<lang>-build-fixer` (build rossa, type check, dipendenze) |
| `frameworks` | react-reviewer, react-build-fixer, vue-reviewer, django-reviewer, django-build-fixer, fastapi-reviewer, flutter-reviewer, harmonyos-specialist |
| `quality` | silent-failure-hunter, type-design-reviewer, test-coverage-reviewer, build-fixer, code-simplifier, comment-analyzer, commit-reviewer, database-reviewer |
| `planning` | planner, code-explorer, code-architect, spec-miner, docs-lookup |
| `ml` | ml-reviewer, rag-reviewer, pytorch-build-fixer |
| `opensource` | open-source-sanitizer, open-source-forker, open-source-packager |
| `harness` | harness-optimizer, agent-evaluator, conversation-analyzer, loop-operator |
| `gan` | gan-planner, gan-generator, gan-evaluator |
| `network` | network-architect, network-config-reviewer, network-troubleshooter, homelab-architect |
| `domains` | healthcare-reviewer, bengali-reviewer |
| `ops` | chief-of-staff |
| `growth` | seo-specialist |

I ruoli con `source: "ECC ..."` sono importati da Everything Claude Code (MIT) con
`tools/import_ecc.py`, che ricostruisce anche la libreria: rilancialo dopo un aggiornamento di ECC.

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
| `/team-workflow:setup [area]` | configura tutto: attivazione (automatica, solo in questo progetto, solo quando la chiami), wizard, team, modelli, ruoli e pack, libreria, team talk, controlli, add-on, preset |
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
| `/team-workflow:options` | cosa puo' proporre il wizard di inizio conversazione in questa app, adesso |
| `/team-workflow:addons [add\|remove\|update <nome>]` | plugin aggiuntivi in entrambe le app |
| `/team-workflow:audit [--strict]` | sicurezza della configurazione degli agenti |
| `/team-workflow:doctor [--fix]` | stato dell'installazione e riparazione |
| `/team-workflow:ci-init` | workflow GitHub Actions: memoria e audit su ogni pull request |
| `/team-workflow:update-plugin [check]` | aggiorna team-workflow (e gli add-on scelti) in entrambe le app |
| `/team-workflow:library [search <parole>\|show <id>\|enable\|disable <id\|pack>]` | la libreria ECC: pack, ricerca, installazione come skill native |
| `/team-workflow:talk [read\|open\|clear <topic>]` | cosa si sono detti gli agenti, domande e sfide ancora aperte |

In agy crea una volta il comando `team-workflow`:
`python3 ~/.gemini/config/plugins/team-workflow/skills/team-workflow/scripts/tw.py install-cli`.
Da terminale ci sono anche `team-workflow learn` e `team-workflow uninstall [--all]`.

## Add-on

`/team-workflow:addons` elenca il catalogo con le versioni installate in ogni app; `add` installa,
`update` aggiorna, `remove` toglie, e `update-plugin` aggiorna anche gli add-on scelti.
`addons add frontend` installa insieme impeccable, taste, frontend-design, solar-icons e
cloudflare: `frontend-dev`, `ui-ux-designer` e `accessibility-specialist` le usano quando ci
sono; `security-reviewer`, `backend-dev` e `devops-engineer` usano le skill Cloudflare nei
progetti su Cloudflare (la sicurezza: `cloudflare-one` per Zero Trust, `turnstile-spin`,
`workers-best-practices`).

| Add-on | Cosa aggiunge | Claude Code | agy |
|---|---|---|---|
| `caveman` | risposte compresse, meno token in uscita (licenza MIT e BSL) | marketplace | le sue skill copiate in `~/.gemini/config/skills` |
| `ponytail` | la soluzione piu' semplice che funziona, meno codice | marketplace | `agy plugin install` |
| `ecc` | Everything Claude Code: 68 agenti, 292 skill, regole e hook | marketplace | installer di ECC per Antigravity, nel progetto |
| `impeccable` | design, critica, audit e rifinitura delle interfacce (Apache-2.0) | marketplace | le sue skill copiate |
| `taste` | direzione artistica anti-"AI slop" per siti e schermate (MIT) | marketplace | le sue skill copiate |
| `frontend-design` | la skill frontend-design di Anthropic (Apache-2.0) | marketplace ufficiale | la skill copiata |
| `solar-icons` | icone Solar: nomi esatti e import per framework (MIT, icone CC BY 4.0) | skill copiata in `~/.claude/skills` | la skill copiata |
| `cloudflare` | skill Cloudflare: Workers best practices, Zero Trust (`cloudflare-one`), Turnstile, web perf (Apache-2.0) | marketplace | le sue skill copiate |
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

**A inizio conversazione** (impostazione `session_wizard`, attiva di default), al primo compito
che usa gli agenti, il wizard ti mostra prima l'elenco completo (`team-workflow options`: i
modelli e gli effort che l'app offre ad agenti nativi e worker, e per ogni ruolo tipo, modello,
effort e come gira davvero; `--app all` per Claude Code, agy e OpenCode insieme), poi chiede il
preset, gli agenti da usare (anche piu' di uno), e per **ogni** agente scelto modello ed effort
(due agenti per domanda, finche' non li ha chiesti tutti). In agy `inherit` e' il modello della sessione (per esempio
`gemini-3.8-flash-high`): i sotto-agenti di agy accettano solo `inherit`, `flash` o `pro`
(Gemini 3.1 Pro, piu' vecchio), quindi un modello esatto diverso gira come worker; lo stesso in
OpenCode per un modello o una variante diversi da quelli del file dell'agente, e in Claude Code
per un effort diverso. Alla fine scegli se usare le scelte solo in questa conversazione o
salvarle come predefinite (per tutti i progetti o per questo).

Poi, ogni volta che partono degli agenti (team, feature, fix, review, rilascio) scegli i ruoli
(anche piu' di uno alla volta), poi un riepilogo con un blocco per agente mostra su cosa lavora,
come, modello, effort, stima di token e costo, e il totale; parte solo con il tuo ok. Con
`wizard: quick` (predefinito) le domande arrivano solo per gli agenti che vuoi cambiare; con
`full` per tutti; con `off` nessuna. I modelli proposti sono solo quelli che l'app offre:
haiku, sonnet, opus, fable in Claude Code; `inherit`, `flash`, `pro` per i sub-agenti di agy e
gli id di `agy models` (es. `gemini-3.8-flash-high`) per i worker; in OpenCode `inherit` o un
`provider/modello` di qualsiasi provider collegato (NanoGPT, OpenRouter, ...), con la variante
come effort (solo quelle del modello: GLM 5.3 ha `low`, `high`, `max`). Il wizard mostra i
provider e i modelli che usi di piu'; gli altri li cerca per nome:
`team-workflow models --app opencode --provider nano-gpt --search "glm 5.3"`.

- **Stime**: `scripts/estimate.py`, tarate su esecuzioni reali; dopo due esecuzioni di un ruolo
  nel progetto usa la mediana della sua storia.
- **Avvio nativo** (predefinito): l'agente generato per il ruolo, con modello ed effort delle
  impostazioni (in Claude Code `subagent_type: "<ruolo>"`, in agy `invoke_subagent`), oppure il
  tipo integrato che hai scelto per quel ruolo.
- **Avvio worker**: `scripts/run_worker.py` esegue `claude -p`, `agy -p` o `opencode run` con
  modello ed effort esatti e registra i token in `~/.team-workflow/ledger/`. Sola lettura, salvo tuo consenso.

## Dashboard dei consumi

`/team-workflow:usage-costs` (o `scripts/dashboard.py --root . --html`) mostra costo ai prezzi di
listino API, token, quota letta dalla cache, consumi per agente, modello e sessione, salute della
memoria e catalogo degli agenti; la pagina HTML e' autonoma, anche in tema scuro. I prezzi stanno
in `skills/team-workflow/pricing.json` (data e fonte indicate, modificabili). Con un abbonamento
i costi indicano consumo, non una fattura.

## agy (Antigravity)

```bash
agy plugin install https://github.com/antoStr/team-workflow   # oppure il percorso locale del repo
python3 ~/.gemini/config/plugins/team-workflow/skills/team-workflow/scripts/tw.py install-cli
# da qui in poi, in un nuovo terminale:
agy plugin update team-workflow     # o `agy plugin update` per tutti i plugin, o `agy plugin update ponytail`
python3 skills/team-workflow/scripts/install_agy.py --workspace /percorso/repo   # un solo progetto
```

agy non ha `plugin update`: `install-cli` crea il comando `team-workflow` in `~/.local/bin` e
aggiunge a `~/.zshrc` e `~/.bashrc` una funzione `agy` che gestisce solo `agy plugin update
[nome...]` e passa ogni altro comando ad agy invariato (per toglierla, cancella il blocco
`team-workflow` dal file; `install-cli --no-shell` non la aggiunge). L'aggiornamento vale per
qualsiasi plugin: lo reinstalla dall'origine da cui agy l'aveva clonato, controlla prima che
l'origine risponda e, se la reinstallazione fallisce, rimette la versione precedente.

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

## OpenCode

```bash
python3 ~/Workspace/team-workflow/skills/team-workflow/scripts/install_opencode.py   # dalla copia del repository
team-workflow install-opencode                                                      # oppure con il comando team-workflow
```

Funziona con la CLI e con l'app desktop (OpenCode 2.x; su Windows la CLI dell'app e'
`%LOCALAPPDATA%\Programs\@opencodedesktop\resources\opencode-cli.exe` e viene trovata da sola).
Scrive in `~/.config/opencode/`: lo skill `team-workflow` (con script, ruoli e wizard), i
comandi `/team-workflow/<nome>` (in una cartella: su Windows i due punti non sono ammessi nei
nomi dei file) e gli agenti dei ruoli attivi.

- **OpenCode 2.x**: i plugin non possono piu' toccare il prompt di sistema ne' intercettare i
  comandi, quindi l'installer aggiunge un blocco a `~/.config/opencode/AGENTS.md`: alla prima
  richiesta di ogni conversazione il modello esegue `session_start.py --text` (memoria,
  impostazioni, wizard di sessione). `settings`, `agents`, `profile`, `models`, `addons`,
  `audit`, `doctor`, `ci-init`, `options` e `update-plugin` eseguono `tw.py` dentro il comando e
  il modello mostra solo l'output (pochi token). Non c'e' un hook di fine turno: il promemoria
  per `STATE.md` e' nelle istruzioni.
- **OpenCode 1.x**: al posto del blocco c'e' il plugin `team-workflow.js` (memoria nel prompt di
  sistema, comandi a 0 token, promemoria `STATE.md` a fine turno).

L'orchestratore lancia i ruoli con lo strumento `subagent` (`task` in 1.x) e fa le domande con lo
strumento `question`. Comandi e istruzioni usano il Python che funziona davvero sulla macchina:
su Windows `python3` e' spesso il segnaposto del Microsoft Store, che fallisce sempre.
`/team-workflow/update-plugin` (o `team-workflow update`) aggiorna anche OpenCode;
`install_opencode.py --uninstall` toglie solo i file scritti da team-workflow (compreso il blocco
in `AGENTS.md`); `team-workflow doctor` segnala le installazioni vecchie da rifare. OpenCode legge
anche le skill in `~/.claude/skills` e `~/.agents/skills`.

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
# agy, dopo `tw.py install-cli` (vedi la sezione agy)
agy plugin update team-workflow
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
| `activation` | `auto` | `auto`: ogni sessione in un repository carica memoria, protocollo e controllo Stop; `manual`: team-workflow resta zitto finche' non lo chiami. Solo in alcuni progetti: `manual` per l'utente e `auto --project` in quei progetti |
| `talk` | `true` | gli agenti di un compito parlano tra loro sul canale condiviso (`TALK.md`) |
| `talk_rounds` | `3` | quanti giri di risposte al massimo prima di portarti il disaccordo |
| `library.packs.<pack>` | spenti | pack della libreria ECC installati come skill native |
| `library.skills.<id>` | - | una singola voce della libreria, accesa o spenta (vince sul pack) |
| `session_wizard` | `true` | a inizio conversazione chiede preset, agenti, modello ed effort tra quelli offerti dall'app |
| `wizard` | `quick` | `quick`: riepilogo con le scelte consigliate, domande solo per chi vuoi cambiare; `full`: tutte le domande; `off`: nessuna |
| `max_agents` | `4` | quanti agenti propone al massimo senza chiedere |
| `launch` | `native` | `native` (sub-agenti dell'app) o `worker` (processi headless con modello ed effort esatti) |
| `worker_edits` | `false` | se i worker possono modificare file senza chiedere ogni volta |
| `auto_security_review` | `true` | aggiunge `security-reviewer` quando la modifica tocca codice sensibile |
| `end_report` | `full` | `short`: solo fatto, verificato, decisioni |
| `update_check` | `true` | avviso di nuova versione all'avvio |
| `stop_check` | `true` | promemoria per aggiornare `STATE.md` |
| `models.claude.<ruolo>` | sonnet (architect e security-reviewer opus, doc-keeper haiku) | modello in Claude Code |
| `models.agy.<ruolo>` | inherit (il modello della sessione) | modello dei sub-agenti agy: inherit, flash o pro |
| `models.opencode.<ruolo>` | inherit | modello dei sotto-agenti OpenCode: inherit o `provider/modello` |
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

`/team-workflow:ci-init` scrive `.github/workflows/team-workflow.yml` e copia in
`.github/team-workflow/` i tre script dei controlli (cosi' la CI non deve scaricare il plugin):
a ogni pull request e push esegue memcheck (se c'e' `docs/memory`) e l'audit della
configurazione degli agenti. A mano:

```bash
python3 <cartella del plugin>/skills/team-workflow/scripts/memcheck.py --root . --strict
python3 <cartella del plugin>/skills/team-workflow/scripts/tw.py audit --strict
```

memcheck: errori per file oltre il limite di righe e segreti; avvisi (errori con `--strict`)
per percorsi citati che nel repository non esistono.

<!-- catalog:begin (generated by tools/readme_catalog.py: do not edit by hand) -->

## Catalogo completo (versione 0.9.0)

### Tutti gli agenti (88)

`ECC` = importato da Everything Claude Code. Accendi un pack con `/team-workflow:agents enable <pack>` (il core e' sempre acceso).

<details><summary><b>core</b> (20)</summary>

| Agente | Cosa fa |
|---|---|
| `accessibility-specialist` | Check and improve the accessibility of a user interface against WCAG 2.2 AA: keyboard use, focus, screen reader semantics, contrast, forms, motion and zoom. |
| `architect` | When a task needs a structural decision before code is written: a new module or service, a change to the data model or a public API, a cross-cutting refactor,… |
| `backend-dev` | Implement or fix server-side, CLI, library, data or infrastructure code once the task is clear: a planned feature in one or more backend areas, a bug with a… |
| `code-reviewer` | Review a change for quality before it is merged: correctness risks the tests may miss, reuse of existing code, simplicity, consistency with the codebase,… |
| `data-analyst` | Study data: spreadsheets (xls, xlsx, csv), JSON, logs or database exports. |
| `database-engineer` | Anything that touches how data is stored: schema design, migrations, indexes, query performance, transactions and locking, data integrity, backups and… |
| `devops-engineer` | Build, delivery and operations: CI/CD pipelines, containers, infrastructure as code, deployments and environments, secrets management, logging, monitoring and… |
| `doc-keeper` | Bring the project memory and documentation in line with the code after a change: it reads the diff, updates docs/memory (STATE.md, area cards, MAP.md,… |
| `e2e-tester` | Test complete user flows end to end, in a real browser or through the real interfaces: sign-up, checkout, forms, navigation, uploads and their error paths, at… |
| `frontend-dev` | Implement or fix user interface code once the task is clear: pages, components, styles, client-side state, forms and their calls to the backend. |
| `market-researcher` | Research a market with sources: competitors with their features and prices, target customers and personas, market size and trends, positioning gaps and demand… |
| `marketing-strategist` | Plan and write how a product is presented and promoted: positioning and messaging, launch plans, landing page and email copy, content and SEO plans, social… |
| `performance-engineer` | When speed, resource use or scale matter: profiling slow code, benchmarks, load and stress tests, memory leaks, bundle size and page speed, and capacity… |
| `product-manager` | Turn an idea or a request into a clear, testable scope before work starts: user stories, acceptance criteria, priorities, what is in and out, and the open… |
| `refactor-specialist` | Improve the structure of existing code without changing what it does: refactoring large files and functions, removing duplication and dead code, cleaning up… |
| `release-manager` | Take verified work to a merge or a release: it runs the full pipeline from PLAYBOOKS.md, checks CI, prepares version, commit message, tag and release notes,… |
| `security-reviewer` | When a change touches security-sensitive code: authentication and sessions, input parsing, file paths, network requests and redirects, SQL or shell commands,… |
| `technical-writer` | Write or fix the documentation people read: README, installation and usage guides, API references, tutorials, changelogs and release notes, and doc comments… |
| `tester` | After code was written or changed, to verify it independently before it is accepted: it runs the project checks, tests the new behavior and its edge cases,… |
| `ui-ux-designer` | Design how a feature looks and behaves before or while it is built: user flows, screen layouts, every state (loading, empty, error), interface copy, visual… |

</details>

<details><summary><b>frameworks</b> (8)</summary>

| Agente | Cosa fa |
|---|---|
| `django-build-fixer` `ECC` | Django/Python build, migration, and dependency error resolution specialist. |
| `django-reviewer` `ECC` | Expert Django code reviewer specializing in ORM correctness, DRF patterns, migration safety, security misconfigurations, and production-grade Django practices. |
| `fastapi-reviewer` `ECC` | Reviews FastAPI applications for async correctness, dependency injection, Pydantic schemas, security, OpenAPI quality, testing, and production readiness. |
| `flutter-reviewer` `ECC` | Flutter and Dart code reviewer. |
| `harmonyos-specialist` `ECC` | HarmonyOS application development expert specializing in ArkTS and ArkUI. |
| `react-build-fixer` `ECC` | Diagnose and fix React build failures across Vite, webpack, Next.js, CRA, Parcel, esbuild, and Bun. |
| `react-reviewer` `ECC` | Expert React/JSX code reviewer specializing in hook correctness, render performance, server/client component boundaries, accessibility, and React-specific… |
| `vue-reviewer` `ECC` | Expert Vue.js code reviewer specializing in Composition API correctness, reactivity pitfalls, component architecture, template security, and Vue-specific… |

</details>

<details><summary><b>quality</b> (8)</summary>

| Agente | Cosa fa |
|---|---|
| `build-fixer` `ECC` | Build and TypeScript error resolution specialist. |
| `code-simplifier` `ECC` | Simplifies and refines code for clarity, consistency, and maintainability while preserving behavior. |
| `comment-analyzer` `ECC` | Analyze code comments for accuracy, completeness, maintainability, and comment rot risk. |
| `commit-reviewer` `ECC` | Reviews a staged diff and drafts a Conventional Commits-compliant message matching the repository's actual history norms. |
| `database-reviewer` `ECC` | PostgreSQL database specialist for query optimization, schema design, security, and performance. |
| `silent-failure-hunter` | Find failures that the code hides: swallowed exceptions, errors turned into empty values or defaults, missing timeouts, lost error context, fire-and-forget… |
| `test-coverage-reviewer` | Judge whether the tests of a change would catch the bugs that matter: untested branches and error paths, assertions that cannot fail, over-mocking, missing… |
| `type-design-reviewer` | Review new or changed types, schemas and data models for how well they protect invariants: illegal states that can be represented, primitive obsession,… |

</details>

<details><summary><b>planning</b> (5)</summary>

| Agente | Cosa fa |
|---|---|
| `code-architect` `ECC` | Designs feature architectures by analyzing existing codebase patterns and conventions, then providing implementation blueprints with concrete files,… |
| `code-explorer` | Understand how an existing feature works before changing it: it traces the execution path from the entry point to storage and back, maps the modules, data… |
| `docs-lookup` `ECC` | When the user asks how to use a library, framework, or API or needs up-to-date code examples, use Context7 MCP to fetch current documentation and return… |
| `planner` | Turn an agreed feature, refactor or migration into an implementation plan before code is written: ordered steps, the files each step touches, dependencies… |
| `spec-miner` `ECC` | Extracts behavioral specs from existing codebases for OpenSpec. |

</details>

<details><summary><b>ml</b> (3)</summary>

| Agente | Cosa fa |
|---|---|
| `ml-reviewer` | Review machine learning code headed for production: data contracts and validation, feature pipelines, training reproducibility, evaluation (leakage, splits,… |
| `pytorch-build-fixer` `ECC` | PyTorch runtime, CUDA, and training error resolution specialist. |
| `rag-reviewer` | Review a retrieval-augmented generation pipeline: document ingestion and chunking, embeddings and the vector store, retrieval and reranking, prompt assembly,… |

</details>

<details><summary><b>harness</b> (4)</summary>

| Agente | Cosa fa |
|---|---|
| `agent-evaluator` `ECC` | Evaluates agent output against 5-axis quality rubric (accuracy, completeness, clarity, actionability, conciseness). |
| `conversation-analyzer` `ECC` | When analyzing conversation transcripts to find behaviors worth preventing with hooks. |
| `harness-optimizer` | Review and tune the AI agent setup of a repository or user: Claude Code and agy settings, permissions, hooks, MCP servers, agents, skills, rules and memory… |
| `loop-operator` `ECC` | Operate autonomous agent loops, monitor progress, and intervene safely when loops stall. |

</details>

<details><summary><b>gan</b> (3)</summary>

| Agente | Cosa fa |
|---|---|
| `gan-evaluator` `ECC` | GAN Harness — Evaluator agent. |
| `gan-generator` `ECC` | GAN Harness — Generator agent. |
| `gan-planner` `ECC` | GAN Harness — Planner agent. |

</details>

<details><summary><b>opensource</b> (3)</summary>

| Agente | Cosa fa |
|---|---|
| `open-source-forker` `ECC` | Fork any project for open-sourcing. |
| `open-source-packager` `ECC` | Generate complete open-source packaging for a sanitized project. |
| `open-source-sanitizer` | Before a repository, a fork or a code sample is made public: it scans the files and the git history for secrets, credentials, personal data, internal… |

</details>

<details><summary><b>network</b> (4)</summary>

| Agente | Cosa fa |
|---|---|
| `homelab-architect` `ECC` | Designs home and small-lab network plans from hardware inventory, goals, and operator experience level, with safe staged changes and rollback guidance. |
| `network-architect` `ECC` | Designs enterprise or multi-site network architecture from requirements, using existing network skills for focused routing, validation, automation, and… |
| `network-config-reviewer` `ECC` | Reviews router and switch configurations for security, correctness, stale references, risky change-window commands, and missing operational guardrails. |
| `network-troubleshooter` `ECC` | Diagnoses network connectivity, routing, DNS, interface, and policy symptoms with a read-only OSI-layer workflow and evidence-backed root cause summary. |

</details>

<details><summary><b>domains</b> (2)</summary>

| Agente | Cosa fa |
|---|---|
| `bengali-reviewer` `ECC` | Reviews code handling Bengali (Bangla) text for Unicode correctness, proper normalization, script-aware processing, and internationalization best practices. |
| `healthcare-reviewer` `ECC` | Reviews healthcare application code for clinical safety, CDSS accuracy, PHI compliance, and medical data integrity. |

</details>

<details><summary><b>ops</b> (1)</summary>

| Agente | Cosa fa |
|---|---|
| `chief-of-staff` `ECC` | Personal communication chief of staff that triages email, Slack, LINE, and Messenger. |

</details>

<details><summary><b>growth</b> (1)</summary>

| Agente | Cosa fa |
|---|---|
| `seo-specialist` | Technical and on-page SEO of a website: crawlability and indexing (robots, sitemaps, canonicals, redirects), metadata and headings, structured data,… |

</details>

<details><summary><b>linguaggi</b> (13 pack, 26 agenti)</summary>

| Pack | Agenti | Cosa controllano |
|---|---|---|
| `cpp` | `cpp-reviewer`, `cpp-build-fixer` | C and C++: memory safety, undefined behavior, ownership, concurrency, modern C++ idioms |
| `csharp` | `csharp-reviewer`, `csharp-build-fixer` | C#: async correctness, nullable references, resource handling, ASP.NET Core and EF Core |
| `dart` | `dart-reviewer`, `dart-build-fixer` | Dart and Flutter: null safety, async, widget lifecycle and rebuilds, state management |
| `fsharp` | `fsharp-reviewer`, `fsharp-build-fixer` | F#: functional design, type safety, pattern matching, async and task code |
| `go` | `go-reviewer`, `go-build-fixer` | Go: error handling, concurrency, context propagation, API and package design |
| `java` | `java-reviewer`, `java-build-fixer` | Java: correctness, resource and transaction handling, concurrency, Spring Boot and Quarkus |
| `kotlin` | `kotlin-reviewer`, `kotlin-build-fixer` | Kotlin: null safety, coroutines and Flow, Android lifecycle, Compose, KMP and Ktor |
| `php` | `php-reviewer`, `php-build-fixer` | PHP: security, types, errors, Laravel and Symfony patterns |
| `python` | `python-reviewer`, `python-build-fixer` | Python: correctness, exceptions, typing, security, Django, FastAPI and data code |
| `ruby` | `ruby-reviewer`, `ruby-build-fixer` | Ruby: correctness, security, Rails patterns and database access |
| `rust` | `rust-reviewer`, `rust-build-fixer` | Rust: ownership and lifetimes, error handling, unsafe code, concurrency, API design |
| `swift` | `swift-reviewer`, `swift-build-fixer` | Swift: memory management, Swift concurrency, value semantics, SwiftUI |
| `typescript` | `typescript-reviewer`, `typescript-build-fixer` | TypeScript and JavaScript: type safety, async correctness, Node and browser security, React, Vue and Next.js |

</details>

### Tutta la libreria (430: 311 skill, 97 comandi, 22 set di regole)

Da Everything Claude Code 2.2.3 (MIT). Cerca con `/team-workflow:library search <parole>`, installa con `library enable <id|pack>`. `ECC runtime` = chiama gli script di ECC: serve `addons add ecc`.

<details><summary><b>agentic-patterns</b> (37): Agentic engineering, autonomous loops, agent harness construction, and LLM pipeline optimization…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `agent-architecture-audit` | skill | Full-stack diagnostic for agent and LLM applications. |
| `agent-harness-construction` | skill | Design and optimize AI agent action spaces, tool definitions, and observation formatting for higher completion rates. |
| `agent-payment-x402` | skill | Add x402 payment execution to AI agents with per-task budgets, spending controls, and non-custodial wallets. |
| `agent-runtime-gateway-smoke-test` | skill | Verify a local agent API, temporary gateway tunnel, and remote sandbox callback with a tool-free task, then restore the original app connection. |
| `agentic-engineering` | skill | Operate as an agentic engineer using eval-first execution, decomposition, and cost-aware model routing. |
| `agentic-os` | skill | Build persistent multi-agent operating systems on Claude Code. |
| `ai-first-engineering` | skill | Engineering operating model for teams where AI agents generate a large share of implementation output. |
| `autonomous-agent-harness` | skill | Transform Claude Code into a fully autonomous agent system with persistent memory, scheduled operations, computer use, and task queuing. |
| `autonomous-loops` | skill | Patterns and architectures for autonomous Claude Code loops — from simple sequential pipelines to RFC-driven multi-agent DAG systems. |
| `blueprint` | skill | Turn a one-line objective into a step-by-step construction plan for multi-session, multi-agent engineering projects: one-PR-sized steps with self-contained… |
| `claude-devfleet` | skill | Orchestrate multi-agent coding tasks via Claude DevFleet — plan projects, dispatch parallel agents in isolated worktrees, monitor progress, and read… |
| `content-hash-cache-pattern` | skill | Cache expensive file processing results using SHA-256 content hashes — path-independent, auto-invalidating, with service layer separation. |
| `continuous-agent-loop` | skill | Patterns for continuous autonomous agent loops with quality gates, evals, and recovery controls. |
| `cost-aware-llm-pipeline` | skill | Cost optimization patterns for LLM API usage — model routing by task complexity, budget tracking, retry logic, and prompt caching. |
| `data-scraper-agent` | skill | Build a fully automated AI-powered data collection agent for any public source — job boards, prices, news, GitHub, sports, anything. |
| `dynamic-workflow-mode` | skill | Design task-local harnesses, eval gates, and reusable skill extraction for Claude dynamic workflow mode and other adaptive agent harnesses. |
| `enterprise-agent-ops` | skill | Operational controls for long-lived or cloud-hosted agent systems — runtime lifecycle (start, pause, stop, restart), observability (logs, metrics, traces),… |
| `gan-style-harness` | skill | GAN-inspired Generator-Evaluator agent harness for building high-quality applications autonomously. |
| `hermes-imports` | skill | Convert local Hermes operator workflows into sanitized ECC skills and release-pack artifacts. |
| `nanoclaw-repl` | skill | Operate and extend NanoClaw, ECC's zero-dependency session-aware REPL, with persistent markdown-backed sessions and slash commands for model switching, skill… |
| `openclaw-persona-forge` | skill | 为 OpenClaw AI Agent 锻造完整的龙虾灵魂方案。根据用户偏好或随机抽卡， 输出身份定位、灵魂描述(SOUL.md)、角色化底线规则、名字和头像生图提示词。 如当前环境提供已审核的生图 skill，可自动生成统一风格头像图片。 当用户需要创建、设计或定制 OpenClaw 龙虾灵魂时使用。… |
| `opensource-pipeline` | skill | Open-source pipeline: fork, sanitize, and package private projects for safe public release. |
| `orch-add-feature` | skill | Orchestrate building a brand-new feature end to end — research, plan, TDD implementation, review, and gated commit — by delegating each phase to the matching… |
| `orch-build-mvp` | skill | Orchestrate bootstrapping a working MVP from a design or spec document — ingest the SDD/PRD, plan thin vertical slices, scaffold the first end-to-end slice,… |
| `orch-change-feature` | skill | Orchestrate altering an existing, working feature to new desired behavior — update its tests to the new spec, change the implementation to match, review, and… |
| `orch-fix-defect` | skill | Orchestrate fixing a bug — reproduce it as a failing regression test, fix to green, review, and gated commit — by delegating each phase to the matching ECC… |
| `orch-pipeline` | skill | Shared orchestration engine behind the orch-* skill family — the gated Research-Plan-TDD-Review-Commit pipeline, size classifier, agent and command map, and… |
| `orch-refine-code` | skill | Orchestrate a behavior-preserving refactor — confirm tests are green, restructure without changing behavior, keep tests green, review, and gated commit. |
| `plan-orchestrate` | skill | Read a plan document, decompose it into steps, classify each step, and emit the ready-to-paste ECC slash command for that step, carrying the step identifier… |
| `prompt-caching-strategy` | skill | Optimize LLM prompt caching hit rate to reduce API costs and improve latency. |
| `prompt-optimizer` | skill | Analyze draft prompts, detect intent and missing context, match ECC commands, skills, and agents, and output a ready-to-paste optimized prompt with diagnosis… |
| `ralphinho-rfc-pipeline` | skill | Split an RFC into a multi-agent execution DAG — decompose into work units with dependencies and acceptance tests, run research, plan, implement, test, and… |
| `regex-vs-llm-structured-text` | skill | Decision framework for parsing structured text (quizzes, forms, invoices, receipts, tables) with a hybrid regex-first pipeline — regex extraction handles 95%+… |
| `search-first` | skill | Research-before-coding workflow: search npm/PyPI, MCP servers, skills, and GitHub for existing tools before writing custom code, then adopt, extend, or build. |
| `team-agent-orchestration` | skill | Run team-based orchestration for agent squads: work items with owners and scope, agent Kanban state, branch isolation, control pane visibility, and merge gates. |
| `team-builder` | skill | Interactive picker that discovers available agent personas via the claude agents command and agents/ markdown globs, groups them into domains, has the user… |
| `token-budget-advisor` | skill | Offer a choice of response depth (25%/50%/75%/100%) with token estimates before answering, then answer at that level. |

</details>

<details><summary><b>business-content</b> (14): Business, writing, market, and investor communication skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `article-writing` | skill | Write articles, guides, blog posts, tutorials, newsletter issues, and other long-form content in a distinctive voice derived from supplied examples or brand… |
| `brand-discovery` | skill | Run a structured, resumable multi-session brand identity interview across 8 modules (purpose, positioning, audience, personality, voice, narrative, founder… |
| `brand-voice` | skill | Build a source-derived writing style profile from real posts, essays, launch notes, docs, or site copy, then reuse that profile across content, outreach, and… |
| `competitive-platform-analysis` | skill | Use when scoping a competitive landscape — identifying, categorising, and score-filtering a competitor set before any benchmarking begins. |
| `competitive-report-structure` | skill | Assemble scored competitor profile cards (from benchmark-methodology) into a decision-grade competitive report with landscape map, competitor tiers,… |
| `content-engine` | skill | Create platform-native content systems for X, LinkedIn, TikTok, YouTube, newsletters, and repurposed multi-platform campaigns. |
| `investor-materials` | skill | Create and update pitch decks, one-pagers, investor memos, accelerator applications, financial models, and fundraising materials. |
| `investor-outreach` | skill | Draft cold emails, warm intro blurbs, follow-ups, update emails, and investor communications for fundraising. |
| `lead-intelligence` | skill | AI-native lead intelligence and outreach pipeline. |
| `market-research` | skill | Conduct market research, competitive analysis, investor due diligence, and industry intelligence with source attribution and decision-oriented summaries. |
| `marketing-campaign` | skill | End-to-end marketing campaign planning and execution. |
| `product-capability` | skill | Translate PRD intent, roadmap asks, or product discussions into an implementation-ready capability plan that exposes constraints, invariants, interfaces, and… |
| `seo` | skill | Audit, plan, and implement SEO improvements across technical SEO, on-page optimization, structured data, Core Web Vitals, and content strategy. |
| `social-graph-ranker` | skill | Weighted social-graph ranking for warm intro discovery, bridge scoring, and network gap analysis across X and LinkedIn. |

</details>

<details><summary><b>commands</b> (97): ECC slash commands, installed as skills you call by name.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `aside` | command | Answer a quick side question without interrupting or losing context from the current task. |
| `astra-review` | command | Send Claude-written code to GPT-6-Astra (ChatGPT, via Codex CLI) for an independent cross-provider review, then fix what it finds. (`ECC runtime`) |
| `auto-update` | command | Pull the latest ECC repo changes and reinstall the current managed targets. (`ECC runtime`) |
| `build-fix` | command | Detect the project build system and incrementally fix build/type errors with minimal safe changes. |
| `checkpoint` | command | Create, verify, or list workflow checkpoints after running verification checks. |
| `code-review` | command | Code review — local uncommitted changes or GitHub PR (pass PR number/URL for PR mode). |
| `cost-report` | command | Generate a local Claude Code cost report from the ECC cost-tracker metrics log. |
| `cpp-build` | command | Fix C++ build errors, CMake issues, and linker problems incrementally. |
| `cpp-review` | command | Comprehensive C++ code review for memory safety, modern C++ idioms, concurrency, and security. |
| `cpp-test` | command | Enforce TDD workflow for C++. |
| `ecc-guide-command` | command | Navigate ECC's current agents, skills, commands, hooks, install profiles, and docs from the live repository surface. |
| `epic-claim` | command | Claim an epic issue, stamp coordination state, and sync local ownership. |
| `epic-decompose` | command | Break an epic into task children without creating task branches. |
| `epic-publish` | command | Publish a validated epic update back to the issue and local cache. |
| `epic-review` | command | Mark epic review requested, approved, or changes requested. |
| `epic-sync` | command | Sync epic issue bodies, labels, and local coordination snapshots from GitHub. |
| `epic-unblock` | command | Sweep blocked epic issues and reopen anything whose dependencies are closed. |
| `epic-validate` | command | Validate epic readiness, dependencies, and coordination policy. |
| `evolve` | command | Analyze instincts and suggest or generate evolved structures (`ECC runtime`) |
| `fastapi-review` | command | Review a FastAPI application for architecture, async correctness, dependency injection, Pydantic schemas, security, performance, and testability. |
| `feature-dev` | command | Guided feature development with codebase understanding and architecture focus |
| `flutter-build` | command | Fix Dart analyzer errors and Flutter build failures incrementally. |
| `flutter-review` | command | Review Flutter/Dart code for idiomatic patterns, widget best practices, state management, performance, accessibility, and security. |
| `flutter-test` | command | Run Flutter/Dart tests, report failures, and incrementally fix test issues. |
| `gan-build` | command | Run a generator/evaluator build loop for implementation tasks with bounded iterations and scoring. |
| `gan-design` | command | Run a generator/evaluator design loop for frontend or visual work with bounded iterations and scoring. |
| `go-build` | command | Fix Go build errors, go vet warnings, and linter issues incrementally. |
| `go-review` | command | Comprehensive Go code review for idiomatic patterns, concurrency safety, error handling, and security. |
| `go-test` | command | Enforce TDD workflow for Go. |
| `gradle-build` | command | Fix Gradle build errors for Android and KMP projects |
| `harness-audit` | command | Run a deterministic repository harness audit and return a prioritized scorecard. |
| `hookify` | command | Create hooks to prevent unwanted behaviors from conversation analysis or explicit instructions. |
| `hookify-configure` | command | Enable or disable hookify rules interactively |
| `hookify-help` | command | Get help with the hookify system |
| `hookify-list` | command | List all configured hookify rules |
| `instinct-export` | command | Export instincts from project/global scope to a file |
| `instinct-import` | command | Import instincts from file or URL into project/global scope (`ECC runtime`) |
| `instinct-status` | command | Show learned instincts (project + global) with confidence (`ECC runtime`) |
| `jira` | command | Retrieve a Jira ticket, analyze requirements, update status, or add comments. |
| `kotlin-build` | command | Fix Kotlin/Gradle build errors, compiler warnings, and dependency issues incrementally. |
| `kotlin-review` | command | Comprehensive Kotlin code review for idiomatic patterns, null safety, coroutine safety, and security. |
| `kotlin-test` | command | Enforce TDD workflow for Kotlin. |
| `learn` | command | Extract reusable patterns from the current session and save them as candidate skills or guidance. |
| `learn-eval` | command | Extract reusable patterns from the session, self-evaluate quality before saving, and determine the right save location (Global vs Project). |
| `loop-start` | command | Prepare a managed autonomous loop pattern with safety defaults and explicit stop conditions, then print the commands to launch and monitor it. |
| `loop-status` | command | Inspect active loop state, progress, failure signals, and recommended intervention. |
| `marketing-campaign-command` | command | Plan and execute a full marketing campaign. |
| `model-route` | command | Recommend the best model tier for the current task based on complexity, risk, and budget. |
| `multi-backend` | command | Run a backend-focused multi-model workflow for APIs, algorithms, data, and business logic. |
| `multi-execute` | command | Execute a multi-model implementation plan while preserving Claude as the only filesystem writer. |
| `multi-frontend` | command | Run a frontend-focused multi-model workflow for components, layouts, animation, and UI polish. |
| `multi-plan` | command | Create a multi-model (Codex + Antigravity) implementation plan without modifying production code. |
| `multi-workflow` | command | Run a full multi-model development workflow with research, planning, execution, optimization, and review. |
| `orch-add-feature-command` | command | Orchestrate building a brand-new feature end to end — research, plan, TDD, review, gated commit. |
| `orch-build-mvp-command` | command | Orchestrate bootstrapping a working MVP from a design/spec doc — ingest, slice, scaffold, TDD, review, gated commit (reuses the GAN harness). |
| `orch-change-feature-command` | command | Orchestrate altering an existing, working feature to new desired behavior — update tests to the new spec, change impl, review, gated commit. |
| `orch-fix-defect-command` | command | Orchestrate fixing a bug — reproduce it as a failing regression test, fix to green, review, gated commit. |
| `orch-refine-code-command` | command | Orchestrate a behavior-preserving refactor — confirm tests green, restructure without changing behavior, keep green, review, gated commit. |
| `orch-review` | command | Run the orch-review native Workflow over a diff (local changes or a GitHub PR) and report blocking vs advisory findings. |
| `plan` | command | Restate requirements, assess risks, and create step-by-step implementation plan. |
| `plan-canvas-command` | command | Open a plan or HTML artifact in the browser Plan Canvas for annotate-and-approve review. |
| `plan-prd` | command | Generate a lean, problem-first PRD and hand off to /plan for implementation planning. |
| `pm2` | command | Analyze a project and generate PM2 service commands for detected frontend, backend, or database services. |
| `pr` | command | Create a GitHub PR from current branch with unpushed commits — discovers templates, analyzes changes, pushes |
| `project-init` | command | Detect a project's stack and produce a dry-run ECC onboarding plan using the repository's install manifests and stack mappings. |
| `projects` | command | List known projects and their instinct statistics (`ECC runtime`) |
| `promote` | command | Promote project-scoped instincts to global scope (`ECC runtime`) |
| `prp-commit` | command | Quick commit with natural language file targeting — describe what to commit in plain English |
| `prp-implement` | command | Execute an implementation plan with rigorous validation loops |
| `prp-plan` | command | Create comprehensive feature implementation plan with codebase analysis and pattern extraction |
| `prp-pr` | command | Alias of /pr for the PRP workflow series. |
| `prp-prd` | command | Interactive PRD generator - problem-first, hypothesis-driven product spec with back-and-forth questioning |
| `prune` | command | Delete pending instincts older than 30 days that were never promoted. (`ECC runtime`) |
| `python-review` | command | Comprehensive Python code review for PEP 8 compliance, type hints, security, and Pythonic idioms. |
| `quality-gate` | command | Run the ECC formatter quality gate for a single file and report remediation steps. |
| `react-build` | command | Fix React build failures (Vite, webpack, Next.js, CRA, Parcel, esbuild, Bun) incrementally — JSX/TSX compile errors, hydration mismatches, server/client… |
| `react-review` | command | Comprehensive React/JSX code review for hook correctness, render performance, server/client component boundaries, accessibility, and React-specific security. |
| `react-test` | command | Enforce TDD workflow for React. |
| `refactor-clean` | command | Safely identify and remove dead code with verification after each change. |
| `resume-session` | command | Load the most recent session file from ~/.claude/session-data/ and resume work with full context from where the last session ended. |
| `review-pr` | command | Comprehensive PR review using specialized agents (code-reviewer, comment-analyzer, pr-test-analyzer, silent-failure-hunter, type-design-analyzer,… |
| `rust-build` | command | Fix Rust build errors, borrow checker issues, and dependency problems incrementally. |
| `rust-review` | command | Comprehensive Rust code review for ownership, lifetimes, error handling, unsafe usage, and idiomatic patterns. |
| `rust-test` | command | Enforce TDD workflow for Rust. |
| `santa-loop` | command | Adversarial dual-review convergence loop — two independent model reviewers must both approve before code ships. |
| `save-session` | command | Save current session state to a dated file in ~/.claude/session-data/ so work can be resumed in a future session with full context. |
| `security-scan-command` | command | Run AgentShield against agent, hook, MCP, permission, and secret surfaces. |
| `sessions` | command | Manage Claude Code session history, aliases, and session metadata. (`ECC runtime`) |
| `setup-pm` | command | Configure your preferred package manager (npm/pnpm/yarn/bun) |
| `skill-create` | command | Analyze local git history to extract coding patterns and generate SKILL.md files. |
| `skill-health` | command | Show skill portfolio health dashboard with charts and analytics. (`ECC runtime`) |
| `skill-host-compat-command` | command | Lint ECC skills for Codex/Cursor-safe frontmatter and Claude-only substitutions before a skill PR. (`ECC runtime`) |
| `test-coverage` | command | Analyze coverage, identify gaps, and generate missing tests toward the target threshold. |
| `token-card-command` | command | Render a token-usage stat card from local agent session logs and commit it to the repo. |
| `update-codemaps` | command | Scan project structure and generate token-lean architecture codemaps. |
| `update-docs` | command | Sync documentation from source-of-truth files such as scripts, schemas, routes, and exports. |
| `vue-review` | command | Comprehensive Vue.js code review for Composition API correctness, reactivity, composable patterns, template security, accessibility, and Vue-specific… |

</details>

<details><summary><b>database</b> (8): Database and persistence-focused skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `clickhouse-io` | skill | ClickHouse database patterns, query optimization, analytics, and data engineering best practices for high-performance analytical workloads. |
| `database-migrations` | skill | Safe, reversible database migration patterns: forward-only production changes, expand-contract zero-downtime renames, concurrent indexes, batched backfills,… |
| `jpa-patterns` | skill | JPA/Hibernate patterns for entity design, relationships, query optimization, transactions, auditing, indexing, pagination, and pooling in Spring Boot. |
| `mybatis-patterns` | skill | MyBatis and MyBatis-Spring patterns for mapper design, XML and annotation SQL, result mapping, dynamic SQL safety, transactions, batching, pagination, and… |
| `mysql-patterns` | skill | MySQL and MariaDB schema, query, indexing, transaction, replication, and connection-pool patterns for production backends. |
| `postgres-patterns` | skill | PostgreSQL database patterns for query optimization, schema design, indexing, and security. |
| `prisma-patterns` | skill | Prisma ORM patterns for TypeScript backends — schema design, query optimization, transactions, pagination, and critical traps like updateMany returning count… |
| `redis-patterns` | skill | Redis data structure patterns, caching strategies, distributed locks, rate limiting, pub/sub, and connection management for production applications. |

</details>

<details><summary><b>devops-infra</b> (17): Deployment workflows, Docker patterns, and infrastructure skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `canary-watch` | skill | Use this skill to monitor and verify a deployed URL after releases — checks HTTP endpoints, SSE streams, static assets, console errors, and performance… |
| `cisco-ios-patterns` | skill | Cisco IOS and IOS-XE review patterns for show commands, config hierarchy, wildcard masks, ACL placement, interface hygiene, and safe change-window verification. |
| `deployment-patterns` | skill | Deployment workflows, CI/CD pipeline patterns, Docker containerization, health checks, rollback strategies, and production readiness checklists for web… |
| `docker-patterns` | skill | Docker and Docker Compose patterns for local development, hardened CLI installer harnesses, container security, networking, volumes, and multi-service… |
| `flox-environments` | skill | Create reproducible, cross-platform (macOS/Linux) development environments with Flox, a declarative Nix-based environment manager. |
| `homelab-network-readiness` | skill | Readiness checklist for homelab VLAN segmentation, local DNS filtering (Pi-hole, AdGuard Home), and WireGuard-style remote access. |
| `homelab-network-setup` | skill | Practical home and homelab network planning for gateways, switches, access points, IP ranges, DHCP reservations, DNS, cabling, and common beginner mistakes. |
| `homelab-pihole-dns` | skill | Pi-hole installation, blocklist management, DNS-over-HTTPS setup, DHCP integration, local DNS records, and troubleshooting broken DNS resolution on a home… |
| `homelab-vlan-segmentation` | skill | Segmenting home networks into VLANs for IoT, guest, trusted, and server traffic using UniFi, pfSense/OPNsense, and MikroTik — including switch trunk config,… |
| `homelab-wireguard-vpn` | skill | WireGuard VPN server setup, peer configuration, key generation, split tunneling vs full tunnel routing, and remote access to a home network from mobile and… |
| `kubernetes-patterns` | skill | Kubernetes workload patterns, resource management, RBAC, probes, autoscaling, ConfigMap/Secret handling, and kubectl debugging for production-grade deployments. |
| `netmiko-ssh-automation` | skill | Safe Python Netmiko patterns for read-only collection, bounded batch SSH, TextFSM parsing, guarded config changes, timeouts, and network automation error… |
| `network-bgp-diagnostics` | skill | Diagnostics-only BGP troubleshooting patterns for neighbor state, route exchange, prefix policy, AS path inspection, and safe evidence collection. |
| `network-config-validation` | skill | Pre-deployment checks for router and switch configuration, including dangerous commands, duplicate addresses, subnet overlaps, stale references,… |
| `network-interface-health` | skill | Diagnose interface errors, drops, CRCs, duplex mismatches, flapping, speed negotiation issues, and counter trends on routers, switches, and Linux hosts. |
| `terminal-opener` | skill | Open an executable and its argument array in a visible terminal window through a reusable, shell-free launch plan with dry-run, JSON, capability detection,… |
| `uncloud` | skill | Use when managing an Uncloud cluster — deploying services, configuring Caddy ingress, adding static proxy routes for non-cluster devices, publishing ports,… |

</details>

<details><summary><b>document-processing</b> (2): Document processing, conversion, and translation skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `nutrient-document-processing` | skill | Process, convert, OCR, extract, redact, sign, and fill documents using the Nutrient DWS API. |
| `visa-doc-translate` | skill | Translate visa document images (bank deposit, employment, income, and retirement certificates; HEIC, PNG, or JPG) into English via OCR and produce a bilingual… |

</details>

<details><summary><b>documentation-change-impact</b> (1): Optional read-only change-impact analysis workflow.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `change-impact` | skill | Perform evidence-backed impact analysis before changing code, data, interfaces, or governance documents, then compare the planned impact with the actual diff… |

</details>

<details><summary><b>documentation-context</b> (1): Optional durable domain-context and ADR handoff workflow.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `context-and-decisions` | skill | Govern stable domain context with a narrowly scoped CONTEXT.md when needed, and route hard-to-reverse decisions to ECC's existing… |

</details>

<details><summary><b>documentation-governance</b> (1): Optional documentation-governance routing and deterministic read-only audits.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `docs-governance` | skill | Route broad documentation-governance requests to existing ECC skills and run an opt-in, read-only audit of mapped documentation roles, links, ADR indexes, and… |

</details>

<details><summary><b>documentation-test-regression</b> (2): Optional test-collaboration and module-regression workflow.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `module-regression` | skill | Govern cross-module regression in large repositories with a REGRESSION.md ledger that records each module's downstream consumers and executable acceptance… |
| `test-collaboration` | skill | Inventory and govern a project's test assets. |

</details>

<details><summary><b>framework-language</b> (71): Core framework, language, and application-engineering skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `accessibility` | skill | Design, implement, and audit accessible UI to WCAG 2.2 Level AA across Web, iOS, and Android — semantic ARIA roles and labels, accessibility traits and hints,… |
| `android-clean-architecture` | skill | Clean Architecture patterns for Android and Kotlin Multiplatform projects — module structure, dependency rules, UseCases, Repositories, and data layer patterns. |
| `angular-developer` | skill | Generates Angular code and provides architectural guidance. |
| `api-design` | skill | REST API design patterns including resource naming, status codes, pagination, filtering, error responses, versioning, and rate limiting for production APIs. |
| `backend-patterns` | skill | Backend architecture patterns, API design, database optimization, and server-side best practices for Node.js, Express, and Next.js API routes. |
| `bengali-nlp` | skill | Bengali (Bangla) text processing patterns including Unicode normalization, script detection, tokenization, conjunct handling, and Bangla-specific NLP best… |
| `bun-runtime` | skill | Bun as runtime, package manager, bundler, and test runner. |
| `coding-standards` | skill | Baseline cross-project coding conventions for naming, readability, immutability, and code-quality review. |
| `compose-multiplatform-patterns` | skill | Compose Multiplatform and Jetpack Compose patterns for KMP projects — state management, navigation, theming, performance, and platform-specific UI. |
| `contract-first` | skill | Coordinate frontend/backend or service-to-service work through one authoritative machine-checkable contract (OpenAPI, AsyncAPI, Protocol Buffers, or JSON… |
| `cpp-coding-standards` | skill | C++ coding standards based on the C++ Core Guidelines (isocpp.github.io). |
| `cpp-testing` | skill | Use only when writing/updating/fixing C++ tests, configuring GoogleTest/CTest, diagnosing failing or flaky tests, or adding coverage/sanitizers. |
| `csharp-testing` | skill | C# and .NET testing patterns with xUnit, FluentAssertions, mocking, integration tests, and test organization best practices. |
| `dart-flutter-patterns` | skill | Production-ready Dart and Flutter patterns covering null safety, immutable state with Freezed, async composition, widget architecture, state management (BLoC,… |
| `design-system` | skill | Generate a design system from an existing codebase or audit one for visual consistency: extract tokens (colors, typography, spacing, shadows) into… |
| `django-celery` | skill | Django + Celery async task patterns — configuration, task design, beat scheduling, retries, canvas workflows, monitoring, and testing. |
| `django-patterns` | skill | Django architecture patterns, REST API design with DRF, ORM best practices, caching, signals, middleware, and production-grade Django apps. |
| `django-tdd` | skill | Django testing strategies with pytest-django, TDD methodology, factory_boy, mocking, coverage, and testing Django REST Framework APIs. |
| `django-verification` | skill | Run the full Django verification loop — environment check, mypy/ruff/black linting, migration safety, pytest with coverage targets, pip-audit and bandit… |
| `dotnet-patterns` | skill | Idiomatic C# and .NET patterns, conventions, dependency injection, async/await, and best practices for building robust, maintainable .NET applications. |
| `fastapi-patterns` | skill | FastAPI best practices covering project structure, Pydantic v2 schemas, dependency injection, async handlers, authentication, authorization, transactional… |
| `flutter-dart-code-review` | skill | Library-agnostic Flutter/Dart code review checklist covering widget best practices, state management patterns (BLoC, Riverpod, Provider, GetX, MobX, Signals),… |
| `frontend-a11y` | skill | Accessibility patterns for React and Next.js — semantic HTML, ARIA attributes, form labeling, keyboard navigation, focus management, and screen reader support. |
| `frontend-design-direction` | skill | Set an ECC-specific frontend design direction for production UI work. |
| `frontend-patterns` | skill | Frontend development patterns for React, Next.js, state management, performance optimization, and UI best practices. |
| `frontend-slides` | skill | Create stunning, animation-rich HTML presentations from scratch or by converting PowerPoint files. |
| `fsharp-testing` | skill | F# testing patterns with xUnit, FsUnit, Unquote, FsCheck property-based testing, integration tests, and test organization best practices. |
| `generating-python-installer` | skill | Commercial-grade Python installer expert for Windows: Nuitka extreme compilation, dist slimming, DLL footprint analysis, and Inno Setup packaging to ship the… |
| `golang-patterns` | skill | Idiomatic Go patterns, best practices, and conventions for building robust, efficient, and maintainable Go applications. |
| `golang-testing` | skill | Go testing patterns including table-driven tests, subtests, benchmarks, fuzzing, and test coverage. |
| `hexagonal-architecture` | skill | Design, implement, and refactor Ports & Adapters systems with clear domain boundaries, dependency inversion, and testable use-case orchestration across… |
| `i18n-sync` | skill | Translate and synchronize application JSON locale files using source-key usage, project terminology, and focused validation. |
| `java-coding-standards` | skill | Java coding standards for Spring Boot and Quarkus services: naming, immutability, Optional usage, streams, exceptions, generics, CDI, reactive patterns, and… |
| `kotlin-coroutines-flows` | skill | Kotlin Coroutines and Flow patterns for Android and KMP — structured concurrency, Flow operators, StateFlow, error handling, and testing. |
| `kotlin-exposed-patterns` | skill | JetBrains Exposed ORM patterns including DSL queries, DAO pattern, transactions, HikariCP connection pooling, Flyway migrations, and repository pattern. |
| `kotlin-ktor-patterns` | skill | Ktor server patterns including routing DSL, plugins, authentication, Koin DI, kotlinx.serialization, WebSockets, and testApplication testing. |
| `kotlin-patterns` | skill | Idiomatic Kotlin patterns, best practices, and conventions for building robust, efficient, and maintainable Kotlin applications with coroutines, null safety,… |
| `kotlin-testing` | skill | Kotlin testing patterns with Kotest, MockK, coroutine testing, property-based testing, and Kover coverage. |
| `laravel-patterns` | skill | Laravel architecture patterns, routing/controllers, Eloquent ORM, service layers, queues, events, caching, and API resources for production apps. |
| `laravel-plugin-discovery` | skill | Discover and evaluate Laravel packages via LaraPlugins.io MCP. |
| `laravel-tdd` | skill | Laravel testing strategies with PHPUnit, Pest, model factories, HTTP tests, Sanctum authentication testing, mocking, and coverage. |
| `laravel-verification` | skill | Verification loop for Laravel projects: env checks, linting, static analysis, tests with coverage, security scans, and deployment readiness. |
| `make-interfaces-feel-better` | skill | Apply concrete design-engineering details that make interfaces feel polished. |
| `mcp-server-patterns` | skill | Build MCP servers with Node/TypeScript SDK — tools, resources, prompts, Zod validation, stdio vs Streamable HTTP. |
| `motion-advanced` | skill | Advanced motion patterns for React / Next.js — drag & drop, gestures, text animations, SVG path drawing, custom hooks, imperative sequences (useAnimate),… |
| `motion-foundations` | skill | Motion tokens, spring presets, performance rules, device adaptation, accessibility enforcement, and SSR safety for React / Next.js using motion/react. |
| `motion-patterns` | skill | Production-ready animation patterns for React / Next.js — button, modal, toast, stagger, page transitions, exit animations, scroll, and layout — built on… |
| `nestjs-patterns` | skill | NestJS architecture patterns for modules, controllers, providers, DTO validation, guards, interceptors, config, and production-grade TypeScript backends. |
| `nextjs-turbopack` | skill | Next.js 16+ and Turbopack guidance — incremental Rust bundling, file-system caching, faster dev startup and HMR, Turbopack vs webpack tradeoffs, and the… |
| `nuxt4-patterns` | skill | Nuxt 4 app patterns for hydration safety, performance, route rules, lazy loading, and SSR-safe data fetching with useFetch and useAsyncData. |
| `perl-patterns` | skill | Modern Perl 5.36+ idioms, best practices, and conventions for building robust, maintainable Perl applications. |
| `perl-testing` | skill | Perl testing patterns using Test2::V0, Test::More, prove runner, mocking, coverage with Devel::Cover, and TDD methodology. |
| `python-patterns` | skill | Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python applications. |
| `python-testing` | skill | Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements. |
| `quarkus-patterns` | skill | Quarkus 3.x LTS architecture patterns with Camel for messaging, RESTful API design, CDI services, data access with Panache, and async processing. |
| `quarkus-tdd` | skill | Test-driven development for Quarkus 3.x LTS using JUnit 5, Mockito, REST Assured, Camel testing, and JaCoCo. |
| `quarkus-verification` | skill | Verification loop for Quarkus projects: build, static analysis (Checkstyle, PMD, SpotBugs), tests with JaCoCo coverage, OWASP dependency and container… |
| `rails-patterns` | skill | Ruby on Rails framework patterns for Rails 7.1+ and 8.x apps. |
| `react-native-patterns` | skill | React Native and Expo app patterns — Expo Router navigation, state separation (server/client/route/form), TanStack Query data fetching with Zod, performant… |
| `react-patterns` | skill | React 18/19 patterns including hooks discipline, server/client component boundaries, Suspense + error boundaries, form actions, data fetching, state… |
| `react-performance` | skill | React and Next.js performance optimization patterns adapted from Vercel Engineering's React Best Practices (https://github.com/vercel-labs/agent-skills). |
| `react-testing` | skill | React component testing with React Testing Library, Vitest/Jest, MSW for network mocking, accessibility assertions with axe, and the decision boundary between… |
| `rust-patterns` | skill | Idiomatic Rust patterns, ownership, error handling, traits, concurrency, and best practices for building safe, performant applications. |
| `rust-testing` | skill | Rust testing patterns including unit tests, integration tests, async testing, property-based testing, mocking, and coverage. |
| `springboot-patterns` | skill | Spring Boot architecture patterns, REST API design, layered services, data access, caching, async processing, and logging. |
| `springboot-tdd` | skill | Test-driven development for Spring Boot using JUnit 5, Mockito, MockMvc, Testcontainers, and JaCoCo. |
| `springboot-verification` | skill | Run the full Spring Boot verification loop — Maven or Gradle build, SpotBugs, PMD, and Checkstyle static analysis, unit and Testcontainers integration tests… |
| `tinystruct-patterns` | skill | Expert guidance for developing with the tinystruct Java framework. |
| `ui-to-vue` | skill | Use when the user has UI screenshots or design exports that need batch conversion into Vue 3 components, especially with Vant, Element Plus, or Ant Design Vue. |
| `vite-patterns` | skill | Vite build tool patterns including config, plugins, HMR, env variables, proxy setup, SSR, library mode, dependency pre-bundling, and build optimization. |
| `vue-patterns` | skill | Vue.js 3 Composition API patterns, component architecture, reactivity best practices, Pinia state management, Vue Router navigation, and Nuxt SSR patterns. |

</details>

<details><summary><b>ito-compute-pack</b> (3): Authenticated Itô GPU inventory, RFQ, status, device revocation, and explicitly gated…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `ito-compute` | skill | Query live GPU inventory, submit an authenticated Itô fixed-rate RFQ, inspect RFQ or procurement status, revoke device credentials, and run explicitly gated… |
| `ito-inference` | skill | Inspect the availability of model serving on a completed Itô compute booking and, when the canonical backend becomes available, hand off an explicitly… |
| `ito-training` | skill | Inspect the availability of ML training on a completed Itô compute booking and, when the canonical backend becomes available, hand off an explicitly confirmed… |

</details>

<details><summary><b>machine-learning</b> (4): Production machine-learning engineering workflows for data contracts, reproducible training,…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `ml-adoption-playbook` | skill | End-to-end methodology for AI agents and software engineers to add machine learning algorithms to existing non-ML codebases. |
| `mle-workflow` | skill | Production machine-learning engineering workflow for data contracts, reproducible training, model evaluation, deployment, monitoring, and rollback. |
| `pytorch-patterns` | skill | PyTorch deep learning patterns and best practices for building robust, efficient, and reproducible training pipelines, model architectures, and data loading. |
| `recsys-pipeline-architect` | skill | Design composable recommendation, ranking, and feed pipelines using the six-stage Source→Hydrator→Filter→Scorer→Selector→SideEffect framework popularized by… |

</details>

<details><summary><b>media-generation</b> (11): Media generation, technical explainers, and AI-assisted editing skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `blender-motion-state-inspection` | skill | Use this skill when inspecting Blender characters, rigs, poses, animation retargeting, ground contact, facing direction, or model-vs-motion alignment where… |
| `fal-ai-media` | skill | Unified media generation via fal.ai MCP — image, video, and audio. |
| `manim-video` | skill | Build reusable Manim explainers for technical concepts, graphs, system diagrams, and product walkthroughs, then hand off to the wider ECC video stack if needed. |
| `remotion-video-creation` | skill | Best practices for Remotion - Video creation in React. |
| `taste` | skill | Creative-direction layer for music videos and short-form edits in the angelcore / cloud-trance / hyperpop family — a named-genre aesthetic vocabulary, mood +… |
| `taste-application` | skill | Generate new video against a distilled style pack and cut it into a finished piece - plan takes from the reference's cut rhythm, generate on fal, grade with… |
| `taste-distillation` | skill | Measure a set of reference videos into a reusable style pack - colour grade as a 3D LUT, cut rhythm as a shot-length distribution, hero stills, screen-blend… |
| `tasteforge-video` | skill | Use for file-driven multimodal image, video, and 3D-asset discovery; taste interviews; distill or apply workflows; style-pack validation; editable EDL/FCPXML… |
| `ui-demo` | skill | Record polished UI demo videos using Playwright. |
| `video-editing` | skill | AI-assisted video editing workflows for cutting, structuring, and augmenting real footage. |
| `videodb` | skill | Ingest, index, search, edit, and monitor video and audio with the VideoDB Python SDK — upload from files, URLs, or RTSP feeds, build spoken and scene indexes… |

</details>

<details><summary><b>nasiko-control-plane-pack</b> (1): Experimental Nasiko CLI lifecycle bridge guidance for pinned installation, read-only status,…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `nasiko-control-plane` | skill | Manage the experimental Nasiko CLI lifecycle through ECC — read-only status checks, consent-gated install of the pinned qualified version with dry-run… |

</details>

<details><summary><b>operator-desk-patterns</b> (4): Generic operator desk patterns: never-silent approval loop, counterparty channel discipline,…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `counterparty-channel-discipline` | skill | Per-channel strict prompts, mention gating, silent observation, and a communication autonomy policy for agents that sit in shared channels with external… |
| `esign-field-placement` | skill | Deterministic method for placing signature, date, and text fields in a web e-signature composer through a browser automation session, using a fixed signature… |
| `master-agreement-generator` | skill | Generate review drafts of counterparty master agreements from one template plus a JSON spec, with role-selected clauses and a Schedule A workflow limited to… |
| `operator-approval-loop` | skill | Operator approval contract with internal filing notices for agent-drafted outbound messages, hashed drafts, epoch-keyed decisions, durable delivery claims and… |

</details>

<details><summary><b>operator-workflows</b> (20): Connected-app operator workflows for setup audits, billing operations, program tracking, Google…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `api-connector-builder` | skill | Build a new API connector or provider by matching the target repo's existing integration pattern exactly. |
| `automation-audit-ops` | skill | Evidence-first automation inventory and overlap audit workflow for ECC. |
| `connections-optimizer` | skill | Reorganize the user's X and LinkedIn network with review-first pruning, add/follow recommendations, and channel-specific warm outreach drafted in the user's… |
| `cost-tracking` | skill | Track and report Claude Code token usage, spending, and budgets from the local ECC cost-tracker metrics log. |
| `customer-billing-ops` | skill | Operate customer billing workflows such as subscriptions, refunds, churn triage, billing-portal recovery, and plan analysis using connected billing tools like… |
| `dashboard-builder` | skill | Build monitoring dashboards that answer real operator questions for Grafana, SigNoz, and similar platforms. |
| `ecc-tools-cost-audit` | skill | Evidence-first ECC Tools burn and billing audit workflow. |
| `email-ops` | skill | Evidence-first mailbox triage, drafting, send verification, and sent-mail-safe follow-up workflow for ECC. |
| `finance-billing-ops` | skill | Evidence-first revenue, pricing, refunds, team-billing, and billing-model truth workflow for ECC. |
| `github-ops` | skill | GitHub repository operations, automation, and management. |
| `google-workspace-ops` | skill | Operate across Google Drive, Docs, Sheets, and Slides as one workflow surface for plans, trackers, decks, and shared documents. |
| `jira-integration` | skill | Use this skill when retrieving Jira tickets, analyzing requirements, updating ticket status, adding comments, or transitioning issues. |
| `knowledge-ops` | skill | Knowledge base management, ingestion, sync, and retrieval across multiple storage layers (local files, MCP memory, vector stores, Git repos). |
| `mailtrap-email-integration` | skill | Guides agents through integrating transactional email sending via Mailtrap's Email API, including sandbox testing, domain verification, and API authentication. |
| `messages-ops` | skill | Evidence-first live messaging workflow for ECC. |
| `project-flow-ops` | skill | Operate execution flow across GitHub and Linear by triaging issues and pull requests, linking active work, and keeping GitHub public-facing while Linear… |
| `terminal-ops` | skill | Evidence-first repo execution workflow for ECC. |
| `token-card` | skill | Render a token-usage stat card from local Claude Code, Codex, Gemini CLI, and OpenCode session logs and commit it into the repository as a file. |
| `unified-notifications-ops` | skill | Operate notifications as one ECC-native workflow across GitHub, Linear, desktop alerts, hooks, and connected communication surfaces. |
| `workspace-surface-audit` | skill | Audit the active repo, MCP servers, plugins, connectors, env surfaces, and harness setup, then recommend the highest-value ECC-native skills, hooks, agents,… |

</details>

<details><summary><b>optimization-workflows</b> (8): Parallel execution, benchmarking, data-throughput, latency, and recursive decision-ledger skills…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `agent-eval` | skill | Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics. |
| `benchmark` | skill | Measure performance baselines and detect regressions across browser Core Web Vitals (LCP, INP, CLS, page weight), API endpoint latency percentiles, and… |
| `benchmark-methodology` | skill | Score a scoped competitor set into comparable profile cards: nine weighted dimensions (positioning, voice, visual craft, offer packaging, evidence,… |
| `benchmark-optimization-loop` | skill | Convert 'make it faster' requests into a bounded measured optimization loop — baseline first, generate one-hypothesis variants, benchmark each against a… |
| `data-throughput-accelerator` | skill | Diagnose and accelerate large data movement — ingestion, backfill, export, ETL, warehouse loading, manifest catch-up, and table synchronization — by isolating… |
| `latency-critical-systems` | skill | Optimize and verify latency-sensitive systems — realtime dashboards, market data feeds, streaming agents, execution gateways, queues, and caches — by tracking… |
| `parallel-execution-optimizer` | skill | Speed up a task by turning it into a dependency graph of parallel lanes with a lane matrix, batched reads and checks, write surfaces isolated by file,… |
| `recursive-decision-ledger` | skill | Run repeated rollouts ("Prime Gauss" style recursive prompting) while keeping an append-only decision ledger of trials, marks, coherence checks, and promotion… |

</details>

<details><summary><b>orchestration</b> (1): Worktree/tmux orchestration runtime and workflow docs.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `dmux-workflows` | skill | Multi-agent orchestration using dmux (tmux pane manager for AI agents). |

</details>

<details><summary><b>prediction-market-skills</b> (3): Public, non-advisory prediction-market workflows and the consolidated read-only Ito baskets data…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `ito-baskets` | skill | Read-only Itô basket and prediction-market data skill. |
| `prediction-market-oracle-research` | skill | Research prediction markets as data sources or oracle signals for products, agents, dashboards, and corporate decision intelligence. |
| `prediction-market-risk-review` | skill | Review prediction-market, basket, oracle, and trading-agent workflows for compliance, safety, data-quality, privacy, and execution risk. |

</details>

<details><summary><b>research-apis</b> (10): Research and API integration skills for deep investigations and model integrations.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `deep-research` | skill | Produce cited research reports from multiple web sources using firecrawl and exa MCP tools — plan sub-questions, search and deep-read sources, then synthesize… |
| `documentation-lookup` | skill | Use up-to-date library and framework docs via Context7 MCP instead of training data. |
| `exa-search` | skill | Neural search via Exa MCP for web, code, and company research. |
| `osint-investigation` | skill | Sparse-clue OSINT investigation methodology for extracting overlooked leads, connecting fragmented evidence, and testing explanations across sources. |
| `research-ops` | skill | Evidence-first current-state research workflow for ECC. |
| `scientific-db-pubmed-database` | skill | Direct PubMed and NCBI E-utilities search workflows for biomedical literature, MeSH queries, PMID lookup, citation retrieval, and API-backed literature… |
| `scientific-db-uspto-database` | skill | USPTO patent and trademark data workflow for official record lookup, PatentSearch queries, TSDR checks, assignment data, and reproducible IP research logs. |
| `scientific-pkg-gget` | skill | Gget CLI and Python workflow for quick genomic database queries, sequence lookup, BLAST-style searches, enrichment checks, and reproducible bioinformatics… |
| `scientific-thinking-literature-review` | skill | Systematic literature-review workflow for academic, biomedical, technical, and scientific topics, including search planning, source screening, synthesis,… |
| `scientific-thinking-scholar-evaluation` | skill | Structured scholarly-work evaluation for papers, proposals, literature reviews, methods sections, evidence quality, citation support, and research-writing… |

</details>

<details><summary><b>rules</b> (22): ECC coding rules: the common set and one set per language or framework.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `rules-angular` | rule | Coding rules from ECC, angular rules: style, patterns, security, testing. |
| `rules-arkts` | rule | Coding rules from ECC, arkts rules: style, patterns, security, testing. |
| `rules-common` | rule | Coding rules from ECC, the rules every language follows: style, patterns, security, testing. |
| `rules-cpp` | rule | Coding rules from ECC, cpp rules: style, patterns, security, testing. |
| `rules-csharp` | rule | Coding rules from ECC, csharp rules: style, patterns, security, testing. |
| `rules-dart` | rule | Coding rules from ECC, dart rules: style, patterns, security, testing. |
| `rules-fsharp` | rule | Coding rules from ECC, fsharp rules: style, patterns, security, testing. |
| `rules-golang` | rule | Coding rules from ECC, golang rules: style, patterns, security, testing. |
| `rules-java` | rule | Coding rules from ECC, java rules: style, patterns, security, testing. |
| `rules-kotlin` | rule | Coding rules from ECC, kotlin rules: style, patterns, security, testing. |
| `rules-nuxt` | rule | Coding rules from ECC, nuxt rules: style, patterns, security, testing. |
| `rules-perl` | rule | Coding rules from ECC, perl rules: style, patterns, security, testing. |
| `rules-php` | rule | Coding rules from ECC, php rules: style, patterns, security, testing. |
| `rules-python` | rule | Coding rules from ECC, python rules: style, patterns, security, testing. |
| `rules-react` | rule | Coding rules from ECC, react rules: style, patterns, security, testing. |
| `rules-react-native` | rule | Coding rules from ECC, react-native rules: style, patterns, security, testing. |
| `rules-ruby` | rule | Coding rules from ECC, ruby rules: style, patterns, security, testing. |
| `rules-rust` | rule | Coding rules from ECC, rust rules: style, patterns, security, testing. |
| `rules-swift` | rule | Coding rules from ECC, swift rules: style, patterns, security, testing. |
| `rules-typescript` | rule | Coding rules from ECC, typescript rules: style, patterns, security, testing. |
| `rules-vue` | rule | Coding rules from ECC, vue rules: style, patterns, security, testing. |
| `rules-web` | rule | Coding rules from ECC, web rules: style, patterns, security, testing. |

</details>

<details><summary><b>security</b> (21): Security review and security-focused framework guidance.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `agent-security-hardening` | skill | Security hardening guidance for AI agent frameworks that process untrusted content, invoke tools, write workspace files, manage runtime identifiers, or handle… |
| `defi-amm-security` | skill | Security checklist for Solidity AMM contracts, liquidity pools, and swap flows. |
| `django-security` | skill | Django security best practices, authentication, authorization, CSRF protection, SQL injection prevention, XSS prevention, and secure deployment configurations. |
| `evm-token-decimals` | skill | Prevent silent decimal mismatch bugs across EVM chains. |
| `gateguard` | skill | PreToolUse fact-forcing gate that denies the first Edit/Write/Bash (including MultiEdit and NotebookEdit) attempt until the agent presents concrete facts… |
| `healthcare-cdss-patterns` | skill | Clinical Decision Support System (CDSS) development patterns. |
| `healthcare-emr-patterns` | skill | EMR/EHR development patterns for healthcare applications. |
| `healthcare-eval-harness` | skill | Patient safety evaluation harness for healthcare application deployments. |
| `healthcare-phi-compliance` | skill | Protected Health Information (PHI) and PII compliance patterns for healthcare applications: data classification, row-level access control, tamper-proof audit… |
| `hipaa-compliance` | skill | HIPAA-specific entrypoint for healthcare privacy and security work. |
| `laravel-security` | skill | Laravel security best practices — authentication, authorization, Eloquent safety, CSRF, XSS prevention, API security, and secure deployment configurations. |
| `llm-trading-agent-security` | skill | Security patterns for autonomous trading agents with wallet or transaction authority. |
| `mcp-dependency-review` | skill | Statically review MCP configuration for mutable package references before approval or CI, without executing discovered MCP servers. |
| `nodejs-keccak256` | skill | Prevent Ethereum hashing bugs in JavaScript and TypeScript. |
| `perl-security` | skill | Comprehensive Perl security covering taint mode, input validation, safe process execution, DBI parameterized queries, web security (XSS/SQLi/CSRF), and… |
| `quarkus-security` | skill | Quarkus security implementation patterns: JWT and OIDC authentication, @RolesAllowed RBAC and SecurityIdentity checks, Bean Validation and custom validators,… |
| `safety-guard` | skill | Guard against destructive operations with three modes: Careful intercepts dangerous commands (rm -rf, git push --force, DROP TABLE) for confirmation, Freeze… |
| `security-bounty-hunter` | skill | Hunt for exploitable, bounty-worthy security issues in repositories. |
| `security-review` | skill | Use this skill when adding authentication, handling user input, working with secrets, creating API endpoints, or implementing payment/sensitive features. |
| `security-scan` | skill | Scan your Claude Code configuration (.claude/ directory) for security vulnerabilities, misconfigurations, and injection risks using AgentShield. |
| `springboot-security` | skill | Spring Security best practices for authn/authz, validation, CSRF, secrets, headers, rate limiting, and dependency security in Java Spring Boot services. |

</details>

<details><summary><b>skill-unified-memory</b> (1): Single-skill unified-memory guidance; requires the separately installed ecc-universal CLI runtime.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `unified-memory` | skill | Share durable, inspectable context and handoffs between Claude, Codex, Hermes, Cursor, OpenCode, and other agents through the local ECC Memory Vault. |

</details>

<details><summary><b>social-distribution</b> (3): Social publishing and distribution skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `crosspost` | skill | Multi-platform content distribution across X, LinkedIn, Threads, and Bluesky. |
| `social-publisher` | skill | Agent-driven scheduling and publishing of social media posts across 13 platforms via SocialClaw. |
| `x-api` | skill | X/Twitter API integration for posting tweets, threads, reading timelines, search, and analytics. |

</details>

<details><summary><b>supply-chain-domain</b> (8): Supply chain, logistics, procurement, and manufacturing domain skills.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `carrier-relationship-management` | skill | Manage truckload, LTL, and intermodal carrier portfolios: sourcing and FMCSA vetting, freight rate and fuel-surcharge negotiation, RFPs and routing guides,… |
| `customs-trade-compliance` | skill | Codified customs and trade compliance expertise — HS/HTS tariff classification with GRI rules, commercial invoices and entry documentation, Incoterms 2020,… |
| `energy-procurement` | skill | Procure electricity and natural gas for commercial and industrial facilities: tariff and rate-schedule optimization, demand-charge mitigation, supplier RFPs,… |
| `inventory-demand-planning` | skill | Codified demand planning expertise for multi-location retailers: demand forecasting method selection, ABC/XYZ segmentation, safety stock and reorder-point… |
| `logistics-exception-management` | skill | Codified freight-exception handling expertise for shipment delays, damages, losses, shortages, and carrier disputes, with escalation protocols,… |
| `production-scheduling` | skill | Codified expertise for production scheduling, job sequencing, line balancing, changeover optimization, and bottleneck resolution in discrete and batch… |
| `quality-nonconformance` | skill | Quality control and non-conformance management for regulated manufacturing (FDA 21 CFR 820, IATF 16949, AS9100): NCR lifecycle and disposition,… |
| `returns-reverse-logistics` | skill | Codified expertise for returns authorization, receipt and inspection, disposition decisions, refund processing, fraud detection, and warranty claims management. |

</details>

<details><summary><b>swift-apple</b> (7): Swift, SwiftUI, and Apple platform skills including concurrency, persistence, and design patterns.</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `foundation-models-on-device` | skill | Apple FoundationModels framework for on-device LLM — text generation, guided generation with @Generable, tool calling, and snapshot streaming in iOS 26+. |
| `ios-icon-gen` | skill | Generate iOS app icons as PNG imagesets for Xcode asset catalogs from SF Symbols (5000+ Apple-native) or Iconify API (275k+ open source icons from 200+… |
| `liquid-glass-design` | skill | IOS 26 Liquid Glass design system — dynamic glass material with blur, reflection, and interactive morphing for SwiftUI, UIKit, and WidgetKit. |
| `swift-actor-persistence` | skill | Thread-safe data persistence in Swift using actors — in-memory cache with file-backed storage, eliminating data races by design. |
| `swift-concurrency-6-2` | skill | Swift 6.2 Approachable Concurrency — single-threaded by default, @concurrent for explicit background offloading, isolated conformances for main actor types. |
| `swift-protocol-di-testing` | skill | Protocol-based dependency injection for testable Swift code — mock file system, network, and external APIs using focused protocols and Swift Testing. |
| `swiftui-patterns` | skill | SwiftUI architecture patterns, state management with @Observable, view composition, navigation, performance optimization, and modern iOS/macOS UI best… |

</details>

<details><summary><b>workflow-quality</b> (52): Evaluation, TDD, verification, compaction, learning, and cross-harness memory skills, including…</summary>

| Voce | Tipo | Cosa fa |
|---|---|---|
| `agent-introspection-debugging` | skill | Structured self-debugging workflow for AI agent failures using capture, diagnosis, contained recovery, and introspection reports. |
| `agent-self-evaluation` | skill | Use after completing any non-trivial task. |
| `agent-sort` | skill | Build an evidence-backed ECC install plan for a specific repo by sorting skills, commands, rules, hooks, and extras into DAILY vs LIBRARY buckets using… |
| `ai-regression-testing` | skill | Regression testing strategies for AI-assisted development. |
| `architecture-decision-records` | skill | Capture architectural decisions as numbered ADR markdown files in docs/adr/ with context, alternatives considered, consequences, and an index README. |
| `brownfield-retrospective` | skill | Run the ECC engineering process retroactively against an existing project slice. |
| `browser-qa` | skill | Run automated post-deploy UI verification with a browser automation MCP (claude-in-chrome, Playwright, or Puppeteer): console-error and Core Web Vitals smoke… |
| `ck` | skill | Persistent per-project memory for Claude Code (Context Keeper) driven by deterministic Node.js /ck commands: init, save, resume, info, list, forget, and… |
| `click-path-audit` | skill | Trace every user-facing button/touchpoint through its full state change sequence to find bugs where functions individually work but cancel each other out,… |
| `code-tour` | skill | Create CodeTour `.tour` files — persona-targeted, step-by-step walkthroughs with real file and line anchors. |
| `codebase-onboarding` | skill | Analyze an unfamiliar codebase and generate a structured onboarding guide with architecture map, key entry points, conventions, and a starter CLAUDE.md. |
| `codehealth-mcp` | skill | Real-time structural Code Health via CodeScene MCP — review before edits, verify score deltas after changes, gate commits and PRs. |
| `config-gc` | skill | Garbage collection for your Claude Code configuration. |
| `configure-ecc` | skill | Run the conversational ECC setup wizard inside the current harness: inventory the install, collect scope (user/project/local) and hook mode… (`ECC runtime`) |
| `context-budget` | skill | Routes live context checks to the native Codex or Claude Code meter without scanning files, and performs a bounded static component audit only when explicitly… |
| `continuous-learning` | skill | [DEPRECATED - use continuous-learning-v2] Legacy v1 stop-hook skill extractor. |
| `continuous-learning-v2` | skill | Instinct-based learning system that observes sessions via hooks, creates atomic instincts with confidence scoring, and evolves them into skills/commands/agents. (`ECC runtime`) |
| `conventional-commit-review` | skill | Reviews staged changes and drafts a Conventional Commits-compliant commit message with the right type, scope, and length. |
| `council` | skill | Convene a four-voice council for ambiguous decisions, tradeoffs, and go/no-go calls. |
| `council-multi-model` | skill | Add one optional external Codex critique after the existing council has produced a decision draft. |
| `deepseek-harness-setup` | skill | Install and operate Everything Claude Code (ECC) on the DeepSeek Harness (DSH): native skill roots (~/.dsh/skills, .agents/skills), the… (`ECC runtime`) |
| `delivery-gate` | skill | Stop hook that blocks Claude from finishing until quality checks pass. |
| `dev-team` | skill | Simulate a collaborative dev team session where multiple role-based personas (PM, Architect, Developer, QA) respond to the same problem together in one session. |
| `e2e-testing` | skill | Playwright E2E testing patterns, Page Object Model, configuration, CI/CD integration, artifact management, and flaky test strategies. |
| `ecc-guide` | skill | Answer questions about ECC by reading the live repo surface — agents, skills, commands, hooks, rules, install profiles, and docs — instead of memory. |
| `ecc-recipes` | skill | Map a described workflow to the right ECC command group with run-order and stop condition, or browse all command-group recipe families read live from the… |
| `error-handling` | skill | Patterns for robust error handling across TypeScript, Python, and Go. |
| `eval-harness` | skill | Eval-driven development (EDD) framework for AI coding sessions — define capability and regression evals before coding, grade with code-based, model-based,… |
| `git-workflow` | skill | Git workflow patterns including branching strategies, commit conventions, keeping history clean and readable, tidying local commits before merging, merge vs… |
| `growth-log` | skill | Write growth log entries that extract reusable patterns from completed work — root cause, transferable rule, and a recognizable signal — instead of… |
| `hookify-rules` | skill | Create and configure hookify rules — markdown files with YAML frontmatter that match bash, file, prompt, or stop events by regex or conditions and show… |
| `inherit-legacy-style` | skill | Prevent AI style drift on legacy projects by scanning the codebase for implicit conventions, resolving conflicts with the operator one at a time, and writing… |
| `intent-driven-development` | skill | Turn ambiguous or high-impact product and engineering changes into scoped, verifiable acceptance criteria before or alongside implementation. |
| `iterative-retrieval` | skill | Pattern for progressively refining context retrieval to solve the subagent context problem. |
| `living-docs-governance` | skill | Keep a long-lived project's documentation from rotting by assigning existing project docs clear constitution, map, status, and history roles, then wiring the… |
| `loop-design-check` | skill | Design a goal-oriented agent loop or review one for failure modes: spinning, Goodhart-gaming the verifier, or running a wrong answer to completion. |
| `plan-canvas` | skill | Open plans and HTML artifacts in a local browser canvas where the human annotates elements, chats, and approves or requests changes without leaving the page. (`ECC runtime`) |
| `plankton-code-quality` | skill | Write-time code quality enforcement using Plankton — auto-formatting, linting, and Claude-powered fixes on every file edit via hooks. |
| `product-lens` | skill | Validate the why before building through four product diagnostics — a YC-style product diagnostic that produces PRODUCT-BRIEF.md with a go/no-go… |
| `production-audit` | skill | Local-evidence production readiness audit for shipped apps, pre-launch reviews, post-merge checks, and "what breaks in prod?" questions without sending repo… |
| `repo-scan` | skill | Bootstrap pointer that installs the external repo-scan skill from a pinned, reviewable commit. |
| `rules-distill` | skill | Scan skills to extract cross-cutting principles and distill them into rules — append, revise, or create new rule files. |
| `santa-method` | skill | Multi-agent adversarial verification: two independent reviewers with the same rubric must both pass before output ships, with a fix-and-re-review convergence… |
| `skill-comply` | skill | Visualize whether skills, rules, and agent definitions are actually followed — auto-generates scenarios at 3 prompt strictness levels, runs agents, classifies… |
| `skill-host-compat` | skill | Lint ECC skills for Codex/Cursor-safe frontmatter and Claude-only substitutions before a skill PR. (`ECC runtime`) |
| `skill-scout` | skill | Search existing local, marketplace, GitHub, and web skill sources before creating a new skill. |
| `skill-stocktake` | skill | Use when auditing Claude skills and commands for quality. |
| `story-lifecycle` | skill | Manage a file-based epic → story → sprint development loop without requiring an external project management tool. |
| `strategic-compact` | skill | Suggests manual context compaction at logical intervals to preserve context through task phases rather than arbitrary auto-compaction. |
| `tdd-workflow` | skill | Test-driven development workflow: write a failing test first, watch it fail, implement the smallest change to green, then refactor with 80%+ coverage across… |
| `verification-loop` | skill | Run a six-phase verification of a Claude Code session's work — build, type check, lint, tests with coverage, security grep, and diff review — then produce a… |
| `windows-desktop-e2e` | skill | E2E testing for Windows native desktop apps (WPF, WinForms, Win32/MFC, Qt) using pywinauto and Windows UI Automation. |

</details>

<!-- catalog:end -->

## Sviluppo

```bash
python3 -m unittest discover -s tests
python3 tools/import_ecc.py <checkout di ECC>   # rigenera ruoli ECC e libreria
python3 tools/readme_catalog.py                  # rigenera il catalogo del README (i test lo controllano)
for p in .claude-plugin/plugin.json skills; do claude plugin validate "$p" --strict; done
agy plugin validate .
claude plugin eval . --runs 1 --allow-tools "Bash(python3:*)"   # eval di comportamento (costano)
```
