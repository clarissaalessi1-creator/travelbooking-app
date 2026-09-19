# Part 1 search and Part 2 foundation evidence log

| Major instruction/decision | Resulting change | Manual review/check | Decision | Remaining limitation |
| --- | --- | --- | --- | --- |
| Use Vue + FastAPI | Added Vue/Vite frontend files and FastAPI backend files in separate folders. | Vue production build passed; browser tests passed with both local services running. | Keep browser UI and API separated. | Manual VS Code inspection remains the student's responsibility. |
| Use instructor CSV files | SQLite is seeded from `hotels.csv`, `trips.csv`, `users.csv`, and `bookings.csv` with UTF-8 BOM support. | CSV inspection confirmed valid headers, IDs, values, and references. | Do not hard-code result data in Vue. | The CSVs are seed sources, not request-time application data. |
| SQLite schema and initial seed | Added tables for hotels, trips, users, bookings, seed metadata, and booking ID state. | Two initializations and a real backend restart each retained 8 hotels, 12 trips, 6 users, and 6 bookings; `PRAGMA foreign_key_check` returned no issues. | Use existing instructor IDs as primary keys and preserve later database changes. | Runtime database remains intentionally out of Git. |
| Join hotels and stays | Backend joins SQLite trips to hotels by `hotel_id` and returns `available_stays`. | FastAPI and browser checks returned `H001` with `T001` and `T009`; the browser no-results query displayed the expected message. | Preserve the Part 1 search endpoint and response shape. | No authentication, payments, or external APIs. |
| Booking CRUD UI | Added traveler selection, Book buttons, booking history, cancellation, and protected test deletion controls. | Browser flow created and cancelled `B007`, deleted it, then created `B008` rather than reusing `B007`. Both test bookings were deleted, and a service restart confirmed neither returned while the six seeded bookings remained. Delete controls are hidden for seeded bookings, and a direct delete attempt for `B001` returned `403`. | Refresh history from FastAPI after every booking mutation and persist the highest issued ID in SQLite. | No authentication, payments, or external APIs. |
| Successful browser search | Search for `Harbor Lantern Hotel`. | Expected: one hotel, `H001`, with *Boston Harbor Weekend* and *Boston Autumn Weekend*. Observed: **Passed** — `T001` and `T009` appeared with Book buttons. | Preserve Part 1 behavior while adding booking actions. | Must be run with both local services running. |
| No-results browser search | Search for `Moonlight Palace Hotel`. | Expected: `No hotels and available stays found for “Moonlight Palace Hotel”.` Observed: **Passed** — the clear no-results message appeared. | Preserve Part 1 no-results behavior. | Must be run with both local services running. |
| Preserve scope | Added the required local search and booking CRUD workflow. | Confirmed no authentication, payment, or external API integration was added. | Keep the interface simple and local. | Student must review all changed files before submission. |

## Screenshot checklist

After the two manual browser tests, capture:

1. The successful `Harbor Lantern Hotel` search showing the search term, table headings, `H001`, and both available stays.
2. The `Moonlight Palace Hotel` no-results search showing the search term and clear no-results message.
3. Optional but useful: VS Code showing `frontend/src/App.vue`, `backend/main.py`, and the two CSV files in the Explorer.

Store any new submission screenshots only if your assignment requires them; do not overwrite the existing Expedia reference images.

## AI assistance disclosure

AI assisted with planning, documentation, and implementation under student direction. Browser verification is recorded above; the student remains responsible for manual VS Code inspection and submission.
