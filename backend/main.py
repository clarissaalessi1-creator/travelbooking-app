"""FastAPI service for the SQLite-backed hotel and available-stay search."""

from contextlib import asynccontextmanager
from datetime import date
import json
import math
import os
from pathlib import Path
import re
import sqlite3
from typing import Any, Optional, Union
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

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
ZIP_CODE_PATTERN = re.compile(r"^\d{5}$")
GEOAPIFY_GEOCODING_URL = "https://api.geoapify.com/v1/geocode/search"
GEOAPIFY_PLACES_URL = "https://api.geoapify.com/v2/places"
GEOAPIFY_HOTEL_CATEGORY = "accommodation.hotel"
GEOAPIFY_RADIUS_METERS = 5_000
GEOAPIFY_RESULT_LIMIT = 20
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


class GeoapifyRequestError(Exception):
    """Represent an upstream failure without retaining URLs or API credentials."""

    def __init__(self, status_code: Optional[int] = None) -> None:
        self.status_code = status_code
        super().__init__("Geoapify request failed")


def load_backend_environment() -> None:
    """Load the single local Geoapify setting from the ignored backend .env file."""
    environment_file = Path(__file__).with_name(".env")
    if not environment_file.is_file():
        return

    for line in environment_file.read_text(encoding="utf-8").splitlines():
        name, separator, value = line.partition("=")
        if separator and name.strip() == "GEOAPIFY_API_KEY" and not os.getenv(name.strip()):
            os.environ[name.strip()] = value.strip()


load_backend_environment()


def get_geoapify_api_key() -> str:
    """Return the local server-only API key or a safe configuration outcome."""
    api_key = os.getenv("GEOAPIFY_API_KEY", "").strip()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "outcome": "configuration_error",
                "message": "Hotel map search is not configured on this server.",
            },
        )
    return api_key


def geoapify_get(url: str, parameters: dict[str, Union[str, int]]) -> dict[str, Any]:
    """Make one bounded GET request and never surface an upstream response body."""
    request = Request(
        f"{url}?{urlencode(parameters)}",
        headers={"Accept": "application/json"},
        method="GET",
    )
    try:
        with urlopen(request, timeout=10) as response:  # noqa: S310 - trusted Geoapify URLs above
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as error:
        raise GeoapifyRequestError(error.code) from error
    except (URLError, TimeoutError, OSError, json.JSONDecodeError) as error:
        raise GeoapifyRequestError() from error


def raise_for_geoapify_error(error: GeoapifyRequestError) -> None:
    """Translate upstream failures into distinct, browser-safe application outcomes."""
    if error.status_code in {401, 403}:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={
                "outcome": "authentication_failure",
                "message": "Hotel map search could not authenticate with its location provider.",
            },
        )
    if error.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "outcome": "rate_limited",
                "message": "Hotel map search is temporarily rate limited. Please try again later.",
            },
        )
    raise HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail={
            "outcome": "api_failure",
            "message": "Hotel map search is temporarily unavailable. Please try again later.",
        },
    )


def is_valid_coordinate(latitude: Any, longitude: Any) -> bool:
    """Accept only finite latitude/longitude values within normal geographic bounds."""
    return (
        isinstance(latitude, (int, float))
        and not isinstance(latitude, bool)
        and isinstance(longitude, (int, float))
        and not isinstance(longitude, bool)
        and math.isfinite(latitude)
        and math.isfinite(longitude)
        and -90 <= latitude <= 90
        and -180 <= longitude <= 180
    )


def clean_text(value: Any) -> Optional[str]:
    """Return a non-empty provider string without inventing a replacement value."""
    if not isinstance(value, str):
        return None
    cleaned = value.strip()
    return cleaned or None


def find_verified_zip_location(
    geocoding_response: dict[str, Any], requested_zip: str
) -> Optional[dict[str, Any]]:
    """Return only a Geoapify result that exactly matches the requested U.S. ZIP."""
    results = geocoding_response.get("results")
    if not isinstance(results, list):
        return None

    for result in results:
        if not isinstance(result, dict):
            continue
        latitude = result.get("lat")
        longitude = result.get("lon")
        country_code = clean_text(result.get("country_code"))
        if (
            country_code is not None
            and country_code.lower() == "us"
            and clean_text(result.get("postcode")) == requested_zip
            and clean_text(result.get("result_type")) == "postcode"
            and is_valid_coordinate(latitude, longitude)
        ):
            return {
                "latitude": float(latitude),
                "longitude": float(longitude),
                "formatted": clean_text(result.get("formatted")),
                "city": clean_text(result.get("city")),
                "state": clean_text(result.get("state")),
            }
    return None


def build_address(properties: dict[str, Any]) -> Optional[str]:
    """Prefer Geoapify's complete address, then keep only supplied components."""
    formatted = clean_text(properties.get("formatted"))
    if formatted:
        return formatted
    parts = [
        clean_text(properties.get("address_line1")),
        clean_text(properties.get("address_line2")),
        clean_text(properties.get("city")),
        clean_text(properties.get("state")),
        clean_text(properties.get("postcode")),
    ]
    address_parts = list(dict.fromkeys(part for part in parts if part))
    return ", ".join(address_parts) if address_parts else None


def normalize_place_feature(feature: Any) -> Optional[dict[str, Any]]:
    """Keep only honest, mappable Geoapify hotel fields needed by the Vue view."""
    if not isinstance(feature, dict):
        return None
    properties = feature.get("properties")
    geometry = feature.get("geometry")
    if not isinstance(properties, dict) or not isinstance(geometry, dict):
        return None
    coordinates = geometry.get("coordinates")
    if not isinstance(coordinates, list) or len(coordinates) < 2:
        return None

    longitude, latitude = coordinates[0], coordinates[1]
    provider_place_id = clean_text(properties.get("place_id"))
    hotel_name = clean_text(properties.get("name"))
    if not provider_place_id or not is_valid_coordinate(latitude, longitude):
        return None

    hotel: dict[str, Any] = {
        "provider_place_id": provider_place_id,
        "latitude": float(latitude),
        "longitude": float(longitude),
    }
    if hotel_name:
        hotel["hotel_name"] = hotel_name
    address = build_address(properties)
    if address:
        hotel["address"] = address
    for field in ("city", "state", "postcode"):
        value = clean_text(properties.get(field))
        if value:
            hotel[field] = value
    categories = properties.get("categories")
    if isinstance(categories, list) and all(isinstance(category, str) for category in categories):
        hotel["categories"] = categories
    return hotel


def normalize_places(places_response: dict[str, Any]) -> list[dict[str, Any]]:
    """Deduplicate valid provider features without filling absent provider data."""
    features = places_response.get("features")
    if not isinstance(features, list):
        return []

    hotels = []
    seen_place_ids = set()
    for feature in features:
        hotel = normalize_place_feature(feature)
        if not hotel or hotel["provider_place_id"] in seen_place_ids:
            continue
        seen_place_ids.add(hotel["provider_place_id"])
        hotels.append(hotel)
        if len(hotels) == GEOAPIFY_RESULT_LIMIT:
            break
    return hotels


def search_nearby_hotels_for_zip(zip_code: str, api_key: str) -> dict[str, Any]:
    """Resolve a verified U.S. ZIP and return up to 20 nearby provider hotels."""
    try:
        geocoding_response = geoapify_get(
            GEOAPIFY_GEOCODING_URL,
            {
                "text": zip_code,
                "filter": "countrycode:us",
                "type": "postcode",
                "limit": 5,
                "format": "json",
                "apiKey": api_key,
            },
        )
    except GeoapifyRequestError as error:
        raise_for_geoapify_error(error)

    location = find_verified_zip_location(geocoding_response, zip_code)
    if location is None:
        return {
            "outcome": "unresolved_zip",
            "zip_code": zip_code,
            "hotels": [],
            "message": "We could not resolve that U.S. ZIP code.",
        }

    try:
        places_response = geoapify_get(
            GEOAPIFY_PLACES_URL,
            {
                "categories": GEOAPIFY_HOTEL_CATEGORY,
                "filter": (
                    f"circle:{location['longitude']},{location['latitude']},"
                    f"{GEOAPIFY_RADIUS_METERS}"
                ),
                "bias": f"proximity:{location['longitude']},{location['latitude']}",
                "limit": GEOAPIFY_RESULT_LIMIT,
                "apiKey": api_key,
            },
        )
    except GeoapifyRequestError as error:
        raise_for_geoapify_error(error)

    hotels = normalize_places(places_response)
    response = {
        "zip_code": zip_code,
        "center": location,
        "hotels": hotels,
        "result_limit": GEOAPIFY_RESULT_LIMIT,
        "provider": "Geoapify Places",
        "inventory_notice": "Results are provider data and are not an exhaustive hotel inventory.",
    }
    if not hotels:
        return {
            **response,
            "outcome": "no_results",
            "message": "No nearby hotels were returned within 5 km of this ZIP-code location.",
        }
    return {
        **response,
        "outcome": "success",
        "message": f"{len(hotels)} nearby hotel result(s) returned by Geoapify.",
    }


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


@app.get("/api/nearby-hotels")
def search_nearby_hotels(zip_code: str = Query(...)) -> dict[str, Any]:
    """Return truthful Geoapify hotel-provider results near a verified U.S. ZIP code."""
    normalized_zip = zip_code.strip()
    if not ZIP_CODE_PATTERN.fullmatch(normalized_zip):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "outcome": "invalid_zip",
                "message": "Enter exactly five digits for a U.S. ZIP code.",
            },
        )
    return search_nearby_hotels_for_zip(normalized_zip, get_geoapify_api_key())


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
