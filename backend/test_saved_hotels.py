"""Focused tests for the Assignment 2 Part 2 in-class saved-hotel controller."""

from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import database
import main


class SavedHotelTests(unittest.TestCase):
    """Run each save workflow against an isolated temporary SQLite database."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "saved_hotels_test.db"
        self.database_path_patch = patch.object(database, "DATABASE_FILE", database_path)
        self.database_path_patch.start()
        self.addCleanup(self.database_path_patch.stop)
        self.addCleanup(self.temporary_directory.cleanup)
        main.initialize_database()

    @staticmethod
    def saved_hotel_request(**overrides: object) -> main.SavedHotelCreate:
        payload = {
            "provider_place_id": "geoapify-save-test-1",
            "hotel_name": "Saved Provider Hotel",
            "address": "1 Test Street, Boston, MA 02108",
            "latitude": 42.358,
            "longitude": -71.064,
            "searched_zip_code": "02108",
        }
        payload.update(overrides)
        return main.SavedHotelCreate(**payload)

    def test_new_save_creates_five_default_simulated_nights(self) -> None:
        saved_hotel, created = main.save_provider_hotel(self.saved_hotel_request())

        self.assertTrue(created)
        self.assertEqual(saved_hotel["provider_place_id"], "geoapify-save-test-1")
        with main.get_connection() as connection:
            nights = connection.execute(
                """SELECT stay_date, nightly_rate_cents, rooms_available
                   FROM demo_hotel_nights
                   WHERE saved_hotel_id = ?
                   ORDER BY stay_date""",
                (saved_hotel["saved_hotel_id"],),
            ).fetchall()

        self.assertEqual(
            [row["stay_date"] for row in nights],
            list(main.DEMO_HOTEL_NIGHT_DATES),
        )
        self.assertTrue(
            all(
                row["nightly_rate_cents"] == 10000 and row["rooms_available"] == 20
                for row in nights
            )
        )

    def test_repeated_save_preserves_existing_hotel_and_nightly_rows(self) -> None:
        saved_hotel, created = main.save_provider_hotel(self.saved_hotel_request())
        self.assertTrue(created)
        with main.get_connection() as connection:
            connection.execute(
                """UPDATE demo_hotel_nights SET rooms_available = 7
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-10'""",
                (saved_hotel["saved_hotel_id"],),
            )

        repeated_hotel, created = main.save_provider_hotel(
            self.saved_hotel_request(
                hotel_name="Changed provider name",
                address="99 Changed Street",
                searched_zip_code="10001",
            )
        )

        self.assertFalse(created)
        self.assertEqual(repeated_hotel["hotel_name"], "Saved Provider Hotel")
        self.assertEqual(repeated_hotel["searched_zip_code"], "02108")
        with main.get_connection() as connection:
            saved_hotel_count = connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[0]
            night_count = connection.execute(
                "SELECT COUNT(*) FROM demo_hotel_nights WHERE saved_hotel_id = ?",
                (saved_hotel["saved_hotel_id"],),
            ).fetchone()[0]
            changed_room_count = connection.execute(
                """SELECT rooms_available FROM demo_hotel_nights
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-10'""",
                (saved_hotel["saved_hotel_id"],),
            ).fetchone()[0]

        self.assertEqual(saved_hotel_count, 1)
        self.assertEqual(night_count, 5)
        self.assertEqual(changed_room_count, 7)

    def test_live_results_are_marked_saved_without_a_local_first_lookup(self) -> None:
        main.save_provider_hotel(self.saved_hotel_request())

        hotels = main.add_saved_status_to_places(
            [
                {"provider_place_id": "geoapify-save-test-1", "latitude": 42.358, "longitude": -71.064},
                {"provider_place_id": "geoapify-not-saved", "latitude": 42.36, "longitude": -71.06},
            ]
        )

        self.assertTrue(hotels[0]["is_saved_locally"])
        self.assertFalse(hotels[1]["is_saved_locally"])

    def test_local_lookup_returns_stored_nights_without_calling_geoapify(self) -> None:
        saved_hotel, _ = main.save_provider_hotel(self.saved_hotel_request())
        with main.get_connection() as connection:
            connection.execute(
                """UPDATE demo_hotel_nights
                   SET nightly_rate_cents = 12345, rooms_available = 7
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-12'""",
                (saved_hotel["saved_hotel_id"],),
            )

        with patch("main.geoapify_get") as geoapify_get:
            response = main.list_saved_hotels("02108")

        geoapify_get.assert_not_called()
        self.assertEqual(response["source"], "local")
        self.assertEqual(response["zip_code"], "02108")
        self.assertEqual(len(response["hotels"]), 1)
        hotel = response["hotels"][0]
        self.assertTrue(hotel["is_saved_locally"])
        self.assertEqual(hotel["provider_place_id"], saved_hotel["provider_place_id"])
        self.assertEqual(len(hotel["simulated_nights"]), len(main.DEMO_HOTEL_NIGHT_DATES))
        updated_night = next(
            night for night in hotel["simulated_nights"] if night["stay_date"] == "2026-10-12"
        )
        self.assertEqual(updated_night["nightly_rate_cents"], 12345)
        self.assertEqual(updated_night["rooms_available"], 7)

    def test_local_lookup_empty_zip_result_can_fall_back_to_geoapify(self) -> None:
        main.save_provider_hotel(self.saved_hotel_request(searched_zip_code="02108"))

        response = main.list_saved_hotels("10001")

        self.assertEqual(response["source"], "local")
        self.assertEqual(response["hotels"], [])
        self.assertIn("No saved local hotels", response["message"])

    def test_local_lookup_database_error_is_clear_and_does_not_fall_back(self) -> None:
        with patch("main.get_connection", side_effect=main.sqlite3.DatabaseError("test failure")):
            with self.assertRaises(main.HTTPException) as error:
                main.list_saved_hotels("02108")

        self.assertEqual(error.exception.status_code, 500)
        self.assertEqual(error.exception.detail, "Could not load saved local hotels. Please try again.")

    def test_remove_saved_hotel_cascades_its_simulated_nights(self) -> None:
        saved_hotel, _ = main.save_provider_hotel(self.saved_hotel_request())

        removed = main.remove_saved_provider_hotel(saved_hotel["provider_place_id"])

        self.assertTrue(removed)
        with main.get_connection() as connection:
            saved_row = connection.execute(
                "SELECT 1 FROM saved_hotels WHERE saved_hotel_id = ?",
                (saved_hotel["saved_hotel_id"],),
            ).fetchone()
            night_count = connection.execute(
                "SELECT COUNT(*) FROM demo_hotel_nights WHERE saved_hotel_id = ?",
                (saved_hotel["saved_hotel_id"],),
            ).fetchone()[0]

        self.assertIsNone(saved_row)
        self.assertEqual(night_count, 0)

    def test_remove_preserves_unrelated_saved_data_and_assignment_one_tables(self) -> None:
        target_hotel, _ = main.save_provider_hotel(self.saved_hotel_request())
        unrelated_hotel, _ = main.save_provider_hotel(
            self.saved_hotel_request(
                provider_place_id="geoapify-save-test-2",
                hotel_name="Unrelated Provider Hotel",
            )
        )
        with main.get_connection() as connection:
            assignment_one_counts = {
                table_name: connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in ("hotels", "trips", "users", "bookings")
            }

        response = main.delete_saved_hotel(target_hotel["provider_place_id"])

        self.assertEqual(response["is_saved_locally"], False)
        self.assertEqual(response["provider_place_id"], target_hotel["provider_place_id"])
        with main.get_connection() as connection:
            remaining_saved_hotels = connection.execute(
                "SELECT provider_place_id FROM saved_hotels ORDER BY saved_hotel_id"
            ).fetchall()
            unrelated_night_count = connection.execute(
                "SELECT COUNT(*) FROM demo_hotel_nights WHERE saved_hotel_id = ?",
                (unrelated_hotel["saved_hotel_id"],),
            ).fetchone()[0]
            final_assignment_one_counts = {
                table_name: connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in ("hotels", "trips", "users", "bookings")
            }

        self.assertEqual(
            [row["provider_place_id"] for row in remaining_saved_hotels],
            [unrelated_hotel["provider_place_id"]],
        )
        self.assertEqual(unrelated_night_count, len(main.DEMO_HOTEL_NIGHT_DATES))
        self.assertEqual(final_assignment_one_counts, assignment_one_counts)

    def test_remove_missing_saved_hotel_returns_a_clear_not_found_error(self) -> None:
        with self.assertRaises(main.HTTPException) as error:
            main.delete_saved_hotel("geoapify-not-saved")

        self.assertEqual(error.exception.status_code, 404)
        self.assertEqual(error.exception.detail, "Saved hotel not found locally.")


if __name__ == "__main__":
    unittest.main()
