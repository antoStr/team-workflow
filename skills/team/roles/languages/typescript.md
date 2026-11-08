---
language: TypeScript and JavaScript
files: "*.ts, *.tsx, *.js, *.jsx, *.mjs, *.cjs, *.vue, package.json"
detect: ["package.json", "tsconfig.json"]
focus: "type safety, async correctness, Node and browser security, React, Vue and Next.js"
triggers: "tsc errors, bundler failures (Vite, webpack, Next.js, esbuild), ESLint, module resolution, dependency conflicts"
---

## Checklist

- **Types**: no new `any`, non-null `!` or `as` casts that hide a real `undefined`; unions
  narrowed before use; external data (API responses, JSON, env) validated at the boundary
  (zod or the project's validator) rather than trusted by a type annotation.
- **Async**: every promise awaited, returned or explicitly handled (no floating promises);
  `await` in loops only when order matters, otherwise `Promise.all` with a concurrency limit;
  errors in `async` event handlers and timers caught; no mixing of callbacks and promises.
- **Security**: no `innerHTML`, `dangerouslySetInnerHTML` or `v-html` with user data; no
  `eval`/`new Function`; SQL and shell built with parameters; SSRF on user-supplied URLs;
  prototype pollution in deep merges; secrets or server-only env vars bundled into client
  code (`NEXT_PUBLIC_`, `VITE_`); CORS and cookies (`httpOnly`, `secure`, `sameSite`).
- **Node**: blocking sync I/O on request paths, unhandled stream errors, missing timeouts on
  outbound requests, unbounded body sizes.
- **React**: hook rules (no conditional hooks); effect dependencies complete and effects
  cleaned up; state derived instead of duplicated; stable keys (not array indexes for
  reorderable lists); memoization only where measured; server/client boundary in Next.js
  (`"use client"`, server-only modules, data fetching and caching semantics).
- **Vue**: reactivity lost by destructuring `props` or reactive objects; `watch` without
  cleanup; `v-if` with `v-for` on the same element; mutating props.
- **Accessibility basics** in UI code: labels, button semantics, focus handling.
- **Tests**: behavior through the public API or the DOM (Testing Library), no snapshot-only
  tests for logic, fake timers restored.

## Build

- `tsc` errors: fix the types at the source; check `strict` flags and path aliases in
  `tsconfig.json` against the bundler's aliases.
- Module resolution: ESM vs CommonJS mismatch (`type: module`, `.cjs/.mjs`, default import
  interop), missing `exports` entries, path aliases not mirrored in Vite/webpack/Jest.
- Dependency conflicts and peer dependencies: fix the version range that is wrong; keep one
  package manager and its lock file.
- Next.js: server-only imports in client components, hydration mismatches (dates, random,
  `window`), edge runtime limits.
- Environment: Node version (`engines`, `.nvmrc`), missing env vars at build time.

## Tools

The project's scripts first (`npm|pnpm|yarn|bun run build`, `test`, `lint`, `typecheck`),
then when configured `tsc --noEmit`, `eslint .`, `vitest run` or `jest`, `npm audit` or the
package manager's equivalent.
