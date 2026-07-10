# Code Context

## Files Retrieved
1. `README.md` (lines 1-10) - states purpose/status.
2. `pyproject.toml` (lines 1-30) - Python/FastAPI dependencies and pytest/ruff config.
3. `compose.yaml` (lines 1-22) - local PostgreSQL/Redis services.
4. `app/main.py` (lines 1-27) - FastAPI app entrypoint and router wiring.
5. `app/core/settings.py` (lines 1-31) - env-driven settings.
6. `app/database/database.py` (lines 1-60) - SQLAlchemy base/engine/session dependency.
7. `app/core/pagination.py` (lines 1-44) - common pagination dependency; currently import-time broken.
8. `app/tasks/models.py` (lines 1-55), `app/tasks/router.py` (lines 1-82), `app/tasks/service.py` (lines 1-42), `app/tasks/repo.py` (lines 1-115), `app/tasks/flows.py` (lines 1-42) - main CRUD/state-machine feature.
9. `app/projects/models.py` (lines 1-62), `app/projects/router.py` (lines 1-76) - project CRUD and task relationship.
10. `app/core/websockets.py` (lines 1-55) - in-memory project websocket manager/route.
11. `app/search/repo.py` (lines 1-96) - reusable text/autocomplete search plus incomplete global/full-text search.
12. `app/jobs/models.py` (lines 1-47), `app/jobs/service.py` (lines 1-47), `app/workers.py` (lines 1-31) - job model/service and broken Celery worker draft.
13. `app/ai/service.py` (lines 1-35) - AI summary service draft.
14. `migrations/env.py` (lines 1-55), `migrations/versions/de88712b196e_create_tasks_table.py` (lines 1-39) - Alembic setup and only migration.
15. `tests/conftest.py` (lines 1-27), `tests/test_main.py` (lines 1-10) - current testing pattern.
16. `app/database/service.py` (lines 1-74) - incomplete filter/sort helper with syntax errors.

## Key Code

### Project purpose/stack
- Purpose: work-in-progress task-tracker named Workflow, built with FastAPI; focus includes tasks, projects, state transitions, search, WebSockets, background jobs, PostgreSQL, and future AI agent features (`README.md`).
- Stack: Python 3.11+, FastAPI, SQLAlchemy 2, Pydantic v2/settings, psycopg/PostgreSQL, Redis, Celery, SlowAPI, LangGraph/LangChain/OpenAI; dev uses pytest, httpx, ruff (`pyproject.toml`).

### Entry points and dependencies
```python
# app/main.py
app = FastAPI()
app.include_router(task_router, prefix="/tasks")
app.include_router(websocket_router)
app.include_router(job_router, prefix="/jobs")
app.include_router(project_router, prefix='/projects')
app.include_router(activity_router)
app.include_router(search_router, prefix='/search')
```
- Settings require `DATABASE_URL` at import time via `get_settings()` in `app/database/database.py`; `.env.example` points to local compose Postgres.
- `compose.yaml` starts Postgres 17 on `5432` and Redis 7 on `6379`.

### Main implementation patterns
- Routers construct a repo/service per request with `Depends(get_db)`, e.g. `app/tasks/router.py` and `app/projects/router.py`.
- Repos own SQLAlchemy session mutations and commit/refresh directly (`app/tasks/repo.py`, `app/projects/repo.py` pattern inferred from router/service structure).
- Pydantic request/response schemas live in the same file as SQLAlchemy models (`app/tasks/models.py`, `app/projects/models.py`, `app/jobs/models.py`).
- Task status transitions use a generic in-memory state machine (`app/tasks/flows.py`) and enum-driven task status/events (`app/tasks/enums.py`, not fully retrieved).
- WebSockets are in-memory only: `WebSocketManager.active_connection: dict[int, list[WebSocket]]`, route `/ws/projects/{project_id}`, no Redis/pubsub or auth (`app/core/websockets.py`).
- Tests use in-memory SQLite with `StaticPool` and `Base.metadata.create_all`, plus direct FastAPI `TestClient` (`tests/conftest.py`, `tests/test_main.py`).

## Architecture
FastAPI app imports all routers at startup. Database setup is global/import-time: `Settings` loads `.env`, `engine = create_engine(settings.database_url)`, `SessionLocal` feeds FastAPI dependencies. Feature modules generally follow `models.py` (SQLAlchemy + Pydantic), `repo.py` (database access), `service.py` (business rules), `router.py` (HTTP). Tasks link to projects via FK/relationship. Search repo is reused by task repo for paginated text search/autocomplete. Jobs are intended for persisted background work, with Celery/Redis intended but currently not functional. AI module is a draft layer around LangGraph summary flows.

## Existing implementation/testing patterns
- CRUD endpoints raise `HTTPException` on `None`/false repo returns.
- Service methods mostly delegate to repo, with validation/business rules in services for task transitions and job payloads.
- Validation command candidates: `uv run pytest -q`, `uv run ruff check .`, `docker compose up -d postgres redis`, `uv run alembic upgrade head`, `uv run uvicorn app.main:app --reload`.
- Alembic only imports task models in `migrations/env.py`, so autogenerate likely misses projects/jobs/activity/etc unless imports are expanded.

## Review Findings
- **High** `app/core/pagination.py:18`: `SortOrder` is referenced but never imported/defined; this prevents app/test import. `uv run pytest -q` fails during collection with `NameError: name 'SortOrder' is not defined`.
- **High** `app/database/service.py:50`: file has invalid syntax (`def ex`) and other undefined names (`Select`, `select`, `func`, `function`) per ruff; any import of this helper will fail.
- **High** `app/workers.py:4-12`: imports `app.database.databse` typo, calls undefined `app_settings()`, and references non-existent `settings.celery_result.backend`; Celery worker path is not runnable.
- **High** `app/search/repo.py:69-95`: global/full-text search references undefined `Project`, `Task`, `SearchResult`, `model`, `query`, `search_columns`; these paths are incomplete.
- **High** `app/tasks/models.py:21` and `app/projects/models.py:29`: forward relationships use `Project`/`Tasks`; ruff reports undefined names. Runtime may require careful import ordering or `TYPE_CHECKING` imports.
- **Medium** `migrations/versions/de88712b196e_create_tasks_table.py:20-28`: migration creates table `tasks`, while model class `Tasks` auto-tablename resolves to `tasks`; however FK in model references `project.id`, and migration lacks FK/project table. Also migration has `project_id` and `description` non-nullable while current model allows null.
- **Medium** `app/ai/service.py:6-35`: service calls `_run_summary_graph` but only defines `_run_text_graph`; success check appears inverted (`if state.get("result"): raise ValueError`).
- **Medium** repo has many lint errors/unfinished modules (`documents`, `notifications`, `logging`, search models), so future implementation should avoid assuming all modules import cleanly.

## Commands/Configs Likely Relevant for Validation
- `uv run pytest -q` - currently fails at import/collection due `SortOrder`.
- `uv run ruff check .` - currently fails with 45 lint/syntax/name errors.
- `docker compose up -d postgres redis` - brings up required local services.
- `uv run alembic upgrade head` - database migration path, but schema is likely stale/incomplete.
- `uv run uvicorn app.main:app --reload` - app startup after import blockers are fixed.

## Repo State / Risks / Constraints
- `git status --short` returned no output: no uncommitted/staged changes observed before this report write.
- Current report file is newly written under `context/`; no source files were modified.
- Import-time settings require `DATABASE_URL`; tests/app import can fail if `.env` is missing. `.env.example` documents expected value.
- Tests are minimal: only root endpoint test plus an SQLite fixture; no coverage for task/project CRUD, websockets, search, jobs, migrations.
- PostgreSQL-specific behavior may diverge from SQLite tests, especially enum/FK/migration behavior.
- In-memory websocket manager will not scale across workers/processes and has no persistence/backplane.

## Start Here
Open `app/main.py` first to see router registration and import surface, then fix import blockers beginning with `app/core/pagination.py` because it currently prevents even `tests/test_main.py` from collecting.

## Remaining Clarification Questions
1. Is the next goal to stabilize the existing app first, or add a new feature despite current import/lint failures?
2. Should PostgreSQL/Alembic schema be treated as source of truth, or should current SQLAlchemy models be migrated forward?
3. Are WebSockets expected to remain in-memory for development, or should Redis/pubsub be introduced for multi-worker broadcasting?
4. Which domains are in scope now: tasks/projects only, or also documents/favourites/activity/notifications/search/jobs/AI drafts?
5. Should validation target SQLite unit tests, local Postgres integration tests, or both?

## Supervisor coordination
No supervisor escalation needed; scouting completed without modifying source files.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete findings include file paths and severities in the Review Findings section, plus residual risks below."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "git status --short",
      "result": "passed",
      "summary": "No output; working tree appeared clean before writing the context report."
    },
    {
      "command": "uv run pytest -q",
      "result": "failed",
      "summary": "Collection failed: app/core/pagination.py references undefined SortOrder."
    },
    {
      "command": "uv run ruff check .",
      "result": "failed",
      "summary": "Reported 45 issues including syntax errors and undefined names."
    }
  ],
  "validationOutput": [
    "pytest: NameError: name 'SortOrder' is not defined in app/core/pagination.py:18",
    "ruff: 45 errors, including invalid syntax in app/database/service.py and undefined names in pagination/search/workers modules"
  ],
  "residualRisks": [
    "Source app currently does not import cleanly, so runtime behavior beyond import surface is uncertain.",
    "Alembic migration appears stale/incomplete relative to current models.",
    "Only minimal tests exist; future changes need additional coverage and likely Postgres validation."
  ],
  "noStagedFiles": true,
  "notes": "Report written to /Users/ashleighhewitt/websocket_ap/context/scout-local-recon.md; no source files modified."
}
```
