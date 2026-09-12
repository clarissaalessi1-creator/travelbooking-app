# Part 1 Evidence Log

| Major instruction/decision | Resulting change | Manual review/check | Decision | Remaining limitation |
| --- | --- | --- | --- | --- |
| Use Vue + FastAPI | Added Vue/Vite frontend files and FastAPI backend files in separate folders. | A temporary Vue/Vite production build passed; inspect `frontend/` and `backend/` in VS Code. | Keep browser UI and API separated. | Project-local dependency installation and browser testing remain pending. |
| Use instructor CSV files | Backend reads `data/hotels.csv` and `data/trips.csv` with UTF-8 BOM support. | Inspect the actual headers and values in both CSV files. | Do not hard-code result data in Vue. | CSV data is read at request time; no database is used. |
| Join hotels and stays | Backend groups trips by `hotel_id` and returns `available_stays` for each matching hotel. | Automated FastAPI HTTP check passed: `H001` returned `T001` and `T009`; inspect `backend/main.py` and run the successful browser search. | Use `hotel_id` as the only join key. | No SQLite schema or CRUD exists. |
| Successful browser search | Search for `Harbor Lantern Hotel`. | Expected: one hotel, `H001`, with *Boston Harbor Weekend* and *Boston Autumn Weekend*. Observed: **Pending your manual browser test.** | Record the observed result after testing. | Must be performed with both local services running. |
| No-results browser search | Search for `Moonlight Palace Hotel`. | Expected: `No hotels and available stays found for “Moonlight Palace Hotel”.` Observed: **Pending your manual browser test.** | Record the observed result after testing. | Must be performed with both local services running. |
| Preserve Part 2 boundary | Excluded SQLite CRUD, booking, authentication, payment, and external APIs. | Confirm no database files or CRUD routes were added. | Keep Part 2 out of this checkpoint. | Future work requires explicit authorization. |

## Screenshot checklist

After the two manual browser tests, capture:

1. The successful `Harbor Lantern Hotel` search showing the search term, table headings, `H001`, and both available stays.
2. The `Moonlight Palace Hotel` no-results search showing the search term and clear no-results message.
3. Optional but useful: VS Code showing `frontend/src/App.vue`, `backend/main.py`, and the two CSV files in the Explorer.

Store any new submission screenshots only if your assignment requires them; do not overwrite the existing Expedia reference images.

## AI assistance disclosure

AI assisted with planning, documentation, and implementation under student direction. Manual VS Code inspection and browser testing remain the student's responsibility, and no manual browser result is claimed until the observed-result fields above are completed.
