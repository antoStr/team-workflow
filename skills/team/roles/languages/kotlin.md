---
language: Kotlin
files: "*.kt, *.kts, build.gradle.kts, settings.gradle.kts"
detect: ["settings.gradle.kts", "build.gradle.kts"]
focus: "null safety, coroutines and Flow, Android lifecycle, Compose, KMP and Ktor"
triggers: "Gradle or Kotlin compiler errors, KSP or kapt failures, Android build variants, dependency conflicts"
---

## Checklist

- **Null safety**: no `!!` on values that can really be null; platform types from Java
  handled; `lateinit` only where initialization is guaranteed.
- **Coroutines**: structured concurrency (no `GlobalScope`), scopes tied to lifecycles
  (`viewModelScope`, `lifecycleScope`), `CancellationException` never swallowed, blocking
  calls moved to `Dispatchers.IO`, exceptions handled in `launch` via handlers or
  `supervisorScope` where siblings must survive.
- **Flow**: cold vs hot semantics understood; `stateIn`/`shareIn` with a sensible
  `SharingStarted`; collection lifecycle-aware on Android (`repeatOnLifecycle`); no heavy work
  in `map` on the main thread.
- **Android**: no context or view leaks (activities held by singletons or long-lived
  callbacks), configuration changes survive, work in the right component (WorkManager for
  deferrable work), permissions requested at use, exported components and intents validated.
- **Compose**: state hoisted, stable parameters, `remember` keys correct, side effects in
  `LaunchedEffect`/`DisposableEffect` with the right keys, no heavy work in composition.
- **Ktor and server code**: blocking calls in handlers, missing timeouts, serialization of
  internal fields, auth on every route.
- **Idiom**: data classes for values, sealed types for states with exhaustive `when`,
  immutability by default, extension functions not hiding side effects.

## Build

- Kotlin and Gradle plugin versions out of sync (Kotlin, AGP, KSP, Compose compiler).
- KSP/kapt processors failing: read the first processor error; generated code stale.
- Android variants and flavors: a source set or resource missing in one variant; minSdk
  API usage; R8/ProGuard rules removing reflected classes.
- KMP: `expect`/`actual` mismatches, a dependency without a target the project builds.

## Tools

`./gradlew build` or the module tasks the project uses (`assembleDebug`, `test`,
`lint`, `detekt`, `ktlintCheck` when configured).
