# Local Travel Booking Application — Part 1

## Repository and commit

- Configured GitHub repository: [clarissaalessi1-creator/travelbooking-app](https://github.com/clarissaalessi1-creator/travelbooking-app)
- The previous local checkpoint commit is [`be143a548fff7623e1e473ce02a9a63350fac8fd`](https://github.com/clarissaalessi1-creator/travelbooking-app/commit/be143a548fff7623e1e473ce02a9a63350fac8fd). It predates the Vue + FastAPI CSV-search conversion and does not represent the current uncommitted changes.

Repository materials: [README](README.md), [AGENTS instructions](AGENTS.md), [design note](docs/design.md), [Part 1 prompt](prompts/01-project-plan.md), [future Part 2 prompt](prompts/02-backend-build.md), [current handoff](handoffs/current.md), and [evidence log](docs/evidence-log.md).

## Implementation

Part 1 implements a Vue/Vite hotel-name search that calls a local Python FastAPI endpoint. FastAPI reads the instructor-supplied [hotels CSV](data/hotels.csv) and [trips CSV](data/trips.csv), joins rows using `hotel_id`, and returns matching hotels with their available stays. Vue renders the returned records in a plain table and displays a clear no-results message when appropriate.

The project does not implement SQLite CRUD, booking, authentication, payments, or external APIs.

Observable Expedia reference screenshots: [search](docs/reference-images/expedia-search.png) and [trips](docs/reference-images/expedia-trips.png). They are reference material only, not copied code or an exact interface reproduction.

## Verification

Source and CSV schemas were inspected. Automated FastAPI HTTP checks passed for the successful and no-results searches, and a temporary Vue/Vite production build passed. Manual browser verification remains required:

- Successful test: search `Harbor Lantern Hotel`; expect `H001` and two available stays.
- No-results test: search `Moonlight Palace Hotel`; expect the clear no-results message.

Expected and observed results, plus screenshot requirements, are recorded in the [evidence log](docs/evidence-log.md). No manual browser verification is claimed before the student performs it.

## Project context and next steps

The repository is a Part 1 Vue + FastAPI + CSV search application. After manually verifying the two searches and recording observations, the student may create a new Part 1 checkpoint if authorized. Part 2 SQLite CRUD is explicitly out of scope until authorized.
