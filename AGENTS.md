# Instructions for Future Coding Agents

## Project goal

Build a small local hotel-booking application in Part 2. It is inspired by Expedia at a high level, but must use only synthetic data and must never rely on private Expedia information.

## Scope rules

- Support only hotel browsing, booking, confirmation, booking history, and booking details.
- Do not add real payments, authentication, real booking/travel APIs, or real personal/travel data.
- Keep the application local and appropriate for a small course project.
- Do not represent planned behavior as implemented behavior.

## Architecture

- Frontend: static HTML, CSS, and browser JavaScript in `frontend/`.
- Backend: Python Flask service in `backend/`.
- Communication: JSON over HTTP with browser `fetch()`.
- Persistence: `data/bookings.json` is the durable local booking store.
- Planned endpoints: `GET /api/hotels`, `POST /api/bookings`, `GET /api/bookings`, and `GET /api/bookings/<id>`.

## Responsibilities

- **Frontend:** render synthetic hotels, collect booking data, call the API, show confirmations/history/details, and make API failures understandable.
- **Backend:** provide synthetic hotels; validate booking requests; calculate totals; generate IDs and simulated confirmation numbers; save, list, and retrieve bookings.
- **Persistence:** preserve the JSON-array format, handle a new empty file safely, and keep stored booking records aligned with the documented data model.

## Review requirements

- Check validation failures, empty history, unknown booking IDs, unavailable-backend behavior, and successful paths.
- Verify saved bookings remain after browser and backend restarts.
- Review the JSON content for valid structure after creating bookings.
- Update documentation and the handoff note to distinguish implemented, checked, and unimplemented work truthfully.

## Git expectations

- Inspect the working tree before editing; preserve unrelated user changes.
- Make focused, reviewable changes and do not commit unless explicitly asked.
- Do not use destructive Git commands without explicit authorization.

## Constraints

- Use synthetic identities and travel data only.
- No real payments, authentication, booking APIs, or private Expedia information.
- Do not claim that code, endpoints, tests, or browser behavior exist unless they actually do and have been checked.
