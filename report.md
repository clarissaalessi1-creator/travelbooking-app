# Local Travel Booking Application — Part 2

## Repository and commit

- GitHub repository: [clarissaalessi1-creator/travelbooking-app](https://github.com/clarissaalessi1-creator/travelbooking-app)
- Part 2 implementation commit: [`e630c44fcaafbc0e372c341a74fce3705f667594`](https://github.com/clarissaalessi1-creator/travelbooking-app/commit/e630c44fcaafbc0e372c341a74fce3705f667594) — `Complete Part 2 SQLite CRUD booking workflow`.
- The Part 1 checkpoint remains preserved in history: [`ade03d9539250857b9f30a97a1b169168b5c5f65`](https://github.com/clarissaalessi1-creator/travelbooking-app/commit/ade03d9539250857b9f30a97a1b169168b5c5f65).

## Implementation

Part 2 keeps the Part 1 Vue + FastAPI hotel search and adds SQLite persistence for all application reads and writes. On first startup, the backend creates the SQLite schema and seeds it from the instructor-supplied [hotels.csv](data/hotels.csv), [trips.csv](data/trips.csv), [users.csv](data/users.csv), and [bookings.csv](data/bookings.csv). A seed marker prevents starter data from being reloaded or reset on later restarts.

`GET /api/search` now queries SQLite. The FastAPI backend also provides `GET /api/users`, `POST /api/bookings`, `GET /api/bookings`, `PATCH /api/bookings/{booking_id}/cancel`, and `DELETE /api/bookings/{booking_id}`. New bookings receive persistent sequential IDs; deleting a booking does not allow its ID to be reused. Instructor bookings B001–B006 are protected from deletion, while application-created test bookings can be deleted.

The Vue interface adds a traveler selector, Book controls for search results, booking history, cancellation controls that retain the record, and test-booking deletion controls. The browser reloads history from the backend, so changes survive refreshes and application restarts.

## Verification

| Check | Expected result | Observed result |
| --- | --- | --- |
| Successful hotel search | A matching search returns its hotel and available stays. | `Harbor Lantern` returned H001 with T001 and T009. |
| No-results hotel search | A non-matching search returns no matches and the UI shows its no-results state. | `Moonlight` returned no matches. |
| Create booking | A selected traveler and trip create a confirmed booking. | B007 was created through the Vue interface and shown with status `confirmed`. |
| Read booking history | Created and seeded bookings are visible with joined traveler, hotel, and trip details. | B007 appeared in history; the six seeded bookings were also present. |
| Cancel booking | Cancelling changes status but retains the record. | B007 changed to `cancelled` and remained in history. |
| Delete test booking | An application-created test booking can be removed. | B007 and later B008 were deleted successfully. |
| Persistence after browser refresh | Bookings and cancelled status remain after refresh. | B007 remained visible as `cancelled` after refresh before deletion. |
| Persistence after backend/frontend restart | SQLite changes remain after both services restart. | Deleted B007 and B008 did not return; B001–B006 remained. |
| Permanent booking IDs | A deleted booking ID is not reused. | After deleting B007, the next created booking was B008. |
| Seeded booking protection | B001–B006 remain intact and cannot use the test-delete route. | All six remained; deleting a seeded booking returned HTTP 403. |
| SQLite relationships | All seeded foreign-key references are valid. | `PRAGMA foreign_key_check` returned no issues. |
| Vue production build | `npm run build` completes successfully. | Passed. |
| Git whitespace check | `git diff --check` reports no whitespace errors. | Passed. |

### Screenshots

![Successful hotel search](<docs/part2-screenshots/search 2026-09-16 at 4.03.03 PM.png>)

![Create booking](<docs/part2-screenshots/create-booking 2026-09-16 at 4.22.50 PM.png>)

![Cancel booking](<docs/part2-screenshots/cancel-booking 2026-09-16 at 4.25.18 PM.png>)

![Delete booking](<docs/part2-screenshots/delete-booking 2026-09-16 at 4.25.30 PM.png>)

![No-results search](<docs/part2-screenshots/no-results 2026-09-16 at 4.25.49 PM.png>)

## Project context and next steps

Repository context: [README.md](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/README.md), [AGENTS.md](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/AGENTS.md), [design note](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/docs/design.md), [project plan prompt](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/prompts/01-project-plan.md), [backend build prompt](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/prompts/02-backend-build.md), and [current handoff](https://github.com/clarissaalessi1-creator/travelbooking-app/blob/main/handoffs/current.md).

This assignment implementation intentionally has no authentication, payment processing, or external travel APIs. The confirmation and deletion UI is intentionally simple for the required CRUD workflow.
