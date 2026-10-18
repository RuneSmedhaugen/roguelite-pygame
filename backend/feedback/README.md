# Feedback API

This Neon Function accepts `POST` JSON at its function URL:

```json
{"type":"bug_report","message":"The opponent froze after round 3."}
```

Allowed `type` values are `bug_report` and `suggestion`. The function uses the branch's injected `DATABASE_URL`; do not put Neon credentials in the game client. Apply `001_create_submissions.sql` before using the endpoint.

The game is configured with the deployed function URL by default. Set `SMALL_PUNCH_PUPPIES_FEEDBACK_URL` if you need to override it (`TROLLGAME_FEEDBACK_URL` is still accepted for compatibility). The existing Neon project is named `trollgame-feedback` (`aged-boat-10504753`, region `aws-us-east-1`).
