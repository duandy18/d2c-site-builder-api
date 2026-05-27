# D2C Site Builder API

Internal Site Builder service for D2C storefront page planning, publishing, and runtime contracts.

## Stage 1 Scope

This bootstrap stage includes:

- FastAPI app skeleton
- Health endpoints
- Alembic baseline
- Lint/test/openapi route checks
- GitHub CI
- Local PostgreSQL helpers through Docker Compose

It intentionally does not migrate any `client_presentation` business logic yet.

## Local setup

Primary setup commands:

    make install
    make dev-db-up
    make dev-db-wait
    make dev-db-reset
    make dev-db-smoke
    make check
    make alembic-check

## Local run

Primary server commands:

    make uvicorn-up
    make uvicorn-status
    make uvicorn-logs
    make uvicorn-restart
    make uvicorn-down

Short aliases are also available:

    make up
    make status
    make logs
    make restart
    make down

Default local ports:

    API: 8035
    PostgreSQL: 55435

## Core commands

    make lint
    make test
    make routes
    make openapi
    make check
    make upgrade-dev
    make alembic-check
    make alembic-current
    make revision MSG="short_message"
