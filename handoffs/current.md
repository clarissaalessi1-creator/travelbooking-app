# Current Handoff

## What currently exists

The repository contains a Vue/Vite search and booking interface backed by FastAPI and SQLite. The backend creates the SQLite schema at startup and seeds it once from the four instructor CSV files. Vue fetches users, search results, and booking history from FastAPI; it creates bookings, cancels them while retaining their rows, and deletes only application-created test bookings. The six instructor bookings are protected, and SQLite never reuses an issued booking ID.

Assignment 2 Part 1 adds a separate, read-only nearby-hotel map. `GET /api/nearby-hotels` accepts exactly five U.S. ZIP digits, keeps leading zeros, verifies a matching U.S. Geoapify postcode, and returns no more than 20 `accommodation.hotel` provider results within 5 km. It never writes Geoapify data to SQLite or attaches provider hotels to bookings/stays. Vue renders these provider results in a keyboard-operable list and Leaflet map using one `selectedPlaceId`; OpenStreetMap attribution remains visible. `GEOAPIFY_API_KEY` is read only from the ignored backend environment file and is never returned to Vue.

## What has been checked

All four CSV files were inspected and validated. Automated checks confirmed 8 hotels, 12 trips, 6 users, and 6 bookings after initial setup and after a real FastAPI restart; SQLite foreign-key validation passed. Browser tests selected `U006`, created and cancelled `B007`, deleted it, then created `B008` to confirm the persistent ID state did not reuse `B007`. Both test bookings were deleted and remained absent after restarting both services; `B001`–`B006` remained intact. The test-delete UI is hidden for seeded bookings, and the backend rejects deletion of `B001` with `403`. Browser tests also passed for both the successful and no-results Part 1 searches.

For Assignment 2, eight focused backend tests passed for success, leading-zero handling, invalid ZIP, unresolved ZIP, empty provider response, missing provider name, simulated provider failure, simulated rate limit, and simulated authentication failure. These are mocked upstream cases. Manual live verification on September 30, 2026 confirmed that `02108` returned HTTP 200 with `outcome: success`, verified the exact requested U.S. ZIP, used the returned center for a 5 km hotel search, and displayed 20 results. The list/marker synchronization, Leaflet/OpenStreetMap attribution, non-exhaustive notice, provider-missing-name text, and custom invalid-ZIP state were also verified. `backend/.env` remained ignored and untracked; no secret was printed or committed.

## What is incomplete

The student still needs to inspect the changed files in VS Code and take any screenshots required by the assignment. The local `GEOAPIFY_API_KEY` has been configured and live-provider verification is complete. Authentication, payments, and Assignment 2 Part 2 shortlist functionality are not implemented.

## Next concrete task

Perform final student review of the changed files and submission evidence. Do not commit until the student approves the reviewed changes.
