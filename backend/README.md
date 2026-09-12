# FastAPI backend

This Part 1 backend provides `GET /api/search?hotel_name=<name>`.

`main.py` reads `data/hotels.csv` and `data/trips.csv`, joins the records on `hotel_id`, and returns matching hotels with their available stays as JSON. `requirements.txt` lists the FastAPI and Uvicorn dependencies.

No SQLite CRUD, booking creation, authentication, payment handling, or external API integration is included.
