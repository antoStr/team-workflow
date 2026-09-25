---
language: Python
files: "*.py, pyproject.toml, requirements*.txt, setup.cfg"
detect: ["pyproject.toml", "requirements.txt", "setup.py", "setup.cfg", "Pipfile"]
focus: "correctness, exceptions, typing, security, Django, FastAPI and data code"
triggers: "import errors, dependency conflicts, type checker or linter failures, packaging, migrations"
---

## Checklist

- **Exceptions**: no bare `except:` or `except Exception: pass`; the narrowest exception
  caught; context kept (`raise ... from err`); resources in `with` blocks; no errors turned
  into `None` or empty values without a log or a reason.
- **Correctness traps**: mutable default arguments, late-binding closures in loops, `is` for
  value comparison, naive vs aware `datetime`, float for money (`Decimal`), integer division
  changes, iterators consumed twice, dict ordering assumptions in older code.
- **Typing**: public functions annotated where the project type-checks; `Optional` handled
  before use; no `Any` or `# type: ignore` without a reason.
- **Security**: SQL through parameters or the ORM (no f-strings in `execute` or `raw`);
  `subprocess` with a list and without `shell=True` on input; `yaml.safe_load`; no `pickle`,
  `eval` or `exec` on untrusted data; paths resolved and checked against a base directory;
  `secrets` for tokens; no secrets in logs or settings committed.
- **Django**: N+1 queries (`select_related`/`prefetch_related`), queries in loops or
  templates, missing transactions around multi-step writes, migrations that lock or rewrite
  big tables, `DEBUG` or open `ALLOWED_HOSTS` in production settings, DRF serializers exposing
  fields or skipping permission classes, CSRF exemptions.
- **FastAPI and async**: blocking calls (requests, sync DB drivers, file I/O) inside `async
  def`; dependencies that leak sessions; Pydantic models that accept more than intended
  (`extra`), response models that expose internal fields; missing auth dependencies.
- **Data and ML code**: silent dtype or NaN handling, data leakage between train and test,
  unseeded randomness in tests, tensors on the wrong device, memory blowups from loading
  whole files.
- **Tests**: pytest fixtures over copied setup, no network in unit tests, assertions on
  behavior not on mocks only.

## Build

- `ModuleNotFoundError`: wrong virtual environment or interpreter, missing dependency in the
  project's manifest (not just installed locally), package layout (`src/`, missing
  `__init__.py`), relative imports run as scripts.
- Dependency conflicts: read the resolver output; fix the constraint that is actually wrong
  instead of pinning everything; keep the lock file in sync (`uv lock`, `poetry lock`,
  `pip-compile`).
- Type checker failures (mypy, pyright): fix the types or the code, not the config.
- Django: migration conflicts (`makemigrations --merge` only when both branches are right),
  missing migrations for model changes, settings importing at module level.
- C extensions and wheels: missing system libraries or a Python version without wheels.

## Tools

The project's runner first (`pytest`, `tox`, `nox`, `make test`), then when configured `ruff
check`, `ruff format --check` or `black --check`, `mypy` or `pyright`, `bandit`,
`pip-audit`; Django `python manage.py check --deploy` and `makemigrations --check`.
