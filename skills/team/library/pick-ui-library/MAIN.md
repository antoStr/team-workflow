---
name: pick-ui-library
description: Intelligent UI component & library selection engine inspired by Emil Kowalski. Audits package.json, prevents hand-rolling complex primitives, and selects battle-tested frontend packages.
metadata:
  origin: emilkowalski/skills
---

# Pick UI Library (Design Engineering Selection Matrix)

Opinionated, battle-tested decision engine for selecting frontend UI libraries, primitives, and animations.
Created to stop AI agents and developers from hand-rolling complex UI components from scratch (like custom toasts, drag-and-drop engines, or accessible dropdowns with raw `<div>` tags) or installing unmaintained npm packages.

## Core Rules

1. **Check `package.json` first**:
   Always inspect existing project dependencies before recommending or installing a new library. If the project already uses Radix, Base UI, Tailwind, or Framer Motion, build upon that ecosystem.
2. **Never hand-roll accessible primitives**:
   Do NOT implement custom dropdowns, dialogs, popovers, tooltips, or command palettes with basic `<div>` tags and manual `onClick` handlers. Hand-rolled implementations invariably break keyboard navigation, focus trapping, screen readers, and mobile viewport positioning.
3. **One definitive recommendation**:
   Do not overwhelm the user with 5 alternative packages. Recommend the single best library suited for the project with clear rationale.
4. **Know when NOT to use a library**:
   - Simple hover/active transitions -> CSS transitions (`transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1)`).
   - Simple disclosures -> Native `<details>` and `<summary>` if unstyled is acceptable.
   - Simple native modal -> Native `<dialog>` only for basic alert prompts without complex animations.

## The Curated Selection Matrix

| Category | Recommended Library | Command / Import | Rationale |
|---|---|---|---|
| **Toasts / Notifications** | **Sonner** | `npm i sonner` | Expandable stacked cards, swipe to dismiss, rich colors, promise toasts, built-in action buttons. Zero friction. |
| **Unstyled Primitives** | **Base UI** or **Radix UI** | `@base-ui-components/react` or `@radix-ui/react-*` | Full WAI-ARIA compliance, keyboard navigation, focus management, unstyled HTML output, slot `asChild` composition. |
| **Component System** | **shadcn/ui** | `npx shadcn@latest add <component>` | Copy-paste ownership, Tailwind CSS integration, customizable themes, accessible primitives underneath. |
| **Command Menu (⌘K)** | **cmdk** | `npm i cmdk` | Fast, unstyled, composable command palette by Paco Coursey. Built-in fuzzy filtering and keyboard navigation. |
| **Drawers / Bottom Sheets** | **Vaul** | `npm i vaul` | Mobile-first & desktop gesture drawer with physics-based spring dragging, snap points, nested drawers, and iOS background scale. |
| **Animated Numbers** | **NumberFlow** | `npm i @number-flow/react` | Continuous smooth number & counter transitions, Intl currency/percentage formatting, layout-shift prevention. |
| **Drag and Drop** | **dnd kit** | `npm i @dnd-kit/core @dnd-kit/sortable` | Lightweight, modular, accessible drag-and-drop toolkit with touch sensors and virtualized list support. |
| **Virtualization** | **react-virtuoso** | `npm i react-virtuoso` | High-performance dynamic list and table virtualization with zero manual item height configuration. |
| **Motion / Physics** | **motion** (Framer Motion) | `npm i motion` | Production spring physics, layout animations, exit animations (`AnimatePresence`), gesture tracking. |
| **Form Validation** | **React Hook Form + Zod** | `npm i react-hook-form zod @hookform/resolvers` | Uncontrolled performant form state with strict TypeScript schema validation. |
| **Styling & Variants** | **Tailwind + CVA + clsx** | `npm i tailwind-merge clsx class-variance-authority` | Type-safe component variant matrices with reliable Tailwind class collision resolution (`cn()`). |
| **Visual Effects / Hero** | **Magic UI** / **Aceternity UI** | `npx shadcn@latest add <registry-url>` | Production-grade bento grids, animated beams, particle backgrounds, 3D card tilt, sparkles. |
| **Component Registry** | **21st.dev** | `npx shadcn@latest add https://21st.dev/r/<item>` | "The npm for Design Engineers", community-verified shadcn-compatible component blocks. |

## Workflow Decision Tree

```
Task: Implement UI Feature
 ├─ Is it an interactive primitive (Dialog, Menu, Tooltip)?
 │   ├─ Yes ──> Does project use shadcn?
 │   │           ├─ Yes ──> `npx shadcn@latest add <component>`
 │   │           └─ No ───> Use `@base-ui-components/react` or `@radix-ui/react-*`
 ├─ Is it a Toast / Alert feed? ──────────────> Use `sonner`
 ├─ Is it a Command Palette (⌘K)? ────────────> Use `cmdk`
 ├─ Is it a Drawer / Bottom Sheet? ──────────> Use `vaul`
 ├─ Is it a Counter / Metric change? ────────> Use `number-flow`
 ├─ Is it an aesthetic hero / animation? ─────> Use `magic-ui` or `aceternity-ui`
 └─ Is it a simple button/card hover? ────────> Use native CSS transition / Tailwind classes
```
