---
id: "{FEATURE_ID}-{TASK_ID}"
title: "{TASK_TITLE}"
status: pending
assignee: code-ai
model: deepseek-v4-flash
provider: custom:opencode-go
dependencies: []
files: []
estimated_lines: 0
phase: EXECUTE
created_at: "{TIMESTAMP}"
---

## Description

{TASK_DESCRIPTION}

## Acceptance Criteria

- [ ] Implementation complete
- [ ] Follows DESIGN-SYSTEM.md
- [ ] Mobile-first (375px base)
- [ ] Max 5 files touched
- [ ] Max 500 lines changed

## Gate Requirements

- UX Review: min 42/60 (if UI task)
- Files touched: ≤ 5
- Lines changed: ≤ 500
- Dependencies satisfied

## Context

- Architecture: `.planning/ARCHITECTURE.md`
- Design System: `.planning/DESIGN-SYSTEM.md`
- Wireframe: `.planning/features/{FEATURE_ID}/WIREFRAMES.md`
