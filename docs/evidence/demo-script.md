# Assignment 2 Part 2 Demonstration Script

Use this script while recording a genuine local demo. Do not promise a provider
result before it appears on screen.

1. Start FastAPI and Vue using the commands in `report.md`. Open
   `http://127.0.0.1:5173/` and briefly show the **Hotel AI Assistant** section.
2. Say: “This assistant answers questions only from saved local hotels. Rates
   and room availability are simulated classroom data.”
3. Show the saved-local result through the existing ZIP search. Point out the
   **Saved locally** label and the stored nightly data. Do not add, remove, or
   edit a hotel during the recording.
4. In the assistant input, enter: `Which saved hotel has rooms from
   2026-10-10 to 2026-10-12?` Then press **Send** once.
5. While waiting, say: “Vue sends the question only to FastAPI. The browser
   never receives the OpenRouter key.” Show the disabled **Sending…** control.
6. If a successful answer appears, say: “The backend accepted a read-only SQL
   proposal, retrieved the two local nightly records, calculated the two-night
   total in integer cents, and checked the minimum rooms available.” Point out
   the two rates, `$225.00` total, and 7-room minimum only if those values are
   visible.
7. If the provider instead fails, show the safe error message and say: “The
   provider result is unavailable; the application did not invent an answer.”
   Stop rather than retrying repeatedly.
8. Enter reversed dates, such as `2026-10-12 to 2026-10-10`, and press **Send**.
   Show the clear invalid-date message. This path does not call the provider.
9. Close by showing `docs/chatbot-verification.md`, the fixed JSON fixture,
   and the test command/result. State that unsafe SQL and provider-error cases
   are isolated mocked tests, not screenshots of a live provider failure.

After recording, replace the placeholder in `report.md` with the accessible
video link and verify that the instructor can open it.
