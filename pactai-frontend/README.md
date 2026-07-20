# PactAI Frontend

React + Vite + Tailwind v4 + react-router-dom. Design language: "ledger & seal" — dark ink hero
on the landing page, warm paper app surfaces, brass accents only on money/status/action, serif
(Fraunces) for authority + mono (IBM Plex Mono) for numbers.

## Run it

```bash
npm install
npm run dev
```

Vite proxies `/api/*` to `http://localhost:8000` — see `vite.config.js`. Change the port there
if your FastAPI backend runs elsewhere.

## Pages

| Route               | What it is                                                                 |
|----------------------|-----------------------------------------------------------------------------|
| `/`                  | Landing page                                                                 |
| `/login`, `/signup`  | Auth                                                                         |
| `/dashboard`         | Shows "Complete Profile" or "Start Negotiation" depending on local completion state |
| `/complete-profile`  | Profile form (also reused for editing)                                       |
| `/settings`          | Tabs: Profile / Security / Theme                                            |
| `/negotiation`       | Chat with PactAI; profile is preloaded, no repeated rate/skill questions     |
| `/proposals`         | Ledger of saved proposals                                                    |
| `/proposals/:id`     | Single proposal detail                                                       |

## API contract actually implemented (matches your `app/schemas` + routers)

- `POST /api/auth/signup` `{ name, email, password }` → `{ message }` (no token issued)
- `POST /api/auth/login` `{ email, password }` → `{ message, user: { name, email } }`
- `GET  /api/profile` → `FreelancerProfile` (always populated — every field has a schema default)
- `POST /api/profile` → save profile, matches `FreelancerProfile` field names exactly
- `POST /api/chat` `{ session_id, message }` → `ChatResponse { stage, reply, decision, recommended_price, minimum_price, estimated_hours, timeline_days }`

`session_id` is a `crypto.randomUUID()` generated client-side per negotiation visit.

## Known gaps — please close these before the demo

1. **No per-user data isolation on the backend.** `/profile` is one global JSON file
   (`ProfileManager.load()/save()`), and `users.json` has no `user_id` linking a user to their
   own profile/negotiations. Right now, if two people use the app at once, they'd see and
   overwrite each other's profile. This needs backend work — scope profile/session storage by
   the logged-in user's email or an id.
2. **No `/proposals` endpoint exists yet.** I stubbed Proposal History with `localStorage`
   (`src/lib/api.js` → `localProposals`) so the page works today, but it won't persist across
   devices or survive a cache clear. Add a real endpoint + DB table, then swap `localProposals`
   calls in `ProposalHistory.jsx` / `ProposalDetail.jsx` / `Negotiation.jsx` for real API calls.
3. **No auth token.** Login/signup return a plain message, not a JWT, so there's no real session
   security — anyone can call `/profile` or `/chat` directly. Fine for a hackathon demo, but
   flag it if judges ask about security.
4. **`minimum_profit_margin`** is stored as a 0–1 fraction in the schema (e.g. `0.80`). The
   profile form shows/collects it as a percentage (`80`) and converts on submit/load — just
   flagging so nothing looks wrong if you inspect the raw saved JSON.
5. **`stage` and `decision` values are unknown to me** — I don't know what strings your
   `NegotiationWorkflow` actually returns (e.g. `"discovery"`, `"negotiation"`, `"closed"`?), so
   the Negotiation page shows the deal-terms card whenever `recommended_price` is present, rather
   than gating on a specific stage. If you tell me the real stage values, I can make the UI
   smarter (e.g. auto-navigate to Proposal History only once truly closed).
