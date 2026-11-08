#!/usr/bin/env python3
"""Import Strix autonomous pentesting skills, vulnerability playbooks, and methodologies into team-workflow library."""
import hashlib
import json
import os
import re
import shutil

STRIX_REPO = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "strix_repo"))
LIBRARY_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "skills", "team-workflow", "library"))
INDEX_FILE = os.path.join(LIBRARY_DIR, "index.json")


def _hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]


def _slug(name):
    clean = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return clean


def _extract_desc(content, default_desc):
    desc = default_desc
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm, body = parts[1], parts[2]
            m = re.search(r"description:\s*(.*?)(?=\n[a-z0-9_-]+:|\n---|\Z)", fm, re.DOTALL)
            if m:
                desc = " ".join(m.group(1).split()).strip('"\'')[:280]
            else:
                lines = [l.strip() for l in body.splitlines() if l.strip() and not l.strip().startswith("#")]
                if lines:
                    desc = lines[0][:280]
    else:
        lines = [l.strip() for l in content.splitlines() if l.strip() and not l.strip().startswith("#")]
        if lines:
            desc = lines[0][:280]
    return desc.replace("prove nothing", "prove no immunity")


def main():
    if not os.path.isdir(STRIX_REPO):
        raise SystemExit(f"Strix repo not found at {STRIX_REPO}")

    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog["packs"]["strix-pentest"] = (
        "Autonomous penetration testing, proof-of-concept exploit verification, "
        "vulnerability playbooks, and counter-evidence analysis from Strix."
    )

    imported_count = 0
    existing_ids = {e["id"] for e in catalog["entries"]}

    # 1. Import high-level consumer skills from skills/
    strix_skills_dir = os.path.join(STRIX_REPO, "skills")
    if os.path.isdir(strix_skills_dir):
        for item in sorted(os.listdir(strix_skills_dir)):
            skill_path = os.path.join(strix_skills_dir, item, "SKILL.md")
            if os.path.isfile(skill_path):
                with open(skill_path, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

                # Extract description from frontmatter
                desc = "Autonomous penetration testing workflow from Strix."
                m = re.search(r"description:\s*(.*?)(?=\n[a-z0-9_-]+:|\n---|\Z)", content, re.DOTALL)
                if m:
                    desc = " ".join(m.group(1).split()).strip('"\'')

                entry_id = f"strix-{_slug(item)}"
                target_dir = os.path.join(LIBRARY_DIR, entry_id)
                os.makedirs(target_dir, exist_ok=True)
                main_file = os.path.join(target_dir, "MAIN.md")

                header = (
                    f"<!-- Imported from usestrix/strix (Apache-2.0) -->\n"
                    f"# Strix Pentest Workflow: {item}\n\n"
                )
                with open(main_file, "w", encoding="utf-8") as f:
                    f.write(header + content)

                if entry_id not in existing_ids:
                    catalog["entries"].append({
                        "id": entry_id,
                        "kind": "skill",
                        "pack": "strix-pentest",
                        "description": desc[:300],
                        "hash": _hash(content)
                    })
                    existing_ids.add(entry_id)
                imported_count += 1

    # 2. Import vulnerability playbooks from strix/skills/vulnerabilities/
    vuln_dir = os.path.join(STRIX_REPO, "strix", "skills", "vulnerabilities")
    if os.path.isdir(vuln_dir):
        for fname in sorted(os.listdir(vuln_dir)):
            if fname.endswith(".md"):
                vpath = os.path.join(vuln_dir, fname)
                with open(vpath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

                base_name = os.path.splitext(fname)[0]
                entry_id = f"pentest-vuln-{_slug(base_name)}"
                title = base_name.replace("_", " ").title()

                desc = _extract_desc(content, f"Penetration testing & vulnerability playbook for {title}.")

                target_dir = os.path.join(LIBRARY_DIR, entry_id)
                os.makedirs(target_dir, exist_ok=True)
                main_file = os.path.join(target_dir, "MAIN.md")

                header = (
                    f"<!-- Imported from usestrix/strix (Apache-2.0) -->\n"
                    f"# Vulnerability Playbook: {title}\n\n"
                )
                with open(main_file, "w", encoding="utf-8") as f:
                    f.write(header + content)

                # Update existing or add new
                found = False
                for e in catalog["entries"]:
                    if e["id"] == entry_id:
                        e["description"] = desc
                        e["hash"] = _hash(content)
                        found = True
                        break
                if not found:
                    catalog["entries"].append({
                        "id": entry_id,
                        "kind": "skill",
                        "pack": "strix-pentest",
                        "description": desc,
                        "hash": _hash(content)
                    })
                    existing_ids.add(entry_id)
                imported_count += 1

    # 3. Import analysis & methodology skills from strix/skills/analysis/
    analysis_dir = os.path.join(STRIX_REPO, "strix", "skills", "analysis")
    if os.path.isdir(analysis_dir):
        for fname in sorted(os.listdir(analysis_dir)):
            if fname.endswith(".md"):
                apath = os.path.join(analysis_dir, fname)
                with open(apath, "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()

                base_name = os.path.splitext(fname)[0]
                entry_id = f"pentest-analysis-{_slug(base_name)}"
                title = base_name.replace("_", " ").title()

                desc = _extract_desc(content, f"Strix analysis methodology for {title}.")

                target_dir = os.path.join(LIBRARY_DIR, entry_id)
                os.makedirs(target_dir, exist_ok=True)
                main_file = os.path.join(target_dir, "MAIN.md")

                header = (
                    f"<!-- Imported from usestrix/strix (Apache-2.0) -->\n"
                    f"# Security Analysis Methodology: {title}\n\n"
                )
                with open(main_file, "w", encoding="utf-8") as f:
                    f.write(header + content)

                # Update existing or add new
                found = False
                for e in catalog["entries"]:
                    if e["id"] == entry_id:
                        e["description"] = desc
                        e["hash"] = _hash(content)
                        found = True
                        break
                if not found:
                    catalog["entries"].append({
                        "id": entry_id,
                        "kind": "skill",
                        "pack": "strix-pentest",
                        "description": desc,
                        "hash": _hash(content)
                    })
                    existing_ids.add(entry_id)
                imported_count += 1

    # Sort entries by ID
    catalog["entries"].sort(key=lambda e: e["id"])

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=1, ensure_ascii=False)

    print(f"Imported {imported_count} Strix skills and playbooks into pack 'strix-pentest'.")
    print(f"Total library entries now: {len(catalog['entries'])}")


if __name__ == "__main__":
    main()
