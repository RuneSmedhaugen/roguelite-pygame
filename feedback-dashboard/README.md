# Small Punch Puppies Feedback Dashboard

A local-only Vite dashboard for reviewing player bug reports and suggestions. It binds to `127.0.0.1` and uses Vite's server-side proxy to add the private admin token; the token is never sent to browser JavaScript.

## Run locally

1. Make sure `feedback-dashboard/.env.local` exists with `FEEDBACK_API_URL` and `FEEDBACK_ADMIN_TOKEN`.
2. From this folder, run `npm install` once.
3. Run `npm run dev` and open the local address printed by Vite (normally `http://127.0.0.1:5173`).

The project owner token is stored in the ignored `.env.local` file. Do not commit it or share it. The feedback API requires that token for reading submissions; the game's submission route remains public.
