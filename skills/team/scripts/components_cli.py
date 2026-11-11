#!/usr/bin/env python3
"""Component Scaffolding CLI for Frontend-Components.

Provides direct scaffolding (`tw.py component add <name>`) for modern UI components:
 - cmdk (Command Palette ⌘K / Ctrl+K)
 - sonner (Stacked modern toast notifications)
 - number-flow (Smooth animated numeric rolling counters)
 - vaul (Mobile gesture bottom-sheet drawer)
 - spotlight (Card hover spotlight glow)
 - marquee (Continuous hardware-accelerated partner marquee)
 - dot-grid (Clean editorial background dot grid)
"""
import os
import sys

TEMPLATES = {
    "cmdk": {
        "title": "CMDK Command Menu (⌘K / Ctrl+K)",
        "files": {
            "cmdk.js": '''function initCmdkPalette() {
  const dialog = document.getElementById("cmdkDialog");
  const triggerBtn = document.getElementById("cmdkTrigger");
  const closeBtn = document.getElementById("cmdkClose");
  const input = document.getElementById("cmdkInput");
  const emptyState = document.getElementById("cmdkEmpty");
  if (!dialog || !input) return;

  const items = Array.from(dialog.querySelectorAll(".cmdk-item"));
  let triggerElement = null;

  function openCmdk(trigger) {
    triggerElement = trigger || triggerBtn || document.activeElement;
    dialog.classList.add("is-open");
    dialog.setAttribute("aria-hidden", "false");
    document.body.style.overflow = "hidden";
    input.value = "";
    filterItems("");
    setTimeout(() => input.focus(), 60);
  }

  function closeCmdk() {
    dialog.classList.remove("is-open");
    dialog.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
    if (triggerElement && typeof triggerElement.focus === "function") {
      triggerElement.focus();
    }
  }

  if (triggerBtn) triggerBtn.addEventListener("click", (e) => { e.preventDefault(); openCmdk(triggerBtn); });
  if (closeBtn) closeBtn.addEventListener("click", closeCmdk);

  dialog.addEventListener("click", (e) => { if (e.target === dialog) closeCmdk(); });

  document.addEventListener("keydown", (e) => {
    if ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")) {
      e.preventDefault();
      dialog.classList.contains("is-open") ? closeCmdk() : openCmdk();
    } else if (e.key === "Escape" && dialog.classList.contains("is-open")) {
      closeCmdk();
    }
  });

  function filterItems(query) {
    const q = query.toLowerCase().trim();
    let visibleCount = 0;
    items.forEach(item => {
      const text = item.textContent.toLowerCase();
      const kw = (item.getAttribute("data-keywords") || "").toLowerCase();
      if (!q || text.includes(q) || kw.includes(q)) {
        item.style.display = "flex";
        visibleCount++;
      } else {
        item.style.display = "none";
      }
    });
    if (emptyState) emptyState.style.display = visibleCount === 0 ? "block" : "none";
  }

  input.addEventListener("input", (e) => filterItems(e.target.value));
}
''',
            "cmdk.css": '''.cmdk-dialog-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.65);
  backdrop-filter: blur(8px);
  z-index: 9998;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding: 10vh 1.5rem 2rem;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.2s cubic-bezier(0.16, 1, 0.3, 1);
}
.cmdk-dialog-backdrop.is-open { opacity: 1; pointer-events: auto; }
.cmdk-modal {
  width: 100%;
  max-width: 640px;
  background: #19191C;
  color: #FFFFFF;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.15);
  box-shadow: 0 24px 60px rgba(0,0,0,0.5);
  overflow: hidden;
}
.cmdk-header { display: flex; align-items: center; gap: 0.75rem; padding: 1rem 1.25rem; border-bottom: 1px solid rgba(255,255,255,0.1); }
.cmdk-input { flex: 1; background: transparent; border: none; outline: none; color: #FFFFFF; font-size: 1rem; }
.cmdk-body { max-height: 380px; overflow-y: auto; padding: 0.75rem; }
.cmdk-item { display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem 0.75rem; border-radius: 6px; cursor: pointer; color: #FFFFFF; text-decoration: none; }
.cmdk-item:hover, .cmdk-item.is-selected { background: rgba(127, 82, 255, 0.22); }
'''
        }
    },
    "sonner": {
        "title": "Sonner Stacked Toast Notification System",
        "files": {
            "sonner.js": '''const toast = (() => {
  let toaster = null;
  function getToaster() {
    if (!toaster) {
      toaster = document.getElementById("sonnerToaster");
      if (!toaster) {
        toaster = document.createElement("div");
        toaster.id = "sonnerToaster";
        toaster.className = "sonner-toaster";
        toaster.setAttribute("role", "region");
        toaster.setAttribute("aria-label", "Notifiche");
        document.body.appendChild(toaster);
      }
    }
    return toaster;
  }
  function createToast(title, desc = "", type = "info") {
    const container = getToaster();
    const item = document.createElement("div");
    item.className = `sonner-toast sonner-toast--${type}`;
    item.innerHTML = `<div class="sonner-content"><strong>${title}</strong>${desc ? `<p>${desc}</p>` : ""}</div><button class="sonner-close">&times;</button>`;
    item.querySelector(".sonner-close").onclick = () => dismiss(item);
    container.prepend(item);
    setTimeout(() => dismiss(item), 4500);
    return item;
  }
  function dismiss(item) {
    item.classList.add("is-dismissing");
    setTimeout(() => item.remove(), 250);
  }
  return {
    success: (t, d) => createToast(t, d, "success"),
    error: (t, d) => createToast(t, d, "error"),
    info: (t, d) => createToast(t, d, "info")
  };
})();
window.toast = toast;
''',
            "sonner.css": '''.sonner-toaster {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  display: flex;
  flex-direction: column-reverse;
  gap: 0.5rem;
  pointer-events: none;
  width: 360px;
  max-width: calc(100vw - 32px);
}
.sonner-toast {
  pointer-events: auto;
  padding: 0.95rem 1.15rem;
  background: #19191C;
  color: #FFFFFF;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  box-shadow: 0 12px 32px rgba(0,0,0,0.4);
  transition: all 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}
.sonner-toast.is-dismissing { opacity: 0; transform: translateX(30px) scale(0.9); }
'''
        }
    },
    "number-flow": {
        "title": "NumberFlow Animated Rolling Counters",
        "files": {
            "number-flow.js": '''function initNumberFlow() {
  const targets = document.querySelectorAll("[data-number-flow]");
  if (!targets.length) return;
  const obs = new IntersectionObserver((entries) => {
    entries.forEach(e => {
      if (e.isIntersecting) {
        animateFlow(e.target);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: 0.2 });
  targets.forEach(t => obs.observe(t));
}

function animateFlow(el) {
  const targetText = el.getAttribute("data-number-flow") || el.textContent.trim();
  const match = targetText.match(/^([^\\d.]*)(\\d+(?:\\.\\d+)?)([^\\d.]*)$/);
  if (!match) return;
  const [, prefix, rawNum, suffix] = match;
  const targetVal = parseFloat(rawNum);
  const isFloat = rawNum.includes(".");
  const decimals = isFloat ? rawNum.split(".")[1].length : 0;
  const startVal = targetVal > 1000 ? targetVal - 100 : 0;
  const duration = 1400;
  const start = performance.now();

  function step(now) {
    const p = Math.min((now - start) / duration, 1);
    const ease = 1 - Math.pow(1 - p, 3);
    const cur = startVal + (targetVal - startVal) * ease;
    el.textContent = `${prefix}${isFloat ? cur.toFixed(decimals) : Math.floor(cur)}${suffix}`;
    if (p < 1) requestAnimationFrame(step);
    else el.textContent = targetText;
  }
  requestAnimationFrame(step);
}
'''
        }
    },
    "vaul": {
        "title": "Vaul Mobile Drawer Bottom Sheet",
        "files": {
            "vaul.css": '''.vaul-drag-handle { width: 44px; height: 5px; background: rgba(0, 0, 0, 0.2); border-radius: 3px; margin: 0.5rem auto 1rem; }
.mobile-nav-drawer {
  position: fixed;
  bottom: 0; left: 0; right: 0;
  background: #FFFFFF;
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -10px 40px rgba(0, 0, 0, 0.15);
  transform: translateY(100%);
  transition: transform 0.38s cubic-bezier(0.32, 0.72, 0, 1);
  z-index: 1001;
  max-height: 85vh;
  overflow-y: auto;
  padding: 1.5rem;
}
.mobile-nav-drawer.is-open { transform: translateY(0); }
'''
        }
    },
    "spotlight": {
        "title": "Card Hover Spotlight Effect",
        "files": {
            "spotlight.css": '''.spotlight-card {
  position: relative;
  overflow: hidden;
}
.spotlight-card::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background: radial-gradient(
    500px circle at var(--spotlight-x, -9999px) var(--spotlight-y, -9999px),
    rgba(127, 82, 255, 0.08),
    transparent 60%
  );
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.3s ease;
  z-index: 1;
}
.spotlight-card:hover::before { opacity: 1; }
''',
            "spotlight.js": '''function initSpotlightCards() {
  document.querySelectorAll(".spotlight-card").forEach(c => {
    c.addEventListener("mousemove", (e) => {
      const r = c.getBoundingClientRect();
      c.style.setProperty("--spotlight-x", `${e.clientX - r.left}px`);
      c.style.setProperty("--spotlight-y", `${e.clientY - r.top}px`);
    });
  });
}
'''
        }
    },
    "marquee": {
        "title": "Continuous Partner Marquee",
        "files": {
            "marquee.css": '''.marquee-container {
  overflow: hidden;
  display: flex;
  mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);
  -webkit-mask-image: linear-gradient(to right, transparent, black 15%, black 85%, transparent);
}
.marquee-track {
  display: flex;
  gap: 3rem;
  width: max-content;
  animation: marquee-scroll 25s linear infinite;
  will-change: transform;
}
.marquee-container:hover .marquee-track { animation-play-state: paused; }
@keyframes marquee-scroll {
  from { transform: translate3d(0, 0, 0); }
  to { transform: translate3d(-50%, 0, 0); }
}
'''
        }
    },
    "dot-grid": {
        "title": "Subtle Dot Grid Background Pattern",
        "files": {
            "dot-grid.css": '''.dot-grid-bg {
  background-image: radial-gradient(rgba(127, 82, 255, 0.12) 1.2px, transparent 1.2px);
  background-size: 24px 24px;
}
'''
        }
    }
}


def list_components():
    """Return all available components with titles."""
    return [{"id": k, "title": v["title"], "files": list(v["files"].keys())} for k, v in TEMPLATES.items()]


def add_component(name, dest_dir=None, root=None):
    """Add component files into destination directory."""
    name = (name or "").lower().strip()
    if name not in TEMPLATES:
        available = ", ".join(sorted(TEMPLATES.keys()))
        return {"ok": False, "error": f"Unknown component '{name}'. Available: {available}"}

    root = os.path.abspath(root or ".")
    dest = os.path.abspath(dest_dir or os.path.join(root, "components", name))
    os.makedirs(dest, exist_ok=True)

    written = []
    comp = TEMPLATES[name]
    for filename, content in comp["files"].items():
        filepath = os.path.join(dest, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        written.append(os.path.relpath(filepath, root))

    return {
        "ok": True,
        "component": name,
        "title": comp["title"],
        "destination": dest,
        "files": written,
        "message": f"Component '{name}' scaffolded successfully ({len(written)} files written)."
    }
