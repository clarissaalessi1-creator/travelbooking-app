# Part 2 Backend Build Prompt

Implement the Flask backend for this local synthetic hotel-booking project, following `docs/design.md` and `AGENTS.md`.

Create `backend/app.py` and `backend/requirements.txt`. Implement:

- `GET /api/hotels` to return a small synthetic hotel list.
- `POST /api/bookings` to validate traveler first/last name, email, check-in, check-out, and hotel ID; require check-out after check-in; calculate total price from nightly price and nights; generate a booking ID and simulated confirmation number; persist a complete booking to `data/bookings.json`; and return the saved booking as JSON.
- `GET /api/bookings` to return saved bookings.
- `GET /api/bookings/<id>` to return one booking or a clear not-found response.

Use JSON request/response bodies and local JSON-file persistence. Handle a missing or empty storage file safely. Use only synthetic data. Do not add payments, authentication, or real external booking APIs. Add proportionate verification and update the README, evidence log, and handoff to describe only behavior that was actually implemented and checked.
