"""FastAPI service for the SQLite-backed hotel and available-stay search."""

from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import get_connection, initialize_database, issue_next_booking_id


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Initialize the database before the API accepts requests."""
    initialize_database()
    yield


app = FastAPI(title="Travel Booking API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)


class BookingCreate(BaseModel):
    """Data required to create a booking from the frontend."""

    user_id: str
    trip_id: str


PROTECTED_SEED_BOOKING_IDS = frozenset({"B001", "B002", "B003", "B004", "B005", "B006"})
BOOKING_HISTORY_QUERY = """
    SELECT
        bookings.booking_id,
        bookings.user_id,
        users.display_name,
        bookings.trip_id,
        trips.trip_name,
        hotels.hotel_name,
        trips.check_in,
        trips.check_out,
        bookings.booked_on,
        bookings.status
    FROM bookings
    JOIN users ON users.user_id = bookings.user_id
    JOIN trips ON trips.trip_id = bookings.trip_id
    JOIN hotels ON hotels.hotel_id = trips.hotel_id
"""


def normalize_identifier(value: str, field_name: str) -> str:
    """Reject blank identifiers before querying SQLite."""
    identifier = value.strip()
    if not identifier:
        raise HTTPException(status_code=422, detail=f"{field_name} is required")
    return identifier


def fetch_booking_history(
    connection: sqlite3.Connection, booking_id: Optional[str] = None
) -> list[dict[str, Any]]:
    """Return booking rows with the traveler, trip, and hotel details needed by the UI."""
    query = BOOKING_HISTORY_QUERY
    parameters: tuple[str, ...] = ()
    if booking_id is not None:
        query += " WHERE bookings.booking_id = ?"
        parameters = (booking_id,)
    query += " ORDER BY bookings.booked_on DESC, bookings.booking_id DESC"
    bookings = []
    for row in connection.execute(query, parameters).fetchall():
        booking = dict(row)
        booking["can_delete"] = booking["booking_id"] not in PROTECTED_SEED_BOOKING_IDS
        bookings.append(booking)
    return bookings


def build_search_results(hotel_name: str) -> list[dict[str, Any]]:
    """Join matching hotels to their trips using SQLite records."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                hotels.hotel_id,
                hotels.hotel_name,
                hotels.city,
                hotels.state,
                hotels.nightly_rate_usd,
                trips.trip_id,
                trips.trip_name,
                trips.check_in,
                trips.check_out
            FROM hotels
            LEFT JOIN trips ON trips.hotel_id = hotels.hotel_id
            WHERE hotels.hotel_name LIKE ? COLLATE NOCASE
            ORDER BY hotels.hotel_id, trips.check_in, trips.trip_id
            """,
            (f"%{hotel_name}%",),
        ).fetchall()

    matching_hotels: list[dict[str, Any]] = []
    hotels_by_id: dict[str, dict[str, Any]] = {}
    for row in rows:
        hotel = hotels_by_id.get(row["hotel_id"])
        if hotel is None:
            hotel = {
                "hotel_id": row["hotel_id"],
                "hotel_name": row["hotel_name"],
                "city": row["city"],
                "state": row["state"],
                "nightly_rate_usd": row["nightly_rate_usd"],
                "available_stays": [],
            }
            hotels_by_id[row["hotel_id"]] = hotel
            matching_hotels.append(hotel)

        if row["trip_id"] is not None:
            hotel["available_stays"].append(
                {
                    "trip_id": row["trip_id"],
                    "trip_name": row["trip_name"],
                    "check_in": row["check_in"],
                    "check_out": row["check_out"],
                }
            )

    return matching_hotels


@app.get("/api/search")
def search_hotels(hotel_name: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Return SQLite hotels matching a name and their available stays."""
    search_term = hotel_name.strip()
    if not search_term:
        return {"search_term": "", "matches": []}

    return {"search_term": search_term, "matches": build_search_results(search_term)}


@app.get("/api/users")
def list_users() -> dict[str, list[dict[str, str]]]:
    """Return the SQLite travelers available for booking."""
    with get_connection() as connection:
        users = [
            dict(row)
            for row in connection.execute(
                "SELECT user_id, display_name FROM users ORDER BY user_id"
            ).fetchall()
        ]
    return {"users": users}


@app.post("/api/bookings", status_code=status.HTTP_201_CREATED)
def create_booking(booking_request: BookingCreate) -> dict[str, Any]:
    """Create a confirmed booking for an existing traveler and trip."""
    user_id = normalize_identifier(booking_request.user_id, "user_id")
    trip_id = normalize_identifier(booking_request.trip_id, "trip_id")

    with get_connection() as connection:
        connection.execute("BEGIN IMMEDIATE")
        if connection.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail=f"User not found: {user_id}")
        if connection.execute("SELECT 1 FROM trips WHERE trip_id = ?", (trip_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail=f"Trip not found: {trip_id}")

        booking_id = issue_next_booking_id(connection)
        connection.execute(
            """
            INSERT INTO bookings (booking_id, user_id, trip_id, booked_on, status)
            VALUES (?, ?, ?, ?, 'confirmed')
            """,
            (booking_id, user_id, trip_id, date.today().isoformat()),
        )
        created_booking = fetch_booking_history(connection, booking_id)[0]

    return created_booking


@app.get("/api/bookings")
def list_booking_history() -> dict[str, list[dict[str, Any]]]:
    """Return persisted booking history with joined traveler, trip, and hotel details."""
    with get_connection() as connection:
        bookings = fetch_booking_history(connection)
    return {"bookings": bookings}


@app.patch("/api/bookings/{booking_id}/cancel")
def cancel_booking(booking_id: str) -> dict[str, Any]:
    """Retain a booking record while changing its status to cancelled."""
    with get_connection() as connection:
        result = connection.execute(
            "UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?", (booking_id,)
        )
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Booking not found: {booking_id}")
        return fetch_booking_history(connection, booking_id)[0]


@app.delete("/api/bookings/{booking_id}")
def delete_booking(booking_id: str) -> dict[str, str]:
    """Delete a booking record, typically used for a temporary test booking."""
    if booking_id in PROTECTED_SEED_BOOKING_IDS:
        raise HTTPException(status_code=403, detail="Instructor-seeded bookings cannot be deleted")

    with get_connection() as connection:
        result = connection.execute("DELETE FROM bookings WHERE booking_id = ?", (booking_id,))
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail=f"Booking not found: {booking_id}")

    return {"message": f"Booking {booking_id} deleted.", "booking_id": booking_id}
