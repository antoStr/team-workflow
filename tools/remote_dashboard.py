#!/usr/bin/env python3
"""Remote Telemetry & Hardware Status Dashboard.

Provides a responsive mobile web dashboard and JSON API on port 8080,
bridged to the outside world via Cloudflare Tunnel for secure, zero-token
remote monitoring from smartphones and external devices.
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
STATUS_FILE = os.path.join(ROOT, "hardware_status.json")
ALERT_FILE = os.path.join(ROOT, "HARDWARE_ALERT.json")
THERMAL_ALERT_FILE = os.path.join(ROOT, "THERMAL_ALERT.json")
THERMAL_FILE = os.path.join(ROOT, "thermal_status.json")


HTML_PAGE = """<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>TEAM-WORKFLOW // REMOTE MONITOR</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b0d13;
      --card-bg: rgba(20, 24, 34, 0.75);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent: #6366f1;
      --green: #10b981;
      --yellow: #f59e0b;
      --red: #ef4444;
      --text: #f3f4f6;
      --text-muted: #9ca3af;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      min-height: 100vh;
      padding: 16px;
      -webkit-font-smoothing: antialiased;
    }
    .header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 16px;
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 12px;
      margin-bottom: 16px;
      backdrop-filter: blur(12px);
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 700;
      font-size: 15px;
      letter-spacing: -0.5px;
    }
    .status-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      font-family: 'JetBrains Mono', monospace;
    }
    .badge-ok { background: rgba(16, 185, 129, 0.15); color: var(--green); border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-warn { background: rgba(245, 158, 11, 0.15); color: var(--yellow); border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-crit { background: rgba(239, 68, 68, 0.2); color: var(--red); border: 1px solid rgba(239, 68, 68, 0.4); animation: pulse 1.5s infinite; }
    @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; }
    .alert-banner {
      background: rgba(239, 68, 68, 0.15);
      border: 1px solid var(--red);
      border-radius: 10px;
      padding: 12px 16px;
      margin-bottom: 16px;
      color: #fca5a5;
      font-size: 13px;
      line-height: 1.5;
    }
    .grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 16px;
    }
    .card {
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 14px;
      padding: 18px;
      backdrop-filter: blur(12px);
    }
    .card-title {
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      color: var(--text-muted);
      margin-bottom: 14px;
      text-transform: uppercase;
    }
    .value-huge {
      font-family: 'JetBrains Mono', monospace;
      font-size: 32px;
      font-weight: 700;
      color: var(--text);
      display: flex;
      align-items: baseline;
      gap: 4px;
    }
    .value-huge span { font-size: 16px; color: var(--text-muted); font-weight: 400; }
    .sub-meta {
      font-size: 12px;
      color: var(--text-muted);
      margin-top: 8px;
      display: flex;
      justify-content: space-between;
    }
    .progress-bar {
      height: 6px;
      background: rgba(255, 255, 255, 0.08);
      border-radius: 999px;
      margin-top: 12px;
      overflow: hidden;
    }
    .progress-fill {
      height: 100%;
      border-radius: 999px;
      transition: width 0.4s ease;
    }
    .fill-green { background: var(--green); }
    .fill-yellow { background: var(--yellow); }
    .fill-red { background: var(--red); }
    .footer {
      text-align: center;
      margin-top: 24px;
      font-size: 11px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
    }
  </style>
</head>
<body>
  <div class="header">
    <div class="brand">
      <span>🧭</span>
      <span>TEAM-WORKFLOW // REMOTE</span>
    </div>
    <div id="statusBadge" class="status-badge badge-ok">
      <span class="dot"></span>
      <span id="statusText">CONNECTING...</span>
    </div>
  </div>

  <div id="alertContainer"></div>

  <div class="grid">
    <div class="card">
      <div class="card-title">
        <span>CPU Monitor</span>
        <span id="cpuLoad">--% Load</span>
      </div>
      <div class="value-huge">
        <span id="cpuTemp">--</span><span>°C</span>
      </div>
      <div class="progress-bar">
        <div id="cpuBar" class="progress-fill fill-green" style="width: 0%"></div>
      </div>
      <div class="sub-meta">
        <span>Max: <b id="cpuMax">--°C</b></span>
        <span>Soglia Critica: 93°C</span>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span id="gpuName">GPU Monitor</span>
        <span id="gpuLoad">--% Util</span>
      </div>
      <div class="value-huge">
        <span id="gpuTemp">--</span><span>°C</span>
      </div>
      <div class="progress-bar">
        <div id="gpuBar" class="progress-fill fill-green" style="width: 0%"></div>
      </div>
      <div class="sub-meta">
        <span>VRAM: <b id="vramText">-- / -- MB</b></span>
        <span>Max: <b id="gpuMax">--°C</b></span>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span>Memoria RAM</span>
        <span id="ramPercent">--%</span>
      </div>
      <div class="value-huge">
        <span id="ramUsed">--</span><span>GB</span>
      </div>
      <div class="progress-bar">
        <div id="ramBar" class="progress-fill fill-green" style="width: 0%"></div>
      </div>
      <div class="sub-meta">
        <span>Totale: <b id="ramTotal">-- GB</b></span>
        <span>Libera: <b id="ramFree">-- GB</b></span>
      </div>
    </div>

    <div class="card">
      <div class="card-title">
        <span>Spazio Disco (C:)</span>
        <span id="diskPercent">--%</span>
      </div>
      <div class="value-huge">
        <span id="diskFree">--</span><span>GB</span>
      </div>
      <div class="progress-bar">
        <div id="diskBar" class="progress-fill fill-green" style="width: 0%"></div>
      </div>
      <div class="sub-meta">
        <span>Spazio Libero Rimasto</span>
        <span>Totale: <b id="diskTotal">-- GB</b></span>
      </div>
    </div>
  </div>

  <div class="footer">
    Aggiornamento real-time (2.5s) · Zero Token Telemetry · <span id="lastUpdated">--:--:--</span>
  </div>

  <script>
    async function updateDashboard() {
      try {
        const res = await fetch('/api/status');
        if (!res.ok) return;
        const data = await res.json();
        
        // Status Badge
        const badge = document.getElementById('statusBadge');
        const stText = document.getElementById('statusText');
        badge.className = 'status-badge ' + (data.status === 'OK' ? 'badge-ok' : (data.status === 'WARNING' ? 'badge-warn' : 'badge-crit'));
        stText.textContent = data.status;

        // Alerts Banner
        const alertBox = document.getElementById('alertContainer');
        if (data.alerts && data.alerts.length > 0) {
          alertBox.innerHTML = '<div class="alert-banner">⚠️ <b>ATTENZIONE REMOTA:</b><br>' + data.alerts.join('<br>') + '</div>';
        } else {
          alertBox.innerHTML = '';
        }

        // CPU
        if (data.CPU) {
          const temp = data.CPU.Temp_C || '--';
          document.getElementById('cpuTemp').textContent = temp;
          document.getElementById('cpuMax').textContent = (data.CPU.Max_Temp_C || '--') + '°C';
          document.getElementById('cpuLoad').textContent = (data.CPU.LoadPercent !== null ? data.CPU.LoadPercent + '%' : '--') + ' Load';
          
          const bar = document.getElementById('cpuBar');
          const pct = Math.min(100, Math.max(0, (temp / 100) * 100));
          bar.style.width = pct + '%';
          bar.className = 'progress-fill ' + (temp >= 93 ? 'fill-red' : (temp >= 85 ? 'fill-yellow' : 'fill-green'));
        }

        // GPU
        if (data.GPU) {
          document.getElementById('gpuName').textContent = data.GPU.Name || 'GPU Monitor';
          const gtemp = data.GPU.Temp_C || '--';
          document.getElementById('gpuTemp').textContent = gtemp;
          document.getElementById('gpuMax').textContent = (data.GPU.Max_Temp_C || '--') + '°C';
          document.getElementById('gpuLoad').textContent = (data.GPU.UtilPercent || '0') + '% Util';
          document.getElementById('vramText').textContent = (data.GPU.MemUsedMB || '0') + ' / ' + (data.GPU.MemTotalMB || '0') + ' MB';

          const gbar = document.getElementById('gpuBar');
          const gpct = Math.min(100, Math.max(0, (gtemp / 100) * 100));
          gbar.style.width = gpct + '%';
          gbar.className = 'progress-fill ' + (gtemp >= 88 ? 'fill-red' : (gtemp >= 80 ? 'fill-yellow' : 'fill-green'));
        }

        // RAM
        if (data.RAM) {
          document.getElementById('ramPercent').textContent = data.RAM.PercentUsed + '%';
          document.getElementById('ramUsed').textContent = data.RAM.UsedGB;
          document.getElementById('ramTotal').textContent = data.RAM.TotalGB + ' GB';
          document.getElementById('ramFree').textContent = data.RAM.FreeGB + ' GB';
          
          const rbar = document.getElementById('ramBar');
          rbar.style.width = data.RAM.PercentUsed + '%';
          rbar.className = 'progress-fill ' + (data.RAM.PercentUsed >= 96 ? 'fill-red' : (data.RAM.PercentUsed >= 90 ? 'fill-yellow' : 'fill-green'));
        }

        // Disk
        if (data.Disks && data.Disks.length > 0) {
          const d = data.Disks[0];
          document.getElementById('diskPercent').textContent = d.PercentUsed + '% Usato';
          document.getElementById('diskFree').textContent = d.FreeGB;
          document.getElementById('diskTotal').textContent = d.TotalGB + ' GB';

          const dbar = document.getElementById('diskBar');
          dbar.style.width = d.PercentUsed + '%';
          dbar.className = 'progress-fill ' + (d.PercentUsed >= 95 ? 'fill-red' : (d.PercentUsed >= 85 ? 'fill-yellow' : 'fill-green'));
        }

        document.getElementById('lastUpdated').textContent = data.timestamp || new Date().toLocaleTimeString();

      } catch (err) {
        console.error("Dashboard poll failed", err);
      }
    }

    setInterval(updateDashboard, 2500);
    updateDashboard();
  </script>
</body>
</html>
"""


# Global in-memory cache for telemetry status
_status_cache = {"data": {"status": "OK", "timestamp": "", "alerts": []}, "mtime": 0}


class DashboardHandler(BaseHTTPRequestHandler):
    def _send_security_headers(self, content_type="text/html; charset=utf-8"):
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

    def do_GET(self):
        try:
            if self.path in ("/", "/index.html"):
                self.send_response(200)
                self._send_security_headers("text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(HTML_PAGE.encode("utf-8"))
            elif self.path == "/api/status":
                global _status_cache
                curr_mtime = 0
                for fpath in (STATUS_FILE, ALERT_FILE, THERMAL_ALERT_FILE, THERMAL_FILE):
                    if os.path.exists(fpath):
                        curr_mtime = max(curr_mtime, os.path.getmtime(fpath))

                if curr_mtime > _status_cache["mtime"] or not (_status_cache["data"].get("Timestamp") or _status_cache["data"].get("timestamp")):
                    data = {"status": "OK", "timestamp": "", "alerts": []}
                    if os.path.exists(STATUS_FILE):
                        try:
                            with open(STATUS_FILE, "r", encoding="utf-8-sig") as f:
                                data = json.load(f)
                        except Exception:
                            pass
                    elif os.path.exists(THERMAL_FILE):
                        try:
                            with open(THERMAL_FILE, "r", encoding="utf-8-sig") as f:
                                th = json.load(f)
                                data["status"] = th.get("Status", "OK")
                                data["timestamp"] = th.get("Timestamp", "")
                                data["CPU"] = {"Temp_C": th.get("CPU_Temp_C"), "Max_Temp_C": th.get("Max_CPU_C")}
                                data["GPU"] = {"Temp_C": th.get("GPU_Temp_C"), "Max_Temp_C": th.get("Max_GPU_C")}
                        except Exception:
                            pass

                    # Normalize keys
                    if "Timestamp" in data and "timestamp" not in data:
                        data["timestamp"] = data["Timestamp"]
                    if "Status" in data and "status" not in data:
                        data["status"] = data["Status"]

                    # Merge any alerts from either HARDWARE_ALERT or THERMAL_ALERT
                    for af in (ALERT_FILE, THERMAL_ALERT_FILE):
                        if os.path.exists(af):
                            try:
                                with open(af, "r", encoding="utf-8-sig") as f:
                                    al = json.load(f)
                                    data["status"] = al.get("Severity", al.get("Status", "CRITICAL"))
                                    msgs = al.get("Messages", [f"Allerta da {os.path.basename(af)}"])
                                    data["alerts"] = list(set(data.get("alerts", []) + msgs))
                            except Exception:
                                pass

                    _status_cache["data"] = data
                    _status_cache["mtime"] = curr_mtime

                payload = json.dumps(_status_cache["data"]).encode("utf-8")
                self.send_response(200)
                self._send_security_headers("application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(payload)
            else:
                self.send_response(404)
                self.end_headers()
        except (ConnectionResetError, BrokenPipeError):
            pass

    def log_message(self, format, *args):
        # Quiet logger
        return


def run_server(port=8080, host="127.0.0.1"):
    server = ThreadingHTTPServer((host, port), DashboardHandler)
    print(f"[Remote Dashboard] Server listening on http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    p = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(p)
