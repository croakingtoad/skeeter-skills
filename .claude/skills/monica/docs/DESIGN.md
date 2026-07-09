# Design: `monica` skill — drive a Monica CRM v4 instance from Claude

*2026-07-09 — phase 1*

## Goal

A shareable Claude Code skill (skills.sh-ready, lives in `croakingtoad/skeeter-skills` at `.claude/skills/monica/`) that lets any Claude session read and write a Monica v4 CRM through its REST API: contacts and their fields, relationships, notes, tags, reminders, and tasks — reliably, without each session re-deriving curl commands or re-discovering API quirks.

**Non-goals (phase 1):** activities, calls, conversations, gifts, debts, journal, life events, documents/photos, pets, companies (phase 2 — same pattern, add later); no MCP server; no support for Monica v5/"Chandler" (different API).

## Compatibility

Targets the **Monica v4 REST API** (Laravel Passport bearer auth) — any self-hosted v4.x instance or app.monicahq.com. Verified against v4.1.2+local-patches.

## Layout

```
.claude/skills/monica/
├── SKILL.md            # frontmatter (name: monica, trigger-rich description), tool table,
│                       #   workflows, safety policy, setup instructions
├── .env.example        # setup template (real creds go in ~/.config/monica-api/.env;
│                       #   repo .gitignore blocks .env and **/.env as a safety net)
├── scripts/monica      # single executable Python 3 CLI — stdlib only, no pip deps
├── scripts/selftest.sh # live lifecycle smoke test (creates + removes "ZZZ Selftest" contact)
├── references/api.md   # endpoint payloads, quirk details, error-code table
└── docs/DESIGN.md      # this document
```

Local development: this repo directory is symlinked to `~/.claude/skills/monica` so the skill is live on this machine while remaining git-tracked. Publish = commit/push here; consumers install via skills.sh.

## Configuration (nothing personal in the repo)

Resolution order:
1. Env vars `MONICA_API_URL`, `MONICA_API_TOKEN`
2. `~/.config/monica-api/.env` (KEY=VALUE lines; recommended, chmod 600)

Optional: `MONICA_API_CA_BUNDLE=/path/to/ca.pem` for self-signed instances (verification stays on; there is deliberately no verification-off switch). SKILL.md documents setup: create a Personal Access Token in Monica → Settings → API, save both values to the env file. The CLI exits with a clear setup message when unconfigured.

## CLI surface (phase 1)

One command, `<resource> <action>` style. Output: compact JSON on stdout (agent-parseable). Errors: message + Monica numeric error code on stderr, non-zero exit.

```
monica whoami                                     # user + me_contact id
monica contacts search "<q>" | list [--tag T] [--page N|--all]
monica contacts get <id> | create --json '{...}' | update <id> --json '{...}'
monica contacts delete <id>      # archiving is NOT exposed by the v4 API (web-only);
                                 # SKILL.md says so and directs archive requests to the web UI
monica fields add <contact> --type <email|phone|...> --value <v> | remove <field-id>
monica addresses add <contact> --json '{...}' | update <addr-id> --json | remove <addr-id>
monica rel link <contact> --type <type> --to <contact> | unlink <rel-id> | types
monica notes add <contact> "<text>" | list <contact> | delete <note-id>
monica tags set <contact> t1,t2 | unset <contact> t1 | list
monica reminders add <contact> --title T --date YYYY-MM-DD [--frequency one_time|week|month|year] | list | delete <id>
monica tasks add <contact> --title T | done <task-id> | list <contact>
monica ref genders | fieldtypes | reltypes        # lookup tables needed for valid writes
```

## Quirks absorbed by the CLI (never re-learned by sessions)

- **Full-payload PUT**: `PUT /contacts/{id}` wipes omitted fields → `contacts update` does GET-merge-PUT automatically.
- **Birthdate composite**: `is_birthdate_known` + `birthdate_day/month/year` (+ age variant) — `update`/`create` accept a simple `birthdate: YYYY-MM-DD` and expand it.
- **Field-type/relationship-type IDs** required for writes → `ref` subcommands fetch and cache them (per-instance cache file under `~/.cache/monica-skill/`).
- **Pagination**: `meta.last_page` traversal behind `--all`.
- **Rate limit**: 429 (Monica error 34) surfaced as "rate limited, retry after a minute", non-zero exit.
- **Plain integer IDs**: the API uses real ids, not the web UI's hashed route ids — SKILL.md warns not to paste ids from URLs.

## Safety policy (SKILL.md instructions to Claude)

- Destructive actions (`contacts delete`, `notes delete`, `tags delete`, `rel unlink`, etc.): show what will be deleted (name/content) and get the user's confirmation before executing. Archiving is not API-exposed in v4, so there is no gentler alternative to offer — direct archive requests to the web UI.
- Never print the token; never write it anywhere but the env file.

## Error handling

Non-2xx → stderr line: `HTTP <status> [monica error <code>]: <message>`, exit 1. Validation errors (422) include field messages verbatim. Unconfigured → setup instructions, exit 2.

## Testing

`scripts/selftest.sh` runs the full lifecycle against the configured instance: whoami → create two "ZZZ Selftest" contacts → update → email field → address → relationship between the two throwaways → note → tag → reminder → task → unlink → untag → delete both, then an unstepped cleanup that removes the selftest tag object. Prints PASS/FAIL per step (PASS=15 expected), leaves no residue. Run at build time and by any adopter to validate their setup.

## Phase 2 (recorded, not built)

activities, calls, conversations/messages, gifts, debts, journal entries (date-capable as of #7280), life events, documents/photos, pets, companies/occupations, audit logs.
