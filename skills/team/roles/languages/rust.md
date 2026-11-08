---
language: Rust
files: "*.rs, Cargo.toml, Cargo.lock"
detect: ["Cargo.toml"]
focus: "ownership and lifetimes, error handling, unsafe code, concurrency, API design"
triggers: "cargo build or check errors, borrow checker, trait bounds, feature flags, dependency resolution"
---

## Checklist

- **Errors**: no `unwrap`/`expect` on fallible input in library or request paths (fine in
  tests and for proven invariants, with a message saying why); `?` with context
  (`anyhow::Context`, typed `thiserror` errors in libraries); no swallowed `Result`
  (`let _ =`) on I/O.
- **Unsafe**: every `unsafe` block has a `// SAFETY:` comment that proves the invariant;
  no UB patterns (aliasing `&mut`, uninitialized memory, lifetime extension through raw
  pointers); FFI boundaries check null and lengths.
- **Ownership**: needless `clone()` in hot paths, `Rc<RefCell>` or `Arc<Mutex>` where a clear
  owner would do; lifetimes that force callers into awkward APIs; `&String`/`&Vec<T>`
  parameters instead of `&str`/`&[T]`.
- **Concurrency and async**: no blocking calls (`std::fs`, `thread::sleep`, heavy CPU) inside
  async tasks without `spawn_blocking`; no lock held across `.await`; `Send`/`Sync` bounds
  justified; spawned tasks joined or supervised.
- **Security**: integer overflow on untrusted sizes (`checked_*`), unbounded allocation from
  input, path traversal, command building, secrets in `Debug` output.
- **API**: public types implement the expected traits (`Debug`, `Clone`, `Error`), builders or
  newtypes instead of boolean parameters, `#[must_use]` where ignoring the value is a bug,
  semver impact of public changes.
- **Tests**: unit tests next to the code, property tests for parsers where the project uses
  them, no tests depending on execution order.

## Build

- Borrow checker: fix the data flow (shorter borrows, split structs, return owned values)
  rather than adding clones or `unsafe`.
- Trait bound and inference errors after a dependency bump: check the crate's changelog and
  feature flags; duplicate versions of the same crate in `cargo tree -d`.
- Feature flags: code behind `#[cfg(feature)]` that does not build with the default or with
  `--all-features`; missing `default-features = false` consequences.
- MSRV: new syntax or APIs above the project's `rust-version`.

## Tools

`cargo check`, `cargo build`, `cargo test`, `cargo clippy -- -D warnings` when the project
uses it, `cargo fmt --check`, `cargo audit` or `cargo deny` when configured.
