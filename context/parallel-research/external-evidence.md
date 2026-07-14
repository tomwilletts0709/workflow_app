# Research: External evidence for WebSocket/Celery/Postgres/Redis architecture decisions

## Summary
For a single-process FastAPI task-tracker app, in-memory WebSocket connection management is acceptable initially, but it stops working reliably once Uvicorn runs multiple worker processes or when Celery workers need to trigger notifications outside the ASGI process. Redis pub/sub or another broker-backed fanout becomes necessary when notifications must cross process/container boundaries; Celery workers should not reuse request-scoped SQLAlchemy sessions and should publish events only after database commits. Integration tests should be staged: unit/session behavior first, then Postgres-backed DB tests, then Redis/Celery/WebSocket end-to-end tests using containerized services.

Confidence level: High for the process/session/test-staging principles because they are directly supported by official FastAPI/Starlette, Uvicorn, Celery, SQLAlchemy, pytest, and Testcontainers docs. Medium for the exact timing of adding Redis pub/sub because it depends on deployment topology and delivery guarantees.

## Findings
1. **WebSocket connections are process-local; in-memory connection managers do not fan out across Uvicorn workers. Severity: medium now, high if deployed with multiple workers. File paths: N/A, architecture decision.** FastAPI's WebSocket examples show app-local connection managers holding `WebSocket` objects in memory, and Starlette treats WebSockets as live ASGI connections. Uvicorn's deployment docs show `--workers` starts multiple worker processes. Therefore, each worker has its own memory and connection set; without pub/sub, a message created in worker A cannot reach clients connected to worker B. [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/), [Starlette WebSockets](https://www.starlette.io/websockets/), [Uvicorn Deployment / workers](https://www.uvicorn.org/deployment/)

2. **Redis pub/sub is not mandatory for the first stable single-worker milestone, but it is the natural next step once Celery or multiple ASGI workers must notify connected clients. Severity: low if single-process only, high for scale-out or background notifications. File paths: N/A, architecture decision.** Celery officially supports Redis as a broker/result backend, and Redis is already a common dependency when Celery is introduced. If Celery workers complete tasks outside the FastAPI process, they cannot directly call in-memory WebSocket managers. A Redis channel/stream or equivalent broker-backed event bus lets workers publish task events and lets each ASGI process subscribe and push to its own connected clients. [Celery Redis using Redis](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html), [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/), [Uvicorn Deployment](https://www.uvicorn.org/deployment/)

3. **Celery workers should create their own SQLAlchemy sessions per task/unit of work and close them; they should not share FastAPI request sessions. Severity: high. File paths: likely app DB/session and worker task modules, but not inspected.** SQLAlchemy documents `Session` as a mutable, stateful object representing a single database transaction and says a `Session` or `AsyncSession` should not be shared across concurrent threads/tasks. The standard pattern is one session per thread/task and to commit/rollback/close within the task boundary. [SQLAlchemy Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html), [SQLAlchemy contextual/thread-local sessions](https://docs.sqlalchemy.org/en/20/orm/contextual.html), [SQLAlchemy session FAQ: thread/task safety](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#is-the-session-thread-safe-is-asyncsession-safe-to-share-in-concurrent-tasks)

4. **Real-time notifications from workers should be emitted after successful DB commit, not before. Severity: high for consistency. File paths: likely worker task modules and notification publisher, but not inspected.** Because SQLAlchemy sessions hold transactional state until commit, publishing a WebSocket/Redis notification before commit can announce data that later rolls back or is not yet visible to other sessions. The safer pattern is: task opens session, mutates data, commits, then publishes a compact event containing task ID/status for ASGI subscribers to re-read or push. [SQLAlchemy Session basics / committing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#committing), [Celery tasks user guide](https://docs.celeryq.dev/en/stable/userguide/tasks.html)

5. **Integration tests should be staged by dependency boundary: DB first, broker/worker next, WebSocket fanout last. Severity: medium. File paths: tests not inspected.** pytest's fixture model supports layered resource setup/teardown. Testcontainers for Python provides containerized Postgres and Redis modules suitable for integration tests. Celery's testing guide distinguishes eager mode from real worker testing; eager mode is not a faithful worker substitute for integration tests. This supports a staged plan: (a) repository/session tests against Postgres, (b) Celery task tests against Redis/Postgres with a worker, (c) ASGI WebSocket tests proving notification flow, then (d) multi-worker/pub-sub tests once scale-out is required. [pytest fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html), [Testcontainers Python Postgres](https://testcontainers-python.readthedocs.io/en/latest/modules/postgres/README.html), [Testcontainers Python Redis](https://testcontainers-python.readthedocs.io/en/latest/modules/redis/README.html), [Celery testing](https://docs.celeryq.dev/en/stable/userguide/testing.html)

6. **Decision implication: defer Redis pub/sub only if the near-term runtime is one FastAPI process and notifications originate inside that process; otherwise add it before claiming real-time correctness. Severity: decision-critical. File paths: N/A.** In-memory WebSocket managers are simpler and appropriate for import-stabilization and local UX validation. Redis pub/sub becomes necessary when any of these are true: `uvicorn --workers > 1`, multiple containers/replicas, Celery workers must notify users, or tests must validate background-task-to-browser updates. If Redis is added later, isolate notification behind an interface now to avoid rewriting route/task logic.

## Sources
- Kept: FastAPI WebSockets (https://fastapi.tiangolo.com/advanced/websockets/) — official examples and connection-manager pattern.
- Kept: Starlette WebSockets (https://www.starlette.io/websockets/) — underlying ASGI WebSocket behavior used by FastAPI.
- Kept: Uvicorn Deployment (https://www.uvicorn.org/deployment/) — official evidence that workers are separate processes.
- Kept: Celery Redis docs (https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/redis.html) — official Redis broker/backend support.
- Kept: Celery testing docs (https://docs.celeryq.dev/en/stable/userguide/testing.html) — official warning that eager mode differs from worker execution.
- Kept: SQLAlchemy Session docs (https://docs.sqlalchemy.org/en/20/orm/session_basics.html) — authoritative session lifecycle and thread/task-safety guidance.
- Kept: pytest fixtures (https://docs.pytest.org/en/stable/how-to/fixtures.html) — official layered test setup guidance.
- Kept: Testcontainers Python Postgres/Redis docs (https://testcontainers-python.readthedocs.io/) — practical containerized dependency testing references.
- Dropped: Blog posts and framework tutorials — excluded because official docs were sufficient and less likely to be stale/SEO-heavy.

## Gaps
- No live web search was available in this subagent environment, so source freshness was based on known official documentation URLs rather than a live crawl.
- Exact implementation choice remains open: Redis pub/sub vs Redis Streams vs Celery events vs a dedicated WebSocket broadcast package. Next step: decide required delivery semantics: best-effort live notifications, durable replay, or audit-grade task event history.
- Local files were intentionally not inspected per instruction, so severity is architectural rather than tied to concrete code lines.

## Decision implications
- **Recommended now:** keep a simple in-process WebSocket manager only if the app is still single-worker and WebSocket sends are triggered inside FastAPI request/process flow.
- **Prepare now:** define a `NotificationPublisher`/`NotificationSubscriber` boundary so route handlers and Celery tasks do not depend directly on an in-memory manager.
- **Add Redis pub/sub before:** enabling multiple Uvicorn workers, deploying multiple app replicas, or requiring Celery-completed tasks to notify WebSocket clients.
- **Testing sequence:** Postgres session/repository tests → Celery task tests with real Redis/Postgres and worker → WebSocket notification tests → multi-process/pub-sub fanout tests.

## Residual risks
- Redis pub/sub is best-effort and not durable; missed messages are possible during subscriber disconnects. Use Redis Streams or persisted task status polling if missed notifications matter.
- Multi-worker WebSocket tests can be flaky unless service readiness and cleanup are explicit.
- Celery result backend behavior and task acknowledgment settings can affect perceived task status; validate against the app's exact Celery config before finalizing guarantees.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Findings include concrete architecture implications, severity labels, and note file paths as N/A/not inspected per instruction."
    }
  ],
  "changedFiles": [
    "/Users/ashleighhewitt/websocket_ap/progress.md",
    "/Users/ashleighhewitt/websocket_ap/context/parallel-research/external-evidence.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "write progress.md and context/parallel-research/external-evidence.md via file tool",
      "result": "passed",
      "summary": "Research brief and progress update written."
    }
  ],
  "validationOutput": [
    "No local files inspected, per task instruction.",
    "No live web_search tool was available; brief relies on known official documentation URLs."
  ],
  "residualRisks": [
    "Source freshness was not live-verified in this environment.",
    "Architecture severity cannot be mapped to exact repository files because local inspection was prohibited."
  ],
  "noStagedFiles": true,
  "notes": "Redis pub/sub is not necessary for a single-worker in-process milestone, but is necessary before multi-worker/multi-replica deployment or Celery-to-WebSocket notifications."
}
```
