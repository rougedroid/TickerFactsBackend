# TickerFacts

TickerFacts is a portfolio-grade backend application designed to surface financial insights and company filings through a FastAPI-based API. This repository is published publicly only for portfolio purposes: to demonstrate the project, show proof of work, and help others verify the implementation. It is not licensed for reuse without explicit written permission.

## What is TickerFacts?

TickerFacts combines real-time market data, SEC filings, and company metadata into a single backend service. It is structured for extendability, with separate modules for authentication, company data, filings, metrics, and real-time data streaming.

## Key Features

- FastAPI backend with versioned API routing
- JWT-based authentication and secure session management
- Company and filing endpoints
- Real-time data pipeline integration using Redis and Finnhub
- Database migrations powered by Alembic
- Environment-based configuration for development and deployment

## Repository Structure

- `app/`: main FastAPI application and backend domain logic
  - `api/`: API route definitions
  - `auth/`: authentication and authorization logic
  - `core/`: application configuration and logging
  - `db/`: database initialization and session handling
  - `models/`: SQLAlchemy ORM models
  - `repositories/`: data access layer
  - `schemas/`: request/response models
  - `realtime/`: real-time integration with Redis and Finnhub
  - `services/`: business logic
- `pipeline/`: data processing and SEC filing ingestion pipeline
- `alembic/`: database migration configuration and scripts
- `run.py`: entrypoint for running the FastAPI app
- `requirements.txt`: Python dependencies
- `.gitignore`: ignored files and directories
- `LICENSE`: license for this repository
- `.env.example`: example environment variable configuration

## Prerequisites

- Python 3.11+ (or compatible Python 3.x version)
- `pip` installed
- PostgreSQL or compatible database for `DATABASE_URL`
- Redis instance for real-time messaging
- Finnhub API key if using live market data

## Setup

1. Clone the repository.
2. Create and activate a virtual environment.

```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies.

```bash
pip install -r requirements.txt
```

4. Copy `.env.example` to `.env` and populate the values.

```bash
cp .env.example .env
```

5. Configure your `.env` values.

## Environment Variables

Use `.env.example` as a starting point. Required variables include:

- `APP_NAME`
- `APP_VERSION`
- `HOST`
- `PORT`
- `DEBUG`
- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `JWT_ALGORITHM`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `REFRESH_TOKEN_EXPIRE_DAYS`
- `DATABASE_URL`
- `SYNC_DATABASE_URL`
- `GOOGLE_CLIENT_ID`
- `PIPELINE_API_KEY`
- `SEC_USER_AGENT`
- `INTERNAL_API_KEY`
- `API_URL`
- `REDIS_URL`
- `FINNHUB_API_KEY`

## Running TickerFacts

Run the server using `run.py`:

```bash
python run.py
```

Or start directly with Uvicorn:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000` by default.

## Database Migrations

This project uses Alembic for database migrations.

```bash
alembic upgrade head
```

## Notes for Portfolio / Proof of Work

TickerFacts is intentionally made public to demonstrate the application architecture, code quality, and technical capabilities. It is shared as proof of work and portfolio material only. No one else may use, copy, distribute, or adapt this code without the express written permission of the project owner.

## License

TickerFacts is licensed under a custom portfolio license. See `LICENSE` for full terms.
