# Playbooks

## Build, lint and test

```bash
<build, lint and test commands>
```

Tests must pass offline and must never touch the user's real data.

## Definition of done

1. The commands above pass; new behavior has tests, and a new test fails without the change.
2. The tester agent approved it; the author never approves their own work.
3. Memory updated: `STATE.md`, plus the area card or `DECISIONS.md` when affected.
4. End-of-task report given; push, tag, release and deletions approved by the user.

## Release

1. Version: <where it lives; it never goes backwards>.
2. Commit, tag and push: <commands and conventions>.
3. Notes: <where they go and in which style>.
