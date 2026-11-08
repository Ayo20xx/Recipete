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

`APP_NAME` defaults to `Recipete`; `ENVIRONMENT`, `DATABASE_URL`, and `SECRET`
must be configured.

Start the API from the repository root, adding the backend package to
`PYTHONPATH`:

```bash
PYTHONPATH=backend uvicorn app.main:app --reload
```

The interactive API documentation is available at
<http://127.0.0.1:8000/docs>, and the OpenAPI schema is at
<http://127.0.0.1:8000/openapi.json>.

For the mobile team's endpoint guide, see [MOBILE_API.md](./MOBILE_API.md).

## Mobile authentication

`POST /api/v1/register` accepts `email`, `password`, and `name`. Registration,
password login, and Google login return an access token and a refresh token.
Send the access token as a bearer token for authenticated API requests.

Access tokens expire after 15 minutes; refresh tokens expire after 30 days.
Send the refresh token to
`POST /api/v1/refresh` to rotate it and receive a new token pair. The old
refresh token becomes invalid after use. Send it to `POST /api/v1/logout` to
revoke it when signing out. Store refresh tokens in the mobile platform's
secure storage.

Recipe search/details, reviews, and notifications are registered as separate
API route groups; existing review and notification URL paths remain unchanged.

## Database migrations

With the same environment variables configured in `.env`, apply migrations
from the repository root:

```bash
PYTHONPATH=backend alembic upgrade head
```

## Tests

The API tests use Python's built-in `unittest` runner and FastAPI's test client:

```bash
PYTHONPATH=backend python -m unittest discover -s tests -v
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

## Deploy to Render

1. Push this repository to GitHub.
2. In Render, choose **New → Blueprint**, connect the repository, and deploy
   the included `render.yaml`.
3. After the first deploy, copy the service URL from the Render dashboard. The
   API docs are available at `<service-url>/docs`.
4. To allow a browser frontend to call the API, add a `CORS_ORIGINS` environment
   variable in Render with the frontend's exact origin, including scheme and
   port if present. For multiple origins, separate them with commas.

The Blueprint uses SQLite on Render's temporary filesystem for a quick demo.
That database can be lost when the service restarts or redeploys. For persistent
data, attach a Render persistent disk mounted at `/var/data`, then set
`DATABASE_URL` to `sqlite+aiosqlite:////var/data/recipete.db`. Persistent disks
require a paid Render service plan. The container applies Alembic migrations
before starting the API. Render PostgreSQL connection URLs using `postgres://`
or `postgresql://` are automatically configured with the async PostgreSQL driver.
