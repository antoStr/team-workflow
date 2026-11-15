# Security policy

## Supported versions

Only the latest release of team-workflow gets security fixes. Update with `/team:update-plugin`
(or `team-workflow update`).

## Reporting a vulnerability

Please **do not open a public issue** for a security problem.

Report it privately through GitHub: the repository's **Security** tab →
**Report a vulnerability** (private vulnerability reporting). Include:

- what is affected (file, command, hook, agent or library entry) and the version;
- the steps to reproduce it and what an attacker gains;
- any proof of concept, kept to the minimum needed to show the problem.

You will get an answer within seven days. Fixes are released as soon as they are verified, and
the report is credited in the release notes unless you ask otherwise.

## Scope

In scope: the plugin's scripts and hooks (`skills/`, `hooks/`, `tools/`), the agent instructions
(`skills/team/roles/`), the installers and the GitHub workflows of this repository.

Out of scope: third-party add-ons and MCP servers installed through `addons` (report those to
their authors), and the imported library content under `skills/team/library/` that keeps its
upstream license (see `skills/team/library/NOTICE.md`), unless the problem comes from how
team-workflow installs or runs it.
