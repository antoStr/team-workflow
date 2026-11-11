---
id: tools-remote_dashboard
title: remote_dashboard.py
layer: tools
tags: [code, py]
aliases: [tools/remote_dashboard.py, remote_dashboard.py]
upstream:
downstream:
files: [tools/remote_dashboard.py]
status: active
last_updated: 2026-11-11T22:06:53
---

# remote_dashboard.py

Remote Telemetry & Hardware Status Dashboard.

Provides a responsive mobile web dashboard and JSON API on port 8080,
bridged to the outside world via Cloudflare Tunnel for secure, zero-token
remote monitoring from smartphones and external devices.

## Contracts

### Classes
- `DashboardHandler` (methods: _send_security_headers, do_GET, log_message)

### Functions
- `run_server(port, host)`

## Dependencies
### Upstream
- None
### Downstream
- None
