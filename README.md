# D2C Site Builder API

Internal Site Builder service for D2C storefront page planning, publishing, and runtime contracts.

## Stage 1 Scope

This bootstrap stage includes:

- FastAPI app skeleton
- Health endpoints
- Alembic baseline
- Lint/test/openapi route checks
- GitHub CI
- Local database helper commands for the shared local PostgreSQL service

It intentionally does not migrate any `client_presentation` business logic yet.

## Local database

Site Builder uses the shared local PostgreSQL port used by the other independent systems:

    Host: 127.0.0.1
    Port: 5433
    Dev database: d2c_site_builder
    Test database: d2c_site_builder_test

Create or reset local databases:

    make dev-db-create
    make dev-db-smoke

Reset only when you intentionally want to drop and recreate the Site Builder dev/test databases:

    make dev-db-reset

By default, local database creation uses the existing local WMS admin role on the shared 5433 PostgreSQL service:

    PSQL_ADMIN_URL=postgresql://wms:wms@127.0.0.1:5433/wms

If your local admin role differs, override `PSQL_ADMIN_URL`:

    make dev-db-create PSQL_ADMIN_URL="postgresql://<admin>:<password>@127.0.0.1:5433/<admin_db>"

## Local setup

Primary setup commands:

    make install
    make dev-db-create
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
    PostgreSQL: 5433

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
