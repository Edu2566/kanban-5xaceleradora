# Kanban Backend

This project provides a simple Kanban style API written with Flask. The service is
designed to be used together with Chatwoot so agents can manage deals directly
from conversations. Below you will find instructions for running the project and
examples of how to interact with the API.

## Setup

1. Clone the repository and install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure the database by setting the `DATABASE_URL` environment variable. By
default the Docker setup uses a local Postgres instance. For local testing you
can skip Docker entirely and rely on SQLite, which is the default when no
`DATABASE_URL` is provided:

```
DATABASE_URL=postgresql://kanban:kanban@db:5432/kanban  # Postgres via Docker
# or
DATABASE_URL=sqlite:///app.db                          # Local SQLite file
```

## Running with Docker

The easiest way to start the service is via Docker Compose:

```bash
docker-compose up --build
```

This command builds the image, starts a Postgres container and exposes the API on
`http://localhost:5000`.

### Applying migrations

After the containers are running apply the database migrations:

```bash
docker-compose exec backend flask db upgrade
```

This will create all required tables in the Postgres database.

### Using SQLite for testing

You can run the API directly with SQLite without Docker. Simply ensure no
`DATABASE_URL` is set (or set it to `sqlite:///app.db`), run the migrations and
start the server:

```bash
export DATABASE_URL=sqlite:///app.db
flask db upgrade
python run.py
```

The commands above will create an `app.db` file in the project directory and run
the API locally on `http://localhost:5000`.

## API usage

### Obtaining an API token via Chatwoot

Chatwoot can call the `/auth/webhook` endpoint when an agent signs in. The
endpoint now expects the required fields as query parameters:

```text
account_id
user_id
user_email
user_name
```

The response contains a token that should be stored as a Chatwoot attribute so it
can be used for subsequent API calls:

```bash
curl "http://localhost:5000/auth/webhook?account_id=1&user_id=10&user_email=agent@example.com&user_name=Agent%20Smith"
```

Response:

```json
{"token": "<generated-token>"}
```

### Working with pipelines

Include the token in the `X-API-Key` header to authenticate. Below is a minimal
example of creating and listing pipelines:

```bash
# create a pipeline
curl -X POST http://localhost:5000/pipelines \
     -H 'Content-Type: application/json' \
     -H 'X-API-Key: <generated-token>' \
     -d '{"name": "Sales"}'

# list pipelines
curl -H 'X-API-Key: <generated-token>' http://localhost:5000/pipelines
```

For more endpoints see the source in `app/pipelines/__init__.py`.

## Running tests

The project uses `pytest`. You can run the unit and integration tests with:

```bash
pytest
```

