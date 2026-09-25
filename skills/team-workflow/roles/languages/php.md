---
language: PHP
files: "*.php, composer.json, composer.lock"
detect: ["composer.json"]
focus: "security, types, errors, Laravel and Symfony patterns"
triggers: "composer install or autoload failures, static analysis (PHPStan, Psalm) errors, PHP version incompatibilities"
---

## Checklist

- **Security**: SQL through bindings or the query builder (no interpolation in `DB::raw` or
  `whereRaw`), output escaped in templates (`{{ }}` not `{!! !!}` with user data), mass
  assignment guarded (`$fillable`), CSRF on forms, file uploads validated and stored outside
  the web root, `unserialize` never on user data, secrets only in `.env`.
- **Types and errors**: `declare(strict_types=1)` where the project uses it, typed properties
  and returns, no `@` error suppression, exceptions not swallowed.
- **Laravel**: N+1 (`with()`), queries in Blade views, validation in form requests,
  authorization with policies or gates on every action, jobs idempotent, migrations
  reversible.
- **Symfony**: services and autowiring, voters for authorization, Doctrine N+1.
- **Style**: PSR-12 where enforced, no business logic in controllers or templates.

## Build

- Composer: platform requirements (PHP version, extensions), version conflicts, autoload
  (`composer dump-autoload`, namespaces matching paths).
- Static analysis: fix the types rather than raising the baseline.

## Tools

`composer validate`, `composer install`, the project's test runner (`php artisan test`,
`vendor/bin/phpunit`, `vendor/bin/pest`), `vendor/bin/phpstan` or `psalm`, `php-cs-fixer`
when configured, `composer audit`.
