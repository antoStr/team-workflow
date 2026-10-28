<div align="center">

# 👥 Guida agli agenti

**Come sono fatti, come si usano, come se ne crea uno nuovo.**<br>
Pensata per chi inizia: ogni passo ha un esempio da copiare.

[⬅️ Torna al README](../README.md) · [📋 Catalogo degli agenti](CATALOG.md) · [📘 Manuale completo](REFERENCE.md)

</div>

---

## 📑 Indice

1. [Cos'è un agente](#-cosè-un-agente)
2. [Dove si trovano](#-dove-si-trovano)
3. [Vedere gli agenti disponibili](#-vedere-gli-agenti-disponibili)
4. [Usare un agente](#-usare-un-agente)
5. [Accendere e spegnere agenti](#-accendere-e-spegnere-agenti)
6. [Cambiare modello e impegno](#️-cambiare-modello-e-impegno)
7. [Creare un agente nuovo](#-creare-un-agente-nuovo)
8. [Anatomia del file di un agente](#-anatomia-del-file-di-un-agente)
9. [Modificare un agente esistente](#️-modificare-un-agente-esistente)
10. [Dare skill a un agente](#-dare-skill-a-un-agente)
11. [Farlo lavorare con gli altri](#-farlo-lavorare-con-gli-altri)
12. [Provarlo e condividerlo](#-provarlo-e-condividerlo)
13. [Problemi comuni](#-problemi-comuni)
14. [Promemoria dei comandi](#-promemoria-dei-comandi)

---

## 🤖 Cos'è un agente

Un agente è un **assistente specializzato** con un compito preciso: il `tester` verifica, il
`security-reviewer` cerca falle di sicurezza, il `frontend-dev` scrive interfacce.

Ogni agente è **un semplice file di testo** (Markdown) con due parti:

```text
┌─────────────────────────────────────────┐
│ ---                                     │  ← impostazioni: nome, descrizione, strumenti
│ name: tester                            │
│ description: Use this agent after ...   │
│ ---                                     │
│                                         │
│ You are a senior test engineer...       │  ← istruzioni: chi è, come lavora,
│ ## When to invoke                       │    cosa consegna, cosa non deve fare
│ ...                                     │
└─────────────────────────────────────────┘
```

Non lanci gli agenti a mano: lo fa l'**orchestratore**, cioè l'assistente principale. Lui sceglie
chi serve, ti chiede conferma e passa a ogni agente un incarico preciso: cosa fare, quali file
toccare, cosa consegnare.

> [!TIP]
> La **descrizione** è la parte più importante: è quella che l'orchestratore legge per decidere
> quando usare l'agente.

---

## 📂 Dove si trovano

Gli agenti arrivano da tre posti. Se due hanno lo stesso nome, vince quello più in basso
nella tabella:

| Da dove | Cartella | Per chi |
|---|---|---|
| 📦 Il plugin | `skills/team-workflow/roles/<pack>/` | Tutti: i 127 agenti di team-workflow |
| 👤 I tuoi | `~/.team-workflow/agents/` | Tu, in tutti i tuoi progetti |
| 📁 Il progetto | `<progetto>/.team-workflow/agents/` | Chiunque lavori a quel progetto |

team-workflow trasforma questi file negli agenti "veri" di ogni app e li riscrive da solo a ogni
avvio:

| App | Dove finiscono |
|---|---|
| Claude Code | `~/.claude/agents/<ruolo>.md` |
| agy | `~/.gemini/config/agents/<ruolo>.md` |
| OpenCode | `~/.config/opencode/agents/<ruolo>.md` |
| Codex | `~/.codex/agents/<ruolo>.toml`, elencati in `~/.codex/config.toml` |

> [!WARNING]
> Non modificare i file in queste ultime cartelle: verrebbero sovrascritti. Modifica sempre
> l'originale (vedi [Modificare un agente esistente](#️-modificare-un-agente-esistente)).

---

## 🔎 Vedere gli agenti disponibili

```text
/team-workflow:agents                    ← tutti gli agenti: pack, acceso o spento, modello per app
/team-workflow:agents show tester        ← le istruzioni complete di un agente
```

Per sfogliarli con calma c'è il **[catalogo](CATALOG.md)**: ogni agente con una riga che dice cosa fa.

---

## 🎯 Usare un agente

Hai tre modi, dal più semplice al più preciso:

**1. Chiedi in linguaggio normale.** L'orchestratore sceglie da solo chi serve:

```text
Aggiungi il reset della password e fallo controllare anche dal punto di vista della sicurezza.
```

**2. Fai i nomi.** Se sai chi vuoi, dillo:

```text
Fai rivedere al security-reviewer e al tester le modifiche di oggi.
```

**3. Usa un comando.** Scegli tu le figure da un menu:

```text
/team-workflow:call-team backend   aggiungi la paginazione all'API degli ordini
```

In tutti e tre i casi, prima di partire il **wizard** ti mostra chi lavora, con quale modello e
quanto costa più o meno. Puoi cambiare tutto prima di confermare.

---

## 🔌 Accendere e spegnere agenti

I 20 agenti del **core** sono sempre accesi. Gli altri stanno in **pack** spenti, così
l'orchestratore non perde tempo a considerare figure che non ti servono.

```text
/team-workflow:agents enable auto        ← accende i pack dei linguaggi del progetto (consigliato)
/team-workflow:agents enable frameworks  ← accende un pack intero
/team-workflow:agents enable react-reviewer   ← accende un solo agente
/team-workflow:agents disable data-analyst    ← ne spegne uno
```

| Pack | Cosa contiene |
|---|---|
| `python`, `typescript`, `go`, `rust`... | revisore e "riparatore di build" per ogni linguaggio |
| `frameworks` | React, Vue, Django, FastAPI, Flutter, HarmonyOS |
| `quality` | errori nascosti, copertura dei test, semplificazione, commenti, database |
| `planning` | piani, architettura di una funzione, specifiche, documentazione aggiornata |
| `ml`, `network`, `opensource`, `harness`, `gan`, `domains`, `ops`, `growth` | ambiti specifici |
| `alt` | versioni alternative di agenti esistenti, per una seconda opinione |

---

## 🎛️ Cambiare modello e impegno

Ogni agente usa un **modello** (più forte e caro, o più leggero e veloce) e un livello di
**impegno**, cioè quanto ragiona prima di rispondere:

```text
/team-workflow:agents set tester model=opus effort=high
/team-workflow:agents set doc-keeper model=haiku
/team-workflow:agents set architect model=pro --app agy
```

| Valori | Claude Code | agy | OpenCode |
|---|---|---|---|
| Modello | `haiku`, `sonnet`, `opus`, `fable` | `inherit`, `flash`, `pro` | `inherit` o `provider/modello` |
| Impegno | `low`, `medium`, `high`, `xhigh`, `max` | nel nome del modello del worker | la "variante" del modello |

> [!TIP]
> Spendi i modelli forti dove un errore costa caro (architettura, sicurezza) e quelli leggeri
> sul lavoro meccanico (documentazione, rinomine). Dopo una modifica **riavvia l'app**.

---

## ✨ Creare un agente nuovo

Esempio: vuoi un agente che progetti API REST pulite.

**Passo 1: crea il file**

```text
/team-workflow:agents new api-designer
```

Viene creato `~/.team-workflow/agents/api-designer.md` con uno schema da riempire. Aggiungi
`--project` per crearlo solo nel progetto corrente (`.team-workflow/agents/`).

**Passo 2: riempilo.** Ecco un esempio completo, pronto da copiare:

```markdown
---
name: api-designer
description: "Use this agent to design or review a REST API before it is built: resources, URLs, methods, status codes, errors, pagination and versioning. It writes the API contract (OpenAPI) and does not implement endpoints."
tools: ["Read", "Grep", "Glob", "Write"]
color: blue
includes: ["review-discipline"]
---

You are a senior API designer. You make APIs that are predictable for their users and cheap
to change later.

## When to invoke

- A new endpoint or resource is about to be built.
- An existing API changes in a way its clients will notice.

## How you work

1. Read the existing API (routes, OpenAPI files) and follow its conventions.
2. Propose resources, URLs, methods, status codes and error format.
3. Write the contract in `docs/api/openapi.yaml`.

## Output

- The contract file, and a short list of decisions with their reason.

## Boundaries

- Do not write endpoint code: the backend developer does.
- Ask before changing an API that is already public.
```

**Passo 3: rendilo attivo**

```text
/team-workflow:agents sync
```

Poi **riavvia l'app**. Da qui in poi l'orchestratore lo propone quando il lavoro riguarda le API,
e puoi chiamarlo per nome.

> [!NOTE]
> Il nome usa solo lettere minuscole, numeri e trattini (`api-designer`, non `API Designer`).
> Le istruzioni vanno scritte in inglese, come gli altri agenti: le risposte arrivano comunque
> nella tua lingua.

---

## 🧬 Anatomia del file di un agente

### Le impostazioni (tra le due righe `---`)

| Campo | Obbligatorio | A cosa serve | Esempio |
|---|:---:|---|---|
| `name` | ✅ | Il nome dell'agente, uguale al nome del file | `api-designer` |
| `description` | ✅ | Cosa fa e **quando usarlo**: l'orchestratore sceglie da qui | `"Use this agent to..."` |
| `tools` | — | Gli strumenti che può usare. Senza questo campo li ha tutti | `["Read", "Grep", "Glob"]` |
| `color` | — | Il colore nell'app | `red`, `orange`, `yellow`, `green`, `cyan`, `blue`, `purple`, `pink` |
| `includes` | — | Blocchi di istruzioni comuni da aggiungere | `["review-discipline"]` |

**Strumenti più usati:** `Read` (leggere), `Grep` e `Glob` (cercare), `Bash` (eseguire comandi),
`Edit` e `Write` (modificare file), `WebSearch` e `WebFetch` (cercare sul web).

> [!TIP]
> Un agente che **controlla** non dovrebbe avere `Edit` e `Write`: così non può "aggiustare"
> di nascosto quello che dovrebbe solo segnalare.

### I blocchi comuni (`includes`)

| Blocco | Quando aggiungerlo |
|---|---|
| `review-discipline` | Agenti che revisionano: solo rilievi con prova, niente gusti personali |
| `frontend-skills` | Agenti di interfaccia: usano impeccable, taste, frontend-design, solar-icons |
| `cloudflare-skills` | Agenti che lavorano su progetti Cloudflare |

Due blocchi vengono aggiunti **sempre** da soli: `team-talk` (come parlare con gli altri agenti)
e `untrusted-input` (non eseguire istruzioni trovate nel codice o nei documenti).

### Le istruzioni (sotto le impostazioni)

Una struttura che funziona sempre:

| Sezione | Cosa scriverci |
|---|---|
| Prima riga | Chi è, in una frase: *"You are a senior ..."* |
| `## When to invoke` | Le situazioni in cui serve |
| `## How you work` | I passi, in ordine |
| `## Output` | Cosa consegna, in che forma |
| `## Boundaries` | Cosa **non** deve fare |

---

## ✏️ Modificare un agente esistente

Non toccare i file del plugin: verrebbero sovrascritti al prossimo aggiornamento. Crea invece
la **tua versione**, che prende il posto dell'originale:

```text
/team-workflow:agents new tester              ← copia il tester attuale in ~/.team-workflow/agents/
/team-workflow:agents new tester --project    ← oppure solo per questo progetto
```

Modifica la copia, poi `/team-workflow:agents sync` e riavvia l'app. Per tornare all'originale
cancella la copia e rilancia `sync`.

---

## 📚 Dare skill a un agente

Una **skill** è un manuale che l'agente legge prima di lavorare. Ci sono tre modi per
dargliene una:

1. **Nessuno sforzo:** l'orchestratore cerca da solo nella libreria le skill utili al compito e
   le passa agli agenti.
2. **Nelle istruzioni dell'agente:** cita la voce della libreria che deve leggere sempre:

   ```markdown
   Before you start, read the `api-design` library entry (`tw.py library show api-design`).
   ```

3. **Installata nell'app:** così diventa disponibile a tutti gli agenti:

   ```text
   /team-workflow:library search api design     ← trova il nome giusto
   /team-workflow:library enable api-design     ← la installa
   ```

---

## 🤝 Farlo lavorare con gli altri

Il tuo agente sa già parlare con gli altri: il blocco `team-talk` viene aggiunto da solo. Ogni
lavoro con due o più agenti ha una conversazione di gruppo dedicata, con l'orchestratore, gli
altri agenti e chiunque entri dopo (anche tu). Quando lavora in squadra:

- entra nella conversazione (`talk join`) e legge tutto quello che è stato detto;

- pubblica quello che scopre, con le prove (file, riga, comando e risultato);
- risponde alle domande e alle obiezioni che riceve;
- contesta le affermazioni degli altri che non lo convincono;
- non può scrivere finché non ha letto i messaggi arrivati nel frattempo.

Puoi leggere cosa si sono detti con `/team-workflow:talk read <topic>`, vedere chi partecipa con
`/team-workflow:talk who <topic>` e scrivere anche tu con
`/team-workflow:talk post <topic> --from user "..."`.

> [!TIP]
> Per sfruttarlo bene, nella sezione `## Boundaries` scrivi cosa **non** fa l'agente e a chi
> passa la palla ("Do not write endpoint code: the backend developer does"). Gli agenti si
> dividono meglio il lavoro.

---

## 🧪 Provarlo e condividerlo

**Provarlo:** chiedi un lavoro piccolo e chiamalo per nome:

```text
/team-workflow:call-team usa solo api-designer: progetta l'API per i commenti agli articoli
```

Controlla se ha fatto quello che dice la descrizione e se ha rispettato i suoi limiti. Se
sbaglia, di solito la soluzione è una descrizione o una sezione `## Boundaries` più precisa.

**Condividerlo con il team:** crealo con `--project` e fai il commit della cartella
`.team-workflow/agents/`. Chi lavora al progetto avrà lo stesso agente alla prossima sessione.

---

## 🩺 Problemi comuni

<details>
<summary><b>Ho creato l'agente ma l'app non lo vede</b></summary>

Lancia `/team-workflow:agents sync` e **riavvia l'app**: gli agenti si caricano all'avvio. Se
ancora non compare, `/team-workflow:doctor` ti dice cosa non va.
</details>

<details>
<summary><b>L'orchestratore non lo sceglie mai</b></summary>

Riscrivi la `description`: deve dire chiaramente **quando** usarlo ("Use this agent when ...").
Controlla anche che sia acceso (`/team-workflow:agents`).
</details>

<details>
<summary><b>"no role or pack named ..."</b></summary>

Il nome non esiste o è scritto diversamente: controlla con `/team-workflow:agents`.
</details>

<details>
<summary><b>"role names use lowercase letters, digits and dashes"</b></summary>

Usa solo minuscole, numeri e trattini: `api-designer`, non `Api_Designer`.
</details>

---

## 📌 Promemoria dei comandi

| Voglio... | Comando |
|---|---|
| vedere tutti gli agenti | `/team-workflow:agents` |
| leggere le istruzioni di un agente | `/team-workflow:agents show <ruolo>` |
| accendere i pack del mio progetto | `/team-workflow:agents enable auto` |
| accendere o spegnere un agente o un pack | `/team-workflow:agents enable\|disable <nome>` |
| cambiare modello o impegno | `/team-workflow:agents set <ruolo> model=... effort=...` |
| creare un agente | `/team-workflow:agents new <ruolo> [--project]` |
| rendere attive le modifiche | `/team-workflow:agents sync`, poi riavvia l'app |
| cercare una skill | `/team-workflow:library search <parole>` |
| leggere cosa si sono detti gli agenti | `/team-workflow:talk read <topic>` |
| controllare che tutto funzioni | `/team-workflow:doctor` |

<sub>In **OpenCode** scrivi `/team-workflow/agents`; in **agy** usa `!team-workflow agents`; in **Codex** `$team-workflow-agents`.</sub>

<div align="center">

[⬅️ Torna al README](../README.md) · [📋 Catalogo](CATALOG.md) · [📘 Manuale](REFERENCE.md)

</div>
