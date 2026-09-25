---
language: Swift
files: "*.swift, Package.swift, *.xcodeproj, *.xcworkspace"
detect: ["Package.swift", "*.xcodeproj"]
focus: "memory management, Swift concurrency, value semantics, SwiftUI"
triggers: "Xcode or swift build errors, SPM resolution, code signing, Swift 6 concurrency checking"
---

## Checklist

- **Memory**: retain cycles in closures (`[weak self]` where the closure outlives the call),
  delegates `weak`, no strong references from long-lived objects to views.
- **Concurrency**: `@MainActor` for UI state, `Sendable` conformance honest (no
  `@unchecked Sendable` without a reason), actors for shared mutable state, no blocking
  calls in async code, tasks cancelled when their owner goes away.
- **Optionals and errors**: no force unwrap (`!`) or `try!` on values that can fail; errors
  thrown or surfaced, not ignored with `try?` silently.
- **Value semantics**: structs for values, classes only for identity; copy-on-write costs for
  large collections in hot paths.
- **SwiftUI**: the right property wrapper (`@State` for local, `@StateObject`/`@Observable`
  ownership, `@Binding`), no heavy work in `body`, stable identities in `ForEach`.
- **Security**: secrets in the Keychain, not `UserDefaults`; ATS exceptions justified;
  URL schemes and universal links validated.

## Build

- SPM resolution: version requirements that cannot be satisfied, a package needing a newer
  tools version.
- Swift 6 strict concurrency errors: fix isolation (actor or `@MainActor`), do not silence
  with `nonisolated(unsafe)` without a proof.
- Code signing and provisioning: report them; they need the user's accounts.
- Module and target membership: a file not in the target, missing `import`.

## Tools

`swift build`, `swift test`, or `xcodebuild` with the project's scheme; `swiftlint` and
`swift-format` when configured.
