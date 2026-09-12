# Vue frontend

This Part 1 Vue/Vite frontend calls the local FastAPI search endpoint and renders matching hotels with their available stays in a plain table.

- `src/App.vue` contains the search interface and no-results message.
- `src/main.js` starts the Vue application.
- `src/style.css` provides intentionally simple form and table styling.
- `package.json` defines the Vue/Vite development commands.

The frontend does not contain hotel result data. FastAPI reads the instructor-supplied CSV files and returns matching records. No SQLite CRUD, booking, authentication, payment, or external API integration is included.
