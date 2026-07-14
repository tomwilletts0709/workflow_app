# Code Context

## Files Retrieved
1. `app/core/settings.py` (lines 11-33) - Settings surface for DB, Redis, and Celery URLs.
2. `app/workers.py` (lines 1-35) - Only Celery app/task definition found.
3. `app/core/websockets.py` (lines 1-57) - WebSocket manager/router and in-memory broadcast implementation.
4. `app/main.py` (lines 1-34) - FastAPI app router wiring, including WebSocket and jobs routers.
5. `app/jobs/router.py` (lines 1-34) - Job HTTP API; creates DB job only.
6. `app/jobs/service.py` (lines 20-45) - Job service validation/status methods.
7. `app/jobs/repo.py` (lines 13-66) - Job persistence/status transitions.
8. `app/jobs/models.py` (lines 13-51) and `app/jobs/enums.py` (lines 3-10) - Job table/schema/status/type definitions.
9. `app/database/database.py` (lines 34-60) - Global SQLAlchemy engine/session from settings.
10. `compose.yaml` (lines 1-23) - Local Postgres and Redis only; no app/worker services.
11. `pyproject.toml` (lines 6-23, 25-34) - Runtime/dev dependencies and pytest config.
12. `tests/conftest.py` (lines 16-34) and `tests/test_main.py` (lines 1-11) - Current test setup and only test.
13. `migrations/env.py` (lines 6-24, 40-61) and `migrations/versions/de88712b196e_create_tasks_table.py` (lines 20-40) - Alembic metadata/imports and only migration.
14. `.env.example` (lines 1-6) - Expected local URL env values.
15. `app/activity/events.py` (lines 5-11), `app/notifications/events.py` (lines 7-14), `app/notifications/service.py` (lines 4-6) - Event/notification placeholders relevant to future WebSocket publishing.

## Key Code

```python
# app/core/settings.py:23-28
redis_url = "redis://localhost:6379/0"
celery_broker_url = "redis://localhost:6379/0"
celery_result_backend = "redis://localhost:6379/1"
```

```python
# app/workers.py:9-17
celery_app = Celery("workflow", broker=settings.celery_broker_url, backend=settings.celery_result_backend)
@celery_app.task(name="jobs.process")
def process_job(job_id: int) -> dict:
```

```python
# app/core/websockets.py:7-31
self.active_connection: dict[int, list[WebSocket]] = defaultdict(list)
async def broadcast_to_project(self, project_id: int, message: dict[str, Any]):
    connections = self.active_connection[project_id]
    for connection in connections:
        await connection.send_json(message)
```

```python
# app/jobs/router.py:16-21
@job_router.post("", response_model=JobRead)
async def create(...):
    return service.create(payload.type, payload.payload)
```

```python
# app/jobs/repo.py:13-18, 32-53
create() persists PENDING jobs; running()/completed()/failed() mutate DB status directly.
```

## Architecture

- FastAPI starts in `app/main.py` and includes `/tasks`, `/jobs`, `/projects`, `/activity`, `/search`, and `/ws/projects/{project_id}`.
- The current WebSocket layer is single-process, in-memory state only. `WebSocketManager.active_connection` is a module global list keyed by project id; no Redis pub/sub, no cross-process fanout, no lifecycle startup listener, and no backpressure/error handling on broadcast.
- Redis is configured and available as a dependency, but only implied as Celery broker/result backend. `redis_url` exists in settings but no direct Redis client or pub/sub code was found by grep.
- Celery exists as `app.workers.celery_app` and task `jobs.process`, but the HTTP job creation path only creates a DB row. There is no `delay()`/`apply_async()` call, no scheduler/dispatcher loop, and compose does not run a worker service.
- Jobs are DB-backed (`Job` model with status/payload/result/error timestamps). Worker processing updates this table through the same global `SessionLocal` used by the web app.
- Integration tests are currently minimal. `tests/conftest.py` defines an in-memory SQLite fixture, but `tests/test_main.py` imports the real app and only tests `GET /`; it does not override `get_db`, exercise jobs, WebSockets, Redis, or Celery.
- Alembic autogenerate imports all models, including jobs, but the only migration creates `tasks`. This implies DB schema drift risk for jobs/projects/activity/etc. unless migrations are intentionally incomplete.

## Concrete Findings

| Severity | Finding | Evidence | Confidence |
|---|---|---|---|
| High | Redis pub/sub is not implemented despite Redis settings/dependency. | `app/core/settings.py:23`; grep found no `pubsub`, `publish`, or `subscribe` usage outside WebSocket manager references. | High |
| High | WebSocket broadcast is local-memory only and will not work across multiple Uvicorn workers/instances or from Celery workers. | `app/core/websockets.py:7-31`; manager is module global at `app/core/websockets.py:33`. | High |
| High | Creating a job does not enqueue Celery work. | `app/jobs/router.py:16-21`; `app/jobs/service.py:24-30`; Celery task exists separately in `app/workers.py:16-35`; grep found no `.delay`/`.apply_async`. | High |
| Medium | Compose supports infra only, not application runtime topology. | `compose.yaml:1-23` has `postgres` and `redis`, no `api` or `worker` service. | High |
| Medium | Celery uses Redis DB 0 as broker and DB 1 as result backend; generic `REDIS_URL` also DB 0, so pub/sub would share broker DB unless separated. | `app/core/settings.py:23-28`; `.env.example:4-6`. | High |
| Medium | Current tests are smoke/unit only, not integration tests. | `tests/test_main.py:1-11`; `tests/conftest.py:16-34` fixture unused by app test. | High |
| Medium | Alembic migrations appear incomplete for the current model set. | `migrations/env.py:9-16` imports all models, but only migration creates tasks at `migrations/versions/de88712b196e_create_tasks_table.py:20-40`. | Medium |
| Low | Notification/activity event classes exist, but notification service is a stub and not tied to WebSockets. | `app/activity/events.py:5-11`; `app/notifications/events.py:7-14`; `app/notifications/service.py:4-6`. | High |

## Recommended Decision Implications

1. Treat Redis pub/sub as a new architecture addition, not stabilization of existing code. Current code implies no Redis event bus yet.
2. If WebSockets must support multi-worker API or worker-originated notifications, choose a Redis-backed bridge/channel layer; the current in-memory manager is only safe for single-process local demos/tests.
3. Decide whether job creation should enqueue Celery immediately (`process_job.delay(job.id)`) or remain DB-pending for a dispatcher. Current code strongly implies the former is missing if Celery is intended.
4. Add separate Redis namespace/DB/channel conventions before using pub/sub, because current `REDIS_URL` and Celery broker both default to DB 0.
5. Add integration tests around: job POST enqueues or dispatches, worker status transitions, WebSocket connect/broadcast, and Redis pub/sub fanout. Use dependency overrides for DB and either eager Celery or a fake enqueue boundary.
6. Before DB-backed integration tests against Postgres, resolve migration coverage for all models or explicitly use metadata-created SQLite for unit tests only.
7. Compose should eventually include `api` and `worker` services if the architecture decision expects reproducible local integration behavior.

## Gaps / Open Questions

- No direct app runtime command or Docker service for FastAPI/Celery worker was found in compose.
- No existing Redis client abstraction to extend for pub/sub.
- No existing tests define expected behavior for job enqueueing or WebSocket messages.
- Need confirmation whether the immediate goal is single-process WebSocket stabilization or production-capable cross-process fanout.

## Start Here

Open `app/core/websockets.py` first. It is the current boundary for client WebSocket connections and the place where an in-memory-only manager would need to be adapted to Redis-backed fanout or wrapped behind an interface.

## Supervisor coordination

No blocker requiring supervisor decision during scouting.

## Acceptance Evidence

- review-findings: See `Concrete Findings` table with severity, exact file paths/line ranges, and confidence.
- residual-risks: See `Gaps / Open Questions` and `Recommended Decision Implications`.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Concrete Findings table includes severity plus exact paths/line ranges for settings, workers, websockets, jobs, compose, migrations, and tests."
    }
  ],
  "changedFiles": [],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "ls/find/read targeted relevant files",
      "result": "passed",
      "summary": "Mapped app, tests, migrations, pyproject, compose, and env example."
    },
    {
      "command": "grep Redis/Celery/WebSocket enqueue/pubsub terms in app and tests",
      "result": "passed",
      "summary": "Confirmed no Redis pub/sub or Celery enqueue call sites; found only settings, worker task, and in-memory WebSocket manager."
    },
    {
      "command": "awk line-number inspection for cited files",
      "result": "passed",
      "summary": "Captured exact line ranges for evidence citations."
    }
  ],
  "validationOutput": [],
  "residualRisks": [
    "Scouting used static inspection only; did not run tests or services.",
    "Migrations were inspected by file presence/content, not by comparing live database schema.",
    "No hidden runtime configuration outside repository was inspected."
  ],
  "noStagedFiles": true,
  "notes": "No source files edited; only wrote requested context report."
}
```