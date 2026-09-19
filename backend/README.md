# FastAPI backend

This backend preserves `GET /api/search?hotel_name=<name>` and now serves its search data from SQLite.

On the first startup, `database.py` creates the schema in `schema.sql` and seeds `data/hotels.csv`, `data/trips.csv`, `data/users.csv`, and `data/bookings.csv`. A `seed_metadata` record prevents later startups from reloading or resetting the starter records. The generated `data/travel_booking.db` is ignored by Git.

The implemented JSON API routes are:

- `GET /api/search?hotel_name=<name>`
- `GET /api/users`
- `POST /api/bookings`
- `GET /api/bookings`
- `PATCH /api/bookings/{booking_id}/cancel`
- `DELETE /api/bookings/{booking_id}`

`booking_id_state` stores the last issued booking number. SQLite advances it inside the create transaction, so a deleted ID is never reused after a refresh or restart. The six instructor bookings (`B001`–`B006`) are protected from the test-delete route; the API returns `403` if deletion is attempted. The Vue interface shows Delete (test) only for application-created bookings. `requirements.txt` lists the FastAPI and Uvicorn dependencies.
