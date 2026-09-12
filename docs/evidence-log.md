# Part 1 Evidence Log

| Major instruction/decision | Resulting change | Manual review/check | Decision | Remaining limitation |
| --- | --- | --- | --- | --- |
| Set up, do not fully implement | Initially created the requested folders, documentation, placeholder readmes, ignore file, and JSON store; a later Part 1 change added the basic static search prototype. | Review the file tree to confirm the static frontend exists and no Flask backend source files exist. | Keep booking implementation deferred to Part 2. | No runnable booking application exists. |
| Use HTML/CSS/JavaScript and Flask | Documented the planned division between browser frontend and Flask API; the browser-only search prototype uses HTML/CSS/JavaScript. | Read `README.md` and `docs/design.md` for consistent architecture. | Use Flask for the API in Part 2. | The Flask backend is not implemented. |
| Use HTTP JSON communication | Documented `fetch()` and the four planned API endpoints. | Verify endpoint names are identical across planning files. | Keep API design REST-style and small. | Requests/responses have not been exercised. |
| Persist to local JSON | Initialized `data/bookings.json` to an empty array and documented on-disk persistence. | Confirm the file contains valid `[]`. | Use the JSON file rather than a database for course-project scope. | No read/write code yet; restart persistence is not tested. |
| Define booking flows and failures | Recorded both flows, Mermaid diagrams, responsible layers, empty states, and failure states. | Read `docs/design.md`; verify listed required failures are present. | Treat validation and error handling as backend/frontend responsibilities in Part 2. | Behaviors are design commitments only. |
| Provide future-agent guidance | Added `AGENTS.md`, Part 2 backend prompt, and handoff note. | Review that all instructions preserve synthetic-only, no-payment, no-auth constraints. | Keep future work narrowly scoped. | Guidance does not replace implementation review. |
| Add a starter hotel search | Created a basic static frontend with three synthetic hotel records, a hotel-name search field, result count, and simple table. | `frontend/app.js` passed a syntax check and source-level checks for all, one, and zero matching results. | Keep this browser-only prototype intentionally separate from the planned backend and booking flows. | No browser test has been recorded; no API, booking, or persistence behavior exists. |

## AI assistance disclosure

AI assisted with converting the supplied assignment requirements into the repository structure, planning documents, prompts, future-agent guidance, and the basic static search prototype. The frontend script received syntax and source-level filtering checks, but no browser testing or end-to-end frontend/backend execution has occurred. The student should manually review all files and is responsible for the final submission.
