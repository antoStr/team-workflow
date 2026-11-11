---
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
