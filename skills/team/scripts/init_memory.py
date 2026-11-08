#!/usr/bin/env python3
"""Create docs/memory from the templates and point AGENTS.md (and GEMINI.md, CLAUDE.md when
they exist) to it. Existing files are never overwritten; running it again changes nothing.

    python3 init_memory.py --root /path/to/repository
"""
import argparse
import json
import os
import re
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES = os.path.join(HERE, "..", "templates", "memory")
START, END = "<!-- team-workflow:start -->", "<!-- team-workflow:end -->"
POINTER = f"""{START}
## Project memory (team-workflow)

Read `docs/memory/INDEX.md` first, then `docs/memory/STATE.md` and the area card for your
task. At the end of every task give a report (done, verified with evidence, findings,
decisions for the user) and ask before applying anything the user did not request. When files
change, update `docs/memory/STATE.md` (and the area card or `DECISIONS.md` when relevant).
{END}
"""
COMMANDS_MARK = "<build, lint and test commands>"


def detect_commands(root):
    """Build, lint and test commands guessed from the files at the repository root."""
    def has(name):
        return os.path.exists(os.path.join(root, name))

    cmds = []
    if has("go.mod"):
        cmds += ["go build ./...", "go vet ./...", "go test ./..."]
    if has("package.json"):
        try:
            with open(os.path.join(root, "package.json"), encoding="utf-8") as f:
                scripts = json.load(f).get("scripts", {})
        except (OSError, ValueError, AttributeError):
            scripts = {}
        cmds += [f"npm run {s}" for s in ("build", "lint", "test") if s in scripts]
    if has("Cargo.toml"):
        cmds += ["cargo build", "cargo clippy", "cargo test"]
    if has("pyproject.toml") or has("setup.py") or has("requirements.txt"):
        cmds += ["python3 -m pytest"]
    if has("pom.xml"):
        cmds += ["mvn -q verify"]
    if has("build.gradle") or has("build.gradle.kts"):
        cmds += ["./gradlew build"]
    return cmds


def copy_templates(root):
    dest_root = os.path.join(root, "docs", "memory")
    created = []
    for dirpath, _, files in os.walk(TEMPLATES):
        for name in sorted(files):
            src = os.path.join(dirpath, name)
            dest = os.path.normpath(os.path.join(dest_root, os.path.relpath(src, TEMPLATES)))
            if os.path.exists(dest):
                continue
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(src, dest)
            created.append(dest)
    return created


def fill_commands(playbooks, cmds):
    with open(playbooks, encoding="utf-8") as f:
        text = f.read()
    if cmds and COMMANDS_MARK in text:
        with open(playbooks, "w", encoding="utf-8") as f:
            f.write(text.replace(COMMANDS_MARK, "\n".join(cmds)))


def add_pointer(path, create):
    """Insert or refresh the pointer block; False when the file is absent and not created."""
    exists = os.path.exists(path)
    if not exists and not create:
        return False
    text = ""
    if exists:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    if START in text:
        block = re.compile(re.escape(START) + r".*?" + re.escape(END) + r"\n?", re.S)
        new = block.sub(lambda _: POINTER, text)
    else:
        new = (text.rstrip("\n") + "\n\n" if text.strip() else "") + POINTER
    if new != text:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new)
    return True


def main():
    ap = argparse.ArgumentParser(description="Create docs/memory and point the agent files to it.")
    ap.add_argument("--root", default=".", help="repository root (default: current directory)")
    root = os.path.abspath(ap.parse_args().root)
    created = copy_templates(root)
    playbooks = os.path.join(root, "docs", "memory", "PLAYBOOKS.md")
    if playbooks in created:
        fill_commands(playbooks, detect_commands(root))
    for path in created:
        print(f"created {os.path.relpath(path, root)}")
    for name, create in (("AGENTS.md", True), ("GEMINI.md", False), ("CLAUDE.md", False)):
        if add_pointer(os.path.join(root, name), create):
            print(f"pointer in {name}")


if __name__ == "__main__":
    main()
