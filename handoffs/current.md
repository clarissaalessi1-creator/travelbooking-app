# Current Handoff

## What currently exists

The repository contains a Vue/Vite search and booking interface backed by FastAPI and SQLite. The backend creates the SQLite schema at startup and seeds it once from the four instructor CSV files. Vue fetches users, search results, and booking history from FastAPI; it creates bookings, cancels them while retaining their rows, and deletes only application-created test bookings. The six instructor bookings are protected, and SQLite never reuses an issued booking ID.

Assignment 2 Part 1 adds a nearby-hotel map. `GET /api/nearby-hotels` accepts exactly five U.S. ZIP digits, keeps leading zeros, verifies a matching U.S. Geoapify postcode, and returns no more than 20 `accommodation.hotel` provider results within 5 km. Vue renders these provider results in a keyboard-operable list and Leaflet map using one `selectedPlaceId`; OpenStreetMap attribution remains visible. `GEOAPIFY_API_KEY` is read only from the ignored backend environment file and is never returned to Vue.

For the Assignment 2 Part 2 in-class Add, Retain, and Remove benchmarks, each unsaved live provider result has an Add to Local action. `POST /api/saved-hotels` saves the selected provider result by unique place ID, creates five dependent simulated classroom-night rows for October 10–14, 2026 (`$100.00` and 20 rooms), and never overwrites an existing save or its nights. Saved live results alone show Remove from Local; `DELETE /api/saved-hotels/{provider_place_id}` deletes that saved row and its related nights via `ON DELETE CASCADE`. The frontend immediately clears the saved label and restores Add to Local after a successful removal. These activity records remain separate from Assignment 1 hotels, trips, bookings, and CSV data.

For Benchmark 4, Vue requests `GET /api/saved-hotels?zip_code=<ZIP>` before the Part 1 Geoapify endpoint. The read-only endpoint returns only matching saved hotels and their stored October 10–14 night rates/rooms. If one or more saves exist, the UI labels the collection `Saved locally`, displays each simulated night, and renders the existing synchronized list/map without a Geoapify request. If the local result is empty, Vue calls the unchanged `GET /api/nearby-hotels` endpoint and labels the collection `API results`. A local lookup error remains visible and deliberately prevents fallback. Local-first lookup never overwrites saved hotels, night values, Assignment 1 tables, or CSVs.

## What has been checked

All four CSV files were inspected and validated. Automated checks confirmed 8 hotels, 12 trips, 6 users, and 6 bookings after initial setup and after a real FastAPI restart; SQLite foreign-key validation passed. Browser tests selected `U006`, created and cancelled `B007`, deleted it, then created `B008` to confirm the persistent ID state did not reuse `B007`. Both test bookings were deleted and remained absent after restarting both services; `B001`–`B006` remained intact. The test-delete UI is hidden for seeded bookings, and the backend rejects deletion of `B001` with `403`. Browser tests also passed for both the successful and no-results Part 1 searches.

For Assignment 2, eight focused backend tests passed for success, leading-zero handling, invalid ZIP, unresolved ZIP, empty provider response, missing provider name, simulated provider failure, simulated rate limit, and simulated authentication failure. These are mocked upstream cases. Manual live verification on September 30, 2026 confirmed that `02108` returned HTTP 200 with `outcome: success`, verified the exact requested U.S. ZIP, used the returned center for a 5 km hotel search, and displayed 20 results. The list/marker synchronization, Leaflet/OpenStreetMap attribution, non-exhaustive notice, provider-missing-name text, and custom invalid-ZIP state were also verified. `backend/.env` remained ignored and untracked; no secret was printed or committed.

For Benchmark 3, `test_saved_hotels.py` and `test_nearby_hotels.py` ran together successfully (14 tests). The removal tests use only a temporary database and verify the FastAPI deletion helper removes a target saved hotel, cascades its five demo-night rows, preserves an unrelated saved hotel and nights, and leaves the Assignment 1 table counts unchanged. A missing saved hotel returns a clear `404`; `npm run build` also passed. The currently saved live hotel in the local application database was not modified during this verification.

For Benchmark 4, the combined saved-hotel and nearby-hotel suites passed 17 tests, including saved local retrieval with stored modified values and no Geoapify call, empty-local behavior, and a clear local database error. The Vue production build passed. Browser checks after restarting the verified project services showed `02108` as one local result with five simulated nights and `10001` as 20 `API results`; no browser action changed data.

## What is incomplete

The student still needs to inspect the changed files in VS Code and take any screenshots required by the assignment. The local `GEOAPIFY_API_KEY` has been configured and live-provider verification is complete. Authentication and payments are not implemented.

## Next concrete task

Perform final student review of the changed files and submission evidence. Do not commit until the student approves the reviewed changes.
