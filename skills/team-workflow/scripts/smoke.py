#!/usr/bin/env python3
"""Smoke-test & Live Run Verifier for applications, games, and servers.

Eliminates the AI hallucination of 'Problem solved!' without actually testing.
Launches the real application process in a monitored environment, checks for boot
crashes, unhandled exceptions, stderr errors, or immediate aborts.

Returns empirical proof of whether an application or game truly boots and runs.
"""
from datetime import datetime, timezone
import os
import re
import subprocess
import sys
import time

FATAL_REGEX = re.compile(
    r"^.*?(?:traceback \(most recent call last\):|unhandled exception|segmentation fault|"
    r"fatal error|core dumped|panic:|nullpointerexception|syntaxerror:|referenceerror:|"
    r"typeerror:|importerror:|modulenotfounderror:|errno \d+|cannot find module|"
    r"process exited with code [1-9]).*?$",
    re.IGNORECASE | re.MULTILINE
)


def to_wsl_path(path):
    """Convert a Windows path (e.g. C:\\dir) to a WSL path (/mnt/c/dir)."""
    if not path:
        return None
    p = os.path.abspath(path).replace("\\", "/")
    if len(p) >= 2 and p[1] == ":":
        drive = p[0].lower()
        return f"/mnt/{drive}{p[2:]}"
    return p


def run_smoke(cmd, timeout=5.0, cwd=None, env=None, wsl=False):
    """Launch process, monitor for `timeout` seconds, verify stability.

    If wsl=True and running on Windows, wraps the execution through WSL bash.

    Returns:
        dict: {
            "ok": bool,
            "status": "STABLE" | "CRASHED" | "FATAL_LOGS" | "CLEAN_EXIT",
            "exit_code": int | None,
            "duration": float,
            "stdout": str,
            "stderr": str,
            "error_summary": str | None
        }
    """
    if not cmd:
        raise ValueError("Smoke test requires a command string or list.")

    use_shell = isinstance(cmd, str)
    popen_kwargs = {}
    if sys.platform != "win32":
        popen_kwargs["start_new_session"] = True

    if wsl and sys.platform == "win32":
        cmd_str = " ".join(cmd) if isinstance(cmd, list) else cmd
        effective_cwd = os.path.abspath(cwd or os.getcwd())
        cmd = ["wsl", "--cd", effective_cwd, "bash", "-c", cmd_str]
        use_shell = False
        cwd = None

    start_time = time.time()

    process = None
    stdout_data = ""
    stderr_data = ""
    crashed = False
    exit_code = None

    try:
        process = subprocess.Popen(
            cmd,
            shell=use_shell,
            cwd=cwd,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            **popen_kwargs
        )

        try:
            # Wait for timeout
            stdout_data, stderr_data = process.communicate(timeout=timeout)
            exit_code = process.returncode
            if exit_code != 0:
                crashed = True
        except subprocess.TimeoutExpired:
            # Process was still running after timeout (normal for games, servers, GUIs)
            # Terminate entire process tree to prevent orphan background zombie processes
            if sys.platform == "win32":
                try:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(process.pid)],
                                   capture_output=True, timeout=5)
                except Exception:
                    try:
                        process.terminate()
                    except Exception:
                        pass
            else:
                try:
                    import signal
                    os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                except Exception:
                    try:
                        process.kill()
                    except Exception:
                        pass
            try:
                stdout_data, stderr_data = process.communicate(timeout=2)
            except Exception:
                pass
            exit_code = process.returncode if process else None

    except OSError as e:
        return {
            "ok": False,
            "status": "LAUNCH_FAILED",
            "exit_code": -1,
            "duration": 0.0,
            "stdout": "",
            "stderr": str(e),
            "error_summary": f"Failed to execute command: {e}"
        }

    duration = round(time.time() - start_time, 2)
    combined_logs = f"{stdout_data}\n{stderr_data}"

    # Check for fatal error patterns in output with single-pass regex
    fatal_hit = None
    match = FATAL_REGEX.search(combined_logs)
    if match:
        fatal_hit = match.group(0).strip()

    if crashed:
        status = "CRASHED"
        ok = False
        summary = f"Process crashed with exit code {exit_code}. {fatal_hit or stderr_data.strip()[:200]}"
    elif fatal_hit:
        status = "FATAL_LOGS"
        ok = False
        summary = f"Process output contains fatal error: {fatal_hit}"
    elif exit_code == 0:
        status = "CLEAN_EXIT"
        ok = True
        summary = f"Process executed and exited cleanly (0) in {duration}s."
    else:
        status = "STABLE"
        ok = True
        summary = f"Process booted and ran stably for {duration}s without crashing or fatal exceptions."

    return {
        "ok": ok,
        "status": status,
        "exit_code": exit_code,
        "duration": duration,
        "stdout": stdout_data[:2000],
        "stderr": stderr_data[:2000],
        "error_summary": summary if not ok else None,
        "summary": summary
    }


def format_report(result):
    flag = "🟢 PASSED" if result["ok"] else "🔴 FAILED"
    lines = [
        f"Smoke Test: {flag} [{result['status']}]",
        f"Duration: {result['duration']}s | Exit code: {result['exit_code']}",
        f"Summary: {result['summary']}"
    ]
    if not result["ok"] and result.get("stderr"):
        lines.append(f"Stderr:\n{result['stderr'][:500]}")
    return "\n".join(lines)
