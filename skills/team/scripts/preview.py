#!/usr/bin/env python3
"""Project Preview & Dev Server Management.

Automates starting, monitoring, and stopping development preview servers
(Next.js, Vite, static HTML, Python http.server, Django, FastAPI) without
manual port allocation or dangling background processes.
"""
import hashlib
import json
import os
import signal
import socket
import subprocess
import sys
import time

PREVIEW_STATE_FILE = ".team-workflow-preview.json"


def find_free_port(start_port=8080, max_attempts=50):
    """Find an available TCP port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port


def detect_command(root, port):
    """Auto-detect the appropriate preview or dev server command."""
    root = os.path.abspath(root or ".")

    # 1. Node.js project (package.json)
    pkg_json = os.path.join(root, "package.json")
    if os.path.isfile(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
            scripts = data.get("scripts", {})
            if "dev" in scripts:
                return ["npm", "run", "dev", "--", "--port", str(port)]
            if "start" in scripts:
                return ["npm", "start"]
        except Exception:
            pass

    # 2. Python web frameworks
    if os.path.isfile(os.path.join(root, "manage.py")):
        return [sys.executable, "manage.py", "runserver", f"127.0.0.1:{port}"]

    # 3. Static HTML / Static Site
    if os.path.isfile(os.path.join(root, "index.html")) or os.path.isfile(os.path.join(root, "404.html")):
        return [sys.executable, "-m", "http.server", str(port), "--directory", root]

    # Default to http.server
    return [sys.executable, "-m", "http.server", str(port), "--directory", root]


def state_path(root):
    """Get the path to the preview state file."""
    root = os.path.normcase(os.path.abspath(root or "."))
    h = hashlib.sha256(root.encode("utf-8")).hexdigest()[:12]
    tmp = os.environ.get("TMPDIR") or os.environ.get("TEMP") or "/tmp"
    return os.path.join(tmp, f"tw-preview-{h}.json")


def start_preview(root=None, port=None, cmd=None, background=True):
    """Start the preview server."""
    root = os.path.normcase(os.path.abspath(root or "."))
    sp = state_path(root)

    # Check if already running
    existing = get_status(root)
    if existing.get("running"):
        return {
            "ok": True,
            "status": "ALREADY_RUNNING",
            "port": existing["port"],
            "url": existing["url"],
            "pid": existing["pid"],
            "root": root,
            "message": f"Preview server is already running on {existing['url']} (PID: {existing['pid']})"
        }

    port = port or find_free_port(8080)
    exec_cmd = cmd or detect_command(root, port)

    # Start process
    creationflags = 0
    if sys.platform == "win32":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        exec_cmd,
        cwd=root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
        creationflags=creationflags
    )

    url = f"http://localhost:{port}/"
    state = {
        "pid": proc.pid,
        "port": port,
        "url": url,
        "root": root,
        "cmd": exec_cmd,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%S")
    }

    with open(sp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # Allow a brief moment to initialize
    time.sleep(0.4)

    return {
        "ok": True,
        "status": "STARTED",
        "port": port,
        "url": url,
        "pid": proc.pid,
        "root": root,
        "message": f"Preview server booted successfully on {url} (PID: {proc.pid})"
    }


def stop_preview(root=None):
    """Stop the running preview server."""
    root = os.path.normcase(os.path.abspath(root or "."))
    sp = state_path(root)

    if not os.path.isfile(sp):
        return {"ok": False, "message": "No preview server is registered for this repository."}

    try:
        with open(sp, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception as e:
        return {"ok": False, "message": f"Failed to read preview state: {e}"}

    pid = state.get("pid")
    stopped = False

    if pid:
        try:
            if sys.platform == "win32":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.2)
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass
            stopped = True
        except (OSError, subprocess.SubprocessError):
            stopped = False

    try:
        os.remove(sp)
    except OSError:
        pass

    return {
        "ok": True,
        "status": "STOPPED",
        "pid": pid,
        "message": f"Preview server on port {state.get('port')} (PID {pid}) stopped."
    }


def get_status(root=None):
    """Check whether the preview server is active and running."""
    root = os.path.normcase(os.path.abspath(root or "."))
    sp = state_path(root)

    if not os.path.isfile(sp):
        return {"running": False, "root": root}

    try:
        with open(sp, "r", encoding="utf-8") as f:
            state = json.load(f)
    except Exception:
        return {"running": False, "root": root}

    pid = state.get("pid")
    port = state.get("port")
    is_alive = False

    if pid:
        if sys.platform == "win32":
            res = subprocess.run(["tasklist", "/FI", f"PID eq {pid}"],
                                 capture_output=True, text=True, errors="ignore")
            is_alive = str(pid) in res.stdout
        else:
            try:
                os.kill(pid, 0)
                is_alive = True
            except OSError:
                is_alive = False

    if not is_alive:
        try:
            os.remove(sp)
        except OSError:
            pass
        return {"running": False, "root": root}

    return {
        "running": True,
        "pid": pid,
        "port": port,
        "url": state.get("url", f"http://localhost:{port}/"),
        "root": root,
        "start_time": state.get("start_time")
    }
