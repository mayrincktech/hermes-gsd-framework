# .planning/ Directory Structure

Every GSD-managed app has a `.planning/` directory at the root.

```
.planning/
├── STATE.md                      # Human-readable current state
├── ROADMAP.md                    # Medium-term vision
├── ARCHITECTURE.md               # Locked stack decisions
├── DESIGN-SYSTEM.md              # Visual tokens, components, references
├── WIREFRAMES.md                 # Approved wireframes (mobile-first)
└── features/
    ├── 01-auth-dashboard/        # Deployed feature
    │   ├── RESEARCH.md           # Research findings
    │   ├── PLAN.md               # Task decomposition
    │   ├── UX-REVIEW.md          # UX Score breakdown
    │   ├── TEST-RESULTS.md       # Build/lint/typecheck/test output
    │   ├── VERIFICATION.md       # QA AI report
    │   └── tasks/
    │       ├── 01-001-create-table.md
    │       └── 01-002-api-routes.md
    └── 02-task-system/           # Active feature
        ├── RESEARCH.md
        ├── PLAN.md
        └── tasks/
            ├── 02-001-db-schema.md
            └── 02-002-list-ui.md
```

## Rules

- STATE.md is the human-readable audit trail (Hermes writes, user reads)
- The Kanban board is the **real-time observability layer** (Hermes updates after each gate)
- Feature directories are numbered, never renamed
- Tasks within features follow `{FEATURE_ID}-{TASK_ID}` naming
- Completed features keep their files (history is preserved)
