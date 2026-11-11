---
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
