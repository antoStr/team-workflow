# team-workflow v2.0.0-alpha.1 — Alpha testing guide

[Versione italiana](ALPHA_TESTING.it.md)

Welcome to the Alpha release **v2.0.0-alpha.1** of `team-workflow`!
This version introduces the new **Brain** engine (Obsidian-compatible knowledge vault), the
**Dual Loader**, the **Rolling Digest** in team talk channels and Windows portability.

---

## 1. Key features

### 🧠 Brain engine (Obsidian vault in `docs/brain/`)
- **Vault layout**: the `docs/brain/` folder with `nodes/`, `areas/`, `decisions/` subfolders.
- **Obsidian Graph View**: automatic `.obsidian/graph.json` setup with colors per layer (core,
  area, decision, interface).
- **Bidirectional wikilinks**: `[[slug]]` links generated automatically between upstream and
  downstream nodes.
- **Token efficiency (~85-90%)**: `tw.py brain query` expands the context with a 1-hop (or
  2-hop) breadth-first search, giving only contracts, interfaces and the essential topology
  instead of whole source files.
- **Vault integrity**: `tw.py brain check` finds orphaned or broken wikilinks, missing files and
  bad frontmatter.

### 🔄 Dual Loader
- Full backward compatibility: when `memory_engine` is `"brain"` and `docs/brain` exists, it
  injects the Brain graph; otherwise it falls back to the classic `docs/memory/INDEX.md` and
  `STATE.md`.

### 💬 Rolling Digest (team talk)
- Automatic compaction when the messages pass the threshold (default: 20).
- Safe archive in `<topic>.archive.jsonl`.
- Atomic rewrite of `<topic>.jsonl` with:
  1. a `[digest]` message summarizing the closed threads;
  2. ALL the threads still open (`open_threads()` never loses an open question or challenge);
  3. a sliding window of the recent messages.

### 🪟 Windows portability
- `python_executable()` resolves the interpreter dynamically and skips the 0-byte Microsoft
  Store placeholders on Windows.

---

## 2. Quickstart for testers

### Test 1: initialize and map the Brain
```bash
# Create the Obsidian vault in docs/brain/
python skills/team/scripts/tw.py brain init

# Scan the codebase and generate the nodes
python skills/team/scripts/tw.py brain map

# Check the graph's integrity
python skills/team/scripts/tw.py brain check
```

### Test 2: context query (token-saving search)
```bash
# A 1-hop query on a module
python skills/team/scripts/tw.py brain query talk --hops 1

# The same query as JSON
python skills/team/scripts/tw.py brain query talk --format json
```

### Test 3: Obsidian Graph View
1. Open **Obsidian**.
2. Choose **Open folder as vault** and pick the `docs/brain/` folder.
3. Press `Ctrl + G` (or open the Graph View).
4. Look at the nodes colored by tag (`#core`, `#area`, `#decision`, `#interface`) and the
   interactive links between modules.

### Test 4: Rolling Digest in talk channels
```bash
# Join a test channel
python skills/team/scripts/tw.py talk join test-digest --as tester "Rolling digest check"

# Compact the channel by hand
python skills/team/scripts/tw.py talk digest test-digest

# Check the open threads
python skills/team/scripts/tw.py talk open test-digest
```

---

## 3. Feedback and reports
Report anomalies, unresolved wikilinks or run problems by opening an issue or sharing the
output of `tw.py doctor`.
