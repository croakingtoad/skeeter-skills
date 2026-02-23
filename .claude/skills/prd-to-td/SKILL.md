---
name: prd-to-td
description: Analyzes PRDs, concept briefs, or feature specs and creates structured td issues with epics, features, tasks, priorities, and dependencies. Bridges product requirements to the td CLI task management system for AI agent workflows.
---

# PRD to td — Requirements Decomposition for td Task Management

Transform product requirements documents into a fully populated `td` backlog with epics, features, tasks, priorities, and dependency tracking.

## When to Use This Skill

Use when:
- You have a PRD, concept brief, feature spec, RFC, or architecture doc
- You need to populate `td` with structured work items
- You're starting a new project or major feature and need a task breakdown
- You want to convert informal requirements into actionable tracked work

## Process Overview

```
PRD/Brief/Spec
     │
     ▼
┌─────────────┐
│  1. PARSE   │  Extract vision, features, constraints, dependencies
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 2. CLASSIFY │  Assign priorities (P0-P3), identify scope boundaries
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 3. DECOMPOSE│  Epic → Feature → Task hierarchy (tasks ≤ 8 hours)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 4. MAP DEPS │  Identify blockers, critical path, execution order
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 5. CREATE   │  td create for each issue, log dependencies
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ 6. PLAN     │  Write plan file with dependency graph + critical path
└─────────────┘
```

## Outputs

| Output | Location | Purpose |
|--------|----------|---------|
| td issues | `.todos/` (via `td create`) | Trackable work items |
| Plan file | `~/.claude/plans/<repo>-plan.md` | Dependency graph, critical path, architecture notes |
| Summary | stdout | Counts, critical path, recommended first actions |

## Quick Start

### Input: Give the skill a document

Any of these work:
- A file path: `Analyze /path/to/prd.md and create td issues`
- Pasted text: `Here's our PRD: [content]`
- A description: `We're building X with these features...`

### The skill then:

1. Reads and analyzes the document
2. Asks clarifying questions if critical gaps exist (max 3-5 questions)
3. Creates the full td backlog
4. Writes the plan file
5. Reports what was created and recommends where to start

---

## Step 1: Parse the Document

Extract these elements from any input format:

| Element | What to Find | Required? |
|---------|-------------|-----------|
| **Vision** | Why build this? Problem solved? | Yes |
| **Users** | Who uses it? Personas? | Yes |
| **Features** | What does it do? | Yes |
| **Scope** | What's included/excluded? | Recommended |
| **Tech stack** | Languages, frameworks, infrastructure | If specified |
| **Constraints** | Timeline, budget, team size | If specified |
| **Dependencies** | External systems, APIs, teams | If specified |
| **Success metrics** | How measured? | If specified |

### Document Types Handled

| Type | Approach |
|------|----------|
| **Formal PRD** | Direct extraction — sections map cleanly |
| **Concept brief** | Infer details, flag assumptions, ask questions |
| **Feature spec** | Technical → functional mapping, reverse-engineer user needs |
| **Architecture doc** | Extract components as epics, interfaces as features |
| **Informal description** | Structure it, propose scope, validate with user |

### Gap Detection

Flag missing information rather than assuming:

```
GAPS IDENTIFIED:
- No success metrics defined
- Authentication method unspecified (SSO? OAuth? Email/password?)
- Mobile behavior not addressed
- Data retention policy unclear

ASSUMPTIONS MADE (flag for user validation):
- English-only (i18n not mentioned)
- Web-only (mobile not specified)
```

If gaps are critical (can't decompose without answers), ask the user before proceeding. Non-critical gaps get logged as notes in the plan file.

---

## Step 2: Classify and Prioritize

### Priority Levels

| Priority | Meaning | Criteria |
|----------|---------|----------|
| **P0** | Must have | Product doesn't work without it. Launch blocker. |
| **P1** | Should have | Significant user value. Not blocking but important. |
| **P2** | Nice to have | Improves experience, not critical. Future iteration candidate. |
| **P3** | Out of scope | Explicitly excluded or deferred. Don't create td issues. |

### Classification Rules

1. If the PRD says "must have" or "required" → P0
2. If it says "should" or "important" → P1
3. If it says "nice to have" or "future" → P2
4. If it says "out of scope" or "not included" → P3 (skip)
5. When unclear, default to P1 and flag for user validation

---

## Step 3: Decompose into Hierarchy

### td Issue Type Mapping

```
PRD Feature Area  →  td epic    (--type epic)
User Capability   →  td feature (--type feature)
Implementation    →  td task    (--type task)
Bug/Fix           →  td bug     (--type bug)
```

### Hierarchy Rules

| Level | td type | Scope | Duration Target |
|-------|---------|-------|-----------------|
| **Epic** | `epic` | Large feature area | 1-4 weeks |
| **Feature** | `feature` | User-facing capability | 1-5 days |
| **Task** | `task` | Implementable unit | 1-8 hours |

### Naming Conventions

Use these prefixes in td issue titles for scannability:

```
Epics:    "E001: User Authentication"
Features: "User registration with email/password"
Tasks:    "Create users table schema"
```

Epic IDs (E001, E002, ...) go in the title. Features and tasks reference their parent epic in the description.

### Decomposition Process

1. **Identify epics** from major feature areas in the PRD
2. **Break each epic** into user-facing features (INVEST criteria: Independent, Negotiable, Valuable, Estimable, Small, Testable)
3. **Break large features** into tasks if they exceed 5 days
4. **Tag everything** with type and priority

### Size Limits

| If estimated at... | Action |
|--------------------|--------|
| > 4 weeks | Split into multiple epics |
| > 5 days (feature) | Split into smaller features or break into tasks |
| > 8 hours (task) | Split into smaller tasks |

---

## Step 4: Map Dependencies

### Dependency Tracking in td

`td` has flat issues with a `block` command that sets status. It does NOT have built-in dependency relationships. Dependencies are tracked in TWO places:

1. **Issue descriptions**: Each issue's description lists what it blocks and what blocks it
2. **Plan file**: The plan file contains the full dependency graph and critical path

### Dependency Template for Issue Descriptions

```
## Dependencies
- Blocks: [list of issue IDs this enables]
- Blocked by: [list of issue IDs that must complete first]
- Related: [list of related but non-blocking issues]
```

### Critical Path

Identify the longest chain of dependent work — this determines minimum project duration.

```
Example:
  DB Schema (2h) → Data Model (3h) → API Layer (8h) → Integration Tests (4h)
  Total critical path: 17h minimum
```

Record the critical path in the plan file.

---

## Step 5: Create td Issues

### Creation Order

1. Create epics first (they're referenced by features/tasks)
2. Create features in dependency order
3. Create tasks in dependency order
4. Log the mapping of td IDs to plan IDs

### td Commands Used

```bash
# Create an epic
td create "E001: User Authentication" --type epic --priority P0

# Create a feature under an epic
td create "User registration with email/password" --type feature --priority P0

# Create a task
td create "Create users table schema" --type task --priority P0

# Log dependency info (since td doesn't have native dep tracking)
td log "Blocked by: td-XXXX (DB schema). Blocks: td-YYYY (API layer)."
```

### Description Template

Every created issue gets a structured description:

```
[One-line summary of what this delivers]

## Parent Epic
E001: [Epic name]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Dependencies
- Blocks: [issue IDs]
- Blocked by: [issue IDs]

## Technical Notes
[Implementation hints, constraints, key files]

## Estimate
[X hours/days]
```

### Batch Creation

When creating many issues, use a work session:

```bash
td ws start "PRD breakdown: [project name]"
# ... create all issues ...
td ws log "Created N epics, M features, K tasks from PRD"
td ws handoff
```

---

## Step 6: Write Plan File

### Location

```
~/.claude/plans/<repo-name>-plan.md
```

If a plan file already exists, append a new section rather than overwriting.

### Plan File Template

```markdown
# [Project Name] — Implementation Plan

**Source**: [PRD filename or "user description"]
**Created**: [date]
**Epics**: [count]
**Features**: [count]
**Tasks**: [count]
**Estimated effort**: [total hours/days]

## Epic Overview

| ID | Epic | Priority | Features | Est. Days |
|----|------|----------|----------|-----------|
| E001 | [Name] | P0 | [count] | [days] |
| E002 | [Name] | P1 | [count] | [days] |

## Dependency Graph

```
E001: DB Foundation
  └── td-XXXX: Create schema ──→ td-YYYY: Data model ──→ td-ZZZZ: API layer
E002: Authentication
  └── td-AAAA: Auth service (blocked by E001) ──→ td-BBBB: Login UI
```

## Critical Path

[Longest dependency chain with total duration]

## Execution Order

Recommended order for starting work:

1. **Start immediately** (no blockers):
   - td-XXXX: [title]
   - td-YYYY: [title]

2. **After phase 1**:
   - td-ZZZZ: [title] (blocked by td-XXXX)

3. **After phase 2**:
   - td-AAAA: [title] (blocked by td-ZZZZ)

## Open Questions

- [Questions flagged during analysis]

## Assumptions

- [Assumptions made during decomposition]
```

---

## Anti-Patterns

| Anti-Pattern | Problem | What to Do Instead |
|---|---|---|
| Creating 100+ flat tasks | Unmanageable backlog | Group under epics, keep features at 5-day max |
| Everything is P0 | No real prioritization | Force-rank: only 30% should be P0 |
| Vague task titles | "Work on auth" — what specifically? | Specific deliverables: "Create JWT token service" |
| Skipping dependency mapping | Work gets blocked unexpectedly | Always identify what blocks what |
| Assuming instead of asking | Build wrong thing | Flag gaps, ask 3-5 clarifying questions |
| Giant tasks (> 8h) | Can't track progress | Split until each piece is ≤ 8 hours |
| No plan file | Dependencies live only in your head | Always write the plan file |

---

## Worked Example

### Input

> "We need a REST API for a bookstore. Users can browse books, search by title/author/genre, add to cart, and checkout. Admin can manage inventory. We're using Python/FastAPI with PostgreSQL."

### Output

```bash
# Epics
td create "E001: Book Catalog & Search" --type epic --priority P0
td create "E002: Shopping Cart" --type epic --priority P0
td create "E003: Checkout & Orders" --type epic --priority P0
td create "E004: Admin Inventory Management" --type epic --priority P1

# E001 Features
td create "Browse books with pagination" --type feature --priority P0
td create "Search books by title, author, genre" --type feature --priority P0
td create "Book detail view with metadata" --type feature --priority P1

# E001 Tasks (for search feature)
td create "Design books table schema" --type task --priority P0
td create "Implement full-text search with pg_trgm" --type task --priority P0
td create "Create /books/search endpoint with filters" --type task --priority P0

# ... continue for all epics
```

Plan file written to `~/.claude/plans/bookstore-api-plan.md` with dependency graph and critical path.

---

## References

- [references/td-mapping.md](references/td-mapping.md) — Detailed mapping from PRD structures to td issue types
- [references/analysis-guide.md](references/analysis-guide.md) — Document parsing methodology and gap detection
