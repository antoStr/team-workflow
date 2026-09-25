---
language: C and C++
files: "*.c, *.cc, *.cpp, *.cxx, *.h, *.hpp, CMakeLists.txt, *.cmake, Makefile, meson.build"
detect: ["CMakeLists.txt", "meson.build", "conanfile.txt", "vcpkg.json"]
focus: "memory safety, undefined behavior, ownership, concurrency, modern C++ idioms"
triggers: "compiler or linker errors, CMake configuration, missing headers or libraries, template errors, sanitizer failures"
---

## Checklist

- **Memory safety**: owning raw pointers (use `unique_ptr`/`shared_ptr` or values), buffer
  indexes checked, no `strcpy`/`sprintf`/`gets`, lifetimes of references and `string_view`
  outliving their owner, iterator invalidation after container changes, use after move.
- **Undefined behavior**: signed overflow, uninitialized reads, strict aliasing, data races,
  out-of-range shifts, dereferencing null or end iterators.
- **Ownership and RAII**: resources released in destructors; rule of zero/five; exception
  safety of multi-step updates; no `new`/`delete` in application code.
- **Concurrency**: shared data protected or atomic with the right memory order; locks in a
  consistent order; `std::thread` joined; condition variables with predicates.
- **Security**: untrusted sizes and lengths validated before allocation or copy; format
  strings constant; integer conversions checked at boundaries.
- **API**: `const` correctness, `noexcept` where it matters for moves, header hygiene
  (include what you use), ABI impact of public header changes.
- **C specifics**: every allocation checked and freed on all paths, `goto cleanup` pattern
  consistent, `size_t` vs `int` for lengths.

## Build

- Undefined reference at link time: missing library in `target_link_libraries`, wrong order,
  symbol visibility, `extern "C"` for C headers, ODR violations.
- Missing header: include paths per target (`target_include_directories`), generated headers
  not built yet (dependencies between targets).
- Template errors: read the first "required from here"; check concepts or constraints.
- Toolchain: standard version (`CMAKE_CXX_STANDARD`), compiler differences, warnings turned
  into errors by `-Werror` (fix the warning).
- Sanitizers (ASan, UBSan, TSan) failures are real bugs: fix the cause.

## Tools

The project's configure and build (`cmake -B build && cmake --build build`, `ctest`, `make`,
`meson test`), plus when configured `clang-tidy`, `cppcheck`, sanitizer builds and
`clang-format --dry-run`.
