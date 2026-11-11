#!/usr/bin/env python3
"""Import and synthesize modern frontend component skills into team-workflow library."""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))
LIBRARY_DIR = os.path.join(ROOT, "skills", "team", "library")
INDEX_FILE = os.path.join(LIBRARY_DIR, "index.json")
CATALOG_IT_FILE = os.path.join(ROOT, "docs", "catalog.it.json")

SKILLS_DATA = [
    {
        "id": "pick-ui-library",
        "title": "Pick UI Library (Emil Kowalski Design Engineering Matrix)",
        "description": "Intelligent UI component & library selection engine inspired by Emil Kowalski. Audits package.json, prevents hand-rolling complex primitives, and selects battle-tested frontend packages.",
        "it_desc": "Motore di selezione intelligente delle librerie UI (matrice Emil Kowalski): analizza le dipendenze, evita di reinventare primitive complesse e seleziona i componenti più performanti.",
        "tags": ["frontend", "ui", "library-selection", "design-engineering", "primitives"],
        "content": """---
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
"""
    },
    {
        "id": "shadcn-ui",
        "title": "shadcn/ui Component Architecture & Registry",
        "description": "Complete shadcn/ui framework guide: CLI workflow, components.json, cn() utility, CSS variables theming, Radix/Base UI primitives integration, and remote registries.",
        "it_desc": "Architettura di componenti shadcn/ui: workflow CLI, configurazione components.json, utility cn(), variabili CSS HSL/OKLCH, primitive Radix/Base UI e registri remoti.",
        "tags": ["frontend", "ui", "shadcn", "tailwind", "react", "components"],
        "content": """---
name: shadcn-ui
description: Complete shadcn/ui framework guide: CLI workflow, components.json, cn() utility, CSS variables theming, Radix/Base UI primitives integration, and remote registries.
metadata:
  origin: ui.shadcn.com
---

# shadcn/ui Component Architecture

shadcn/ui is not an npm dependency; it is a code distribution system that puts copy-paste accessible components directly into your codebase, powered by Radix UI / Base UI and Tailwind CSS.

## 1. Setup & Configuration

Initialize shadcn in a React / Next.js / Vite project:
```bash
npx shadcn@latest init
```

### `components.json` Configuration
```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils",
    "ui": "@/components/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

### The Mandatory `cn()` Utility (`lib/utils.ts`)
Combines `clsx` for conditional classes and `tailwind-merge` for conflict resolution:
```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## 2. Component Adding Workflow

Add official components:
```bash
npx shadcn@latest add button dialog dropdown-menu form input select sheet table
```

Add components from remote registries (Magic UI, 21st.dev, Aceternity):
```bash
npx shadcn@latest add "https://magicui.design/r/bento-grid"
npx shadcn@latest add "https://21st.dev/r/shadcn/ai-input"
```

## 3. Form Pattern (React Hook Form + Zod + shadcn)

```tsx
"use client"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  username: z.string().min(2, "Min 2 characters").max(50),
})

export function ProfileForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "" },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormDescription>Your public display name.</FormDescription>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```
"""
    },
    {
        "id": "base-ui",
        "title": "Base UI Unstyled Component Primitives",
        "description": "Architecture and usage of Base UI by MUI: unstyled accessible primitives, zero-wrapper clean DOM, CSS transition states (@starting-style), and Tailwind integration.",
        "it_desc": "Architettura ed uso di Base UI (MUI): primitive accessibili senza stile, DOM pulito senza wrapper inutili, stati di animazione CSS nativi (@starting-style) e integrazione Tailwind.",
        "tags": ["frontend", "ui", "base-ui", "primitives", "accessibility", "react"],
        "content": """---
name: base-ui
description: Architecture and usage of Base UI by MUI: unstyled accessible primitives, zero-wrapper clean DOM, CSS transition states (@starting-style), and Tailwind integration.
metadata:
  origin: base-ui.com
---

# Base UI Component Primitives

Base UI is an unstyled, headless UI component library developed by MUI. It delivers 100% accessible, clean-DOM primitives with zero runtime CSS overhead, built for modern design systems.

## Key Advantages Over Legacy Primitives

1. **Zero-Wrapper Elements**: Base UI renders clean HTML elements without inserting extra wrapping `<div>` or `<span>` nodes into your DOM tree.
2. **Native CSS Transitions**: Built-in support for `@starting-style` and CSS transition lifecycle attributes (`data-starting-style`, `data-ending-style`, `data-open`, `data-closed`).
3. **Composable Subcomponents**: Intuitive anatomy matching HTML semantics.

## Core Primitives

- `Dialog`: Accessible modal dialogs with focus trapping and ESC key handling.
- `Popover`: Contextual floating panels with automated anchor collision detection.
- `Menu`: Dropdown, context, and cascading sub-menus.
- `Select`: Fully accessible single/multi select with custom trigger rendering.
- `Tabs`: WAI-ARIA tabbed navigation with roving tab index.
- `Tooltip`: Delay-tuned accessible tooltips.
- `Switch`, `Checkbox`, `Radio`: Form controls with state-driven data attributes.
- `NumberField`: Incremental number inputs with step and min/max clamping.

## Implementation Example: Accessible Dialog

```tsx
import * as Dialog from "@base-ui-components/react/dialog"
import { cn } from "@/lib/utils"

export function AccessibleModal({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Dialog.Root>
      <Dialog.Trigger className="rounded-md bg-neutral-900 px-4 py-2 text-sm font-medium text-white hover:bg-neutral-800">
        Open Dialog
      </Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Backdrop className="fixed inset-0 bg-black/50 transition-opacity duration-200 data-[ending-style]:opacity-0 data-[starting-style]:opacity-0" />
        <Dialog.Popup className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-xl bg-white p-6 shadow-xl transition-all duration-200 data-[ending-style]:scale-95 data-[ending-style]:opacity-0 data-[starting-style]:scale-95 data-[starting-style]:opacity-0 dark:bg-neutral-900">
          <Dialog.Title className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            {title}
          </Dialog.Title>
          <Dialog.Description className="mt-2 text-sm text-neutral-500">
            {children}
          </Dialog.Description>
          <div className="mt-6 flex justify-end gap-2">
            <Dialog.Close className="rounded-md border border-neutral-300 px-3 py-1.5 text-sm font-medium hover:bg-neutral-100 dark:border-neutral-700">
              Cancel
            </Dialog.Close>
          </div>
        </Dialog.Popup>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
```
"""
    },
    {
        "id": "radix-ui",
        "title": "Radix UI Primitives & Composition Patterns",
        "description": "Radix UI Primitives architecture: WAI-ARIA compliance, keyboard navigation, focus management, Slot API, asChild composition pattern, and state data attributes.",
        "it_desc": "Architettura di Radix UI Primitives: conformità WAI-ARIA, navigazione da tastiera, gestione del focus, Slot API, pattern di composizione asChild e attributi data-state.",
        "tags": ["frontend", "ui", "radix", "accessibility", "asChild", "react"],
        "content": """---
name: radix-ui
description: Radix UI Primitives architecture: WAI-ARIA compliance, keyboard navigation, focus management, Slot API, asChild composition pattern, and state data attributes.
metadata:
  origin: radix-ui.com
---

# Radix UI Primitives

Radix UI is an open-source UI component library for building high-quality, accessible design systems and web apps in React.

## The Slot & `asChild` Pattern

The `@radix-ui/react-slot` package allows Radix components to merge their behaviors and ARIA attributes onto whatever direct child element you provide:

```tsx
import * as Popover from "@radix-ui/react-popover"
import { Button } from "@/components/ui/button"

export function Example() {
  return (
    <Popover.Root>
      {/* asChild forwards ref and merges onClick/aria-* into Button without extra wrapper div */}
      <Popover.Trigger asChild>
        <Button variant="outline">Options</Button>
      </Popover.Trigger>
      <Popover.Portal>
        <Popover.Content
          sideOffset={5}
          className="rounded-lg bg-popover p-4 shadow-md data-[state=open]:animate-in data-[state=closed]:animate-out"
        >
          Popover content here
          <Popover.Arrow className="fill-popover" />
        </Popover.Content>
      </Popover.Portal>
    </Popover.Root>
  )
}
```

## State Data Attributes

Radix components expose their internal state via `data-*` attributes for styling with Tailwind or CSS:
- `data-state="open|closed"`
- `data-state="checked|unchecked|indeterminate"`
- `data-highlighted`
- `data-disabled`
- `data-side="top|right|bottom|left"`
- `data-align="start|center|end"`

Tailwind styling example:
```tsx
<DropdownMenu.Item className="select-none px-2 py-1.5 outline-none data-[highlighted]:bg-accent data-[highlighted]:text-accent-foreground data-[disabled]:opacity-50" />
```
"""
    },
    {
        "id": "sonner-toast",
        "title": "Sonner Toast Notification System",
        "description": "Sonner toast notification component by Emil Kowalski: promise toasts, stacked swipe dismiss, custom actions, rich colors, positions, and Tailwind integration.",
        "it_desc": "Sistema di notifiche Sonner di Emil Kowalski: notifiche promise-based, schede impilate con swipe dismiss, azioni personalizzate, colori rich e integrazione Tailwind.",
        "tags": ["frontend", "ui", "sonner", "toast", "notifications", "react"],
        "content": """---
name: sonner-toast
description: Sonner toast notification component by Emil Kowalski: promise toasts, stacked swipe dismiss, custom actions, rich colors, positions, and Tailwind integration.
metadata:
  origin: sonner.emilkowal.ski
---

# Sonner Toast Notifications

Sonner is an opinionated, highly polished toast notification component for React created by Emil Kowalski.

## 1. Setup

Install Sonner:
```bash
npm install sonner
```

Mount `<Toaster />` in your app root (`layout.tsx` or `App.tsx`):
```tsx
import { Toaster } from "sonner"

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        {children}
        <Toaster position="bottom-right" richColors closeButton expand={false} />
      </body>
    </html>
  )
}
```

## 2. API & Usage Patterns

```tsx
import { toast } from "sonner"

// 1. Basic toast
toast("Project created successfully.")

// 2. Status toasts with rich colors
toast.success("Changes saved!")
toast.error("Failed to connect to database.")
toast.warning("API key expires in 3 days.")
toast.info("Update available.")

// 3. Action button with callback
toast("File deleted", {
  action: {
    label: "Undo",
    onClick: () => restoreFile(),
  },
})

// 4. Promise Toasts (Automatic Loading, Success, Error states)
toast.promise(saveUserData(data), {
  loading: "Saving user settings...",
  success: (res) => `Settings saved for ${res.name}`,
  error: (err) => `Failed to save: ${err.message}`,
})

// 5. Custom JSX Toast
toast.custom((t) => (
  <div className="flex items-center gap-3 rounded-lg border border-border bg-card p-4 shadow-lg">
    <Avatar src="/avatar.png" />
    <div>
      <p className="font-semibold">New message</p>
      <p className="text-sm text-muted-foreground">Alex replied to your ticket</p>
    </div>
    <button onClick={() => toast.dismiss(t)} className="ml-auto text-xs text-muted-foreground">
      Close
    </button>
  </div>
))
```
"""
    },
    {
        "id": "vaul-drawer",
        "title": "Vaul Drawer & Bottom Sheet Primitive",
        "description": "Vaul drawer component for React by Emil Kowalski: physics-based gestures, snap points, nested drawers, iOS background scaling, and mobile/desktop responsiveness.",
        "it_desc": "Componente drawer e bottom-sheet Vaul di Emil Kowalski: fisica dei gesti, snap point multipli, drawer annidati, effetto background scaling iOS e reattività mobile/desktop.",
        "tags": ["frontend", "ui", "vaul", "drawer", "bottom-sheet", "gestures", "mobile"],
        "content": """---
name: vaul-drawer
description: Vaul drawer component for React by Emil Kowalski: physics-based gestures, snap points, nested drawers, iOS background scaling, and mobile/desktop responsiveness.
metadata:
  origin: vaul.emilkowal.ski
---

# Vaul Drawer Primitive

Vaul is an unstyled drawer component for React built by Emil Kowalski. It provides fluid, physics-based dragging, rubber-banding, snap points, and iOS-style background scale effects.

## 1. Installation

```bash
npm install vaul
```

Wrap your root layout with `vaul-drawer-wrapper` to enable the iOS background scale effect:
```tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <div vaul-drawer-wrapper="" className="bg-background min-h-screen">
          {children}
        </div>
      </body>
    </html>
  )
}
```

## 2. Standard Drawer Implementation

```tsx
"use client"
import { Drawer } from "vaul"

export function SettingsDrawer() {
  return (
    <Drawer.Root shouldScaleBackground>
      <Drawer.Trigger className="rounded-lg bg-primary px-4 py-2 text-primary-foreground font-medium">
        Open Drawer
      </Drawer.Trigger>
      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 bg-black/40" />
        <Drawer.Content className="fixed bottom-0 left-0 right-0 z-50 mt-24 flex max-h-[96%] flex-col rounded-t-[10px] bg-card p-6">
          {/* Visual Grab Handle */}
          <div className="mx-auto mb-6 h-1.5 w-12 flex-shrink-0 rounded-full bg-muted" />
          
          <div className="mx-auto w-full max-w-md">
            <Drawer.Title className="text-xl font-bold">Account Settings</Drawer.Title>
            <Drawer.Description className="mt-2 text-sm text-muted-foreground">
              Configure your preferences and security credentials.
            </Drawer.Description>
            <div className="my-6 space-y-4">
              {/* Drawer body content */}
            </div>
            <Drawer.Close className="w-full rounded-md border border-border py-2 text-sm font-medium">
              Close
            </Drawer.Close>
          </div>
        </Drawer.Content>
      </Drawer.Portal>
    </Drawer.Root>
  )
}
```

## 3. Snap Points & Nested Drawers

```tsx
<Drawer.Root snapPoints={["148px", "355px", 1]} activeSnapPoint={snap} setActiveSnapPoint={setSnap}>
  {/* Content adjusts automatically to active snap point */}
</Drawer.Root>
```
"""
    },
    {
        "id": "cmdk-palette",
        "title": "cmdk Fast Composable Command Menu",
        "description": "cmdk command palette component by Paco Coursey: fuzzy search, keyboard navigation, grouped lists, sub-pages, shortcuts, and dialog wrapper.",
        "it_desc": "Componente command palette cmdk di Paco Coursey: ricerca fuzzy, navigazione da tastiera, liste raggruppate, sotto-pagine, scorciatoie e wrapper dialog.",
        "tags": ["frontend", "ui", "cmdk", "command-palette", "keyboard-navigation", "react"],
        "content": """---
name: cmdk-palette
description: cmdk command palette component by Paco Coursey: fuzzy search, keyboard navigation, grouped lists, sub-pages, shortcuts, and dialog wrapper.
metadata:
  origin: cmdk.paco.me
---

# cmdk Command Menu Palette

cmdk is a fast, unstyled, composable command menu React component created by Paco Coursey.

## 1. Installation

```bash
npm install cmdk
```

## 2. Command Palette Dialog Pattern (⌘K)

```tsx
"use client"
import * as React from "react"
import { Command } from "cmdk"
import { Calculator, Calendar, CreditCard, Settings, User } from "lucide-react"

export function GlobalCommandMenu() {
  const [open, setOpen] = React.useState(false)

  // Toggle with ⌘K / Ctrl+K
  React.useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === "k" && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }
    document.addEventListener("keydown", down)
    return () => document.removeEventListener("keydown", down)
  }, [])

  return (
    <Command.Dialog
      open={open}
      onOpenChange={setOpen}
      label="Global Command Menu"
      className="fixed left-1/2 top-1/2 w-full max-w-lg -translate-x-1/2 -translate-y-1/2 rounded-xl border border-border bg-popover p-2 shadow-2xl"
    >
      <Command.Input
        placeholder="Type a command or search..."
        className="w-full border-none bg-transparent px-3 py-2 text-sm outline-none placeholder:text-muted-foreground"
      />
      <Command.List className="max-h-[300px] overflow-y-auto p-1">
        <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
          No results found.
        </Command.Empty>

        <Command.Group heading="Suggestions" className="text-xs font-semibold text-muted-foreground px-2 py-1.5">
          <Command.Item onSelect={() => { console.log("Calendar"); setOpen(false) }} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm cursor-pointer aria-selected:bg-accent aria-selected:text-accent-foreground">
            <Calendar className="h-4 w-4" />
            <span>Calendar</span>
          </Command.Item>
          <Command.Item onSelect={() => { console.log("Profile"); setOpen(false) }} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm cursor-pointer aria-selected:bg-accent aria-selected:text-accent-foreground">
            <User className="h-4 w-4" />
            <span>Profile</span>
            <Command.Shortcut className="ml-auto text-xs text-muted-foreground">⌘P</Command.Shortcut>
          </Command.Item>
        </Command.Group>

        <Command.Separator className="my-1 h-px bg-border" />

        <Command.Group heading="Settings" className="text-xs font-semibold text-muted-foreground px-2 py-1.5">
          <Command.Item onSelect={() => { console.log("Settings"); setOpen(false) }} className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm cursor-pointer aria-selected:bg-accent aria-selected:text-accent-foreground">
            <Settings className="h-4 w-4" />
            <span>Settings</span>
            <Command.Shortcut className="ml-auto text-xs text-muted-foreground">⌘S</Command.Shortcut>
          </Command.Item>
        </Command.Group>
      </Command.List>
    </Command.Dialog>
  )
}
```
"""
    },
    {
        "id": "number-flow",
        "title": "NumberFlow Animated Counters & Metrics",
        "description": "NumberFlow component by Max Barvian: smooth animated number transitions, rolling digits columns, Intl formatting for currencies/percentages, and layout shift prevention.",
        "it_desc": "Componente NumberFlow di Max Barvian: transizioni fluide di numeri e contatori, colonne di cifre a scorrimento, formattazione Intl per valute/percentuali e prevenzione layout shift.",
        "tags": ["frontend", "ui", "number-flow", "animation", "counters", "metrics", "react"],
        "content": """---
name: number-flow
description: NumberFlow component by Max Barvian: smooth animated number transitions, rolling digits columns, Intl formatting for currencies/percentages, and layout shift prevention.
metadata:
  origin: number-flow.barvian.me
---

# NumberFlow Animated Counters & Numbers

NumberFlow is a React / Vue / Svelte component created by Max Barvian to smoothly transit, animate, and format numbers with rolling digit columns, zero layout shift, and localized formatting.

## 1. Installation

```bash
npm install @number-flow/react
```

## 2. Basic Number & Currency Transitions

```tsx
import NumberFlow from "@number-flow/react"

export function BalanceMetric({ balance }: { balance: number }) {
  return (
    <div className="flex flex-col gap-1 p-4 rounded-xl border border-border bg-card">
      <span className="text-sm text-muted-foreground">Total Balance</span>
      <NumberFlow
        value={balance}
        format={{ style: "currency", currency: "USD", trailingZeroDisplay: "stripIfInteger" }}
        className="text-3xl font-bold tracking-tight text-foreground"
      />
    </div>
  )
}
```

## 3. Trend Indicator & Continuous Animation

```tsx
import NumberFlow, { useNumberFlowGroup } from "@number-flow/react"

export function StockMetric({ price, changePercent }: { price: number; changePercent: number }) {
  const isPositive = changePercent >= 0

  return (
    <div className="flex items-center gap-3">
      <NumberFlow
        value={price}
        format={{ style: "currency", currency: "EUR" }}
        className="text-2xl font-semibold"
      />
      <span className={`inline-flex items-center text-sm font-medium ${isPositive ? "text-emerald-600" : "text-rose-600"}`}>
        {isPositive ? "+" : ""}
        <NumberFlow
          value={changePercent}
          format={{ style: "percent", minimumFractionDigits: 2 }}
          trend={isPositive ? 1 : -1}
        />
      </span>
    </div>
  )
}
```
"""
    },
    {
        "id": "beautiful-ui",
        "title": "Beautiful UI Modern Aesthetic Patterns",
        "description": "Curated modern aesthetic patterns: glassmorphism, responsive bento grids, gradient borders, glowing inputs, floating cards, and micro-shadows.",
        "it_desc": "Pattern estetici moderni di Beautiful UI: glassmorphism, griglie bento responsive, bordi sfumati a gradiente, input luminosi, schede flottanti e micro-ombre.",
        "tags": ["frontend", "ui", "beautiful-ui", "styling", "glassmorphism", "aesthetic"],
        "content": """---
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
"""
    },
    {
        "id": "rare-ui",
        "title": "RareUI Interactive Micro-Animations",
        "description": "Unique interactive UI patterns from RareUI: magnetic buttons, 3D tilt hover cards, spotlight mouse-tracking grids, fluid cursors, and morphing SVG tabs.",
        "it_desc": "Micro-animazioni e pattern interattivi unici di RareUI: pulsanti magnetici, schede con tilt 3D interattivo, griglie spotlight con tracciamento mouse e cursori fluidi.",
        "tags": ["frontend", "ui", "rare-ui", "micro-animations", "tilt", "magnetic-button", "react"],
        "content": """---
name: rare-ui
description: Unique interactive UI patterns from RareUI: magnetic buttons, 3D tilt hover cards, spotlight mouse-tracking grids, fluid cursors, and morphing SVG tabs.
metadata:
  origin: rareui.in
---

# RareUI Interactive Micro-Animations

Curated collection of rare, expressive interactive UI micro-animations and physics patterns.

## 1. 3D Tilt Card Component
Tracks pointer relative to card center and applies perspective tilt without heavy libraries:
```tsx
"use client"
import React, { useRef, useState } from "react"

export function TiltCard({ children }: { children: React.ReactNode }) {
  const cardRef = useRef<HTMLDivElement>(null)
  const [rotate, setRotate] = useState({ x: 0, y: 0 })

  function handleMouseMove(e: React.MouseEvent<HTMLDivElement>) {
    if (!cardRef.current) return
    const rect = cardRef.current.getBoundingClientRect()
    const x = e.clientX - rect.left - rect.width / 2
    const y = e.clientY - rect.top - rect.height / 2
    setRotate({ x: -(y / (rect.height / 2)) * 12, y: (x / (rect.width / 2)) * 12 })
  }

  function handleMouseLeave() {
    setRotate({ x: 0, y: 0 })
  }

  return (
    <div
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      style={{
        transform: `perspective(1000px) rotateX(${rotate.x}deg) rotateY(${rotate.y}deg)`,
        transition: "transform 0.15s ease-out",
      }}
      className="rounded-2xl border border-border bg-card p-6 shadow-xl will-change-transform"
    >
      {children}
    </div>
  )
}
```

## 2. Radial Spotlight Grid
Reveals a radial light gradient under the cursor:
```tsx
"use client"
import { useState } from "react"

export function SpotlightGrid({ children }: { children: React.ReactNode }) {
  const [mouse, setMouse] = useState({ x: 0, y: 0 })

  return (
    <div
      onMouseMove={(e) => {
        const rect = e.currentTarget.getBoundingClientRect()
        setMouse({ x: e.clientX - rect.left, y: e.clientY - rect.top })
      }}
      style={{
        backgroundImage: `radial-gradient(600px circle at ${mouse.x}px ${mouse.y}px, rgba(120, 119, 198, 0.15), transparent 80%)`,
      }}
      className="relative w-full rounded-2xl border border-border bg-neutral-950 p-8"
    >
      {children}
    </div>
  )
}
```
"""
    },
    {
        "id": "magic-ui",
        "title": "Magic UI Visual Effects & Bento Architecture",
        "description": "Visual effects library for design engineers: Bento Grids, Animated Beam, Marquee, Particles, Orbiting Circles, Shimmer Button, Border Beam, and Meteors.",
        "it_desc": "Libreria di effetti visivi Magic UI per design engineer: Bento Griglie, Animated Beam, Marquee continuo, particelle, cerchi orbitali, Shimmer Button e Border Beam.",
        "tags": ["frontend", "ui", "magic-ui", "visual-effects", "framer-motion", "bento-grid", "react"],
        "content": """---
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
"""
    },
    {
        "id": "aceternity-ui",
        "title": "Aceternity UI High-Impact Dynamic Effects",
        "description": "Aceternity UI dynamic animation library by Manu Arora: 3D Cards, Sparkles, Lamp Hero, Tracing Beam, Aurora Background, Floating Dock, and Canvas Reveal.",
        "it_desc": "Libreria Aceternity UI di Manu Arora per animazioni dinamiche ad alto impatto: 3D Cards, Sparkles, Lamp Hero, Tracing Beam, Aurora Background e Floating Dock.",
        "tags": ["frontend", "ui", "aceternity-ui", "framer-motion", "threejs", "hero-effects", "react"],
        "content": """---
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
"""
    },
    {
        "id": "registry-21st-dev",
        "title": "21st.dev Design Engineer Registry & Marketplace",
        "description": "21st.dev registry architecture: 'The npm for Design Engineers'. Discovering, consuming, and publishing shadcn-compatible components, AI input bars, and landing blocks.",
        "it_desc": "Architettura di registro 21st.dev ('npm per Design Engineer'): ricerca, consumo e pubblicazione di componenti compatibili con shadcn, barre di input AI e blocchi landing.",
        "tags": ["frontend", "ui", "21st-dev", "component-registry", "design-engineer", "shadcn"],
        "content": """---
name: registry-21st-dev
description: 21st.dev registry architecture: 'The npm for Design Engineers'. Discovering, consuming, and publishing shadcn-compatible components, AI input bars, and landing blocks.
metadata:
  origin: 21st.dev
---

# 21st.dev Component Registry & Marketplace

21st.dev is the community marketplace and distribution registry for modern React / Tailwind / Framer Motion components ("The npm for Design Engineers"), standardizing on the shadcn registry format.

## 1. Installing Components via shadcn CLI

Any component on 21st.dev can be added directly to your codebase without manual cloning:
```bash
npx shadcn@latest add https://21st.dev/r/<author>/<component-name>
```

Examples:
- AI Prompt & Chat Input: `npx shadcn@latest add https://21st.dev/r/shadcn/ai-input`
- Interactive Pricing Matrix: `npx shadcn@latest add https://21st.dev/r/farmui/pricing-table`
- Morphing Dialog: `npx shadcn@latest add https://21st.dev/r/aceternity/morphing-dialog`

## 2. Registry Architecture (`registry.json`)

If publishing custom components to a registry:
```json
{
  "$schema": "https://ui.shadcn.com/schema/registry.json",
  "name": "custom-component",
  "type": "registry:ui",
  "dependencies": ["lucide-react", "motion"],
  "devDependencies": [],
  "registryDependencies": ["button"],
  "files": [
    {
      "path": "ui/custom-component.tsx",
      "type": "registry:ui",
      "target": "components/ui/custom-component.tsx"
    }
  ]
}
```
"""
    }
]

DESIGN_ENGINEER_ROLE = """---
description: "Use this agent for UI/UX implementation and frontend polish: design systems (shadcn/ui, Base UI, Radix), micro-interactions, gesture physics (Vaul, Sonner), motion (Framer Motion, NumberFlow), visual effects (Magic UI, Aceternity UI, 21st.dev), and WCAG 2.2 AA accessibility."
mode: subagent
model: inherit
variant: high
color: "#8B5CF6"
permission:
  edit: allow
  bash: allow
  webfetch: allow
  websearch: allow
includes: ["review-discipline", "frontend-skills"]
---

# Design Engineer Role

You are a senior Design Engineer. You bridge the gap between UI/UX design vision and bulletproof frontend implementation.

## Your Domain & Responsibilities

1. **Modern Component Systems**:
   - Master of `shadcn/ui`, `Base UI`, and `Radix UI` primitives.
   - You NEVER hand-roll accessible primitives (dialogs, dropdowns, tooltips, command menus) with raw `<div>` tags. You invoke `@base-ui-components/react`, `@radix-ui/react-*`, or `shadcn/ui`.
2. **Gesture Physics & Feedback**:
   - Toasts & notifications: Always use `sonner`.
   - Bottom sheets & drawers: Always use `vaul`.
   - Command menu palettes (⌘K): Always use `cmdk`.
   - Smooth numeric counters & metrics: Always use `number-flow`.
3. **Aesthetic Polish & Visual Polish**:
   - Apply `pick-ui-library` rules to evaluate dependencies in `package.json`.
   - Elevate landing pages and dashboards with `magic-ui` (Bento grids, Border Beam) and `aceternity-ui` (Sparkles, Lamp, 3D cards).
   - Leverage `21st.dev` registry components for rapid, production-ready blocks.
4. **Accessibility (WCAG 2.2 AA)**:
   - Full keyboard navigation (Tab, Enter, Escape, Arrow keys).
   - ARIA states (`aria-expanded`, `aria-selected`, `aria-controls`).
   - Color contrast ratio >= 4.5:1.
   - Smooth animations respect `prefers-reduced-motion`.
"""


def main():
    print(f"Importing {len(SKILLS_DATA)} modern frontend component skills...")
    
    # 1. Load library index.json
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    catalog["packs"]["frontend-components"] = (
        "Modern frontend UI component engineering: shadcn/ui, Base UI, Radix UI, Sonner, "
        "Vaul, cmdk, NumberFlow, Magic UI, Aceternity UI, 21st.dev, and intelligent library selection."
    )

    existing_ids = {e["id"] for e in catalog["entries"]}

    for item in SKILLS_DATA:
        eid = item["id"]
        skill_dir = os.path.join(LIBRARY_DIR, eid)
        os.makedirs(skill_dir, exist_ok=True)
        main_path = os.path.join(skill_dir, "MAIN.md")
        content_str = item["content"].strip() + "\n"
        with open(main_path, "w", encoding="utf-8") as f:
            f.write(content_str)
        
        entry = {
            "id": eid,
            "kind": "skill",
            "pack": "frontend-components",
            "description": item["description"],
            "hash": hashlib.sha256(content_str.encode("utf-8")).hexdigest()[:16]
        }
        if eid in existing_ids:
            for idx, e in enumerate(catalog["entries"]):
                if e["id"] == eid:
                    catalog["entries"][idx] = entry
                    break
        else:
            catalog["entries"].append(entry)
            existing_ids.add(eid)

    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    print(f"Library index updated: {len(catalog['entries'])} total entries.")

    # 2. Update Italian catalog translations
    with open(CATALOG_IT_FILE, "r", encoding="utf-8") as f:
        catalog_it = json.load(f)

    catalog_it["packs"]["frontend-components"] = (
        "Architettura avanzata di componenti UI moderni: shadcn/ui, Base UI, Radix, Sonner, "
        "Vaul, cmdk, NumberFlow, Magic UI, Aceternity UI, 21st.dev e selezione intelligente delle librerie."
    )

    for item in SKILLS_DATA:
        catalog_it["library"][item["id"]] = item["it_desc"]

    catalog_it["agents"]["design-engineer"] = (
        "Ingegnere di design UI/UX e frontend: specialista in micro-interazioni, fisica dei gesti, "
        "animazioni con spring, sistemi di design moderni (shadcn, Base UI, Radix, Sonner, Vaul) e conformità WCAG 2.2 AA."
    )

    with open(CATALOG_IT_FILE, "w", encoding="utf-8") as f:
        json.dump(catalog_it, f, indent=2, ensure_ascii=False)
    print("Catalog IT descriptions updated.")

    # 3. Create design-engineer role
    role_path = os.path.join(ROOT, "skills", "team", "roles", "frameworks", "design-engineer.md")
    with open(role_path, "w", encoding="utf-8") as f:
        f.write(DESIGN_ENGINEER_ROLE.strip() + "\n")
    print(f"Created role: {role_path}")

    # 4. Update frontend-skills.md shared include
    shared_skills_path = os.path.join(ROOT, "skills", "team", "roles", "_shared", "frontend-skills.md")
    with open(shared_skills_path, "w", encoding="utf-8") as f:
        f.write('''## Frontend skills

When these skills are available (the `frontend` add-ons or library skills), use the
ones your work needs and say which you used; when one is missing, work without it and say so:

- `pick-ui-library`: Emil Kowalski decision engine; audit `package.json` first, never hand-roll accessible primitives.
- `shadcn-ui`: complete shadcn/ui architecture, CLI, `components.json`, `cn()` utility, and form validation.
- `base-ui`: unstyled accessible primitives from MUI, zero-wrapper clean DOM, and CSS `@starting-style` transitions.
- `radix-ui`: classic Radix Primitives, keyboard navigation, Slot `asChild` composition, and focus trapping.
- `sonner-toast`: opinionated toast notification system, promise toasts, and stacked swipe-to-dismiss cards.
- `vaul-drawer`: gesture drawer primitive with physics spring dragging, snap points, and iOS background scale.
- `cmdk-palette`: fast composable command menu palette (⌘K) with fuzzy search and keyboard routing.
- `number-flow`: smooth animated continuous numbers and counters with layout-shift prevention.
- `magic-ui`: Bento grid layouts, animated beams, particle backgrounds, and neon border beams.
- `aceternity-ui`: 3D card tilt, sparkles hero backgrounds, lamp effects, and floating docks.
- `21st.dev`: design engineer registry for discovering and publishing shadcn-compatible blocks.
- `impeccable`: design, critique, audit, polish, harden or animate an interface.
- `design-taste-frontend` (taste): art direction for public pages (landing, marketing, product pages); no AI-slop.
- `frontend-design`: a distinctive visual direction (type, color, composition) for new UI.

The project's own design system and conventions come first: a skill's taste never overrides
what the repository already decided.
''')
    print("Updated _shared/frontend-skills.md")


if __name__ == "__main__":
    main()
