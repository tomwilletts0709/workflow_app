# Code Context

## Files Retrieved
1. `pyproject.toml` (lines 1-38) - package dependencies, dev tools, pytest and ruff config.
2. `README.md` (lines 1-9) - project scope/status.
3. `compose.yaml` (lines 1-23) - local PostgreSQL/Redis integration services.
4. `.env.example` (lines 1-3) - required runtime env vars.
5. `app/main.py` (lines 1-31) - FastAPI app entrypoint and router registration.
6. `app/core/settings.py` (lines 11-29) - Pydantic settings/API env contract.
7. `app/database/database.py` (lines 11-60) - SQLAlchemy Base, engine, session dependency.
8. `app/core/pagination.py` (lines 7-29) - shared query params dependency used by task/search routers.
9. `app/tasks/router.py` (lines 1-85) - task API surface.
10. `app/projects/router.py` (lines 1-72) - project API surface.
11. `app/jobs/router.py` (lines 1-34) - job API surface.
12. `app/activity/router.py` (lines 1-21) - activity API surface.
13. `app/search/router.py` (lines 1-22) - global search API surface.
14. `app/core/websockets.py` (lines 1-42) - WebSocket manager and `/ws/projects/{project_id}` endpoint.
15. `tests/conftest.py` (lines 1-28) - current database test fixture.
16. `tests/test_main.py` (lines 1-10) - only current test.
17. `migrations/env.py` (lines 1-53) and `migrations/versions/de88712b196e_create_tasks_table.py` (lines 1-41) - Alembic integration.
18. `app/workers.py` (lines 1-35) - Celery integration point.
19. `docs/structure.md` (lines 1-31) - intended module layout, partially stale.

## Key Code

- Entrypoint/API composition: `app/main.py` creates a global `FastAPI()` app, includes routers under `/tasks`, `/jobs`, `/projects`, `/search`, activity routes with no prefix, and WebSockets with no prefix; root health-ish endpoint returns `{"App": "Is Running"}`.
- Settings: `app/core/settings.py` requires `DATABASE_URL`; defaults `REDIS_URL`; has a likely alias bug where `celery_broker_url` reads `CELERY_RESULT_BACKEND` instead of a broker env var.
- Database: `app/database/database.py` instantiates `settings = get_settings()` and `engine = create_engine(...)` at import time. Any import of routers/services that reach `get_db` can require a valid DB URL before tests override anything.
- Shared query params: `app/core/pagination.py` references `SortOrder` in `common_params()` but does not define/import it, and returns `sort_by`/`sort_order` into `CommonParams` which currently only has `page`, `page_size`, `query`.
- WebSocket surface: `app/core/websockets.py` tracks in-memory connections by `project_id`; `broadcast_to_project()` sends JSON to all connections for that project; endpoint path is `/ws/projects/{project_id}`.
- Tests: `tests/test_main.py` imports `app.main` and asserts only root endpoint. `tests/conftest.py` builds SQLite in-memory DB but only imports `app.tasks.models`, so other model tables are not registered for service tests unless imported manually.

## Architecture

FastAPI routers call thin service factories that build SQLAlchemy-backed repos from `get_db`. Models mix SQLAlchemy ORM classes and Pydantic request/response schemas in the same files. Search/tasks share `CommonParamsDependency`. Alembic pulls metadata from `Base`, but currently imports only task models. Celery is intended to process job records against the same database and Redis broker/backend, but the worker module is currently not importable.

Local integration expects PostgreSQL and Redis from `compose.yaml`; `.env.example` provides a Postgres `DATABASE_URL`. Test integration is minimal and currently broken at collection due to import-time app wiring.

## Concrete Findings

- **High severity: test collection is broken.** `pytest` fails importing `app.main` because `app/core/pagination.py:18` references undefined `SortOrder`. This blocks all current validation. Evidence: command `DATABASE_URL=sqlite:// pytest -q` exits 2 with `NameError: name 'SortOrder' is not defined`.
- **High severity: `CommonParams` contract mismatch.** `app/core/pagination.py:20-26` passes `sort_by` and `sort_order` into `CommonParams`, but `CommonParams` only declares `page`, `page_size`, and `query` at lines 7-10. After fixing `SortOrder`, this likely needs either model fields or removal.
- **High severity: Celery worker integration is not importable.** `app/workers.py:4` imports `app.database.databse` (typo), line 8 calls undefined `app_settings()`, and line 14 references nonexistent `settings.celery_result.backend`. Any future background-job work must fix this integration first.
- **Medium severity: job 404 handler returns instead of raises.** `app/jobs/router.py:29-33` returns an `HTTPException` object rather than raising it, likely causing a 200/serialization failure instead of 404.
- **Medium severity: migrations are incomplete/stale.** `migrations/env.py:8` imports only task models, so project/job/activity/etc. metadata is absent from autogenerate. The only revision creates `tasks` with `project_id`/`description` non-null and no foreign key (`migrations/versions/de88712b196e_create_tasks_table.py:22-31`), while current ORM has nullable `project_id`, nullable `description`, and FK to `project.id` (`app/tasks/models.py`).
- **Medium severity: import-time DB engine creation reduces testability.** `app/database/database.py:34-35` creates settings and engine at import time; tests must set `DATABASE_URL` before importing app modules and cannot easily swap engine without dependency overrides.
- **Medium severity: test DB fixture has limited metadata.** `tests/conftest.py:6-7` imports only task models; service/API tests involving projects/jobs/activity/search will need imports/metadata registration and likely FastAPI dependency overrides for `get_db`.
- **Low severity: package/config cleanup.** `pyproject.toml:13` and `pyproject.toml:19` duplicate `redis`; no explicit scripts are defined for app/dev/test commands. README is minimal and docs/structure.md appears stale relative to current files.

## Start Here

Open `app/core/pagination.py` first. It currently prevents importing `app.main`, so no API/test validation can run until its `SortOrder` and `CommonParams` contract are clarified.

## Remaining Clarification Questions

1. What feature/fix is actually requested, and which API surface should be prioritized: tasks, projects, jobs, search, WebSockets, AI, or migrations?
2. Should the project standardize on PostgreSQL-only behavior, or must SQLite in-memory tests be first-class?
3. Are Alembic migrations expected to be authoritative for all current models, or is `Base.metadata.create_all()` acceptable in development/tests?
4. Should background jobs use Celery now, or is the worker module experimental/deferred?
5. What response envelope/pagination/sorting contract is intended for list/search endpoints?
6. Should WebSocket broadcasts be in-memory only, or integrated with Redis/pub-sub for multi-process deployment?

## Supervisor coordination

No supervisor decision requested; scouting was completed without modifying repository source files.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete findings include file paths, line references, and severity labels under 'Concrete Findings'; validation command evidence documents the current pytest collection failure."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "DATABASE_URL=sqlite:// pytest -q",
      "result": "failed",
      "summary": "Pytest collection fails importing app.main because app/core/pagination.py references undefined SortOrder."
    },
    {
      "command": "targeted ls/find/read/grep inspections plus line-numbered awk snippets",
      "result": "passed",
      "summary": "Mapped package config, tests, entrypoints, routers, settings, database, migrations, worker, docs, and compose integration."
    }
  ],
  "validationOutput": [
    "ERROR tests/test_main.py - NameError: name 'SortOrder' is not defined",
    "Command exited with code 2"
  ],
  "residualRisks": [
    "Requested feature/fix is unspecified, so findings are integration-oriented and not a final implementation plan.",
    "Source files were not modified; existing validation remains red.",
    "Only targeted files were inspected; deeper service/repo/model behavior may contain additional issues."
  ],
  "noStagedFiles": true,
  "notes": "Report written to /Users/ashleighhewitt/websocket_ap/context/scout-validation-integration.md."
}
```
