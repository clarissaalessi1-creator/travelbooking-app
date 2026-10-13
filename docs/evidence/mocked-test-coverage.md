# Offline Mocked-Test Evidence

**Evidence type: automated tests with mocked OpenRouter replies and temporary
SQLite databases. This is not a live provider demonstration.**

The final command was:

```sh
PYTHONPYCACHEPREFIX=/private/tmp/travelbooking-pycache \
  backend/.venv/bin/python -m unittest discover -s backend -p 'test*.py' -v
```

Observed result: **40 tests passed**.

| Requirement scenario | Test evidence |
| --- | --- |
| Successful two-night result, total, minimum rooms, checkout exclusion | `test_successful_two_stage_answer_uses_integer_cents_and_excludes_checkout` |
| Missing night and zero rooms | `test_missing_night_is_not_available_and_preserves_manual_values`; `test_zero_room_night_is_not_an_available_complete_stay` |
| Dates outside stored demo data | `test_dates_outside_stored_demo_nights_return_no_matches` |
| Invalid dates | `test_invalid_dates_do_not_contact_provider` |
| Fenced/prose JSON and malformed first-stage output | First-stage parser tests |
| Unsafe SQL | `test_unsafe_generated_sql_is_rejected_without_data_changes` |
| Read-only database guard | `test_readonly_connection_rejects_direct_write_attempt` |
| Model/provider/timeouts/network/invalid response | `test_openrouter_failures_have_distinct_safe_outcomes` |
| Grounded second-stage answers | JSON, plain-text, missing-answer, ungrounded-price, and invented-name tests |
| ZIP, local-first, add/remove preservation | Existing nearby-hotel and saved-hotel tests in the same 40-test suite |

The exact fixture is
[`../../backend/fixtures/chatbot-availability-fixture.json`](../../backend/fixtures/chatbot-availability-fixture.json).
