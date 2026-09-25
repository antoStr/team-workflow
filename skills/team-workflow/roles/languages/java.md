---
language: Java
files: "*.java, pom.xml, build.gradle, build.gradle.kts, *.properties, *.yml"
detect: ["pom.xml", "build.gradle", "build.gradle.kts"]
focus: "correctness, resource and transaction handling, concurrency, Spring Boot and Quarkus"
triggers: "Maven or Gradle compilation failures, dependency convergence, annotation processing, Spring context startup errors"
---

## Checklist

- **Correctness**: `equals`/`hashCode` together and consistent; `Optional` not used for
  fields or parameters, never `get()` without a check; no `==` on strings or boxed numbers;
  `BigDecimal` for money with explicit scale and rounding; time with `java.time` and explicit
  zones.
- **Exceptions and resources**: try-with-resources for streams, connections and locks; no
  empty catch or `catch (Exception e)` that hides failures; exceptions keep their cause.
- **Concurrency**: shared mutable state guarded; `ConcurrentHashMap` compound operations with
  `compute*`; executors shut down; no blocking on virtual threads while pinned
  (`synchronized` around I/O); `CompletableFuture` exceptions handled.
- **Spring Boot**: `@Transactional` on public methods called from outside the bean (self
  calls bypass the proxy), read-only transactions for queries, lazy loading outside a
  transaction, N+1 with JPA (fetch joins, entity graphs); constructor injection;
  validation (`@Valid`) on request bodies; controllers not returning entities directly;
  security config (`permitAll` scopes, CSRF, CORS), actuator endpoints exposed.
- **Quarkus**: blocking calls on the event loop (`@Blocking` where needed), reflection
  config for native builds, Panache queries built from strings.
- **Security**: SQL and JPQL with parameters, deserialization of untrusted data, XXE in XML
  parsers, path traversal, secrets in `application.*` files, logging of personal data.
- **Tests**: JUnit 5 with meaningful assertions (AssertJ where used), Testcontainers or slices
  instead of mocking the database, no order-dependent tests.

## Build

- Compilation after a dependency bump: API removed or moved; check `mvn dependency:tree` or
  `gradle dependencies` for conflicting versions and fix convergence at the right place (BOM,
  constraints) rather than excluding blindly.
- Annotation processors (Lombok, MapStruct) missing from the compiler path or in the wrong
  order; generated sources stale.
- Java version mismatch between toolchain, `release`/`targetCompatibility` and CI.
- Spring context failures: read the root cause at the bottom of the stack trace (missing
  bean, circular dependency, bad property binding).

## Tools

`mvn -q verify` or `./gradlew build` (the wrapper the project uses), plus when configured
Checkstyle, SpotBugs, PMD, Error Prone and OWASP dependency-check.
