# Instructions for Future Coding Agents

## Part 1 goal

Maintain a small local hotel and available-stay search using Vue, Python, FastAPI, and the instructor-supplied CSV files. This is a Part 1 search implementation, not a booking system.

## Architecture

- **Frontend:** Vue 3 + Vite in `frontend/`.
- **Backend:** Python FastAPI in `backend/main.py`.
- **Communication:** Vue uses `fetch()` to call `GET /api/search?hotel_name=<name>` over local HTTP.
- **Data:** `data/hotels.csv` and `data/trips.csv` are the required sources.
- **Join:** the backend joins hotel and trip rows through `hotel_id` before returning JSON.

## Scope rules

- Keep the search interface plain: input, Search button, clear table labels, and a no-results message.
- Do not hard-code hotel or trip results in the Vue source; all search results must come from FastAPI.
- Do not alter instructor CSV values or replace them with invented records.
- Do not add SQLite, CRUD, booking creation, authentication, payment handling, or external APIs until explicitly authorized for Part 2.
- Use the Expedia screenshots only as observable visual references; never copy proprietary code or claim an exact reproduction.

## Responsibilities

- **Vue frontend:** collect the hotel-name query, call FastAPI, display matching hotels and available stays, and show loading, error, and no-results states.
- **FastAPI backend:** read both CSV files, validate required CSV headers, join data with `hotel_id`, filter by hotel name, and return JSON.
- **CSV data:** preserve `hotels.csv` and `trips.csv` as supplied. The backend must handle the UTF-8 BOM using `utf-8-sig`.

## Verification and documentation

- Manually inspect changed files in VS Code.
- Test a successful browser search and a no-results browser search.
- Record the expected and observed result for both tests in `docs/evidence-log.md`.
- Take the required screenshots listed in the evidence log.
- Keep `README.md`, `docs/design.md`, `handoffs/current.md`, `report.md`, and prompts accurate about implemented versus unimplemented work.

## Git expectations

- Inspect the working tree before editing and preserve user changes.
- Do not commit or push unless explicitly asked.
- Keep changes focused and do not use destructive Git commands without authorization.
