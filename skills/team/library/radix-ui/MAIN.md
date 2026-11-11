---
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
