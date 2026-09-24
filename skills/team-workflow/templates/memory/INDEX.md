# Project memory: start here

Shared memory for people and AI agents. Read in this order and stop when you have what you
need:

1. `STATE.md`: version, latest changes, known limits, resume point.
2. `MAP.md`: every module in one line, with the area card that covers it.
3. The area card for your task, in `areas/`.
4. Only the code files the card points to.

Long documents (README, design notes, archives) are for grep, never for reading whole.

| File | Holds | Update when |
|---|---|---|
| `STATE.md` | Version, latest changes, known limits, what to verify, resume point | Files change |
| `MAP.md` | One line per module and its card | A module is added, moved or removed |
| `areas/*.md` | Key files, contracts, tests, known traps of one area | Its behavior changes |
| `DECISIONS.md` | Structural decisions with alternatives and consequences | A structural choice is made |
| `PLAYBOOKS.md` | Build, test and release commands; definition of done | A procedure changes |
| `ACCESS.md` | Folders, what they hold, who may touch them | Folders or permissions change |

## Rules

- Facts only: every file, function and command named here exists. Check before writing.
- Short files, within the limits checked by `memcheck.py`: summarize, archive old history.
- Lessons that would have saved time go in the area card, under "Known traps".
- No secrets, tokens or personal data.
- Keep the language this memory already uses.
