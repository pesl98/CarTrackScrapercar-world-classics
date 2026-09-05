# CarWorld Classics Tracker

Flask + SQLite app that scrapes [CarWorld Classics](https://www.carworldclassics.com/aanbod) inventory, tracks price changes, and flags cars as sold when they disappear from the listing pages.

The live inventory source is **https://www.carworldclassics.com/aanbod** (paginated as `/aanbod?page=N`).

## Install

Python 3.11+ is required. Dependencies are declared in `pyproject.toml`.

With [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

With pip:

```bash
python -m venv .venv
source .venv/bin/activate
pip install .
```

## Initialize the database

The SQLite file `car_tracker.db` is created locally and is **not** committed. Schema comes from `init_db()`:

```bash
python -c "from database import Database; Database().init_db()"
```

Starting the app also calls `init_db()`, so this step is only required if you want the empty database before the first run.

## Run the app

```bash
python app.py
```

The dashboard listens on `http://0.0.0.0:5000`.

- Dashboard: `/`
- Cars API: `/api/cars`
- Stats: `/api/stats`

## Run a scrape

Trigger a scrape from a running app:

```bash
curl -X POST http://localhost:5000/api/scrape
```

Or from the command line (still uses `init_db` if the file is missing):

```bash
python -c "from database import Database; from multi_dealer_scraper import MultiDealerScraper; db = Database(); db.init_db(); MultiDealerScraper(db).scrape_all_dealers()"
```

A background scheduler also scrapes daily at 08:00 and every 6 hours while the app is running.

## Sold / re-list rules

- A listing is marked **sold** only if it is missing from a complete scrape **and** `last_seen` is older than **2 days**.
- If a scrape returns **0 cars**, or fewer than **70%** of that dealer’s currently active cars, sold-marking is skipped (protects against site outages or HTML changes).
- When a previously sold car **reappears**, `touch_car_seen()` updates `last_seen`, sets `is_sold` back to false, and clears `sold_date`.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Project layout

| Path | Role |
| --- | --- |
| `app.py` | Flask dashboard and API |
| `database.py` | SQLite schema and queries |
| `multi_dealer_scraper.py` | CarWorld Classics scraper |
| `scheduler.py` | Periodic scrape jobs |
