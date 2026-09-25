---
language: Go
files: "*.go, go.mod, go.sum"
detect: ["go.mod"]
focus: "error handling, concurrency, context propagation, API and package design"
triggers: "go build, go vet or linter errors, module resolution, build tags or cgo"
---

## Checklist

- **Errors**: no discarded errors (`_ =` or unchecked returns) on I/O, parsing, DB or network
  calls; errors wrapped with context (`fmt.Errorf("doing x: %w", err)`); `errors.Is/As` instead
  of `==` or string matching; no `panic` for recoverable conditions; sentinel and typed errors
  kept stable where callers depend on them.
- **Concurrency**: every goroutine has a way to stop (context, done channel) and its errors
  reach someone; shared state guarded (mutex held with `defer Unlock`, or owned by one
  goroutine); no copied `sync` values; channels closed by the sender only; `WaitGroup.Add`
  before the goroutine starts; the change is clean under `go test -race`.
- **Context**: `ctx context.Context` first parameter, passed down, never stored in structs;
  deadlines on network and DB calls; `context.Background()` only at program edges.
- **Resources**: `defer Close()` right after a successful open, checked where the error
  matters (writes); no `defer` inside long loops; HTTP response bodies always closed.
- **Security**: SQL with placeholders, never string building; `exec.Command` with separate
  arguments and validated input; file paths cleaned and checked against a base directory;
  no `InsecureSkipVerify`; secrets not logged; `crypto/rand` for tokens.
- **API and packages**: small interfaces defined by the consumer; exported names documented;
  zero values useful; no mutable package-level state; no import cycles or `internal/` leaks.
- **Performance traps**: allocations in hot loops (`strings.Builder`, preallocated slices),
  N+1 queries, unbounded goroutines or buffers, `time.After` in loops.
- **Tests**: table-driven where the codebase uses them, `t.Helper`, `t.Parallel` only for
  independent tests, no sleeps for synchronization.

## Build

- Module errors: `go.mod`/`go.sum` out of date (`go mod tidy`), a replace directive pointing
  nowhere, a major version without the `/vN` path, private modules without `GOPRIVATE`.
- Type errors after an API change in a dependency: read its changelog before editing callers.
- Build tags and `GOOS/GOARCH` files missing a counterpart; cgo needing `CGO_ENABLED` and a C
  toolchain; generated code (`go generate`, protobuf) stale.
- `go vet` findings are real bugs (printf verbs, copied locks, unreachable code): fix them.

## Tools

`go build ./...`, `go vet ./...`, `go test -race ./...`, and when configured
`staticcheck ./...`, `golangci-lint run`, `govulncheck ./...`.
