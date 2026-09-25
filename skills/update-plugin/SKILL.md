---
name: update-plugin
description: Update the team-workflow plugin to the latest version in Claude Code and agy, or just check which version is installed
argument-hint: "[check]"
disable-model-invocation: true
---

Use the team-workflow skill to update the plugin itself: $ARGUMENTS

1. Run `python3 <team-workflow skill folder>/scripts/update_plugin.py`, adding `--check` when the
   user wrote "check" (show the versions, change nothing). It updates every harness where the
   plugin is installed: Claude Code through its marketplace, agy by uninstalling and installing
   it again from GitHub (`--source <path or url>` to install from elsewhere).
2. Report in the user's language: latest version, installed version per harness, what was
   updated, and any failure with its output. If the agy install failed, give the retry command
   the script printed.
3. Remind the user to restart the session so the new version is loaded.
