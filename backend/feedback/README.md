# Feedback API

This Neon Function accepts player tickets via `POST` JSON at its function URL:

```json
{"type":"bug_report","title":"Opponent froze","message":"The opponent froze after round 3.","severity":"major"}
```

Allowed ticket types are `bug_report` and `feedback`; both require a title and message. Bug reports also require severity (`critical`, `major`, or `minor`). Public `GET /changelog` returns published player-facing notes. Admin `GET /` lists tickets, admin `GET /changelog` includes linked tickets, and admin `POST /changelog` publishes an entry with optional `submissionIds`.

The function uses the branch's injected `DATABASE_URL`; do not put Neon credentials in the game client. For a fresh database, apply `001_create_submissions.sql`. For an existing feedback database, apply `002_ticket_changelog.sql` to preserve and migrate current tickets.

The game is configured with the deployed function URL by default. Set `SMALL_PUNCH_PUPPIES_FEEDBACK_URL` if you need to override it (`TROLLGAME_FEEDBACK_URL` is still accepted for compatibility). The existing Neon project is named `trollgame-feedback` (`aged-boat-10504753`, region `aws-us-east-1`).
