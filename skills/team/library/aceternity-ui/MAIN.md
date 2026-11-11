---
name: aceternity-ui
description: Aceternity UI dynamic animation library by Manu Arora: 3D Cards, Sparkles, Lamp Hero, Tracing Beam, Aurora Background, Floating Dock, and Canvas Reveal.
metadata:
  origin: ui.aceternity.com
---

# Aceternity UI Dynamic Effects

Aceternity UI provides trending, high-polish dynamic animation components built on Framer Motion and Tailwind CSS by Manu Arora.

## 1. Key Component Catalogue

- **Sparkles Core**: Interactive particle canvas background with physics for hero sections.
- **Lamp Effect**: Ambient overhead spotlight hero header.
- **3D Card**: Multi-layered card with depth-projected translation on hover.
- **Tracing Beam**: Scroll-driven glowing neon SVG trace alongside content streams.
- **Aurora Background**: Fluid mesh gradient animated background.
- **Floating Dock**: macOS-style magnification toolbar.
- **Canvas Reveal Effect**: Dot-matrix / shader reveal animations on hover.

## 2. Floating Dock Pattern (macOS magnification)

```tsx
import { FloatingDock } from "@/components/ui/floating-dock"
import { IconHome, IconTerminal, IconSettings, IconBrandGithub } from "@tabler/icons-react"

const links = [
  { title: "Home", icon: <IconHome className="h-full w-full" />, href: "/" },
  { title: "Terminal", icon: <IconTerminal className="h-full w-full" />, href: "/terminal" },
  { title: "Settings", icon: <IconSettings className="h-full w-full" />, href: "/settings" },
  { title: "GitHub", icon: <IconBrandGithub className="h-full w-full" />, href: "https://github.com" },
]

export function NavigationBar() {
  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-50">
      <FloatingDock items={links} />
    </div>
  )
}
```
