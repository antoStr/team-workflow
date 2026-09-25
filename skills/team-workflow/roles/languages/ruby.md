---
language: Ruby
files: "*.rb, Gemfile, Gemfile.lock, *.erb, config/**/*.yml"
detect: ["Gemfile"]
focus: "correctness, security, Rails patterns and database access"
triggers: "bundle install failures, load errors, Zeitwerk autoloading, RuboCop, migrations"
---

## Checklist

- **Security**: SQL with placeholders or Arel (no interpolation in `where` strings), strong
  parameters on every write, `html_safe`/`raw` never on user data, CSRF protection on,
  `send`/`constantize` never on user input, secrets in credentials not in code.
- **Rails**: N+1 (`includes`), callbacks with hidden side effects, validations backed by
  database constraints, transactions around multi-step writes, background jobs idempotent,
  migrations safe on big tables (no default rewrites, indexes concurrently on PostgreSQL).
- **Correctness**: `nil` handled (`&.`, explicit checks), time zones (`Time.zone`), money
  as integers or `BigDecimal`, frozen string literals where the project uses them.
- **Tests**: RSpec or Minitest as the project does, factories over fixtures only where used,
  no reliance on test order.

## Build

- Bundler: Ruby version, native extensions needing system libraries, platform entries in the
  lock file.
- Zeitwerk: file names that do not match constants.
- Pending or conflicting migrations; schema file out of date.

## Tools

`bundle exec rspec` or `bin/rails test`, `bundle exec rubocop`, `bin/rails zeitwerk:check`,
`bundle audit` and `brakeman` when configured.
