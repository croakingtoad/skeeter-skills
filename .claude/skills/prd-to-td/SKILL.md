---
name: prd-to-td
description: >
  Use when you have a PRD, concept brief, feature spec, RFC, or architecture doc and need to
  populate `td` with structured work items. Also triggers on: "break this PRD into tasks",
  "create td issues from this spec", "analyze this brief and make a backlog", "decompose this
  feature into td issues", "I need a task breakdown for this", or any request to convert
  requirements into tracked work.
---

# PRD to td — Requirements Decomposition

Transform product requirements documents into a fully populated `td` backlog with epics,
features, tasks, priorities, and dependency tracking.

## Process Overview

```
PRD/Brief/Spec
     ↓
1. PARSE     →  Extract vision, features, constraints, dependencies. Flag gaps, don't assume.
2. CLASSIFY  →  Assign P0–P3 priorities. Force-rank: only ~30% should be P0.
3. DECOMPOSE →  Epic (1–4 wk) → Feature (1–5 d) → Task (≤ 8 h). Split anything that exceeds.
4. MAP DEPS  →  Identify blockers, critical path, execution order.
5. CREATE    →  td create for each issue; log dependency info in descriptions.
6. PLAN      →  Write plan file to ~/.claude/plans/<repo>-plan.md.
```

→ See `references/analysis-guide.md` for parsing methodology, gap detection, priority rules,
decomposition criteria, anti-patterns, and a worked example.
→ See `references/td-mapping.md` for td command templates, description template, and plan file template.

## Quick Start

Give the skill any of:
- A file path: `Analyze /path/to/prd.md and create td issues`
- Pasted text: `Here's our PRD: [content]`
- A description: `We're building X with these features...`

The skill reads the document, asks up to 3–5 clarifying questions if critical gaps exist,
creates the full td backlog, writes the plan file, and reports what was created with
recommended first actions.

## td Issue Hierarchy

| PRD Concept   | td type   | Duration Target |
|---------------|-----------|-----------------|
| Feature area  | `epic`    | 1–4 weeks       |
| User capability | `feature` | 1–5 days       |
| Implementation unit | `task` | 1–8 hours    |

Naming: `td create "E001: User Authentication" --type epic --priority P0`

## Outputs

| Output     | Location                              |
|------------|---------------------------------------|
| td issues  | `.todos/` (via `td create`)           |
| Plan file  | `~/.claude/plans/<repo>-plan.md`      |
| Summary    | stdout — counts, critical path, recommended first actions |

## References

- [references/analysis-guide.md](references/analysis-guide.md) — Parsing, gap detection, priority rules, decomposition, anti-patterns, worked example
- [references/td-mapping.md](references/td-mapping.md) — td command templates, description template, plan file template
