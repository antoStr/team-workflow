---
language: C#
files: "*.cs, *.csproj, *.sln, *.props, *.targets"
detect: ["*.sln", "*.csproj"]
focus: "async correctness, nullable references, resource handling, ASP.NET Core and EF Core"
triggers: "dotnet build errors, NuGet restore or version conflicts, analyzer warnings as errors, target framework mismatches"
---

## Checklist

- **Async**: no `async void` (except event handlers), no `.Result`/`.Wait()` on tasks
  (deadlocks, thread starvation), `CancellationToken` accepted and passed through,
  `ConfigureAwait(false)` in libraries where the project uses it, `ValueTask` consumed once.
- **Nullability**: nullable reference types respected, no `!` suppression on values that can
  be null, guard clauses at public boundaries.
- **Resources**: `using`/`await using` for disposables; `HttpClient` from
  `IHttpClientFactory`, not created per request.
- **ASP.NET Core**: model validation on inputs, authorization attributes or policies on every
  endpoint, no entities returned directly, DI lifetimes (no scoped service captured by a
  singleton), middleware order (auth before endpoints).
- **EF Core**: N+1 and lazy loading surprises, `AsNoTracking` for reads, queries evaluated on
  the client, migrations that rewrite large tables, raw SQL with parameters only.
- **Security**: secrets in `appsettings*.json`, deserialization of untrusted types,
  path traversal, logging personal data.
- **Idiom**: records and immutability for values, pattern matching over type checks, LINQ
  not enumerated twice.

## Build

- NuGet restore: version conflicts (NU1605/NU1608), central package management, private
  feeds needing credentials.
- Target framework mismatches between projects; SDK version in `global.json`.
- Analyzer warnings as errors: fix the code the analyzer points to.
- Source generators and Razor: stale generated code, missing partial declarations.

## Tools

`dotnet build`, `dotnet test`, `dotnet format --verify-no-changes` and
`dotnet list package --vulnerable` when configured.
