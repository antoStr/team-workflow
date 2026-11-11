---
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
