## Review discipline

- **Report only what you can defend.** Before writing a finding, check: can I cite the exact
  line? Can I name the input or state that triggers it and the bad outcome? Did I read the
  callers, types and tests around it? Is the severity proportionate? If any answer is no,
  downgrade it or drop it.
- **Critical and high need proof**: the snippet with its line, the failure scenario (input,
  state, outcome) and why existing guards (types, validation, framework defaults, callers) do
  not stop it. Without all three, it is at most medium.
- **Zero findings is a valid review.** Never invent findings to justify the call; say what you
  checked and that it holds.
- **Consolidate** repeated issues into one finding with every location; review changed code,
  and unchanged code only when the change makes it wrong or it is a critical security issue.
- **Common false positives to skip** unless this codebase proves otherwise: error handling
  already done by a caller or the framework; validation already done by every caller; well
  known constants flagged as magic numbers; long but flat code (switches, tables, config,
  generated code); intentionally detached calls (logging, metrics); style the formatter owns;
  suggestions to change the language or stack.
- **Code written by an AI or a tool** deserves extra checks: every imported function, flag and
  config key really exists in the installed version; no invented APIs or files; no duplicated
  helpers that already exist in the codebase; no speculative abstractions or over-defensive
  branches; tests that assert behavior, not their own mocks; no silent scope creep; no
  escalation to expensive models or services without a reason.
