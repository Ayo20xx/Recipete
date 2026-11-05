# Recipete API

Recipete is a FastAPI backend for recipe search and details, user authentication,
saved recipes, reviews, and notifications. The API is versioned under
`/api/v1`.

## Requirements

- Python 3.12 or newer
- Docker (optional)

## Local setup

From the repository root, create a virtual environment and install the
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the repository root:

```dotenv
APP_NAME=Recipete API
ENVIRONMENT=development
DEBUG=true
DATABASE_URL=sqlite+aiosqlite:///./app.db
SECRET=replace-this-with-at-least-32-random-bytes
# Optional:
# GOOGLE_WEB_CLIENT_ID=
# MEALDB_API_KEY=
```

Start the API from the repository root. The backend package currently lives in
the `Backend ` directory (including the trailing space), so add it to
`PYTHONPATH`:

```bash
PYTHONPATH="Backend " uvicorn app.main:app --reload
```

The interactive API documentation is available at
<http://127.0.0.1:8000/docs>, and the OpenAPI schema is at
<http://127.0.0.1:8000/openapi.json>.

## Database migrations

With the same environment variables configured in `.env`, apply migrations
from the repository root:

```bash
PYTHONPATH="Backend " alembic upgrade head
```

## Tests

The API tests use Python's built-in `unittest` runner and FastAPI's test client:

```bash
PYTHONPATH="Backend " python -m unittest discover -s tests -v
```

## Docker

Build the image from the repository root:

```bash
docker build -t recipete-api .
```

Start it with the required settings and a persistent SQLite volume:

```bash
docker run --rm -p 8000:8000 \
  -e APP_NAME="Recipete API" \
  -e ENVIRONMENT=production \
  -e SECRET="replace-this-with-at-least-32-random-bytes" \
  -e DATABASE_URL="sqlite+aiosqlite:////data/recipete.db" \
  -v recipete-data:/data \
  recipete-api
```

Apply database migrations before using the API:

```bash
docker run --rm \
  -e APP_NAME="Recipete API" \
  -e ENVIRONMENT=production \
  -e SECRET="replace-this-with-at-least-32-random-bytes" \
  -e DATABASE_URL="sqlite+aiosqlite:////data/recipete.db" \
  -v recipete-data:/data \
  recipete-api alembic upgrade head
```

Do not use the example secret in production. Supply a securely generated value
of at least 32 bytes.
