# Stato del Progetto

## Versione Corrente: v2.3.0 (Release Ufficiale)

### 1. Nuove Funzionalità Core (v2.3.0)
- **Preview Server Manager (`tw.py preview`)**:
  - Avvio (`tw.py preview start`), monitoraggio (`tw.py preview status`) e arresto (`tw.py preview stop`) dei dev server di progetto.
  - Rilevamento automatico dello stack: static HTML (`python -m http.server`), Node/Vite/Next.js (`npm run dev`), Django (`manage.py runserver`).
  - Ricerca automatica di porte libere (a partire da 8080) e gestione trasparente dei processi daemon con memorizzazione di PID, porta e timestamp.
- **Patch-Bridge Atomico (`tw.py patch`)**:
  - Applicazione atomica di diff unificati standard (`git diff`, `diff -u` o blocchi markdown ` ```diff `) con parsing sicuro di hunk e validazione preventiva (`--dry-run`).
  - Consente ai subagent esecutivi di proporre modifiche multi-file senza rischiare corruzioni parziali o conflitti di IO.
- **Component Scaffolding CLI (`tw.py component`)**:
  - Comando CLI `tw.py component list` e `tw.py component add <name>` per generare e iniettare istantaneamente componenti moderni e accessibili:
    `cmdk`, `sonner`, `number-flow`, `vaul`, `spotlight`, `marquee`, `dot-grid`.
- **Auditor Responsive & Visivo (`tw.py visual-check`)**:
  - Controllo automatico di conformità mobile e responsive: presenza del meta tag viewport, assenza di larghezze fisse rischiose per overflow orizzontale (`width > 500px` senza max-width), presenza di `@media (prefers-reduced-motion)` e gerarchia corretta degli heading (`<h1>`).
- **Chiusura Rapida Canali Team Talk (`tw.py talk close`)**:
  - Comando one-shot `tw.py talk close <topic> [--summary "..."]` che auto-risolve tutti i thread pendenti e registra una decisione finale di chiusura nel log JSONL del canale.

### 2. Suite Componenti Frontend Avanzata (`frontend-components`)
- **13 nuove skill specializzate per ingegneria frontend e design engineering**:
  - `pick-ui-library`: Motore di selezione e matrice decisionale (ispirato ad Emil Kowalski). Ispeziona `package.json`, previene l'anti-pattern di reinventare primitive accessibili da zero e seleziona la libreria migliore per ogni categoria.
  - `shadcn-ui`: Architettura completa shadcn/ui (CLI, `components.json`, utility `cn()`, variabili CSS HSL/OKLCH, validazione form React Hook Form + Zod e registri remoti).
  - `base-ui`: Primitive accessibili headless sviluppate dal team MUI, rendering DOM pulito senza wrapper inutili, transizioni CSS native con `@starting-style` e integrazione Tailwind.
  - `radix-ui`: Primitives accessibili WAI-ARIA (`@radix-ui/react-*`), navigazione da tastiera, focus trap, Slot API e pattern di composizione `asChild`.
  - `sonner-toast`: Sistema di notifiche Sonner di Emil Kowalski (toast basati su promise, schede impilate con swipe dismiss, rich colors, custom styling e pulsanti d'azione).
  - `vaul-drawer`: Componente drawer e bottom sheet di Emil Kowalski con fisica dei gesti (trascinamento a molla, snap point multipli, drawer annidati e background scale iOS).
  - `cmdk-palette`: Command menu palette (⌘K) di Paco Coursey con ricerca fuzzy rapida, navigazione da tastiera, sotto-pagine e dialog overlay.
  - `number-flow`: Componente di Max Barvian per transizioni continue e contatori animati con rolling digits, formattazione valute/percentuali `Intl` e prevenzione di layout shift.
  - `beautiful-ui`: Pattern estetici moderni (glassmorphism, griglie bento responsive, input con bordi luminosi, micro-ombre e contrasto WCAG).
  - `rare-ui`: Micro-animazioni interattive uniche (pulsanti magnetici con fisica del cursore, schede con tilt 3D interattivo, griglie spotlight con mouse tracker radiale).
  - `magic-ui`: Libreria di effetti visivi per design engineer (Bento grid, Animated Beam, Marquee continuo, particelle, Border Beam e Shimmer button via registry shadcn).
  - `aceternity-ui`: Effetti dinamici di Manu Arora (3D cards, Sparkles canvas, Lamp hero section, Tracing Beam, Aurora background e Floating Dock macOS).
  - `registry-21st-dev`: Architettura e marketplace dei componenti 21st.dev ("The npm for Design Engineers"), con consumo e pubblicazione diretta via CLI shadcn.
- **Nuovo ruolo specialista**: `design-engineer` (`skills/team/roles/frameworks/design-engineer.md`).
- **Include condiviso aggiornato**: `skills/team/roles/_shared/frontend-skills.md` sincronizzato con tutte le nuove skill.
- **Totale libreria**: **525 voci di libreria** (409 skill, 94 comandi, 22 set di regole) in 31 pack.
- **Totale agenti**: **131 specialisti** con catalogo e traduzioni bilingue sincronizzati.

### 3. Zero-Ghosting per Domande Intercalate ("writing-in-between")
- Codificata la regola tassativa in `rules/AGENTS.md` e `skills/team/SKILL.md`:
  Qualora l'utente inserisca considerazioni, dubbi, perplessità o domande intercalate nel testo della richiesta ("writing-in-between"), l'orchestratore e tutti gli agenti DEVONO prima identificare ciascuna domanda e rispondere esaurientemente all'inizio della risposta prima o contestualmente all'avvio dei task operativi.
- È severamente vietato ignorare le domande dell'utente per eseguire solo il comando primario.

### 4. Scelta Dinamica e Catalogo Flessibile degli Agenti (Superamento Limite 4 Scelte)
- Abolito il vincolo rigido a 4 scelte e superata l'imposizione dei preset prefissati (`solo`, `duo`, `trio`).
- Aggiunta azione CLI `tw.py agents catalog` per consultare l'intero catalogo di 131 agenti specializzati suddivisi per pack funzionale.
- Rispettato alla lettera il numero e i ruoli esatti richiesti dall'utente con massima precisione (es. "voglio 3 agenti: frontend-dev, tester, pentester").
- Supporto alla riconfigurazione dinamica in qualsiasi momento: l'utente può aggiungere, rimuovere o sostituire agenti durante il workflow.

### 5. Repository Scan & Stack Profiler (`tw.py scan`)
- Creato `skills/team/scripts/scan.py` e integrato come comando `tw.py scan`:
  - Rileva branch git, stato del working tree e ultimo commit.
  - Rileva linguaggi e framework (Next.js, React, Vue, Tailwind, Python, pytest, Rust, Go, .NET).
  - Rileva stack UI moderno in `package.json` (shadcn, radix, base-ui, sonner, vaul, cmdk, number-flow, framer-motion, lucide).
  - Ottimizzazione cross-platform Windows / WSL con gestione timeout per filesystem bridge `/mnt/c`.
  - Verifica la presenza e la salute della documentazione di progetto (`INDEX.md`, `STATE.md`, Brain vault, vaccini attivi).
  - Obbligatorio all'avvio di ogni chiamata `/team`.

### 6. Gate di Verifica Documentale & Workflow Proof (`tw.py verify-docs`)
- Creato `skills/team/scripts/verify_docs.py` e integrato come comando `tw.py verify-docs`:
  - Accerta che `docs/memory/STATE.md` esista e sia aggiornato rispetto alle modifiche reali del codice.
  - Accerta l'integrità del grafo Brain Obsidian (0 broken link, 0 file mancanti).
  - Valida la sincronizzazione del catalogo (`docs/CATALOG.md`).
  - Flag `--strict` per bloccare release o conclusioni di task se la documentazione non è allineata.

### 7. Test Suite Completa & Verifiche di Integrità
- Suite pytest: **110 passed, 2 skipped** (112 test totali).
- 2 test skipped gestiti intenzionalmente per compatibilità OS (Linux `/proc/self` vs Windows NTFS colon naming).
- Brain Graph Vault: **54 nodi** verificati, 0 issue.

### 6. WSL Bridge & Collaudo Nativo Linux
- Verificata la compatibilità multipiattaforma in ambiente Linux Ubuntu via WSL (Python 3.14.4).
- `tw.py smoke "<cmd>" --wsl` validato per test live di comandi e processi Linux su Windows.
- `tw.py doctor`, `tw.py audit`, `tw.py scan`, `tw.py verify-docs` e suite di test verificate con successo sia in ambiente Windows (Python 3.15.2) sia in ambiente WSL.

### 7. Suite Test & Validazione
- Test suite completa: **107 test passati** (105 ok, 2 skipped, 0 errori).
- Aggiunti test dedicati in `tests/test_scan_verify_catalog.py` (scan stack, verify-docs, ricerca libreria frontend, ruolo design-engineer).
- Strict brain check: **OK (54 nodi, 0 problemi)**.
- Audit prompt agenti: **OK (0 problemi critici o alti)**.
- Documentazione e cataloghi: bilingue, allineati in `docs/CATALOG.md` e `docs/catalog.it.json`.
