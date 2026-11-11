---
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
