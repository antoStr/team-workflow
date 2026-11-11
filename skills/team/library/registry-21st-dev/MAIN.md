---
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
