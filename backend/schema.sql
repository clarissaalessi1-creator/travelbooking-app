PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS hotels (
    hotel_id TEXT PRIMARY KEY,
    hotel_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    nightly_rate_usd REAL NOT NULL CHECK (nightly_rate_usd > 0)
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id TEXT PRIMARY KEY,
    hotel_id TEXT NOT NULL,
    trip_name TEXT NOT NULL,
    check_in TEXT NOT NULL,
    check_out TEXT NOT NULL,
    FOREIGN KEY (hotel_id) REFERENCES hotels (hotel_id),
    CHECK (check_out > check_in)
);

CREATE TABLE IF NOT EXISTS users (
    user_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    trip_id TEXT NOT NULL,
    booked_on TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('confirmed', 'cancelled')),
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    FOREIGN KEY (trip_id) REFERENCES trips (trip_id)
);

CREATE TABLE IF NOT EXISTS booking_id_state (
    state_id INTEGER PRIMARY KEY CHECK (state_id = 1),
    last_issued_number INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS seed_metadata (
    seed_name TEXT PRIMARY KEY,
    completed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Assignment 2 Part 2 in-class data is intentionally separate from the
-- instructor-supplied hotels and trips. Geoapify results retain the provider's
-- stable identifier and only the fields returned by the Part 1 endpoint.
CREATE TABLE IF NOT EXISTS saved_hotels (
    saved_hotel_id INTEGER PRIMARY KEY,
    provider_place_id TEXT NOT NULL UNIQUE,
    hotel_name TEXT,
    address TEXT,
    latitude REAL NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude REAL NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    searched_zip_code TEXT NOT NULL
        CHECK (searched_zip_code GLOB '[0-9][0-9][0-9][0-9][0-9]')
);

-- These simulated nightly values are only for the in-class saved-hotel
-- activity. Deleting a saved hotel also deletes its related nightly records.
CREATE TABLE IF NOT EXISTS demo_hotel_nights (
    demo_hotel_night_id INTEGER PRIMARY KEY,
    saved_hotel_id INTEGER NOT NULL,
    stay_date TEXT NOT NULL CHECK (
        stay_date IN (
            '2026-10-10',
            '2026-10-11',
            '2026-10-12',
            '2026-10-13',
            '2026-10-14'
        )
    ),
    nightly_rate_cents INTEGER NOT NULL DEFAULT 10000 CHECK (nightly_rate_cents >= 0),
    rooms_available INTEGER NOT NULL DEFAULT 20 CHECK (rooms_available >= 0),
    UNIQUE (saved_hotel_id, stay_date),
    FOREIGN KEY (saved_hotel_id) REFERENCES saved_hotels (saved_hotel_id) ON DELETE CASCADE
);
