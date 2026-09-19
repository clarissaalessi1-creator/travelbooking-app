# Local Travel Booking Application — Part 2 SQLite CRUD

This repository preserves the Part 1 hotel and available-stay search and adds the Part 2 SQLite-backed booking workflow. Vue and FastAPI remain the frontend and backend. On the first backend start, FastAPI seeds SQLite from the four instructor-supplied CSV files; after that, application reads and writes use SQLite.

## Part 1 behavior

The user enters a hotel name and selects Search. The Vue frontend calls the local FastAPI backend, which joins SQLite hotel and trip records using `hotel_id` and returns matching hotels with their available stays. The frontend displays the results in a plain table with clear labels. If no hotel name matches, it displays a clear no-results message.

## Technology choices

| Technology | Role | Practical reason |
| --- | --- | --- |
| Vue 3 + Vite | Frontend search interface | Provides reactive form, request-state, and table rendering in a small component-based frontend. |
| Python | Backend language | Keeps CSV handling concise and readable for a course project. |
| FastAPI | HTTP API | Provides a lightweight, typed local API for JSON search responses. |
| `fetch()` + JSON | Frontend/backend communication | Uses standard browser HTTP requests and structured responses. |
| CSV files | One-time seed source | Preserves the instructor-supplied hotel, trip, user, and booking data. |
| SQLite | Persistent application data | Keeps search data and future booking changes after backend restarts. |

## Current implementation state

Implemented:

- A Vue hotel-name search interface with a Search button.
- A FastAPI endpoint: `GET /api/search?hotel_name=<name>`.
- SQLite tables for hotels, trips, users, and bookings with foreign keys.
- One-time, idempotent CSV seeding for all four instructor data files.
- A SQLite `hotel_id` join that returns each matching hotel with available stays.
- A traveler dropdown populated from SQLite through FastAPI.
- Book buttons for every returned trip and a success/error status message.
- Booking-history table with cancellation and test-deletion controls.
- Persistent booking IDs that are not reused after a test booking is deleted; instructor bookings `B001`–`B006` are protected from deletion.
- A plain results table, clear no-results message, and browser-verified persistence across refreshes and service restarts.

Not implemented:

- Authentication, payments, or external APIs.

## Booking API

The Vue interface calls these routes:

- `GET /api/users` — demo travelers from SQLite.
- `POST /api/bookings` — create a confirmed booking from `user_id` and `trip_id`.
- `GET /api/bookings` — booking history with traveler, trip, and hotel details.
- `PATCH /api/bookings/{booking_id}/cancel` — retain a booking and mark it `cancelled`.
- `DELETE /api/bookings/{booking_id}` — remove a temporary test booking.

## Run locally

### Backend

From the repository root:

```sh
python3 -m venv backend/.venv
source backend/.venv/bin/activate
pip install -r backend/requirements.txt
uvicorn main:app --app-dir backend --reload
```

The FastAPI service runs at `http://127.0.0.1:8000`.

### Frontend

In a second terminal:

```sh
cd frontend
npm install
npm run dev
```

Open the localhost URL printed by Vite, normally `http://localhost:5173`.

## Manual verification

The Vue production build passed. Browser verification confirmed the full booking lifecycle: selected a traveler, created `B007`, refreshed to confirm it persisted, cancelled it, refreshed to confirm the cancelled status persisted, deleted it, refreshed to confirm it remained deleted, then restarted both services and confirmed it did not return. The six seeded bookings remained intact.

The original Part 1 browser checks also passed:

1. With both services running, search for `Harbor Lantern Hotel`.
   - Expected: one matching hotel (`H001`) and two stays: *Boston Harbor Weekend* and *Boston Autumn Weekend*.
2. Search for `Moonlight Palace Hotel`.
   - Expected: `No hotels and available stays found for “Moonlight Palace Hotel”.`

The observed results are recorded in [docs/evidence-log.md](docs/evidence-log.md).

## Repository structure

```text
AGENTS.md
README.md
report.md
frontend/
    index.html
    package.json
    vite.config.js
    src/
        App.vue
        main.js
        style.css
backend/
    main.py
    requirements.txt
data/
    hotels.csv
    trips.csv
    users.csv
    bookings.csv
docs/
    design.md
    evidence-log.md
    reference-images/
        expedia-search.png
        expedia-trips.png
handoffs/
    current.md
prompts/
    01-project-plan.md
    02-backend-build.md
```

- `frontend/` contains the Vue/Vite search UI.
- `backend/` contains the FastAPI service, SQLite initialization code, and schema.
- `data/` contains the instructor-supplied CSV seed sources. The generated `travel_booking.db` is intentionally ignored by Git.
- `docs/` contains the design, verification record, and observable Expedia visual references.
- `handoffs/` records the current implementation state.
- `prompts/` preserves the Part 1 build direction and a future Part 2 prompt.

## Reference and AI disclosure

[Expedia](https://www.expedia.com/) is an observable visual reference only. This project does not copy Expedia code, private information, or its interface exactly. AI assisted with planning, documentation, and implementation under student review; the student remains responsible for verification and submission.
