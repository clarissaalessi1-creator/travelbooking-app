# Local Travel Booking Application — Part 1

This repository contains the Part 1 implementation of a local hotel and available-stay search. It uses the instructor-supplied CSV files, a Vue frontend, and a Python FastAPI backend. It is not a booking or SQLite CRUD application.

## Part 1 behavior

The user enters a hotel name and selects Search. The Vue frontend calls the local FastAPI backend, which reads `data/hotels.csv` and `data/trips.csv`, joins the records using `hotel_id`, and returns matching hotels with their available stays. The frontend displays the results in a plain table with clear labels. If no hotel name matches, it displays a clear no-results message.

## Technology choices

| Technology | Role | Practical reason |
| --- | --- | --- |
| Vue 3 + Vite | Frontend search interface | Provides reactive form, request-state, and table rendering in a small component-based frontend. |
| Python | Backend language | Keeps CSV handling concise and readable for a course project. |
| FastAPI | HTTP API | Provides a lightweight, typed local API for JSON search responses. |
| `fetch()` + JSON | Frontend/backend communication | Uses standard browser HTTP requests and structured responses. |
| CSV files | Part 1 data source | Uses the instructor-supplied hotel and trip data directly, without a database. |

## Current implementation state

Implemented in Part 1:

- A Vue hotel-name search interface with a Search button.
- A FastAPI endpoint: `GET /api/search?hotel_name=<name>`.
- CSV reads for `data/hotels.csv` and `data/trips.csv`.
- A `hotel_id` join that returns each matching hotel with available stays.
- A plain results table and a no-results message.
- Automated FastAPI HTTP checks and a temporary Vue/Vite production build.

Not implemented:

- SQLite or any Part 2 CRUD.
- Booking creation, confirmation, booking history, authentication, payments, or external APIs.
- Manual browser verification; the required manual test results are recorded as pending in the evidence log until completed.

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

Automated verification confirmed that FastAPI returns `H001` with both of its joined stays for a successful search and returns an empty match list for the fake search. A temporary Vue/Vite build also passed. The following browser checks are still required:

1. With both services running, search for `Harbor Lantern Hotel`.
   - Expected: one matching hotel (`H001`) and two stays: *Boston Harbor Weekend* and *Boston Autumn Weekend*.
2. Search for `Moonlight Palace Hotel`.
   - Expected: `No hotels and available stays found for “Moonlight Palace Hotel”.`

Record what you observe in [docs/evidence-log.md](docs/evidence-log.md), then take the screenshots listed there.

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
- `backend/` contains the FastAPI CSV-search service.
- `data/` contains the instructor-supplied CSV sources.
- `docs/` contains the design, verification record, and observable Expedia visual references.
- `handoffs/` records the current implementation state.
- `prompts/` preserves the Part 1 build direction and a future Part 2 prompt.

## Reference and AI disclosure

[Expedia](https://www.expedia.com/) is an observable visual reference only. This project does not copy Expedia code, private information, or its interface exactly. AI assisted with planning, documentation, and implementation under student review; the student remains responsible for verification and submission.
