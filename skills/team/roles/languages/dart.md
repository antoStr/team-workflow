---
language: Dart and Flutter
files: "*.dart, pubspec.yaml, analysis_options.yaml"
detect: ["pubspec.yaml"]
focus: "null safety, async, widget lifecycle and rebuilds, state management"
triggers: "dart analyze errors, pub dependency conflicts, build_runner, platform build failures"
---

## Checklist

- **Null safety**: no `!` on values that can be null, `late` only with guaranteed
  initialization.
- **Async**: futures awaited or handled, `mounted` checked before using `BuildContext` after
  an `await`, streams and subscriptions cancelled in `dispose`.
- **Widgets**: controllers (text, animation, scroll) disposed; `const` constructors where
  possible; no heavy work or network calls in `build`; keys on reorderable lists.
- **State management**: one approach used consistently (Provider, Riverpod, Bloc...),
  state not rebuilt at the top of the tree for local changes.
- **Platform and security**: secrets not in the Dart code or assets; platform channels
  validate their input; permissions requested at use.

## Build

- `pub get` conflicts: fix the constraint in `pubspec.yaml`; check the Dart SDK range.
- `build_runner` output stale or conflicting (`--delete-conflicting-outputs` only when the
  generated files are not hand edited).
- Android and iOS builds: Gradle/AGP, CocoaPods and minimum OS versions.

## Tools

`dart analyze` or `flutter analyze`, `flutter test` or `dart test`, `dart format
--set-exit-if-changed .`.
