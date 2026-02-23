# td Mapping Reference

How PRD structures map to `td` CLI commands and issue types.

## Type Mapping

| PRD Concept | td `--type` | When to Use |
|-------------|-------------|-------------|
| Feature area / module | `epic` | Groups of related work (1-4 weeks) |
| User-facing capability | `feature` | Deliverable user value (1-5 days) |
| Implementation unit | `task` | Concrete coding work (1-8 hours) |
| Known defect | `bug` | Fix for broken behavior |
| Research / investigation | `task` | Spike or exploration (timebox it) |

## Priority Mapping

| PRD Language | td `--priority` | Notes |
|---|---|---|
| "Must have", "required", "launch blocker", "MVP" | `P0` | ~30% of issues |
| "Should have", "important", "high value" | `P1` | ~40% of issues |
| "Nice to have", "future", "enhancement" | `P2` | ~25% of issues |
| "Out of scope", "not included", "deferred" | Skip | Don't create td issues for P3 |

## td create Examples

### Epic

```bash
td create "E001: Knowledge Graph Pipeline" \
  --type epic \
  --priority P0
```

Then log the scope:

```bash
td log "Scope: entity extraction, relationship mapping, passage linking. Excludes: graph visualization (P2)."
```

### Feature

```bash
td create "Entity extraction from ingested chunks" \
  --type feature \
  --priority P0
```

Description should reference parent epic and include acceptance criteria:

```bash
td log "Parent: E001. Acceptance: extracts people, places, works, concepts from chunk text. Stores in Neo4j with typed edges."
```

### Task

```bash
td create "Implement NER prompt template for entity extraction" \
  --type task \
  --priority P0
```

### Logging Dependencies

Since `td block` only sets status (not relationships), log dependencies explicitly:

```bash
# On the blocked issue
td log "BLOCKED BY: td-a1b2 (DB schema must exist first)"

# On the blocking issue
td log "BLOCKS: td-c3d4 (API layer needs this schema)"
```

## Work Session for Batch Creation

When creating many issues from a PRD:

```bash
# Start a work session
td ws start "PRD decomposition: Project Name"

# Create all issues
td create "E001: ..." --type epic --priority P0
td create "E002: ..." --type epic --priority P1
# ... features and tasks ...

# Log summary
td ws log "Created 5 epics, 18 features, 12 tasks from architecture doc"

# End session with handoff
td ws handoff
```

## Handling Existing td Backlogs

If td already has issues:

1. Run `td list` first to see existing work
2. Check for overlap — don't duplicate existing issues
3. Reference existing issue IDs in new dependency chains
4. Use `td log` on existing issues to add new context from the PRD

## ID Convention

Use sequential epic IDs in titles for easy reference:

```
E001, E002, E003...
```

These are human-readable labels in the title, not td's internal IDs (`td-XXXX`). The plan file maps between them:

```markdown
| Epic ID | td Issue | Title |
|---------|----------|-------|
| E001 | td-a1b2 | Knowledge Graph Pipeline |
| E002 | td-c3d4 | Voice Profile System |
```

## Size Guidelines

### When to Create Separate Issues vs. Log Notes

| Situation | Action |
|-----------|--------|
| Work item > 1 hour | Create a td issue |
| Sub-step < 1 hour | Log it as a note on the parent issue |
| Configuration change | Log note unless it's complex |
| Documentation | Create issue only if substantial |

### Target Counts

| Project Size | Epics | Features | Tasks |
|---|---|---|---|
| Small (1-2 weeks) | 2-4 | 5-15 | 0-10 |
| Medium (1-2 months) | 5-10 | 15-40 | 10-30 |
| Large (3+ months) | 10-20 | 40-80 | 30-60 |

More than 80 total issues signals over-decomposition. Keep it actionable.
