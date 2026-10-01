"""Focused tests for the Assignment 2 Part 1 Geoapify ZIP-search controller."""

import unittest
from unittest.mock import patch

from fastapi import HTTPException

import main


def verified_geocode_response() -> dict:
    return {
        "results": [
            {
                "country_code": "us",
                "postcode": "02108",
                "result_type": "postcode",
                "lat": 42.3577,
                "lon": -71.0636,
                "formatted": "Boston, MA 02108, United States of America",
            }
        ]
    }


def valid_place_response() -> dict:
    return {
        "features": [
            {
                "properties": {
                    "place_id": "geoapify-hotel-1",
                    "name": "Provider Hotel",
                    "formatted": "1 Example Street, Boston, MA 02108, United States",
                    "categories": ["accommodation.hotel"],
                },
                "geometry": {"coordinates": [-71.064, 42.358]},
            }
        ]
    }


class NearbyHotelSearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api_key_patch = patch("main.get_geoapify_api_key", return_value="test-key")
        self.api_key_patch.start()
        self.addCleanup(self.api_key_patch.stop)

    def test_successful_leading_zero_zip_uses_verified_location_and_hotel_fields(self) -> None:
        calls = []

        def fake_geoapify_get(url, parameters):
            calls.append((url, parameters))
            if url == main.GEOAPIFY_GEOCODING_URL:
                return verified_geocode_response()
            return valid_place_response()

        with patch("main.geoapify_get", side_effect=fake_geoapify_get):
            result = main.search_nearby_hotels("02108")

        self.assertEqual(result["outcome"], "success")
        self.assertEqual(calls[0][1]["text"], "02108")
        self.assertEqual(calls[0][1]["filter"], "countrycode:us")
        self.assertEqual(calls[1][1]["categories"], "accommodation.hotel")
        self.assertIn(",5000", calls[1][1]["filter"])
        self.assertEqual(calls[1][1]["limit"], 20)
        self.assertEqual(result["hotels"][0]["provider_place_id"], "geoapify-hotel-1")
        self.assertNotIn("test-key", str(result))

    def test_invalid_zip_is_rejected_before_key_or_upstream_request(self) -> None:
        with patch("main.geoapify_get") as geoapify_get:
            with self.assertRaises(HTTPException) as raised:
                main.search_nearby_hotels("2108")
        self.assertEqual(raised.exception.status_code, 422)
        self.assertEqual(raised.exception.detail["outcome"], "invalid_zip")
        geoapify_get.assert_not_called()

    def test_unresolved_zip_does_not_call_places(self) -> None:
        with patch("main.geoapify_get", return_value={"results": []}) as geoapify_get:
            result = main.search_nearby_hotels("02108")
        self.assertEqual(result["outcome"], "unresolved_zip")
        self.assertEqual(result["hotels"], [])
        self.assertEqual(geoapify_get.call_count, 1)

    def test_empty_places_response_is_a_no_results_outcome(self) -> None:
        with patch(
            "main.geoapify_get", side_effect=[verified_geocode_response(), {"features": []}]
        ):
            result = main.search_nearby_hotels("02108")
        self.assertEqual(result["outcome"], "no_results")
        self.assertEqual(result["center"]["latitude"], 42.3577)

    def test_missing_provider_name_is_not_replaced_with_an_address(self) -> None:
        feature = valid_place_response()["features"][0]
        del feature["properties"]["name"]
        hotel = main.normalize_place_feature(feature)
        self.assertIsNotNone(hotel)
        self.assertNotIn("hotel_name", hotel)
        self.assertEqual(hotel["address"], "1 Example Street, Boston, MA 02108, United States")

    def test_upstream_failure_is_not_reported_as_no_results(self) -> None:
        with patch("main.geoapify_get", side_effect=main.GeoapifyRequestError(500)):
            with self.assertRaises(HTTPException) as raised:
                main.search_nearby_hotels("02108")
        self.assertEqual(raised.exception.status_code, 502)
        self.assertEqual(raised.exception.detail["outcome"], "api_failure")

    def test_rate_limit_is_distinct_and_simulated_without_provider_calls(self) -> None:
        with patch("main.geoapify_get", side_effect=main.GeoapifyRequestError(429)):
            with self.assertRaises(HTTPException) as raised:
                main.search_nearby_hotels("02108")
        self.assertEqual(raised.exception.status_code, 429)
        self.assertEqual(raised.exception.detail["outcome"], "rate_limited")

    def test_authentication_failure_is_distinct(self) -> None:
        with patch("main.geoapify_get", side_effect=main.GeoapifyRequestError(401)):
            with self.assertRaises(HTTPException) as raised:
                main.search_nearby_hotels("02108")
        self.assertEqual(raised.exception.detail["outcome"], "authentication_failure")


if __name__ == "__main__":
    unittest.main()
