# Monica v4 API reference (as consumed by this skill)

This documents exactly what `scripts/monica` calls — endpoints, methods, and payload
fields — plus the numeric error codes Monica returns. All paths are relative to
`MONICA_API_URL` (e.g. `https://your-instance.example.com/api`). Auth: `Authorization:
Bearer <token>` (Laravel Passport personal access token).

## Endpoints

| CLI command | Method | Path | Payload / params |
|---|---|---|---|
| `whoami` | GET | `me` | — |
| `ref genders` | GET | `genders` | paginated, cached |
| `ref fieldtypes` | GET | `contactfieldtypes` | paginated, cached |
| `ref reltypes` | GET | `relationshiptypes` | paginated, cached |
| `contacts search` | GET | `contacts` | `query`, `limit` |
| `contacts list` (no `--tag`) | GET | `contacts` | `page` |
| `contacts list --tag T` | GET | `tags/{tag_id}/contacts` | `page` (tag resolved to id via `tags list`) |
| `contacts list --all` | GET | `contacts` or `tags/{id}/contacts` | pages until `meta.last_page` |
| `contacts get <id>` | GET | `contacts/{id}` | — |
| `contacts create` | POST | `contacts` | full contact payload, see below (birthdate shorthand expanded first) |
| `contacts update <id>` | GET then PUT | `contacts/{id}` | GET current, merge user `--json`, PUT full payload, see below |
| `contacts delete <id>` | DELETE | `contacts/{id}` | — |
| `fields add` | POST | `contactfields` | `{contact_id, contact_field_type_id, data}` (`contact_field_type_id` resolved from `--type` via `ref fieldtypes`) |
| `fields list` | GET | `contacts/{id}/contactfields` | — |
| `fields remove` | DELETE | `contactfields/{field_id}` | — |
| `addresses add` | POST | `addresses` | user `--json` + `{contact_id}` |
| `addresses list` | GET | `contacts/{id}/addresses` | — |
| `addresses update` | GET then PUT | `addresses/{address_id}` | GET current, merge `{contact_id, name, street, city, province, postal_code, country}` with user `--json`, PUT |
| `addresses remove` | DELETE | `addresses/{address_id}` | — |
| `rel types` | GET | `relationshiptypes` | paginated, cached |
| `rel list` | GET | `contacts/{id}/relationships` | — |
| `rel link` | POST | `relationships` | `{contact_is, relationship_type_id, of_contact}` — `contact_is` "is the type of" `of_contact` |
| `rel unlink` | DELETE | `relationships/{rel_id}` | — |
| `notes add` | POST | `notes` | `{contact_id, body}` |
| `notes list` | GET | `contacts/{id}/notes` | — |
| `notes delete` | DELETE | `notes/{note_id}` | — |
| `tags list` | GET | `tags` | paginated |
| `tags set` | POST | `contacts/{id}/setTags` | `{"tags": ["name1", "name2", ...]}` — tag **names**, comma-split from CLI arg |
| `tags unset` | POST | `contacts/{id}/unsetTag` | `{"tags": [tag_id]}` — see quirk below |
| `tags delete` | DELETE | `tags/{tag_id}` | — |
| `reminders add` | POST | `reminders` | `{contact_id, title, initial_date, frequency_type, frequency_number: 1}` |
| `reminders list` | GET | `contacts/{id}/reminders` | — |
| `reminders delete` | DELETE | `reminders/{reminder_id}` | — |
| `tasks add` | POST | `tasks` | `{contact_id, title, completed: 0}` |
| `tasks done` | GET then PUT | `tasks/{task_id}` | GET current, PUT `{contact_id, title, description, completed: 1}` |
| `tasks list` | GET | `contacts/{id}/tasks` | — |
| `tasks delete` | DELETE | `tasks/{task_id}` | — |

### Quirk: `unsetTag` payload shape

Live-verified against a running Monica v4 instance: `POST contacts/{id}/unsetTag` rejects
a bare `{"tag_id": <int>}` body with a 422 (`"The tags field is required."` /
`"The tag id must be an integer."`). The **working** payload is:

```json
{"tags": [<tag_id_int>]}
```

i.e. the same `tags` array key as `setTags`, but containing the numeric tag id (not a
name) as its single element. This is what the CLI sends.

### Contact update — full payload field list

`PUT /contacts/{id}` (Monica's `UpdateContact` request rules) requires the **entire**
contact representation on every call — any field omitted is wiped, not left unchanged.
Fields the CLI's GET-merge-PUT cycle populates:

- `first_name` (required)
- `middle_name`
- `last_name`
- `nickname`
- `gender_id`
- `description`
- `is_birthdate_known` (required) + `birthdate_day` / `birthdate_month` / `birthdate_year`
  + `birthdate_is_age_based` + `birthdate_age`
- `is_deceased` (required) + `is_deceased_date_known` (required) + `deceased_date_day` /
  `deceased_date_month` / `deceased_date_year`

The CLI derives this full set from `GET /contacts/{id}` (which exposes birthdate/deceased
date as nested `information.dates.*` objects, and gender as a **name**, never
`gender_id`), merges the caller's partial `--json` on top, then expands any
`birthdate: "YYYY-MM-DD"` shorthand into the composite fields before sending the PUT. An
explicit `"gender_id": null` in `--json` is respected as an intentional clear, overriding
the gender preserved from the current contact.

## Error codes

Source: `config/api.php` (`error_codes`) in the Monica v4 codebase — this is the
authoritative list; it differs from commonly-cited older docs, so treat this table as
current:

| Code | Meaning |
|---|---|
| 30 | The limit parameter is too big |
| 31 | The resource has not been found |
| 32 | Error while trying to save the data |
| 33 | Too many parameters |
| 34 | Too many attempts, please slow down the request (rate limited — the CLI appends a retry hint on HTTP 429) |
| 35 | This email address is already taken |
| 36 | You can't set a partner or a child to a partial contact |
| 37 | Problems parsing JSON |
| 38 | Date should be in the future |
| 39 | The sorting criteria is invalid |
| 40 | Invalid query |
| 41 | Invalid parameters |
| 42 | Not authorized |

The CLI surfaces these as `HTTP <status> [monica error <code>]: <message>` on stderr,
plus field-level detail for 422 validation responses.
