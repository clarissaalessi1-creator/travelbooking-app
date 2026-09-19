# Vue frontend

This Vue/Vite interface preserves the hotel search and adds the Part 2 booking workflow. It fetches all displayed travelers, search results, and booking history from FastAPI; the backend serves the data from SQLite.

- `src/App.vue` contains the traveler selector, hotel search, trip Book buttons, booking history, cancellation, and test-deletion controls.
- `src/main.js` starts the Vue application.
- `src/style.css` provides intentionally simple form and table styling.
- `package.json` defines the Vue/Vite development commands.

The frontend does not hard-code hotel, trip, traveler, or booking records. Booking state is refreshed from FastAPI after each create, cancel, or delete action and again when the browser reloads. Delete (test) is displayed only for application-created bookings; the six instructor bookings are protected by the backend. Authentication, payments, and external API integration are not included.
