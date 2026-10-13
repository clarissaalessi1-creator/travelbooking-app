"""Focused isolated tests for the Assignment 2 Part 2 two-stage hotel chatbot."""

import json
from pathlib import Path
import sqlite3
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import database
import main


FIXTURE_PATH = Path(__file__).with_name("fixtures") / "chatbot-availability-fixture.json"


class ChatbotBackendTests(unittest.TestCase):
    """Exercise generated-SQL safety and grounded answers without the live provider or app DB."""

    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temporary_directory.name) / "chatbot_test.db"
        self.database_path_patch = patch.object(database, "DATABASE_FILE", database_path)
        self.database_path_patch.start()
        self.addCleanup(self.database_path_patch.stop)
        self.addCleanup(self.temporary_directory.cleanup)
        main.initialize_database()

        self.saved_hotel, _ = main.save_provider_hotel(
            main.SavedHotelCreate(
                provider_place_id="chatbot-test-hotel",
                hotel_name="Chatbot Test Hotel",
                address="1 Test Street, Boston, MA 02108",
                latitude=42.358,
                longitude=-71.064,
                searched_zip_code="02108",
            )
        )
        with main.get_connection() as connection:
            connection.execute(
                """UPDATE demo_hotel_nights
                   SET nightly_rate_cents = 12500, rooms_available = 7
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-10'""",
                (self.saved_hotel["saved_hotel_id"],),
            )
            connection.execute(
                """UPDATE demo_hotel_nights
                   SET nightly_rate_cents = 10000, rooms_available = 20
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-11'""",
                (self.saved_hotel["saved_hotel_id"],),
            )

    def database_counts(self) -> dict[str, int]:
        with main.get_connection() as connection:
            return {
                table_name: connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                for table_name in (
                    "hotels",
                    "trips",
                    "users",
                    "bookings",
                    "saved_hotels",
                    "demo_hotel_nights",
                )
            }

    @staticmethod
    def sql_proposal(check_in: str = "2026-10-10", check_out: str = "2026-10-12") -> str:
        return json.dumps(
            {
                "sql": main.CHATBOT_APPROVED_SQL,
                "parameters": [check_in, check_out],
            }
        )

    @staticmethod
    def fixed_fixture() -> dict[str, object]:
        return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

    @staticmethod
    def grounded_answer() -> str:
        return json.dumps(
            {
                "answer": (
                    "Chatbot Test Hotel has a two-night simulated classroom total of $225.00 "
                    "and a minimum of 7 rooms available."
                )
            }
        )

    def grounded_context(self) -> tuple[dict[str, object], list[dict[str, object]]]:
        check_in = main.date(2026, 10, 10)
        check_out = main.date(2026, 10, 12)
        rows = main.execute_chatbot_query(
            main.CHATBOT_APPROVED_SQL, [check_in.isoformat(), check_out.isoformat()]
        )
        return main.stay_metadata(check_in, check_out), main.calculate_complete_stays(
            rows, check_in, check_out
        )

    def patched_provider(self, responses: list[str]):
        return patch("main.openrouter_chat_completion", side_effect=responses)

    def test_successful_two_stage_answer_uses_integer_cents_and_excludes_checkout(self) -> None:
        fixture = self.fixed_fixture()
        question = fixture["question"]
        before_counts = self.database_counts()
        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with self.patched_provider([self.sql_proposal(), self.grounded_answer()]) as provider:
                response = main.answer_chatbot_question(question)

        self.assertEqual(response["status"], "success")
        self.assertEqual(provider.call_count, 2)
        self.assertEqual(response["stay"]["night_count"], 2)
        self.assertFalse(response["stay"]["checkout_included"])
        self.assertEqual(len(response["retrieved_records"]), 2)
        self.assertEqual(
            json.loads(self.sql_proposal()), fixture["first_stage_expected_shape"]
        )
        fixture_records = [
            {
                key: record[key]
                for key in ("hotel_name", "stay_date", "nightly_rate_cents", "rooms_available")
            }
            for record in response["retrieved_records"]
        ]
        self.assertEqual(fixture_records, fixture["retrieved_records"])
        expected_stay = fixture["expected_complete_stay"]
        self.assertEqual(response["complete_stays"][0]["total_rate_cents"], expected_stay["total_rate_cents"])
        self.assertEqual(
            response["complete_stays"][0]["minimum_rooms_available"],
            expected_stay["minimum_rooms_available"],
        )
        self.assertIn("simulated classroom", response["final_answer"])
        self.assertNotIn("provider_place_id", str(response["retrieved_records"]))
        self.assertEqual(self.database_counts(), before_counts)

    def test_zero_room_night_is_not_an_available_complete_stay(self) -> None:
        with main.get_connection() as connection:
            connection.execute(
                """UPDATE demo_hotel_nights
                   SET rooms_available = 0
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-11'""",
                (self.saved_hotel["saved_hotel_id"],),
            )

        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with self.patched_provider([self.sql_proposal()]) as provider:
                response = main.answer_chatbot_question(
                    "Find saved rooms from 2026-10-10 to 2026-10-12."
                )

        self.assertEqual(response["status"], "no_matches")
        self.assertEqual(provider.call_count, 1)

    def test_dates_outside_stored_demo_nights_return_no_matches(self) -> None:
        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with self.patched_provider([self.sql_proposal("2026-10-14", "2026-10-16")]) as provider:
                response = main.answer_chatbot_question(
                    "Find saved rooms from 2026-10-14 to 2026-10-16."
                )

        self.assertEqual(response["status"], "no_matches")
        self.assertEqual(provider.call_count, 1)

    def test_health_check_reports_ready(self) -> None:
        self.assertEqual(main.health_check(), {"status": "ok"})

    def test_missing_night_is_not_available_and_preserves_manual_values(self) -> None:
        with main.get_connection() as connection:
            connection.execute(
                """DELETE FROM demo_hotel_nights
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-11'""",
                (self.saved_hotel["saved_hotel_id"],),
            )

        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with self.patched_provider([self.sql_proposal()]) as provider:
                response = main.answer_chatbot_question(
                    "Find saved rooms from 2026-10-10 to 2026-10-12."
                )

        self.assertEqual(response["status"], "no_matches")
        self.assertEqual(provider.call_count, 1)
        with main.get_connection() as connection:
            remaining_rate = connection.execute(
                """SELECT nightly_rate_cents FROM demo_hotel_nights
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-10'""",
                (self.saved_hotel["saved_hotel_id"],),
            ).fetchone()[0]
        self.assertEqual(remaining_rate, 12500)

    def test_invalid_dates_do_not_contact_provider(self) -> None:
        with patch("main.openrouter_chat_completion") as provider:
            response = main.answer_chatbot_question(
                "Find a room from 2026-10-12 to 2026-10-10."
            )

        self.assertEqual(response["status"], "invalid_dates")
        provider.assert_not_called()

    def test_first_stage_sql_parser_accepts_json_fences_and_surrounding_text(self) -> None:
        expected_parameters = ["2026-10-10", "2026-10-12"]
        valid_json = self.sql_proposal()
        responses = {
            "valid JSON": valid_json,
            "JSON code fence": f"```json\n{valid_json}\n```",
            "surrounding text": f"Here is the requested query:\n{valid_json}\nUse it safely.",
        }

        for label, provider_content in responses.items():
            with self.subTest(label=label):
                proposed_sql, parameters = main.extract_sql_proposal(provider_content)
                self.assertEqual(proposed_sql, main.CHATBOT_APPROVED_SQL)
                self.assertEqual(parameters, expected_parameters)

    def test_first_stage_sql_parser_rejects_malformed_or_incomplete_objects(self) -> None:
        malformed_responses = (
            '{"sql":"SELECT"',
            '{"sql":"SELECT 1"}',
            "I cannot provide a query.",
            '{"sql":"SELECT 1"}{"parameters":[]}',
        )

        for provider_content in malformed_responses:
            with self.subTest(provider_content=provider_content):
                with self.assertRaises((ValueError, main.ChatbotSqlRejectedError)):
                    main.extract_sql_proposal(provider_content)

    def test_openrouter_text_reader_accepts_text_content_blocks(self) -> None:
        proposal = self.sql_proposal()
        content = main.extract_openrouter_text_content(
            {
                "choices": [
                    {
                        "message": {
                            "content": [{"type": "text", "text": proposal}],
                            "role": "assistant",
                        }
                    }
                ]
            }
        )

        proposed_sql, parameters = main.extract_sql_proposal(content)
        self.assertEqual(proposed_sql, main.CHATBOT_APPROVED_SQL)
        self.assertEqual(parameters, ["2026-10-10", "2026-10-12"])

    def test_openrouter_text_reader_rejects_reasoning_without_final_content(self) -> None:
        response_payload = {
            "choices": [
                {
                    "message": {
                        "content": None,
                        "reasoning": "I should use the approved query.",
                        "reasoning_details": [{"type": "reasoning.text", "text": "..."}],
                    }
                }
            ]
        }

        with self.assertRaises(main.OpenRouterRequestError) as raised:
            main.extract_openrouter_text_content(response_payload)

        self.assertEqual(raised.exception.kind, "reasoning_only")

    def test_openrouter_text_reader_rejects_empty_final_content(self) -> None:
        with self.assertRaises(main.OpenRouterRequestError) as raised:
            main.extract_openrouter_text_content(
                {"choices": [{"message": {"content": ""}}]}
            )

        self.assertEqual(raised.exception.kind, "invalid_response")

    def test_openrouter_request_uses_no_reasoning_effort_and_final_content(self) -> None:
        provider_response = MagicMock()
        provider_response.read.return_value = json.dumps(
            {"choices": [{"message": {"content": self.sql_proposal()}}]}
        ).encode("utf-8")
        provider_response.__enter__.return_value = provider_response

        with patch("main.urlopen", return_value=provider_response) as mocked_urlopen:
            content = main.openrouter_chat_completion(
                "test-key", "test-model", [{"role": "user", "content": "test"}], 100
            )

        request = mocked_urlopen.call_args.args[0]
        request_body = json.loads(request.data.decode("utf-8"))
        self.assertEqual(request_body["reasoning_effort"], "none")
        self.assertEqual(content, self.sql_proposal())

    def test_unsafe_generated_sql_is_rejected_without_data_changes(self) -> None:
        unsafe_proposals = {
            "write": {
                "sql": "DROP TABLE saved_hotels",
                "parameters": ["2026-10-10", "2026-10-12"],
            },
            "multiple statements": {
                "sql": main.CHATBOT_APPROVED_SQL + "; SELECT * FROM bookings",
                "parameters": ["2026-10-10", "2026-10-12"],
            },
            "unauthorized table": {
                "sql": "SELECT booking_id FROM bookings LIMIT 25",
                "parameters": ["2026-10-10", "2026-10-12"],
            },
            "unbounded query": {
                "sql": "SELECT * FROM saved_hotels JOIN demo_hotel_nights "
                "ON saved_hotels.saved_hotel_id = demo_hotel_nights.saved_hotel_id",
                "parameters": ["2026-10-10", "2026-10-12"],
            },
        }
        before_counts = self.database_counts()

        for label, proposal in unsafe_proposals.items():
            with self.subTest(label=label):
                with patch(
                    "main.get_openrouter_configuration", return_value=("test-key", "test-model")
                ):
                    with self.patched_provider([json.dumps(proposal)]) as provider:
                        response = main.answer_chatbot_question(
                            "Find rooms from 2026-10-10 to 2026-10-12."
                        )
                self.assertEqual(response["status"], "rejected_sql")
                self.assertEqual(provider.call_count, 1)
                self.assertEqual(self.database_counts(), before_counts)

    def test_readonly_connection_rejects_direct_write_attempt(self) -> None:
        with main.get_chatbot_readonly_connection() as connection:
            with self.assertRaises(sqlite3.DatabaseError):
                connection.execute("DELETE FROM saved_hotels")

        with main.get_connection() as connection:
            saved_hotel_count = connection.execute("SELECT COUNT(*) FROM saved_hotels").fetchone()[0]
            saved_rate = connection.execute(
                """SELECT nightly_rate_cents FROM demo_hotel_nights
                   WHERE saved_hotel_id = ? AND stay_date = '2026-10-10'""",
                (self.saved_hotel["saved_hotel_id"],),
            ).fetchone()[0]
        self.assertEqual(saved_hotel_count, 1)
        self.assertEqual(saved_rate, 12500)

    def test_model_unavailable_is_a_clear_structured_error(self) -> None:
        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with patch(
                "main.openrouter_chat_completion", side_effect=main.OpenRouterRequestError(404)
            ):
                response = main.answer_chatbot_question(
                    "Find rooms from 2026-10-10 to 2026-10-12."
                )

        self.assertEqual(response["status"], "model_unavailable")
        self.assertIsNone(response["proposed_sql"])
        self.assertEqual(response["retrieved_records"], [])

    def test_provider_http_5xx_is_safe_and_structured(self) -> None:
        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with patch(
                "main.openrouter_chat_completion", side_effect=main.OpenRouterRequestError(503)
            ):
                response = main.answer_chatbot_question(
                    "Find rooms from 2026-10-10 to 2026-10-12."
                )

        self.assertEqual(response["status"], "provider_unavailable")
        self.assertNotIn("test-key", str(response))

    def test_openrouter_failures_have_distinct_safe_outcomes(self) -> None:
        cases = (
            (main.OpenRouterRequestError(503, "http_status"), "provider_unavailable", 502),
            (main.OpenRouterRequestError(kind="timeout"), "provider_timeout", 504),
            (main.OpenRouterRequestError(kind="network"), "provider_network_error", 502),
            (main.OpenRouterRequestError(kind="invalid_response"), "provider_invalid_response", 502),
            (
                main.OpenRouterRequestError(kind="reasoning_only"),
                "provider_reasoning_only_response",
                502,
            ),
            (main.OpenRouterRequestError(429, "http_status"), "provider_rate_limited", 429),
        )

        for error, outcome, expected_status in cases:
            with self.subTest(outcome=outcome):
                response = main.map_openrouter_error("Safe test question", error)
                self.assertEqual(response["status"], outcome)
                self.assertEqual(main.chatbot_http_status(outcome), expected_status)
                self.assertNotIn("test-key", str(response))

    def test_second_stage_accepts_a_valid_grounded_json_answer(self) -> None:
        stay, complete_stays = self.grounded_context()

        answer = main.extract_grounded_answer(self.grounded_answer(), stay, complete_stays)

        self.assertIn("Chatbot Test Hotel", answer)
        self.assertIn("$225.00", answer)
        self.assertIn("7 rooms", answer)

    def test_second_stage_accepts_safe_plain_text_when_json_is_not_supported(self) -> None:
        stay, complete_stays = self.grounded_context()
        plain_text = (
            "Chatbot Test Hotel has a total of $225.00 for 2 nights and a minimum of "
            "7 rooms available. Rates and rooms are simulated classroom data."
        )

        answer = main.extract_grounded_answer(plain_text, stay, complete_stays)

        self.assertEqual(answer, plain_text)

    def test_second_stage_rejects_malformed_json_and_missing_answer(self) -> None:
        stay, complete_stays = self.grounded_context()

        with self.assertRaises(ValueError):
            main.extract_grounded_answer('{"answer":"missing closing quote}', stay, complete_stays)
        with self.assertRaises(ValueError):
            main.extract_grounded_answer('{"summary":"No answer field"}', stay, complete_stays)

    def test_second_stage_rejects_ungrounded_numerical_claims(self) -> None:
        stay, complete_stays = self.grounded_context()
        ungrounded_answer = json.dumps(
            {
                "answer": (
                    "Chatbot Test Hotel costs $999.99 for 2 nights and has 99 rooms "
                    "available as simulated classroom data."
                )
            }
        )

        with self.assertRaises(ValueError):
            main.extract_grounded_answer(ungrounded_answer, stay, complete_stays)

    def test_second_stage_rejects_an_invented_hotel_name(self) -> None:
        stay, complete_stays = self.grounded_context()
        invented_hotel = json.dumps(
            {
                "answer": (
                    "Imaginary Grand Hotel costs $225.00 for 2 nights and has 7 rooms "
                    "available as simulated classroom data."
                )
            }
        )

        with self.assertRaises(ValueError):
            main.extract_grounded_answer(invented_hotel, stay, complete_stays)

    def test_route_returns_structured_success_response(self) -> None:
        with patch("main.get_openrouter_configuration", return_value=("test-key", "test-model")):
            with self.patched_provider([self.sql_proposal(), self.grounded_answer()]):
                response = main.ask_hotel_chatbot(
                    main.ChatbotQuestion(
                        question="Find rooms from 2026-10-10 to 2026-10-12."
                    )
                )

        payload = json.loads(response.body)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["status"], "success")
        self.assertEqual(payload["question"], "Find rooms from 2026-10-10 to 2026-10-12.")


if __name__ == "__main__":
    unittest.main()
