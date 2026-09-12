# Local Travel Booking Application

This repository is the **Part 1 planning and setup checkpoint** for a small, local hotel-booking application inspired by [Expedia](https://www.expedia.com/). It includes a very small static hotel-search prototype, not a working booking application. Part 2 will implement the planned Flask API and booking features.

## Purpose and scope

The application will use **synthetic hotel and traveler data only** and will support hotel bookings only. It intentionally excludes real payments, authentication, real travel-provider APIs, and any private Expedia information.

### Required future flows

1. **Make a booking:** a traveler views synthetic hotel results, selects a hotel, enters traveler and date details, and submits the booking. The backend will validate the request, calculate the total, create a simulated confirmation number, save the booking, and return a confirmation view.
2. **Review booking history:** a traveler opens booking history, receives saved bookings from the backend, selects one, and views its full details.

## Planned architecture

| Layer | Planned responsibility |
| --- | --- |
| Interface | HTML/CSS/JavaScript screens for hotel selection, booking entry, confirmation, and history. |
| Logic | Flask API validates requests, calculates prices, and generates booking identifiers and confirmation numbers. |
| Data | Synthetic hotel records plus traveler and booking JSON objects. |
| Persistence | `data/bookings.json` stores booking records on disk. |

The browser frontend will call the Flask backend through HTTP `fetch()` requests with JSON request and response bodies. The backend will read and write the local JSON file. Consequently, booking history is planned to survive browser/frontend/backend restarts, but deleting `data/bookings.json` will erase it.

## Technology choices

| Technology | Role | Why it was chosen |
| --- | --- | --- |
| HTML | Page structure | Simple, direct markup for a small course project. |
| CSS | Presentation | Keeps layout and visual styling understandable and separate from behavior. |
| JavaScript | Browser behavior and `fetch()` calls | Supports interactive screens and standard HTTP/JSON communication without a frontend framework. |
| Python Flask | Backend API | Lightweight framework suited to a small REST-style service. |
| JSON file | Local persistence | Provides durable, inspectable storage without database setup complexity. |

## Current repository state

A basic standalone frontend prototype exists in `frontend/`: `index.html`, `styles.css`, and `app.js`. It displays three synthetic hotels in a simple table and filters them by hotel name when the Search button is used. It has no backend connection, API routes, booking behavior, persistence, booking history, or booking form. No `app.py` or `requirements.txt` exists, and the planned end-to-end application has not been browser-tested.

## Planned structure

```text
README.md
AGENTS.md
.gitignore
frontend/
    README.md
    index.html
    styles.css
    app.js
backend/
    README.md
data/
    bookings.json
docs/
    design.md
    evidence-log.md
    reference-images/
        expedia-search.png
        expedia-trips.png
handoffs/
    current.md
prompts/
    01-project-plan.md
    02-backend-build.md
```

- `README.md` explains the project and its planned architecture.
- `AGENTS.md` gives project-specific instructions to future coding agents.
- `.gitignore` prevents common local/generated files from being tracked.
- `frontend/` contains the implemented basic hotel-search prototype; its booking interface and API integration remain planned.
- `backend/` is reserved for the future Flask service.
- `data/bookings.json` is the initialized on-disk booking store.
- `docs/` contains the detailed design, evidence log, and `reference-images/`.
- `docs/reference-images/` contains Expedia screenshots used as observable visual references for the planned interface design; they are not copied code or an exact interface specification.
- `handoffs/current.md` records the honest implementation handoff state.
- `prompts/` preserves the planning request and a Part 2 backend build prompt.

## Part 2 remaining work

Part 2 must build the Flask backend, connect the frontend to the planned API, add booking and confirmation pages, implement booking history/details, add validation, price calculation, confirmation-number generation, JSON-file persistence, and perform proportionate testing/manual verification.

## AI assistance disclosure

AI was used to help organize this Part 1 repository scaffold and draft its planning documentation from the assignment requirements. The repository owner should review the material, confirm it reflects the assignment, and remain responsible for all submitted work.
