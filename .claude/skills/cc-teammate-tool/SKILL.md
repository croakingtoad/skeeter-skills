---
name: claude-code-agent-teams
description: >
  Guide for orchestrating Claude Code agent teams — multiple parallel Claude Code sessions
  coordinated by a team lead. Use this skill when the user mentions agent teams, teammates,
  parallel agents, multi-agent workflows, spawning agents, coordinating agents, delegate mode,
  plan approval for teammates, TeammateIdle or TaskCompleted hooks, or wants to break a task
  into parallel independent work streams. Also trigger on questions about tmux split-pane mode,
  in-process teammate mode, Shift+Up/Down agent switching, shared task lists, inter-agent
  messaging, or designing tasks for multi-agent decomposition. This is an experimental feature
  requiring CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS to be enabled.
---

# Claude Code Agent Teams

Agent teams coordinate multiple Claude Code sessions. One session acts as the **team lead**,
spawning **teammates** that work independently and communicate through a shared task list and
mailbox messaging system.

> Experimental. Enable with `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`.
> See [Setup and Configuration](./references/setup-and-configuration.md).

## When to Use Agent Teams

Use when parallel exploration adds real value: research across multiple dimensions, independent
modules, debugging competing hypotheses, or cross-layer changes (frontend/backend/tests).
Avoid for sequential tasks, same-file edits, or tasks a single session handles efficiently.

→ See [Use Case Examples](./references/use-case-examples.md) for end-to-end workflows.

|                   | Subagents                             | Agent Teams                              |
| :---------------- | :------------------------------------ | :--------------------------------------- |
| **Communication** | Report to caller only                 | Teammates message each other directly    |
| **Coordination**  | Caller manages all work               | Shared task list with self-coordination  |
| **Cost**          | Lower                                 | Higher (each teammate is a full instance)|

## Starting a Team

Describe the task and team structure in natural language:

```
Create an agent team to review PR #142: one focused on security, one on performance,
one on test coverage. Have them each review and report findings.
```

Claude proposes a team structure and always asks for confirmation first.

## Core Concepts

| Component     | Role                                                                    |
| :------------ | :---------------------------------------------------------------------- |
| **Team lead** | Creates team, spawns teammates, coordinates work                        |
| **Teammates** | Separate Claude Code instances working on assigned tasks                |
| **Task list** | Shared work items teammates claim and complete, with dependency tracking |
| **Mailbox**   | Direct messaging between agents                                         |

**Display modes**: In-process (default, navigate with Shift+Up/Down) or split panes (requires
tmux/iTerm2). Override with `teammateMode` in settings or `--teammate-mode` flag.

Teammates do not inherit the lead's conversation history. Each loads project context (CLAUDE.md,
MCP servers, skills) plus the spawn prompt.

## Lead Controls

**Delegate mode** — Restrict the lead to coordination-only tools so it focuses on orchestration
instead of implementing. Toggle with **Shift+Tab**.

**Plan approval** — Require teammates to plan before implementing. The lead approves or rejects
with feedback autonomously. Influence with criteria: "only approve plans that include test coverage."

**Quality gate hooks**:
- `TeammateIdle` — exit code 2 sends feedback and keeps the teammate working
- `TaskCompleted` — exit code 2 prevents completion and sends feedback

→ See [Setup and Configuration](./references/setup-and-configuration.md) for hook configuration.

## Task Decomposition

**Core principles**: maximize independence (zero cross-teammate dependencies is ideal), minimize
write conflicts (each teammate owns distinct files), prefer read-heavy work, right-size tasks
(5–6 per teammate).

**Anti-patterns**: sequential chains where step 2 depends on step 1, multiple teammates editing
the same file, micro-tasks not worth spawn overhead, prompts that assume shared context.

→ See [Task Decomposition Patterns](./references/task-decomposition-patterns.md) for detailed examples.

## Best Practices

- Give teammates enough context in spawn prompts — they start fresh, not from the lead's history
- Tell the lead to wait for teammates before proceeding if it starts implementing itself
- Start with research and review tasks before attempting parallel implementation
- Pre-approve common operations in permission settings to reduce teammate interruptions
- Monitor and steer — check progress, redirect failing approaches, synthesize findings

## Quick Reference

| Action              | How                                                         |
|---------------------|-------------------------------------------------------------|
| Enable feature      | `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in env/settings   |
| Start a team        | Describe task and structure in natural language             |
| Navigate teammates  | Shift+Up / Shift+Down (in-process) or click pane (split)   |
| Toggle task list    | Ctrl+T                                                      |
| Delegate mode       | Shift+Tab                                                   |
| Specify models      | Include in prompt: `"Use Sonnet for each teammate"`         |

## Reference Documentation

- [Setup and Configuration](./references/setup-and-configuration.md)
- [Architecture and Communication](./references/architecture-and-communication.md)
- [Task Decomposition Patterns](./references/task-decomposition-patterns.md)
- [Use Case Examples](./references/use-case-examples.md)
- [Troubleshooting](./references/troubleshooting.md)

Official documentation: https://code.claude.com/docs/en/agent-teams
