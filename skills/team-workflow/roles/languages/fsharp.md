---
language: F#
files: "*.fs, *.fsi, *.fsx, *.fsproj"
detect: ["*.fsproj"]
focus: "functional design, type safety, pattern matching, async and task code"
triggers: "dotnet build errors, file ordering in the project, type inference errors, NuGet conflicts"
---

## Checklist

- **Types**: illegal states unrepresentable (discriminated unions, single-case wrappers),
  exhaustive pattern matches without catch-all `_` that hides new cases, `option` instead of
  null, `Result` for expected failures.
- **Effects**: side effects at the edges, pure core; `task { }` or `async { }` used
  consistently, no `.Result` blocking, cancellation passed through.
- **Interop**: nulls from .NET APIs checked at the boundary, mutable .NET collections not
  leaked into the functional core.
- **Idiom**: pipelines readable, no deep nesting of `match`, active patterns only when they
  clarify.

## Build

- Compilation order: files in the `.fsproj` must come after what they use.
- Type inference: add annotations at the boundary of the failing expression.
- NuGet and target framework mismatches as in C#.

## Tools

`dotnet build`, `dotnet test`, and `fantomas --check` when configured.
