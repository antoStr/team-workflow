---
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
