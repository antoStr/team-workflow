---
name: beautiful-ui
description: Curated modern aesthetic patterns: glassmorphism, responsive bento grids, gradient borders, glowing inputs, floating cards, and micro-shadows.
metadata:
  origin: beautifului.dev
---

# Beautiful UI Aesthetic Patterns

Curated aesthetic recipes and styling rules for creating modern, professional, high-polish user interfaces that avoid the generic "AI-slop" default look.

## 1. Modern Glassmorphism Card
```tsx
export function GlassCard({ children }: { children: React.ReactNode }) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-xl shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] dark:border-neutral-800/60 dark:bg-neutral-900/40">
      <div className="pointer-events-none absolute -inset-px rounded-2xl opacity-0 transition duration-300 hover:opacity-100 bg-gradient-to-r from-blue-500/20 via-purple-500/20 to-pink-500/20" />
      {children}
    </div>
  )
}
```

## 2. Gradient Border Glow Input
```tsx
export function GlowingInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  return (
    <div className="relative group rounded-lg p-[1px] transition duration-300 bg-gradient-to-r from-neutral-700 to-neutral-800 focus-within:from-blue-500 focus-within:via-indigo-500 focus-within:to-purple-500">
      <input
        {...props}
        className="w-full rounded-[7px] bg-neutral-950 px-4 py-2.5 text-sm text-neutral-100 placeholder:text-neutral-500 outline-none"
      />
    </div>
  )
}
```
