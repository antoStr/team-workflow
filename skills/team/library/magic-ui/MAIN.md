---
name: magic-ui
description: Visual effects library for design engineers: Bento Grids, Animated Beam, Marquee, Particles, Orbiting Circles, Shimmer Button, Border Beam, and Meteors.
metadata:
  origin: magicui.design
---

# Magic UI Visual Effects & Bento Grid

Magic UI is a curated collection of animated components for design engineers built with React, TypeScript, Tailwind CSS, and Framer Motion / Motion.

## 1. Adding Magic UI Components via shadcn CLI

Magic UI integrates directly with shadcn registry:
```bash
npx shadcn@latest add "https://magicui.design/r/bento-grid"
npx shadcn@latest add "https://magicui.design/r/animated-beam"
npx shadcn@latest add "https://magicui.design/r/marquee"
npx shadcn@latest add "https://magicui.design/r/border-beam"
npx shadcn@latest add "https://magicui.design/r/shimmer-button"
npx shadcn@latest add "https://magicui.design/r/particles"
```

## 2. Bento Grid Layout Pattern

```tsx
import { BentoCard, BentoGrid } from "@/components/magicui/bento-grid"
import { Bell, FileText, Globe, Sparkles } from "lucide-react"

const features = [
  {
    Icon: FileText,
    name: "Automated Reports",
    description: "Generate structured analysis in real time.",
    href: "/reports",
    cta: "View reports",
    className: "col-span-3 lg:col-span-2",
  },
  {
    Icon: Sparkles,
    name: "AI Agents",
    description: "Multi-agent autonomous engineering workflow.",
    href: "/agents",
    cta: "Explore team",
    className: "col-span-3 lg:col-span-1",
  },
  {
    Icon: Globe,
    name: "Global Edge",
    description: "Zero latency deployment on edge networks.",
    href: "/edge",
    cta: "Learn more",
    className: "col-span-3 lg:col-span-1",
  },
  {
    Icon: Bell,
    name: "Smart Alerts",
    description: "Immediate hardware and thermal notifications.",
    href: "/alerts",
    cta: "Configure",
    className: "col-span-3 lg:col-span-2",
  },
]

export function DashboardBento() {
  return (
    <BentoGrid>
      {features.map((feature, idx) => (
        <BentoCard key={idx} {...feature} />
      ))}
    </BentoGrid>
  )
}
```

## 3. Border Beam Neon Perimeter

```tsx
import { BorderBeam } from "@/components/magicui/border-beam"

export function HighlightedCard() {
  return (
    <div className="relative rounded-xl border border-border bg-card p-6 shadow-md overflow-hidden">
      <h3 className="text-lg font-semibold">Pro Plan</h3>
      <p className="mt-2 text-sm text-muted-foreground">Everything you need to ship autonomously.</p>
      <BorderBeam size={250} duration={12} delay={9} colorFrom="#3b82f6" colorTo="#8b5cf6" />
    </div>
  )
}
```
