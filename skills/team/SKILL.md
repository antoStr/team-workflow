---
name: team
description: Il comando rapido e universale di team: risolve qualsiasi compito (bug, feature, refactoring, audit) gestendo in autonomia team di agenti, navigazione intelligente su codebase enormi e verifica reale (l'app o il gioco viene effettivamente avviato e testato prima di dichiarare il problema risolto).
argument-hint: "<cosa vuoi fare o quale problema risolvere>"
---

# /team — Autonomous Engineering & Live-Verified Team Execution

Questo è il comando principale e semplificato di **team**.
Non serve ricordare comandi lunghi o configurazioni complesse: scrivi semplicemente `/team <compito>` e l'orchestratore gestisce l'intero ciclo in autonomia.

## Come opera l'orchestratore con `/team`

Quando ricevi il comando `/team $ARGUMENTS`:

- **Se l'argomento è un'azione zero-token di sistema**:
  - `upgrade` o `update`: esegui immediatamente `python skills/team/scripts/tw.py update`. Mostra l'esito e termina.
  - `doctor`: esegui immediatamente `python skills/team/scripts/tw.py doctor`. Se richiesto fix: `tw.py doctor --fix`.
  - `audit`: esegui immediatamente `python skills/team/scripts/tw.py audit`.
  - `settings`: esegui `python skills/team/scripts/tw.py settings`.
  - `status`, `hardware` o `thermal`: esegui `python skills/team/scripts/tw.py hardware`.
  - `scan`: esegui immediatamente `python skills/team/scripts/tw.py scan`.
  - `verify-docs`: esegui immediatamente `python skills/team/scripts/tw.py verify-docs`.
  - `catalog`: esegui immediatamente `python skills/team/scripts/tw.py agents catalog`.
  - Per queste azioni zero-token non spawnare subagenti e non consumare inferenze inutili.

- **Comandi storici incorporati in `/team`**:
  I vecchi comandi v1 (`fix-bug`, `new-feature`, `call-team`, `review-changes`, `setup-memory`, `start`, `release`, `ci-init`, `end-session`) sono ora completamente integrati in `/team`: basta digitare ad es. `/team fix-bug <problema>`, `/team new-feature <idea>` o `/team call-team <ruoli>` per avviare il flusso corrispondente.

### 0. Zero-Ghosting per Domande Intercalate ("writing-in-between")
> [!IMPORTANT]
> **MAI GHOSTARE O IGNORARE LE DOMANDE DELL'UTENTE.**
> Se l'utente inserisce considerazioni, dubbi, perplessità o domande intercalate nel testo della richiesta ("writing-in-between"), l'orchestratore e tutti gli agenti DEVONO prima identificare ciascuna domanda e rispondere esaurientemente all'inizio della risposta prima o contestualmente all'avvio dei task operativi.

### 1. Scansione Iniziale della Repository & Orientamento Brain Engine
- All'avvio di ogni chiamata `/team` su una codebase, esegui una scansione immediata dello stack e dell'ambiente:
  `python skills/team/scripts/tw.py scan`
- Rileva framework, linguaggi, librerie UI presenti in `package.json`, stato git e stato della memoria di progetto.
- Se la codebase è grande o sconosciuta, consulta il Brain del progetto:
  `python skills/team/scripts/tw.py brain context <modulo_o_area>`
- Ottieni in meno di 2.000 token il grafo esatto: chi chiama quel modulo, da cosa dipende, e quali **vaccini/errori passati** sono stati registrati per quell'area.
- Cerca automaticamente nella libreria le skill pertinenti al task:
  `python skills/team/scripts/tw.py library search <parole chiave>`

### 2. Dimensionamento Flessibile & Scelta Dinamica degli Agenti (Nessun Limite a 4 Scelte)
- **Nessuna scelta forzata**: non limitare l'utente a 4 opzioni rigide o a preset prefissati (`solo`, `duo`, `trio`).
- **Catalogo Completo**: l'utente può consultare l'intero catalogo di 131 agenti specializzati:
  `python skills/team/scripts/tw.py agents catalog`
- **Precisione Assoluta**: rispetta alla lettera il numero e i ruoli esatti richiesti dall'utente (es. "voglio 3 agenti: frontend-dev, tester, pentester").
- **Flessibilità Dinamica**: l'utente può aggiungere, rimuovere, sostituire o scalare i ruoli in qualsiasi momento in maniera interattiva.
- **Suite Frontend Componenti (`frontend-components`)**:
  Per task frontend, design system o UI:
  - `pick-ui-library` per la selezione mirata senza reinventare componenti;
  - `shadcn-ui`, `base-ui`, `radix-ui` per primitive e componenti accessibili (WCAG 2.2 AA);
  - `sonner-toast`, `vaul-drawer`, `cmdk-palette`, `number-flow` per feedback, gesture e palette;
  - `magic-ui`, `aceternity-ui`, `21st.dev`, `beautiful-ui`, `rare-ui` per effetti visivi e blocchi design moderni.
  - Ruolo specialista dedicato: `design-engineer` affiancato da `frontend-dev` e `ui-ux-designer`.

### 3. LA REGOLA FONDAMENTALE: Verifica Reale in Esecuzione ("Zero Fake-Solved")
> [!CAUTION]
> **È SEVERAMENTE VIETATO DICHIARARE UN PROBLEMA RISOLTO SENZA AVER AVVIATO E TESTATO L'APPLICAZIONE REALE.**
> Guardare il codice o far passare un unit test isolato NON è sufficiente se l'applicazione reale poi crasha al boot.

Prima di dichiarare completato il lavoro:
1. **Lancia lo Smoke Test di avvio reale**:
   `python skills/team/scripts/tw.py smoke "<comando_avvio_app_o_gioco>" --timeout 5`
2. **Verifica empirica di non-crash**:
   - Controlla che il processo si avvii correttamente.
   - Verifica che `stderr` e i log di runtime non contengano `Traceback`, `Fatal Error`, `Exception`, `NullPointer`, o `Segmentation fault`.
   - Per un gioco o GUI: verifica che il loop principale parta e mantenga lo stato attivo per la durata del test.
   - Per un sito web/frontend: verifica che il server risponda su localhost con codice 200 e senza errori console JS.
3. Se l'applicazione crasha: il problema **NON è risolto**. L'agente deve analizzare il log di crash, applicare il fix e ripetere lo smoke test.

### WSL Bridge (Esecuzione & Test Linux su Windows)
Su ambienti Windows, **WSL (Windows Subsystem for Linux)** è attivo e utilizzabile direttamente:
- Usa `wsl <comando>` per utility POSIX (`bash`, `grep`, `awk`, `sed`), binari ELF, compilatori Linux o kernel `/proc`.
- Per smoke test e avvio di runtime Linux: `python skills/team/scripts/tw.py smoke "<comando>" --wsl`.
- Per analisi di binari e reverse engineering su Linux: il `reverse-engineer` e il `pentester` possono sfruttare l'ambiente Linux nativo via WSL.
- **Non saltare test o verifiche Linux su Windows**: se un tool richiede Linux, eseguilo semplicemente attraverso `wsl`.

### 4. Adversarial Gate & Auto-Learning
- Fai sfidare la modifica dal tester/pentester per verificare che i casi limite non rompano il gioco/app.
- Ogni errore trovato ed evitato viene registrato automaticamente nel Brain per vaccinare i task futuri:
  `python skills/team/scripts/tw.py learn record --title "..." --trigger "..." --anti-pattern "..." --solution "..."`

### 5. Gate di Verifica Documentale & Esecuzione Workflow
Prima di rilasciare o dichiarare concluso qualsiasi workflow:
1. **Verifica Documentazione e Memoria**:
   `python skills/team/scripts/tw.py verify-docs --strict`
2. Assicurati che `docs/memory/STATE.md` sia stato aggiornato con le modifiche reali.
3. Verifica che il grafo Brain Obsidian sia integro e che non vi siano collegamenti spezzati o file mancanti.

### 6. Ciclo GitHub Integrato (Issue, PR, CI/CD, Release)
Se il compito tocca GitHub (`issue`, `pr`, `review`, `ci`, `release`):
- **Issue Triage & Fix**: legge l'issue con `gh issue view`, crea un branch dedicato, implementa il fix verificandolo con `tw.py smoke`, e apre la PR che la chiude (`Closes #num`).
- **Creazione Pull Request**: crea PR professionali con `gh pr create` includendo riassunto delle modifiche, motivazione e le prove di esecuzione reale dello smoke test.
- **Revisione PR**: `code-reviewer` esamina i diff delle PR altrui (`gh pr diff`), testando che non introducano regressioni.
- **CI/CD Debugging**: se un workflow GitHub Actions fallisce, scarica i log con `gh run view --log-failed` e delega a `build-fixer`.
- **Release Management**: `release-manager` cura versioning semantico, changelog, tag e pubblicazione via `gh release create`.

### 7. Hardware & Thermal Guard (A Casa vs Fuori Casa / Remoto)
Monitoraggio hardware e termico continuo a **zero token** per prevenire surriscaldamenti e monitorare lo stato dell'host:
- **Controllo stato istantaneo**:
  `python skills/team/scripts/tw.py hardware` (oppure `team hardware` da terminale).
- **Se l'utente è A CASA** (`tw.py hardware --home`):
  Modalita allarme sonoro ATTIVA: se la CPU o la GPU superano le soglie critiche (CPU > 85°C, GPU > 80°C) viene emesso un segnale acustico immediato per allertare l'utente alla scrivania.
- **Se l'utente è FUORI CASA / REMOTO** (`tw.py hardware --remote`):
  Modalita silenziosa ATTIVA: zero suoni o beep, telemetria e alert indirizzati automaticamente alla dashboard web remota via Cloudflare Tunnel per consultazione da smartphone: `https://payments-baghdad-oakland-dsc.trycloudflare.com`.

### 8. Report Finale
Mostra all'utente solo l'essenziale:
- **Risposta alle domande intercalate** (se presenti nel prompt dell'utente).
- **Cosa è stato fatto** (in modo chiaro e conciso, nella lingua dell'utente).
- **Esito scansione e documentazione** (`tw.py scan` e `tw.py verify-docs`).
- **La prova di esecuzione reale** (output dello smoke test / tempo di esecuzione senza crash).
- **Cosa verificare con i tuoi occhi** (il comando esatto per giocare o usare l'app).
