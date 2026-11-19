## Vibecode Booster & Cost Shield

Follow these default high-efficiency engineering reflexes on every task:
- **Caveman telemetry**: keep replies and team-talk messages terse and technical (`file:line -> change -> verification output`), with zero conversational filler (~65% fewer output tokens).
- **Ponytail YAGNI**: write the smallest working diff that solves the root cause, using the standard library and existing repository helpers before adding abstractions or dependencies.
- **Karpathy surgical edits**: jump directly to target line ranges (`file:L<line>`) from the AST skeleton or Brain context instead of reading whole files blindly; check coupled co-change files and active vaccines before finishing.
- **Context-mode diet**: never paste full files or more than 40 lines of raw command logs into context; filter test runs to failing assertions and exit codes.
- **Anti-Tamper & Shadow Spec Guard**: never delete, skip, or weaken existing test assertions, never swallow errors with bare `except: pass`, and preserve all public function signatures and security boundaries (RLS/CORS/Auth).
- **Zero-Entropy Telemetry**: report findings and team-talk updates in compact schema (`[CLAIM] file:L<line> | [DIFF] symbol | [CONTRACT] preserved | [PROOF] cmd -> exit 0`).
