# Gunpla Price Tool

A web app for querying and managing Gunpla (Gundam model) prices with scraping, wishlist/collection, and sharing features.

## Features

- Multi-region price display (JPY, USD, CNY)
- Auto price conversion
- Wishlist and collection management
- Coupon analysis tools
- Category and keyword search
- Grade-specific scrapers with subcategory detection
- CSV import/export and shareable list links
- Optional user accounts (login/register)

## Quick Start

### 1) Install dependencies

```bash
pip install -r requirements.txt
```

### 2) Run the app

```bash
python app.py
```

### 3) Open in browser

Visit http://localhost:5000

## Project Structure

```
gunpla_price_tool/
├── app.py               # Flask app
├── models.py            # Database models
├── config.py            # Config (rates, secrets)
├── requirements.txt     # Python dependencies
├── docs/                # Usage and maintenance docs
├── scripts/             # Tooling scripts
│   ├── scrapers/         # Grade-specific scrapers
│   ├── migrations/       # Database migrations
│   ├── debug/            # Debug scripts
│   └── examples/         # Examples
├── templates/           # HTML templates
└── static/              # Static assets
```

## Database

SQLite is used by default (file: `gunpla.db`). Tables are created on first run.

For production, use PostgreSQL (Render provides a free tier).

## Default Data (CSV Seed)

If the database is empty, the app will load `data/seed_gunpla.csv` on startup.
Use `scripts/migrations/export_gunpla_to_csv.py` to regenerate the seed from local `gunpla.db`.

## Scrapers

Scrapers live in `scripts/scrapers/` and target specific grades:

- RG, PG, MG
- HGUC, HGGTO, HGBF/BD
- 30MM, SDCS, FM, HGIBO, EG

Each scraper filters out non-target grades and non-priced items.

## User Accounts and Sharing

- Register/Login/Logout via Flask-Login
- Wishlist and collection are user-specific when logged in
- CSV import/export for lists
- Shareable read-only list links

## Deployment (Render)

This project includes:

- `Procfile` with `gunicorn app:app`
- `requirements.txt` including `gunicorn`

When deploying on Render:

- Build: `pip install -r requirements.txt`
- Start: `gunicorn app:app`
- Set `SECRET_KEY` in environment variables

## Notes

- Exchange rates can be adjusted in `config.py`.
- SQLite data on free hosting may be ephemeral.

