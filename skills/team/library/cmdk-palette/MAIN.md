---
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
