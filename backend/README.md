# FastAPI backend

This backend preserves `GET /api/search?hotel_name=<name>` and now serves its search data from SQLite.

On the first startup, `database.py` creates the schema in `schema.sql` and seeds `data/hotels.csv`, `data/trips.csv`, `data/users.csv`, and `data/bookings.csv`. A `seed_metadata` record prevents later startups from reloading or resetting the starter records. The generated `data/travel_booking.db` is ignored by Git.

The implemented JSON API routes are:

- `GET /api/search?hotel_name=<name>`
- `GET /api/health`
- `POST /api/chatbot`
- `GET /api/users`
- `POST /api/bookings`
- `GET /api/bookings`
- `PATCH /api/bookings/{booking_id}/cancel`
- `DELETE /api/bookings/{booking_id}`

`booking_id_state` stores the last issued booking number. SQLite advances it inside the create transaction, so a deleted ID is never reused after a refresh or restart. The six instructor bookings (`B001`–`B006`) are protected from the test-delete route; the API returns `403` if deletion is attempted. The Vue interface shows Delete (test) only for application-created bookings. `requirements.txt` lists the FastAPI and Uvicorn dependencies.

`POST /api/chatbot` is backend-only. It accepts `{"question": "..."}` with
exactly two `YYYY-MM-DD` dates, validates a constrained first-stage OpenRouter
SQL proposal, and queries only `saved_hotels` and `demo_hotel_nights` through a
separate read-only SQLite connection. Checkout is excluded from the billable
nights; every requested night must exist and have positive stored rooms before a
stay matches. The second provider stage receives only the approved retrieved
records and deterministic integer-cent totals. The route returns a structured
body for success, no match, invalid dates, SQL rejection, configuration/model,
and provider errors. Set `OPENROUTER_API_KEY` and `OPENROUTER_MODEL` only in the
ignored `backend/.env`; do not put credentials in frontend source or Git.
