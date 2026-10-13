# Assignment 2 Part 2 Rubric Self-Check

This checklist is based on the revised requirements supplied for this project.
It distinguishes verified work from a recording that still needs student action.

| Requirement | Evidence / status |
| --- | --- |
| Research and early mockup | Complete — `docs/assignment2-chatbot-research.md` and `docs/assignment2-chatbot-early-mockup.svg`. |
| Instructor-approved OpenRouter Nemotron configuration | Complete — backend-only `.env` support and pinned free model identifier; no key is tracked. |
| Two-stage LLM workflow | Complete — SQL proposal, validation/retrieval, then grounded answer in `backend/main.py`. |
| Strict read-only SQL | Complete — exact allowlist, bound parameters, `mode=ro`, `query_only`, authorizer, progress budget, and tests. |
| Saved-hotel / demo-night integration | Complete — only `saved_hotels` and `demo_hotel_nights` are read. |
| Multi-night price and availability logic | Complete — checkout excluded, integer cents, full-night requirement, positive room minimum. |
| Vue interface and states | Complete — keyboard input, Enter/Send, loading, success data card, and safe errors. |
| Fixed JSON sample | Complete — `backend/fixtures/chatbot-availability-fixture.json`. |
| Expected-versus-observed verification | Complete — `docs/chatbot-verification.md`. |
| Automated tests and frontend build | Complete — 40 backend tests passed; Vite production build passed. |
| Genuine local evidence | Complete — `docs/evidence/` screenshots are labeled as local UI captures. |
| Live provider result | Complete once — October 13 HTTP 200 success is documented; no additional provider call was made for evidence. |
| Recorded demo | **Incomplete** — use `docs/evidence/demo-script.md` and replace the video-link placeholder after recording. |
| Final report and AI disclosure | Complete in `report.md`; update it with the real video link before Canvas submission. |
