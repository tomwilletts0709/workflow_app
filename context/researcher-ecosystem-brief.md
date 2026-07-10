# Research: External ecosystem context for FastAPI task-tracker planning

## Summary
The strongest external guidance comes from official FastAPI, SQLAlchemy, Pydantic Settings, Alembic, Celery, Redis, and Starlette documentation. The key implementation decisions are: use request-scoped SQLAlchemy sessions via FastAPI dependencies, configure settings with Pydantic v2 `pydantic-settings` aliases deliberately, ensure Alembic imports all model metadata before autogenerate, configure Celery Redis broker/result backend explicitly, and do not rely on in-memory WebSocket connection state for multi-process/task-worker broadcasts.

## Findings

1. **FastAPI dependency/session pattern should create one SQLAlchemy session per request and close it reliably.** — FastAPI's official SQL database tutorial shows a dependency using `with Session(engine) as session: yield session`, then injecting that dependency into path operations. Practical implication: likely affected files are database/session setup and API route modules, e.g. `app/database.py`, `app/db/session.py`, `app/main.py`, and route files; severity: **high** if sessions are global/shared or not closed, because this can cause leaked connections and transaction-state bugs. [FastAPI SQL Databases tutorial](https://fastapi.tiangolo.com/tutorial/sql-databases/)

2. **SQLAlchemy 2.0 favors explicit `Session` lifecycle and transaction boundaries.** — SQLAlchemy 2.0 docs describe `Session` as a mutable, stateful object representing a single database transaction and recommend context-manager patterns such as `with Session(engine) as session:` and `with session.begin():`. Practical implication: the repo should avoid module-global sessions and should make commit/rollback ownership explicit; likely affected files are DB session factory, CRUD/service functions, and tests; severity: **high** for write endpoints or background tasks. [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

3. **Pydantic v2 settings aliases are explicit and can change environment variable names.** — Pydantic Settings docs distinguish `alias`, `validation_alias`, and related alias behavior for environment loading. Practical implication: if the repo uses Pydantic v2, env vars such as database URL, Redis URL, Celery broker, or secret settings should be documented and tested against the actual aliases; likely affected files are settings/config modules and `.env.example`; severity: **medium-high** because silent env-name mismatches can break deploys. [Pydantic Settings documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)

4. **Alembic autogenerate only detects models present in `target_metadata`; model imports matter.** — Alembic's autogenerate docs require `target_metadata` to point to the application's SQLAlchemy `MetaData`; imported model modules must have registered their tables with that metadata. Practical implication: migration env setup should import all model modules or a central models package before `target_metadata` is evaluated; likely affected files are `alembic/env.py`, model package `__init__.py`, and migration scripts; severity: **high** if schema changes are expected, because autogenerate can emit empty/incomplete migrations. [Alembic autogenerate docs](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)

5. **Celery supports Redis as broker and result backend, but URLs and backend behavior must be configured deliberately.** — Celery's Redis guide documents broker URLs like `redis://localhost:6379/0`, result backend URLs, Sentinel support, visibility timeout caveats, and credential forms. Practical implication: broker and backend should be separate settings, preferably environment-driven; tasks should not assume result backend presence unless needed; likely affected files are Celery app/config module, settings module, worker startup docs, and compose/deployment config; severity: **medium-high**, especially if task status is user-visible. [Celery Redis guide](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html)

6. **Redis itself is commonly used as both Celery transport dependency and pub/sub/message fanout primitive, but semantics differ.** — Redis docs describe Pub/Sub as fire-and-forget message broadcasting to subscribed clients, not durable queueing. Practical implication: Redis Pub/Sub may be suitable for live WebSocket notifications but not for guaranteed task history; persistent state should remain in the database or a durable queue/result backend; likely affected files are WebSocket manager, Celery task event hooks, and Redis client integration; severity: **medium** unless delivery guarantees are required. [Redis Pub/Sub docs](https://redis.io/docs/latest/develop/pubsub/)

7. **Starlette/FastAPI WebSocket connection managers are process-local unless backed by external infrastructure.** — FastAPI's WebSocket docs show an in-memory `ConnectionManager` and explicitly warn that it only works while the process is running and with a single process; for robust or distributed cases they point to external broadcast tooling such as `encode/broadcaster`. Practical implication: if the repo will run with multiple Uvicorn/Gunicorn workers, multiple containers, or Celery-originated events, it needs Redis-backed pub/sub/broadcast or another shared broker; likely affected files are WebSocket endpoint/manager modules and deployment worker configuration; severity: **high** for multi-process deployments, **low-medium** for local single-process demos. [FastAPI WebSockets docs](https://fastapi.tiangolo.com/advanced/websockets/)

8. **Uvicorn multi-worker deployments create separate processes and therefore separate memory.** — Uvicorn deployment docs document running multiple workers as separate worker processes. Practical implication: any in-memory list/dict of active WebSocket clients, task statuses, or subscriptions will not be shared across workers; likely affected files are deployment scripts/config and WebSocket manager; severity: **high** if deployment uses more than one worker. [Uvicorn deployment docs](https://www.uvicorn.org/deployment/)

## Practical implications for this repo before planning

- **Database/session layer — severity: high.** Plan around SQLAlchemy 2 `Session` factories and FastAPI `Depends` request-scoped sessions. Avoid passing live request sessions into Celery tasks; pass identifiers and create a new session inside the task if DB access is needed.
- **Settings/env layer — severity: medium-high.** Confirm whether the repo uses Pydantic v1 or v2. If v2, prefer `pydantic-settings` and explicitly verify env aliases for `DATABASE_URL`, `REDIS_URL`, Celery broker/backend URLs, and any secrets.
- **Alembic migrations — severity: high.** Ensure `alembic/env.py` imports all models before assigning `target_metadata`; otherwise autogenerate evidence is unreliable.
- **Celery/Redis — severity: medium-high.** Treat Redis broker URL, result backend URL, visibility timeout, and result persistence as implementation decisions, not incidental defaults.
- **WebSocket broadcasting — severity: high when multi-process or Celery-driven.** Single-process in-memory managers are acceptable only for demo/local scope. Multi-worker or background-task-originated status updates need shared broadcast infrastructure, commonly Redis Pub/Sub or a maintained ASGI broadcast abstraction.

## Where external evidence is not needed yet

- Exact endpoint shape, task schema, and domain model do not need more external research until the user picks a feature or fix.
- Choice between polling, Server-Sent Events, and WebSockets is product/UX-dependent; current evidence only says WebSockets need shared fanout when scaled beyond one process.
- Specific SQL schema/index choices require local model inspection and expected query patterns, not more ecosystem research.
- Celery task retry policy, idempotency design, and result retention duration depend on product requirements; official docs are enough for initial planning.
- Whether to add `encode/broadcaster`, direct Redis client Pub/Sub, Celery events, or another message layer depends on the selected feature and deployment target.

## Sources

- Kept: FastAPI SQL Databases tutorial (https://fastapi.tiangolo.com/tutorial/sql-databases/) — official dependency/session pattern used by FastAPI apps.
- Kept: SQLAlchemy 2.0 Session basics (https://docs.sqlalchemy.org/en/20/orm/session_basics.html) — authoritative session lifecycle and transaction guidance.
- Kept: Pydantic Settings documentation (https://docs.pydantic.dev/latest/concepts/pydantic_settings/) — official v2 env/alias behavior.
- Kept: Alembic autogenerate documentation (https://alembic.sqlalchemy.org/en/latest/autogenerate.html) — authoritative migration metadata requirements.
- Kept: Celery Redis guide (https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html) — official Redis broker/backend configuration.
- Kept: Redis Pub/Sub documentation (https://redis.io/docs/latest/develop/pubsub/) — primary source for Redis Pub/Sub delivery semantics.
- Kept: FastAPI WebSockets documentation (https://fastapi.tiangolo.com/advanced/websockets/) — official in-memory manager example and single-process warning.
- Kept: Uvicorn deployment documentation (https://www.uvicorn.org/deployment/) — primary deployment source for multi-worker process behavior.
- Dropped: Broad third-party tutorials/blogs — excluded because official/current docs cover the relevant decisions with less risk of stale guidance.
- Dropped: Package-specific examples for alternative broadcast libraries — excluded until the user chooses a concrete feature/fix requiring that dependency decision.

## Gaps

- I could not inspect local files by instruction, so file paths above are likely affected path categories, not verified repo paths.
- No live web-search tool was available in this subagent environment; sources are official/current documentation URLs selected from known primary sources rather than freshly fetched search results.
- Need user/deployment clarification before deciding whether Redis Pub/Sub/broadcast is required for WebSockets.
- Need local confirmation of Pydantic version, SQLAlchemy style, Alembic layout, Celery initialization, and deployment worker model before implementation planning.

## Remaining clarification questions

1. Will production run more than one Uvicorn/Gunicorn worker or more than one container instance?
2. Must WebSocket task updates be delivered from Celery workers in real time, or is HTTP polling acceptable?
3. Are task results/statuses durable product state, or only ephemeral progress messages?
4. Is the codebase already on Pydantic v2 / `pydantic-settings`, SQLAlchemy 2.0, and Alembic?
5. Is Redis already available in the target deployment, and should it be used for both Celery and broadcast fanout?

## Acceptance evidence

- review-findings: Concrete findings are listed above with severity and likely affected file/path categories where local inspection was disallowed.
- residual-risks: Main risks are absence of live web search in this environment, no local file inspection by task instruction, and unresolved deployment/product requirements.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Provided concrete ecosystem findings with severity and likely affected file/path categories for database/session setup, settings, Alembic env, Celery config, WebSocket manager, and deployment config; included review-findings and residual-risks sections."
    }
  ],
  "changedFiles": [
    "/Users/ashleighhewitt/websocket_ap/context/researcher-ecosystem-brief.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "write /Users/ashleighhewitt/websocket_ap/context/researcher-ecosystem-brief.md",
      "result": "passed",
      "summary": "Created the requested source-backed ecosystem brief without inspecting or modifying local repo files."
    }
  ],
  "validationOutput": [],
  "residualRisks": [
    "No live web_search/fetch tool was available in this environment, so sources were selected from known official documentation rather than freshly searched.",
    "Local file paths could not be verified because the task explicitly prohibited inspecting local files.",
    "Implementation confidence still depends on deployment model, required WebSocket delivery guarantees, and installed library versions."
  ],
  "noStagedFiles": true,
  "notes": "Only the requested markdown brief was written; no local source files were inspected or edited."
}
```
