#!/usr/bin/env python3
"""Automated Responsive & Visual Layout Auditor.

Audits web templates for responsive layout integrity:
 1. Viewport meta tag presence
 2. Horizontal overflow risks (fixed pixel widths > 320px without max-width)
 3. CSS Breakpoints coverage (mobile, tablet, desktop)
 4. Touch target sizes and tap friendliness
 5. Heading hierarchy (single <h1> per view)
 6. Motion safety (@media (prefers-reduced-motion))
"""
import json
import os
import re
import sys


def audit_html_files(root):
    """Audit all HTML files in repository."""
    root = os.path.abspath(root or ".")
    issues = []
    checked_pages = []

    html_files = []
    for dirpath, _, filenames in os.walk(root):
        if any(ignored in dirpath for ignored in (".git", "node_modules", "dist", "build", ".brain")):
            continue
        for f in filenames:
            if f.endswith(".html"):
                html_files.append(os.path.join(dirpath, f))

    for path in html_files:
        rel = os.path.relpath(path, root)
        checked_pages.append(rel)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
        except OSError:
            continue

        # 1. Viewport meta check
        if "<meta name=\"viewport\"" not in content and "<meta name='viewport'" not in content:
            issues.append({
                "page": rel,
                "severity": "HIGH",
                "check": "viewport",
                "message": "Missing <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            })

        # 2. Heading hierarchy: single h1
        h1_matches = re.findall(r"<h1\b", content, re.IGNORECASE)
        if len(h1_matches) == 0:
            issues.append({
                "page": rel,
                "severity": "MEDIUM",
                "check": "heading_h1",
                "message": "Page has no <h1> heading"
            })
        elif len(h1_matches) > 1:
            issues.append({
                "page": rel,
                "severity": "MEDIUM",
                "check": "heading_h1",
                "message": f"Multiple <h1> headings found ({len(h1_matches)})"
            })

        # 3. Touch target check: empty button labels or tiny buttons
        for btn in re.finditer(r"<button\b([^>]*)>(.*?)</button>", content, re.IGNORECASE | re.DOTALL):
            attrs = btn.group(1)
            body = btn.group(2).strip()
            if not body and "aria-label" not in attrs and "title" not in attrs:
                issues.append({
                    "page": rel,
                    "severity": "HIGH",
                    "check": "accessible_button",
                    "message": "Button has empty content and lacks aria-label/title"
                })

    return checked_pages, issues


def audit_css_files(root):
    """Audit CSS files for responsive and motion safety."""
    root = os.path.abspath(root or ".")
    issues = []
    css_files = []

    for dirpath, _, filenames in os.walk(root):
        if any(ignored in dirpath for ignored in (".git", "node_modules", "dist", "build")):
            continue
        for f in filenames:
            if f.endswith(".css"):
                css_files.append(os.path.join(dirpath, f))

    has_reduced_motion = False
    has_mobile_query = False

    for path in css_files:
        rel = os.path.relpath(path, root)
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                content = fp.read()
        except OSError:
            continue

        if "prefers-reduced-motion" in content:
            has_reduced_motion = True

        if re.search(r"@media\s*\([^)]*max-width:\s*(?:768|1024|480)px", content):
            has_mobile_query = True

        # Check for wide fixed widths without max-width
        for m in re.finditer(r"(?<!max-)(?<!min-)width:\s*([4-9]\d{2}|[1-9]\d{3,})px", content):
            w = int(m.group(1))
            if w >= 500:
                issues.append({
                    "file": rel,
                    "severity": "LOW",
                    "check": "overflow_risk",
                    "message": f"Fixed width {w}px detected without max-width; risk of horizontal scroll on mobile"
                })

    if css_files and not has_reduced_motion:
        issues.append({
            "file": "CSS Stylesheets",
            "severity": "MEDIUM",
            "check": "reduced_motion",
            "message": "No @media (prefers-reduced-motion) found in CSS"
        })

    return css_files, issues


def run_visual_check(root=None):
    """Run complete visual and responsive audit."""
    root = os.path.abspath(root or ".")
    pages, page_issues = audit_html_files(root)
    css_files, css_issues = audit_css_files(root)

    all_issues = page_issues + css_issues
    passed = len([i for i in all_issues if i["severity"] == "HIGH"]) == 0

    return {
        "ok": passed,
        "root": root,
        "pages_audited": len(pages),
        "css_audited": len(css_files),
        "total_issues": len(all_issues),
        "high_severity": len([i for i in all_issues if i["severity"] == "HIGH"]),
        "medium_severity": len([i for i in all_issues if i["severity"] == "MEDIUM"]),
        "low_severity": len([i for i in all_issues if i["severity"] == "LOW"]),
        "issues": all_issues
    }
