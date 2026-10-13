# Assignment 2 Part 2 — Chatbot Verification

## Fixed offline fixture

[`backend/fixtures/chatbot-availability-fixture.json`](../backend/fixtures/chatbot-availability-fixture.json)
defines a deterministic two-night saved-hotel case. The tests create equivalent
records in a temporary SQLite database; they never write to
`data/travel_booking.db`.

| Check | Expected | Observed from mocked two-stage test |
| --- | --- | --- |
| First-stage proposal | LLM returns the approved read-only query and `2026-10-10`, `2026-10-12` bound parameters. | Accepted, then validated against the exact allowlisted query. |
| Nights returned | Oct. 10 and Oct. 11 only; checkout Oct. 12 excluded. | Two rows returned. |
| Price calculation | 12,500 + 10,000 integer cents = 22,500 cents / `$225.00`. | Matched. |
| Availability | Minimum of 7 and 20 is 7 rooms. | Matched. |
| Grounding | Answer names only the local test hotel and labels data simulated. | Matched. |

## Negative and resilience checks

The isolated suite also verifies missing records, zero rooms, unsupported demo
dates, invalid/reversed dates, malformed provider output, SQL writes and other
unsafe proposals, read-only connection enforcement, model/provider failures,
timeouts, network failures, and ungrounded answers. Frontend behavior is
verified separately against the running local FastAPI service: the assistant
shows a loading state, clear local/provider errors, and server-returned stay
cards without exposing an API key.

## Live result

On October 13, 2026, one user-authorized request to the configured
`nvidia/nemotron-3-ultra-550b-a55b:free` model completed with HTTP `200` and
`status: success`. There was no retry.

| Stage | Observed result |
| --- | --- |
| Stage 1 | Nemotron returned a parseable SQL proposal with the two validated date parameters. FastAPI accepted it only because its normalized form matched the exact fixed read-only query. |
| Read-only retrieval | Returned two local records: Oct. 10 — 12,500 cents / 7 rooms; Oct. 11 — 10,000 cents / 20 rooms. |
| Deterministic stay | Checkout was excluded; total was 22,500 cents / `$225.00`; minimum availability was 7 rooms. |
| Stage 2 | Nemotron received the original question and approved local context, then returned a grounded answer accepted by FastAPI. |
| Vue rendering | The assistant first showed a disabled **Sending…** state, then showed the answer, dates, both nightly rows, `$225.00`, 7 rooms, and simulated-data labels. |

The saved row's `hotel_name` is null, so the accepted answer said “saved local
hotel” and the card said “Saved hotel name unavailable.” This preserves the
stored record rather than inventing a hotel name.
