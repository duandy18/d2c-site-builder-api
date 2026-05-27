PYTHON ?= python3
VENV_PYTHON ?= .venv/bin/python3

D2C_SITE_BUILDER_ENV ?= local
HOST ?= 0.0.0.0
PORT ?= 8035
PID_FILE ?= /tmp/d2c_site_builder_api_8035.pid
LOG_FILE ?= /tmp/d2c_site_builder_api_8035.log
HEALTH_URL ?= http://127.0.0.1:$(PORT)/system/health

D2C_SITE_BUILDER_DB_PORT ?= 55435
D2C_SITE_BUILDER_DB_USER ?= d2c_site_builder
D2C_SITE_BUILDER_DB_PASSWORD ?= d2c_site_builder
D2C_SITE_BUILDER_DB_NAME ?= d2c_site_builder
D2C_SITE_BUILDER_TEST_DB_NAME ?= d2c_site_builder_test

D2C_SITE_BUILDER_DEV_DB_DSN ?= postgresql+psycopg://$(D2C_SITE_BUILDER_DB_USER):$(D2C_SITE_BUILDER_DB_PASSWORD)@127.0.0.1:$(D2C_SITE_BUILDER_DB_PORT)/$(D2C_SITE_BUILDER_DB_NAME)
D2C_SITE_BUILDER_DEV_TEST_DB_DSN ?= postgresql+psycopg://$(D2C_SITE_BUILDER_DB_USER):$(D2C_SITE_BUILDER_DB_PASSWORD)@127.0.0.1:$(D2C_SITE_BUILDER_DB_PORT)/$(D2C_SITE_BUILDER_TEST_DB_NAME)

PSQL_DEV_URL ?= postgresql://$(D2C_SITE_BUILDER_DB_USER):$(D2C_SITE_BUILDER_DB_PASSWORD)@127.0.0.1:$(D2C_SITE_BUILDER_DB_PORT)/$(D2C_SITE_BUILDER_DB_NAME)
PSQL_TEST_URL ?= postgresql://$(D2C_SITE_BUILDER_DB_USER):$(D2C_SITE_BUILDER_DB_PASSWORD)@127.0.0.1:$(D2C_SITE_BUILDER_DB_PORT)/$(D2C_SITE_BUILDER_TEST_DB_NAME)

DEV_ENV := D2C_SITE_BUILDER_ENVIRONMENT="$(D2C_SITE_BUILDER_ENV)" D2C_SITE_BUILDER_DATABASE_URL="$(D2C_SITE_BUILDER_DEV_DB_DSN)" D2C_SITE_BUILDER_TEST_DATABASE_URL="$(D2C_SITE_BUILDER_DEV_TEST_DB_DSN)" PYTHONPATH=.
TEST_ENV := D2C_SITE_BUILDER_ENVIRONMENT=test D2C_SITE_BUILDER_DATABASE_URL="$(D2C_SITE_BUILDER_DEV_TEST_DB_DSN)" D2C_SITE_BUILDER_TEST_DATABASE_URL="$(D2C_SITE_BUILDER_DEV_TEST_DB_DSN)" PYTHONPATH=.

TESTS ?= tests
PYTEST_ARGS ?=

.PHONY: clean-pyc install lint test routes openapi check
.PHONY: upgrade-dev upgrade-test alembic-check alembic-current alembic-history revision
.PHONY: dev-db-up dev-db-wait dev-db-down dev-db-reset dev-db-smoke
.PHONY: uvicorn uvicorn-up uvicorn-down uvicorn-restart uvicorn-status uvicorn-logs
.PHONY: up down restart status logs

clean-pyc:
	find . -type d -name "__pycache__" -prune -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

install:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install -U pip
	$(VENV_PYTHON) -m pip install -e ".[dev]"

lint: clean-pyc
	$(VENV_PYTHON) -m ruff check app tests scripts alembic

test: clean-pyc
	$(TEST_ENV) $(VENV_PYTHON) -m pytest $(TESTS) $(PYTEST_ARGS)

routes:
	PYTHONPATH=. $(VENV_PYTHON) scripts/list_routes.py

openapi:
	PYTHONPATH=. $(VENV_PYTHON) scripts/export_openapi.py

check: lint test routes openapi

upgrade-dev:
	$(DEV_ENV) $(VENV_PYTHON) -m alembic upgrade head

upgrade-test:
	$(TEST_ENV) $(VENV_PYTHON) -m alembic upgrade head

alembic-check:
	$(DEV_ENV) $(VENV_PYTHON) -m alembic check

alembic-current:
	$(DEV_ENV) $(VENV_PYTHON) -m alembic current

alembic-history:
	$(DEV_ENV) $(VENV_PYTHON) -m alembic history

revision:
	$(DEV_ENV) $(VENV_PYTHON) -m alembic revision --autogenerate -m "$(MSG)"

dev-db-up:
	D2C_SITE_BUILDER_DB_PORT="$(D2C_SITE_BUILDER_DB_PORT)" docker compose up -d site-builder-postgres

dev-db-wait:
	@for i in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15; do \
	  if docker exec d2c_site_builder_postgres pg_isready -U "$(D2C_SITE_BUILDER_DB_USER)" -d "$(D2C_SITE_BUILDER_DB_NAME)" >/dev/null 2>&1; then \
	    echo "site builder postgres ready on 127.0.0.1:$(D2C_SITE_BUILDER_DB_PORT)"; \
	    break; \
	  fi; \
	  echo "waiting site builder postgres attempt $$i"; \
	  sleep 1; \
	done

dev-db-down:
	D2C_SITE_BUILDER_DB_PORT="$(D2C_SITE_BUILDER_DB_PORT)" docker compose down

dev-db-reset: dev-db-up dev-db-wait
	@echo "recreating dev/test databases"
	@docker exec d2c_site_builder_postgres psql -U "$(D2C_SITE_BUILDER_DB_USER)" -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname IN ('$(D2C_SITE_BUILDER_DB_NAME)', '$(D2C_SITE_BUILDER_TEST_DB_NAME)') AND pid <> pg_backend_pid();" >/dev/null
	@docker exec d2c_site_builder_postgres psql -U "$(D2C_SITE_BUILDER_DB_USER)" -d postgres -c "DROP DATABASE IF EXISTS $(D2C_SITE_BUILDER_DB_NAME);"
	@docker exec d2c_site_builder_postgres psql -U "$(D2C_SITE_BUILDER_DB_USER)" -d postgres -c "DROP DATABASE IF EXISTS $(D2C_SITE_BUILDER_TEST_DB_NAME);"
	@docker exec d2c_site_builder_postgres psql -U "$(D2C_SITE_BUILDER_DB_USER)" -d postgres -c "CREATE DATABASE $(D2C_SITE_BUILDER_DB_NAME);"
	@docker exec d2c_site_builder_postgres psql -U "$(D2C_SITE_BUILDER_DB_USER)" -d postgres -c "CREATE DATABASE $(D2C_SITE_BUILDER_TEST_DB_NAME);"
	$(MAKE) upgrade-dev
	$(MAKE) upgrade-test

dev-db-smoke:
	@echo "dev db:"
	@psql -P pager=off "$(PSQL_DEV_URL)" -c "SELECT current_database(), current_user;"
	@echo "test db:"
	@psql -P pager=off "$(PSQL_TEST_URL)" -c "SELECT current_database(), current_user;"

uvicorn:
	PYTHONPATH=. $(VENV_PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT)

uvicorn-up:
	@if [ -f "$(PID_FILE)" ] && kill -0 "$$(cat $(PID_FILE))" 2>/dev/null; then \
	  echo "d2c-site-builder-api already running: $(HEALTH_URL)"; \
	else \
	  echo "starting d2c-site-builder-api on $(HOST):$(PORT)"; \
	  nohup env PYTHONPATH=. D2C_SITE_BUILDER_API_PORT="$(PORT)" D2C_SITE_BUILDER_DATABASE_URL="$(D2C_SITE_BUILDER_DEV_DB_DSN)" \
	    $(VENV_PYTHON) -m uvicorn app.main:app --host $(HOST) --port $(PORT) >"$(LOG_FILE)" 2>&1 & \
	  echo $$! > "$(PID_FILE)"; \
	  for i in 1 2 3 4 5 6 7 8 9 10; do \
	    if curl -fsS "$(HEALTH_URL)" >/dev/null 2>&1; then \
	      echo "d2c-site-builder-api ready: $(HEALTH_URL)"; \
	      break; \
	    fi; \
	    echo "waiting d2c-site-builder-api attempt $$i"; \
	    sleep 1; \
	  done; \
	fi

uvicorn-down:
	@if [ -f "$(PID_FILE)" ]; then \
	  OLD_PID="$$(cat $(PID_FILE))"; \
	  echo "stopping d2c-site-builder-api pid: $$OLD_PID"; \
	  kill "$$OLD_PID" 2>/dev/null || true; \
	  for i in 1 2 3 4 5; do \
	    if kill -0 "$$OLD_PID" 2>/dev/null; then \
	      sleep 1; \
	    else \
	      break; \
	    fi; \
	  done; \
	  if kill -0 "$$OLD_PID" 2>/dev/null; then \
	    echo "force stopping d2c-site-builder-api pid: $$OLD_PID"; \
	    kill -9 "$$OLD_PID" 2>/dev/null || true; \
	  fi; \
	  rm -f "$(PID_FILE)"; \
	fi
	@echo "d2c-site-builder-api stopped if it was running"

uvicorn-restart: uvicorn-down uvicorn-up

uvicorn-status:
	@if [ -f "$(PID_FILE)" ] && kill -0 "$$(cat $(PID_FILE))" 2>/dev/null; then \
	  echo "running pid=$$(cat $(PID_FILE))"; \
	  curl -fsS "$(HEALTH_URL)" || true; \
	else \
	  echo "not running"; \
	fi

uvicorn-logs:
	@if [ -f "$(LOG_FILE)" ]; then \
	  tail -n 120 "$(LOG_FILE)"; \
	else \
	  echo "no log file: $(LOG_FILE)"; \
	fi

up: uvicorn-up
down: uvicorn-down
restart: uvicorn-restart
status: uvicorn-status
logs: uvicorn-logs
