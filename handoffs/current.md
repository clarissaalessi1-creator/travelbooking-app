# Current Handoff

## What currently exists

Part 1 now contains a Vue/Vite frontend in `frontend/` and a Python FastAPI backend in `backend/`. The backend reads the instructor-supplied `data/hotels.csv` and `data/trips.csv`, joins records by `hotel_id`, and exposes a hotel-name search endpoint. The frontend requests that endpoint and renders matching hotels with available stays in a plain table or a no-results message.

## What has been checked

The actual CSV headers and contents were inspected. Source files were checked to confirm that the frontend has no hard-coded hotel results and that FastAPI reads both CSV files. Temporary automated checks passed: the FastAPI endpoint returned `H001` joined to `T001`/`T009`, and the Vue/Vite frontend built successfully. Project-local dependency installation and browser verification have not been performed, so the evidence log retains pending observed-result fields for the required manual tests.

## What is incomplete

The student still needs to install dependencies, inspect the changed files in VS Code, run a successful browser search and a no-results browser search, record observed results, and take the required screenshots. SQLite CRUD, bookings, authentication, payments, and external APIs are intentionally not implemented.

## Next concrete task

Run the FastAPI backend and Vue frontend, then complete the two manual tests recorded in `docs/evidence-log.md`. Do not start Part 2 SQLite CRUD without explicit authorization.
