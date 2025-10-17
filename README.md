# Budget Planner

A simple Flask budgeting app that records monthly income and bills using an SQLite database. The interface is intentionally minimal and spreadsheet-like for quick entry and review. The database connection string is compatible with SQLite today and can be pointed at PostgreSQL in the future.

## Getting started

### Requirements

- Python 3.10+
- `pip`

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Running the app

```bash
flask --app app run --debug
```

By default the application stores data in `budget.db` using SQLite. To switch to PostgreSQL later, set the `DATABASE_URL` environment variable to the appropriate SQLAlchemy connection string.

## Project structure

```
app.py            # Flask application factory and routes
templates/        # HTML templates
static/           # Stylesheets and other static assets
budget.db         # SQLite database (created on first run)
```
