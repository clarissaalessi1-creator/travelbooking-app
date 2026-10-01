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

## Assignment 2 Part 1 MVC responsibilities (design only)

The ZIP-code hotel-map feature is planned work. It must not change the existing
Assignment 1 hotel search, booking workflow, SQLite records, or instructor CSV
values.

- **Model:** SQLite remains the authoritative source for Assignment 1 hotels,
  trips, users, and bookings. For the map feature, FastAPI will create
  short-lived, validated geocoding/place result objects; it will not write
  Geoapify data into the existing database during Part 1. It will validate a
  U.S. ZIP code, verify the returned U.S. postcode and coordinates, and retain
  only the response fields needed by the view.
- **Controller:** FastAPI will expose a local, read-only endpoint that receives
  the ZIP code, reads `GEOAPIFY_API_KEY` from server configuration, calls the
  Geoapify forward-geocoding endpoint and then the Places endpoint, maps
  upstream errors to safe local responses, and never returns or logs the API
  key. It will use a fixed 5 km radius and the `accommodation.hotel` category.
- **View:** Vue will collect the ZIP code, call the local FastAPI endpoint, and
  render loading, invalid-ZIP, unresolved-ZIP, empty-result, and API-error
  states. It will render the same returned hotel collection as both an
  accessible list and Leaflet markers. A single `selectedPlaceId` state will
  synchronize list selection, marker highlighting, popup/focus behavior, and
  the accompanying text label; color alone must not indicate selection.

Before implementation, consult `docs/assignment2-research.md` and
`docs/assignment2-early-design-mockup.svg`. Keep Geoapify requests on the
backend so the API key does not enter browser source, network requests, or Git.
