# Document Analysis Guide

How to parse different document types and extract actionable requirements for td issue creation.

## Three-Pass Analysis

### Pass 1: Structure Recognition

Read the full document and identify:

1. **Document type** — PRD, concept brief, architecture doc, RFC, informal description
2. **Section mapping** — Where are features, constraints, users, scope?
3. **Completeness** — What's present vs. missing?

### Pass 2: Information Extraction

Extract into these categories:

```
VISION & GOALS
- Primary problem solved
- Target outcome
- Success metrics (if defined)

USERS & PERSONAS
- Primary user type
- Secondary users
- Usage context (when/where/how)

FEATURES & REQUIREMENTS
- Core features (explicit in doc)
- Supporting features (implied)
- Non-functional requirements (performance, security, scale)

CONSTRAINTS
- Technical (stack, integrations)
- Business (timeline, budget, team)
- Regulatory (compliance, privacy)

DEPENDENCIES
- Internal (other modules, shared services)
- External (third-party APIs, teams)
- Data (required sources, formats)
```

### Pass 3: Gap Analysis

Identify what's missing and categorize:

| Gap Type | Action |
|----------|--------|
| **Critical** — Can't decompose without it | Ask user before proceeding |
| **Important** — Affects scope decisions | Flag as assumption, note in plan |
| **Minor** — Implementation detail | Note in plan, decide during dev |

## Document Type Strategies

### Formal PRD

Well-structured with clear sections. Direct extraction:
- Map "Requirements" → features
- Map "Success Metrics" → acceptance criteria
- Map "Non-Goals" → P3 exclusions
- Map "Technical Constraints" → architecture notes in plan

### Concept Brief / Pitch

High-level, vision-focused. Needs expansion:
- Extract the "what" from vision statements
- Propose specific features for each capability mentioned
- Flag all scope assumptions
- Expect 3-5 clarifying questions

### Architecture Document

Technical, component-focused. Reverse-engineer user value:
- Each component/module → candidate epic
- Each interface/API → candidate feature
- Integration points → dependency edges
- Map technical layers to user-facing capabilities

### RFC / Design Doc

Proposal-focused with alternatives. Extract decisions:
- "Proposed solution" → features and tasks
- "Alternatives considered" → log as decisions in plan
- "Open questions" → flag for user
- "Implementation plan" (if present) → direct task source

### Informal Description / Chat Thread

Scattered, possibly contradictory. Consolidate:
- List every stated requirement
- Identify contradictions — flag for resolution
- Propose a scope boundary
- Get user validation before creating issues

## Feature Extraction Patterns

### Explicit Features

Look for:
- "The system should..." / "Users can..."
- Bulleted feature lists
- User stories (As a... I want... So that...)
- Acceptance criteria sections

### Implicit Features

Infer from:
- "Users will need to log in" → Authentication epic
- "Data is stored in PostgreSQL" → Database schema tasks
- "API for mobile clients" → API layer epic
- "Must handle 10k concurrent users" → Performance/scaling tasks

### Feature Scope Boundaries

For each feature, determine:
1. **Minimum viable version** — What's the simplest thing that works? (P0)
2. **Full version** — What would the complete feature look like? (P1)
3. **Deluxe version** — What's the ideal but non-essential? (P2)

Create P0 issues. Note P1/P2 in the plan file for future iterations.

## Dependency Detection

### Common Dependency Patterns

| Pattern | Example | Dependency |
|---------|---------|------------|
| **Data before logic** | Schema → Model → API | Sequential |
| **Backend before frontend** | API → UI integration | Sequential |
| **Auth before everything** | Auth system → protected features | Fan-out |
| **Shared service** | Logging, config → all modules | Foundation |
| **Integration last** | Unit features → E2E integration | Converging |

### Identifying the Critical Path

1. List all dependency chains
2. Estimate duration for each chain
3. The longest chain = critical path = minimum project duration
4. Mark critical path items as high priority for attention

### Breaking Circular Dependencies

If A needs B and B needs A:
1. **Extract the shared contract** — define the interface first
2. **Stub one side** — implement A with a known interface, then B implements it
3. **Redesign** — circular deps often signal a design problem

## Acceptance Criteria Generation

When the PRD doesn't specify acceptance criteria, generate them:

### For API Features
- Endpoint responds with correct status codes
- Request validation rejects malformed input
- Response matches documented schema
- Error cases return meaningful messages

### For Data Features
- Schema handles all specified data types
- Queries perform within acceptable latency
- Migrations are reversible
- Constraints enforce data integrity

### For UI Features
- User can complete the described workflow
- Edge cases are handled (empty state, error state, loading state)
- Accessibility requirements met
- Works across specified platforms/browsers

### For Infrastructure Features
- Service starts and passes health check
- Configuration is externalized (env vars)
- Logging captures key operations
- Graceful degradation when dependencies are unavailable

## Estimation Heuristics

When the PRD doesn't include estimates:

| Task Type | Typical Range | Notes |
|-----------|---------------|-------|
| DB schema + migrations | 2-4h | Per table |
| CRUD API endpoint | 2-4h | Per resource |
| Complex query/search | 4-8h | Depends on filters |
| Authentication flow | 1-2 days | OAuth adds complexity |
| File parsing/ingestion | 4-8h | Per format |
| LLM prompt engineering | 2-4h | Per prompt + iteration |
| UI component | 2-4h | Simple; 4-8h complex |
| Integration test suite | 4-8h | Per feature area |
| CI/CD pipeline | 4-8h | Initial setup |

### Adjustment Factors

| Factor | Multiply estimate by |
|--------|---------------------|
| New technology to team | 1.5-2x |
| Unclear requirements | 1.3-1.5x |
| Integration with legacy system | 1.3-1.5x |
| High test coverage required | 1.2-1.3x |

## Quality Checklist

Before creating td issues, verify:

- [ ] Every epic has at least 2 features
- [ ] Every feature has acceptance criteria (generated if not in PRD)
- [ ] No feature exceeds 5 days estimated effort
- [ ] No task exceeds 8 hours
- [ ] Dependencies are mapped (even if approximate)
- [ ] Critical path is identified
- [ ] P0 items represent ≤ 30% of total issues
- [ ] Scope exclusions are documented
- [ ] Open questions are flagged (not silently assumed)
