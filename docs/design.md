# Part 2 Foundation Design: Vue, FastAPI, and SQLite

## 1. Purpose and reference

This Part 1 application is a local hotel and available-stay search. [Expedia](https://www.expedia.com/) and the screenshots in `docs/reference-images/` are observable references for information hierarchy only. The project does not copy Expedia proprietary code, private data, or reproduce its interface exactly.

- [Expedia search reference](reference-images/expedia-search.png) informs the placement of search information and hotel results.
- [Expedia trips reference](reference-images/expedia-trips.png) informs the grouping of stored trip-style information and reservation details.

## 2. Current scope

The implemented scope is a hotel-name search. The user submits a name, sees matching hotels and their available stays in a plain table, or sees a clear no-results message.

Implemented in this milestone: SQLite schema creation, one-time instructor CSV seeding, SQLite-backed search, booking CRUD API routes, and the Vue booking interface. Authentication, payments, and external APIs remain out of scope.

## 3. Architecture and responsibilities

| Layer | Implemented responsibility |
| --- | --- |
| Interface | Vue traveler selector, search input, Book buttons for returned trips, status messages, and booking-history table with Cancel and Delete (test) actions. |
| Logic | FastAPI initializes SQLite at startup, searches joined hotel/trip rows, and creates, reads, cancels, or deletes booking rows. |
| Data | Instructor-supplied hotel, trip, user, and booking CSV files seed SQLite once. No hotel result data is stored in Vue source. |
| Communication | Browser `fetch()` calls FastAPI over local HTTP; FastAPI returns JSON. |

## 4. SQLite data model and seed source

`data/hotels.csv` has `hotel_id`, `hotel_name`, `city`, `state`, and `nightly_rate_usd`.

`data/trips.csv` has `trip_id`, `hotel_id`, `trip_name`, `check_in`, and `check_out`; `trips.hotel_id` references `hotels.hotel_id`.

`data/users.csv` has `user_id` and `display_name`. `data/bookings.csv` has `booking_id`, `user_id`, `trip_id`, `booked_on`, and `status`; bookings reference users and trips.

FastAPI reads the CSV files with UTF-8 BOM handling only during the initial seed. A `seed_metadata` marker prevents reloads on later backend starts. `booking_id_state` keeps the highest issued booking number, so deleted test-booking IDs are not reused. Search requests use the persistent SQLite tables, and a matching response contains a hotel's fields plus an `available_stays` collection formed from joined trip rows.

## 5. Search flow

```mermaid
flowchart TD
  A[User enters hotel name] --> B[Vue sends GET /api/search]
  B --> C[FastAPI queries SQLite hotels and trips]
  C --> D[Join trips to hotels using hotel_id]
  D --> E[Filter hotel names case-insensitively]
  E --> F{Matches found?}
  F -->|Yes| G[Return matching hotels with available stays as JSON]
  G --> H[Vue renders a labeled table]
  F -->|No| I[Return an empty matches array]
  I --> J[Vue displays a no-results message]
```

## 6. API contract

### `GET /api/search?hotel_name=<name>`

- **Input:** a non-empty `hotel_name` query parameter.
- **Output:** JSON with `search_term` and `matches`.
- **Each match:** hotel ID, name, city, state, nightly rate, and joined `available_stays` containing trip ID, name, check-in, and check-out.

### Booking API

- `GET /api/users` returns SQLite users for the traveler selector.
- `POST /api/bookings` accepts an existing `user_id` and `trip_id`, generates a unique `B`-prefixed ID, uses today's date, and defaults status to `confirmed`.
- `GET /api/bookings` returns history joined to user, trip, and hotel details.
- `PATCH /api/bookings/{booking_id}/cancel` changes only the status to `cancelled`.
- `DELETE /api/bookings/{booking_id}` removes an application-created test booking; instructor bookings `B001`–`B006` return `403` and have no Delete control in Vue.

Missing users, trips, or bookings return `404`; blank create identifiers return `422`.

## 7. User-visible states

| State | Expected interface behavior |
| --- | --- |
| Empty input | Prompt the user to enter a hotel name before searching. |
| Matching search | Show the number of matching hotels and a table containing hotel and available-stay details. |
| No results | Show `No hotels and available stays found for “<search term>”.` |
| Booking created | Show the generated booking ID and refresh booking history from FastAPI. |
| Booking cancelled | Keep the booking row and display `cancelled` after refreshing history. |
| Test booking deleted | Remove the row only after the API confirms deletion, then refresh history. |
| Backend unavailable | Show the API error message rather than presenting stale or invented results. |

## 8. Verification plan

The student must manually inspect the changed files in VS Code and perform two browser searches after starting FastAPI and Vue:

| Test | Search term | Expected result | Observed result |
| --- | --- | --- | --- |
| Successful search | `Harbor Lantern Hotel` | `H001` appears with two stays: *Boston Harbor Weekend* and *Boston Autumn Weekend*. | Passed in browser: `T001` and `T009` displayed with Book buttons. |
| No-results search | `Moonlight Palace Hotel` | The clear no-results message appears and no results table is shown. | Passed in browser: the clear no-results message displayed. |

The same expected/observed record is maintained in `docs/evidence-log.md`.

## 9. Current state and next boundary

Implemented: Vue/Vite frontend source, FastAPI search and booking CRUD routes, a SQLite schema, one-time CSV seeding, SQLite `hotel_id` join logic, plain table rendering, traveler selection, booking history, cancellation, and test deletion. Browser tests passed for create, refresh persistence, cancellation, deletion, and restart persistence.

Not yet implemented: authentication, payments, and external APIs.
