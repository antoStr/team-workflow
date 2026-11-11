---
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
