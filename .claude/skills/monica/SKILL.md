---
name: monica
description: >
  Use when the user wants to read or update their Monica CRM: add/edit/find contacts,
  record emails/phones/addresses, link family or friend relationships, jot notes about
  people, tag contacts, set reminders or tasks. Triggers on: "add X to monica",
  "what do I know about X", "X's birthday is...", "remind me to call X", "X is Y's wife",
  "note that X mentioned...", or any personal-CRM request. Requires a Monica v4 instance
  (self-hosted or app.monicahq.com) and a Personal Access Token.
---

# Monica CRM

Drive a Monica CRM v4 instance from the CLI at `scripts/monica` — a single stdlib-only
Python 3 script. Every command prints compact JSON on stdout; errors go to stderr with
a Monica error code and a non-zero exit.

## Setup

1. Get a Personal Access Token: in Monica, go to **Settings → API → Create Personal Access
   Token**.
2. Copy `.env.example` to `~/.config/monica-api/.env` (chmod 600) and fill in
   `MONICA_API_URL` (e.g. `https://your-instance.example.com/api`) and `MONICA_API_TOKEN`.
   Env vars `MONICA_API_URL`/`MONICA_API_TOKEN` override the file if set. Self-signed
   instances can point `MONICA_API_CA_BUNDLE` at a CA file — TLS verification is always on.
3. Verify: `scripts/monica whoami` — should print your user + `me_contact` object.
4. Full validation: `scripts/selftest.sh` — runs a live create/read/update/delete cycle
   against the configured instance (creates and fully removes "ZZZ Selftest" contacts and
   a scratch tag; **this touches the live instance**, not a sandbox). Expect
   `PASS=15 FAIL=0` and `tag cleanup: ok`.

Never print the token in chat; it lives only in the env file.

## Tool table

Every command is `monica <resource> <action> [args]`.

| Command | Purpose |
|---|---|
| `whoami` | Current user + `me_contact` (id needed for "me/my" relationships) |
| `ref genders\|fieldtypes\|reltypes [--refresh]` | Cached lookup tables (ids for gender, contact-field types, relationship types) |
| `contacts search <query> [--limit N]` | Search contacts by name (default limit 25) |
| `contacts list [--tag T] [--page N] [--all]` | List contacts, optionally by tag; `--all` follows pagination |
| `contacts get <id>` | Fetch one contact |
| `contacts create --json '{...}'` | Create a contact |
| `contacts update <id> --json '{...}'` | Update a contact (GET-merge-PUT, see Workflows) |
| `contacts delete <id>` | Permanently delete a contact — **confirm first** (see Safety) |
| `fields add <contact> --type <t> --value <v>` | Add a contact field (email, phone, etc.) |
| `fields list <contact>` | List a contact's fields |
| `fields remove <field_id>` | Remove a contact field |
| `addresses add <contact> --json '{...}'` | Add an address |
| `addresses list <contact>` | List a contact's addresses |
| `addresses update <address_id> --json '{...}'` | Update an address (GET-merge-PUT) |
| `addresses remove <address_id>` | Remove an address |
| `rel types` | List relationship types (cached) |
| `rel list <contact>` | List a contact's relationships |
| `rel link <contact> --type <T> --to <other>` | Create a relationship — direction matters, see Workflows |
| `rel unlink <rel_id>` | Remove a relationship — **confirm first** (see Safety) |
| `notes add <contact> "<text>"` | Add a note |
| `notes list <contact>` | List a contact's notes |
| `notes delete <note_id>` | Delete a note — **confirm first** (see Safety) |
| `tags list` | List all tags |
| `tags set <contact> <t1,t2,...>` | Attach one or more tags (comma-separated, creates if new) |
| `tags unset <contact> <tag>` | Detach a tag from a contact (tag itself may remain, see Workflows) |
| `tags delete <tag_id>` | Permanently delete a tag object — **confirm first** (see Safety) |
| `reminders add <contact> --title T --date YYYY-MM-DD [--frequency one_time\|week\|month\|year]` | Add a reminder (default frequency `one_time`) |
| `reminders list <contact>` | List a contact's reminders |
| `reminders delete <reminder_id>` | Delete a reminder |
| `tasks add <contact> --title T` | Add a task |
| `tasks done <task_id>` | Mark a task completed |
| `tasks list <contact>` | List a contact's tasks |
| `tasks delete <task_id>` | Delete a task |

## Workflows

**Resolve people before acting.** Never guess a contact id. Use `contacts search "<name>"`
first, and if results are ambiguous, ask the user which one. IDs are plain API integers —
never the hashed ids visible in the Monica web UI's URLs; don't paste those in.

**"Me/my" relationships.** Run `whoami` and read `me_contact.id` from the output — that's
"me" for any relationship the user describes from their own perspective.

**Relationship direction — the #1 confusion risk.** `rel link A --type T --to B` means
*"A is the T of B"* — read it left-to-right as a sentence, not as "A relates to B via T".

Worked example — user says "my wife is contact 5":
```
monica whoami                                          # → me_contact.id = 2
monica rel types                                       # confirm the exact type name, e.g. "significant other"
monica rel link 5 --type "significant other" --to 2    # "contact 5 is contact 2's significant other"
```
If you get the direction backwards you'll create "contact 2 is contact 5's significant
other" instead — same relationship type, but stored against the wrong contact if the
type isn't symmetric. When unsure which contact is "A" and which is "B", say the sentence
out loud with the type name substituted and check it matches what the user described.

**Updating contacts.** `contacts update <id> --json '{...}'` does the full GET-merge-PUT
cycle automatically: it fetches the current contact, merges your partial JSON on top,
preserves fields you didn't mention (including gender — the API resource exposes only a
gender *name*, so the CLI resolves it back to `gender_id` for you), and sends the full
payload the API requires. You only ever pass the fields you want to change. To
intentionally clear a contact's gender, pass `"gender_id": null` explicitly in `--json` —
that's the one case where an explicit key overrides the preserved value.

**Birthdates.** Both `create` and `update` accept the shorthand `"birthdate": "YYYY-MM-DD"`
in `--json`; the CLI expands it into Monica's composite `birthdate_day/month/year` +
`is_birthdate_known` fields for you. Don't build the composite fields by hand.

**Reference data caching.** `ref genders|fieldtypes|reltypes` results are cached per-instance
under `~/.cache/monica-skill/`. If the user (or an admin) adds/changes types on the server
side — a new relationship type, a new contact field type — pass `--refresh` once to bust
the cache: `monica ref reltypes --refresh`.

## Safety

Before any of `contacts delete`, `notes delete`, `tags delete`, `rel unlink`: fetch and
show the user what will be deleted (contact name, note content, tag name, or the two
contacts and relationship type involved) and get explicit confirmation before running the
command. These are permanent — there is no undo endpoint.

**Archiving is not exposed by the Monica v4 API.** If the user asks to "archive" a
contact rather than delete them, say so plainly and direct them to do it from the Monica
web UI — do not substitute `contacts delete` for an archive request.

## Limits

- **Rate limit**: Monica's default is 60 requests/minute. A `429` response is surfaced by
  the CLI as an `HTTP 429 [monica error 34]: ... (rate limited — wait a minute and retry)`
  message on stderr — back off and retry after about a minute, don't hammer it.
- **Updates are GET-merge-PUT**, handled by the CLI for `contacts update` and
  `addresses update` — never send a partial payload directly to the raw API outside this
  tool, it will wipe omitted fields.
- **IDs are plain API integers.** Never use the hashed ids from Monica web UI URLs.

See `references/api.md` for the full endpoint table, error-code reference, and the
contact-update payload field list.
