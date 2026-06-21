# Local Repository Scout Findings

## 1. Repo map
- `README.md` (lines 1-9): identifies project as **Workflow**, a work-in-progress FastAPI task tracker with task management, state transitions, pagination, search, WebSockets, background jobs, and PostgreSQL; future AI-agent scope is mentioned.
- `pyproject.toml` (lines 1-26): Python 3.11+ project using FastAPI, SQLAlchemy 2, Pydantic 2, pydantic-settings, Redis client, SlowAPI, psycopg, Alembic; dev tools are pytest, httpx, ruff. Pytest path is `tests`, pythonpath is `.`; Ruff line length 88.
- `app/main.py` (lines 1-26): FastAPI app entrypoint. Routers mounted: `/tasks`, WebSocket router at `/ws/projects/{project_id}`, `/jobs`; root returns `{"App": "Is Running"}`; SlowAPI limiter is installed.
- `app/tasks/` (models/repo/service/router/enums/flows): most complete feature area. Provides SQLAlchemy `Tasks`, Pydantic request/response models, repository/service/router layers, search integration, and a state machine for task transitions.
- `app/core/websockets.py`: in-memory WebSocket manager keyed by `project_id`; accepts clients and broadcasts JSON to project connections, but no task/job code currently calls `broadcast_to_project`.
- `app/database/database.py` (lines 1-60): SQLAlchemy engine/session setup from `DATABASE_URL`, dynamic table naming, DB dependency `get_db`. **High severity:** `Base.metadata = MetaData` assigns the class, not the `metadata` instance defined at lines 11-19.
- `app/search/repo.py`: generic text search/autocomplete repository used by `TaskRepo`.
- `app/jobs/`: job router/service/repo/models exist but appear less stable; Ruff reports undefined `Job` references in `app/jobs/repo.py`.
- `app/projects/`, `app/favourites/`, `app/search/`: partial modules exist but are not mounted in `app/main.py`; several have undefined names/typos per Ruff.
- `migrations/` and `alembic.ini`: Alembic is configured; one migration exists for tasks table (`migrations/versions/de88712b196e_create_tasks_table.py`).
- `compose.yaml`: PostgreSQL 17-alpine service exposed on localhost:5432 with database/user/password matching `.env.example`.
- `tests/`: only `tests/test_main.py` and `tests/conftest.py` Python files found. `tests/conftest.py` is stale/broken.

## 2. Existing patterns/constraints
- Architecture pattern: FastAPI router -> service -> repository -> SQLAlchemy model. Dependency injection creates repos/services per request using `get_db`.
- Models combine SQLAlchemy ORM and Pydantic schemas in the same `models.py` files, at least for tasks and jobs.
- Task flow:
  - `app/tasks/router.py`: endpoints create/get/list/update/delete/transition tasks.
  - `app/tasks/service.py`: thin business layer; transition calls state machine.
  - `app/tasks/repo.py`: commits DB writes directly and delegates search to `SearchRepo`.
  - `app/tasks/enums.py` + `app/tasks/flows.py`: `TaskStatus` and `TaskEvent` are `StrEnum`; state transitions raise `InvalidTransition`, mapped to HTTP 409.
- Search/pagination: `/tasks` list endpoint uses `CommonParamsDependency` from `app/core/pagination.py`; `SearchRepo.text_search` returns dict with `items`, `page`, `page_size`, `total`, `has_next`.
- WebSockets: current manager is process-local memory only; no Redis/pubsub despite Redis dependency. This limits multi-worker/multi-process broadcast correctness.
- Configuration: importing `app.database.database` immediately calls `get_settings()` and `create_engine(settings.database_url)`. A missing `DATABASE_URL` can break imports unless `.env` exists or env vars are set.
- Build/run likely commands:
  - App: `uv run uvicorn app.main:app --reload` or `python -m app.main` equivalent.
  - Tests: `uv run pytest -q`.
  - Lint: `ruff check .` (or `uv run ruff check .` if ruff is only in the uv env).
  - DB: `docker compose up postgres` then Alembic migrations if needed.
- Git state: `git status --short --branch` returned `## main...origin/main`; no local modified/staged files were shown before writing this scout output.
- Current validation state:
  - **High severity:** `uv run pytest -q` fails during conftest import: `ModuleNotFoundError: No module named 'app.core.database'` from `tests/conftest.py:6`; actual DB module is `app/database/database.py`.
  - **High severity:** `ruff check .` found 55 errors, including undefined names in jobs/projects/search and stale test imports.

## 3. Likely integration points for future changes
- API/task behavior: start with `app/tasks/router.py`, `app/tasks/service.py`, `app/tasks/repo.py`, `app/tasks/models.py`, `app/tasks/enums.py`, and `app/tasks/flows.py`.
- Real-time/project notification behavior: `app/core/websockets.py` is the broadcast manager; likely future task/project updates would call `manager.broadcast_to_project(project_id, message)` from service/router code or a domain event layer.
- Search/listing behavior: `app/search/repo.py` and `app/core/pagination.py`; task-specific wiring is `TaskRepo.search_tasks` and `TaskRepo.autocomplete_search`.
- DB/session/migration behavior: `app/database/database.py`, `alembic.ini`, `migrations/env.py`, and migrations under `migrations/versions/`.
- Background job behavior: `app/jobs/router.py`, `app/jobs/service.py`, `app/jobs/repo.py`, `app/workers.py`; treat as unstable until undefined names are fixed.
- New routers must be included in `app/main.py`; project/favourites routers currently are not included.
- Tests will likely need repair before feature work can have meaningful CI confidence: `tests/conftest.py` should import the real DB base/module and remove nonexistent category/items imports.

## 4. Risks/unknowns affecting implementation confidence
- **High severity:** User intent is missing. The concrete feature/bug request is not provided, so integration points above are inferred only from repository shape.
- **High severity:** Test suite currently cannot start because `tests/conftest.py` imports nonexistent modules.
- **High severity:** Static analysis shows many undefined names/typos outside tasks (`Job`, `Project`, `projects`, `mapped_columnn`, `Mapped`, `mapped_column`, `datetine`, etc.). Future work in those modules may require cleanup before implementation.
- **High severity:** `app/database/database.py` likely has a metadata bug (`Base.metadata = MetaData` instead of the `metadata` instance), which may break table creation/migrations/runtime ORM behavior.
- **Medium severity:** App import/runtime depends on `DATABASE_URL` at import time, reducing test isolation and making simple endpoint tests DB-config dependent.
- **Medium severity:** WebSocket manager is in-memory and not resilient to multi-worker deployment; broadcasts may not reach clients connected to other processes.
- **Medium severity:** `app/main.py` imports unused `WebSocket`/`APIRouter`; not functionally severe but indicates code hygiene issues.
- **Medium severity:** Docs (`docs/structure.md`) describe older/nonexistent paths such as `core/config.py`, `tasks/schemas.py`, and `realtime/`, so docs cannot be treated as authoritative.

## 5. Remaining clarification questions
1. What is the concrete feature/bug to implement? Current request explicitly lacks implementation intent.
2. Should future work prioritize making the existing test/lint baseline pass before feature implementation?
3. Should WebSocket behavior remain in-memory/single-process, or should Redis-backed cross-worker messaging be implemented?
4. Should project/jobs/favourites/search modules be considered active targets despite current undefined names and not all routers being mounted?
5. What database/test strategy is desired: real PostgreSQL via compose, SQLite unit tests, or dependency-overridden FastAPI tests?

## Acceptance evidence
- review-findings: concrete repo findings above cite exact paths and severity where applicable.
- residual-risks: missing intent, broken test baseline, ruff errors, DB metadata issue, import-time DB settings, and in-memory WebSocket limitations are documented above.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Findings include concrete file paths such as app/main.py, app/tasks/router.py, app/database/database.py, tests/conftest.py, and severity-tagged risks for broken tests, ruff errors, DB metadata, and missing intent."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git status --short --branch",
      "result": "passed",
      "summary": "Reported ## main...origin/main with no modified files shown before scout output was written."
    },
    {
      "command": "uv run pytest -q",
      "result": "failed",
      "summary": "Failed during tests/conftest.py import: ModuleNotFoundError: No module named 'app.core.database'."
    },
    {
      "command": "ruff check .",
      "result": "failed",
      "summary": "Found 55 lint/static errors, including undefined names in jobs/projects/search and stale imports in tests."
    }
  ],
  "validationOutput": [
    "pytest: ImportError while loading conftest; tests/conftest.py:6 imports app.core.database, which does not exist.",
    "ruff: Found 55 errors; 21 fixable with --fix."
  ],
  "residualRisks": [
    "Concrete implementation intent is missing, so no feature-specific plan should be assumed.",
    "Existing test and lint baselines are failing before any implementation work.",
    "Writing this required creating the requested context-gathering output file; source/project files were not modified."
  ],
  "noStagedFiles": true,
  "notes": "Scout output was written to /Users/ashleighhewitt/websocket_ap/context-gathering/scout-local-context.md."
}
```
