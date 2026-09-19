"""SQLite initialization and CSV seeding for the travel booking application."""

import csv
import re
import sqlite3
from pathlib import Path

PROJECT_DIRECTORY = Path(__file__).resolve().parent.parent
DATA_DIRECTORY = PROJECT_DIRECTORY / "data"
DATABASE_FILE = DATA_DIRECTORY / "travel_booking.db"
SCHEMA_FILE = Path(__file__).with_name("schema.sql")

SEED_FILES = {
    "hotels": {
        "filename": "hotels.csv",
        "columns": ("hotel_id", "hotel_name", "city", "state", "nightly_rate_usd"),
    },
    "trips": {
        "filename": "trips.csv",
        "columns": ("trip_id", "hotel_id", "trip_name", "check_in", "check_out"),
    },
    "users": {
        "filename": "users.csv",
        "columns": ("user_id", "display_name"),
    },
    "bookings": {
        "filename": "bookings.csv",
        "columns": ("booking_id", "user_id", "trip_id", "booked_on", "status"),
    },
}

ID_PATTERNS = {
    "hotel_id": re.compile(r"H\d{3}"),
    "trip_id": re.compile(r"T\d{3}"),
    "user_id": re.compile(r"U\d{3}"),
    "booking_id": re.compile(r"B\d{3}"),
}


def get_connection() -> sqlite3.Connection:
    """Open a connection with foreign-key validation enabled."""
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def read_seed_rows(filename: str, columns: tuple[str, ...]) -> list[dict[str, str]]:
    """Read and validate one instructor CSV before it is inserted into SQLite."""
    path = DATA_DIRECTORY / filename
    try:
        with path.open(encoding="utf-8-sig", newline="") as csv_file:
            reader = csv.DictReader(csv_file)
            headers = set(reader.fieldnames or [])
            missing_columns = set(columns) - headers
            if missing_columns:
                missing_text = ", ".join(sorted(missing_columns))
                raise ValueError(f"{filename} is missing required columns: {missing_text}")
            rows = list(reader)
    except FileNotFoundError as error:
        raise RuntimeError(f"Required seed file not found: {filename}") from error

    for line_number, row in enumerate(rows, start=2):
        for column in columns:
            if row.get(column) is None or not row[column].strip():
                raise ValueError(f"{filename} line {line_number} has a blank {column}")
        for identifier, pattern in ID_PATTERNS.items():
            if identifier in row and not pattern.fullmatch(row[identifier]):
                raise ValueError(f"{filename} line {line_number} has malformed {identifier}")

    return rows


def seed_table(connection: sqlite3.Connection, table_name: str) -> None:
    """Insert starter rows once, leaving existing rows unchanged on later starts."""
    seed_info = SEED_FILES[table_name]
    columns = seed_info["columns"]
    rows = read_seed_rows(seed_info["filename"], columns)
    column_list = ", ".join(columns)
    placeholders = ", ".join("?" for _ in columns)
    statement = f"INSERT OR IGNORE INTO {table_name} ({column_list}) VALUES ({placeholders})"
    connection.executemany(statement, [tuple(row[column] for column in columns) for row in rows])


def initialize_booking_id_state(connection: sqlite3.Connection) -> None:
    """Store the highest issued booking number once and never lower it."""
    if connection.execute("SELECT 1 FROM booking_id_state WHERE state_id = 1").fetchone():
        return

    booking_numbers = [
        int(row["booking_id"][1:])
        for row in connection.execute("SELECT booking_id FROM bookings")
        if ID_PATTERNS["booking_id"].fullmatch(row["booking_id"])
    ]
    connection.execute(
        "INSERT INTO booking_id_state (state_id, last_issued_number) VALUES (1, ?)",
        (max(booking_numbers, default=0),),
    )


def issue_next_booking_id(connection: sqlite3.Connection) -> str:
    """Advance the persistent booking counter and return its new B-prefixed ID."""
    connection.execute(
        "UPDATE booking_id_state SET last_issued_number = last_issued_number + 1 WHERE state_id = 1"
    )
    row = connection.execute(
        "SELECT last_issued_number FROM booking_id_state WHERE state_id = 1"
    ).fetchone()
    if row is None:
        raise RuntimeError("Booking ID state was not initialized")
    return f"B{row['last_issued_number']:03d}"


def initialize_database() -> None:
    """Create the schema and run the instructor seed only once per database."""
    with get_connection() as connection:
        connection.executescript(SCHEMA_FILE.read_text(encoding="utf-8"))
        already_seeded = connection.execute(
            "SELECT 1 FROM seed_metadata WHERE seed_name = 'instructor_csv_seed'"
        ).fetchone()
        if not already_seeded:
            for table_name in ("hotels", "trips", "users", "bookings"):
                seed_table(connection, table_name)
            connection.execute("INSERT INTO seed_metadata (seed_name) VALUES ('instructor_csv_seed')")

        initialize_booking_id_state(connection)
