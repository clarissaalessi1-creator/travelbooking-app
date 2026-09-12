"""FastAPI service for the Part 1 hotel and available-stay search."""

import csv
from collections import defaultdict
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

DATA_DIRECTORY = Path(__file__).resolve().parent.parent / "data"
HOTELS_FILE = DATA_DIRECTORY / "hotels.csv"
TRIPS_FILE = DATA_DIRECTORY / "trips.csv"

REQUIRED_HOTEL_FIELDS = {"hotel_id", "hotel_name", "city", "state", "nightly_rate_usd"}
REQUIRED_TRIP_FIELDS = {"trip_id", "hotel_id", "trip_name", "check_in", "check_out"}

app = FastAPI(title="Part 1 Hotel Search API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


def read_csv_records(path: Path, required_fields: set[str]) -> list[dict[str, str]]:
    """Read an instructor CSV and ensure it has the columns required by Part 1."""
    try:
        with path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames or [])
            if not required_fields.issubset(headers):
                missing_fields = ", ".join(sorted(required_fields - headers))
                raise HTTPException(
                    status_code=500,
                    detail=f"{path.name} is missing required columns: {missing_fields}",
                )
            return list(reader)
    except FileNotFoundError as error:
        raise HTTPException(status_code=500, detail=f"Required data file not found: {path.name}") from error


def build_search_results(hotel_name: str) -> list[dict[str, Any]]:
    """Join matching hotels to their available trips using hotel_id."""
    hotels = read_csv_records(HOTELS_FILE, REQUIRED_HOTEL_FIELDS)
    trips = read_csv_records(TRIPS_FILE, REQUIRED_TRIP_FIELDS)

    trips_by_hotel_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    for trip in trips:
        trips_by_hotel_id[trip["hotel_id"]].append(trip)

    normalized_name = hotel_name.casefold()
    matching_hotels: list[dict[str, Any]] = []
    for hotel in hotels:
        if normalized_name not in hotel["hotel_name"].casefold():
            continue

        matching_hotels.append(
            {
                "hotel_id": hotel["hotel_id"],
                "hotel_name": hotel["hotel_name"],
                "city": hotel["city"],
                "state": hotel["state"],
                "nightly_rate_usd": hotel["nightly_rate_usd"],
                "available_stays": [
                    {
                        "trip_id": trip["trip_id"],
                        "trip_name": trip["trip_name"],
                        "check_in": trip["check_in"],
                        "check_out": trip["check_out"],
                    }
                    for trip in trips_by_hotel_id[hotel["hotel_id"]]
                ],
            }
        )

    return matching_hotels


@app.get("/api/search")
def search_hotels(hotel_name: str = Query(..., min_length=1)) -> dict[str, Any]:
    """Return hotels matching a name and their available stays from the two CSV files."""
    search_term = hotel_name.strip()
    if not search_term:
        return {"search_term": "", "matches": []}

    return {"search_term": search_term, "matches": build_search_results(search_term)}
