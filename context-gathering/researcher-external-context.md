# External ecosystem context for `websocket_ap`

Local clues used: `README.md` describes a FastAPI task/workflow app with WebSockets, background jobs, PostgreSQL, pagination/search, and possible future AI-agent scope. `pyproject.toml` declares Python >=3.11 with FastAPI, Uvicorn standard, SQLAlchemy 2.x, Pydantic 2.x, Redis, psycopg 3, Alembic, SlowAPI, pytest/httpx/ruff. `app/core/websockets.py` currently uses FastAPI/Starlette `WebSocket` and an in-memory connection manager keyed by `project_id`.

## 1. External sources consulted with links and why they matter

- FastAPI WebSockets docs — https://fastapi.tiangolo.com/advanced/websockets/ — primary framework guidance for declaring websocket routes, accepting connections, receiving/sending messages, dependencies, and handling disconnects.
- Starlette WebSockets docs — https://www.starlette.io/websockets/ — FastAPI builds on Starlette; this is the lower-level API reference for `WebSocket.accept()`, `send_json()`, `receive_*()`, close codes, and iterator helpers.
- Uvicorn settings docs — https://www.uvicorn.org/settings/ — authoritative runtime options relevant to local development and deployment, including `reload`, host/port, workers, and WebSocket protocol implementation settings.
- Uvicorn deployment docs — https://www.uvicorn.org/deployment/ — matters for production process model and the important constraint that multiple workers are separate processes.
- Python `websockets` project docs — https://websockets.readthedocs.io/ — relevant because `uvicorn[standard]` commonly installs the `websockets` implementation used by Uvicorn for WebSocket protocol handling.
- MDN WebSocket API — https://developer.mozilla.org/en-US/docs/Web/API/WebSocket — browser/client-side API reference for connection lifecycle, message format, close/error events, and client limitations.
- RFC 6455: The WebSocket Protocol — https://www.rfc-editor.org/rfc/rfc6455 — protocol-level source for handshake, framing, close semantics, and status codes.
- FastAPI lifespan/events docs — https://fastapi.tiangolo.com/advanced/events/ — relevant for future Redis/Postgres clients, background workers, or connection-pool setup/teardown.
- SQLAlchemy 2.0 documentation — https://docs.sqlalchemy.org/en/20/ — primary source for SQLAlchemy 2.x session/transaction patterns used by the repository's service/repository layers.
- Psycopg 3 docs — https://www.psycopg.org/psycopg3/docs/ — primary source for PostgreSQL driver behavior, connection pooling options, and async/sync choices.
- Redis Python client docs — https://redis.readthedocs.io/ — primary source for redis-py behavior if cross-process pub/sub, queues, rate limiting, or background jobs are implemented.
- SlowAPI docs — https://slowapi.readthedocs.io/ — relevant because the project has a `Limiter`; it documents FastAPI integration, decorators, storage backends, and limitations.
- HTTPX async/testing docs — https://www.python-httpx.org/async/ and https://www.python-httpx.org/advanced/transports/ — relevant to FastAPI test-client style, though WebSocket testing often uses Starlette/FastAPI test clients rather than plain HTTPX.

## 2. Key ecosystem constraints/best practices likely relevant to implementation

1. FastAPI WebSocket handlers run on Starlette's ASGI WebSocket interface. A server must explicitly accept a connection before normal send/receive operations; disconnect handling should use `WebSocketDisconnect` or Starlette iterator helpers. This matches the local `manager.connect(... await websocket.accept())` pattern.
2. The current in-memory connection manager is only safe for a single Python process. Uvicorn production workers are separate processes, so `active_connection` will not be shared across workers or machines. Any feature that must broadcast reliably across all clients in production should plan for an external broker/backplane such as Redis pub/sub, PostgreSQL LISTEN/NOTIFY, or another message bus.
3. Broadcasting sequentially with `await connection.send_json(...)` can let one slow/broken client delay all later clients. Robust implementations usually snapshot the connection list, handle send exceptions, remove dead sockets, and consider per-connection queues or bounded fan-out for larger rooms/projects.
4. Authentication/authorization for WebSocket routes must be planned separately from normal request handlers. FastAPI supports dependencies on websocket routes, but browsers cannot set arbitrary headers on the native `WebSocket` constructor; common approaches include cookies, same-origin protections, short-lived query tokens, or subprotocol-based/token negotiation with care.
5. Rate limiting middleware/decorators may not automatically protect WebSocket message throughput. SlowAPI is primarily request/response oriented; connection limits, per-message limits, and per-project fan-out limits may need explicit implementation or ASGI/server-layer controls.
6. Keep application startup/shutdown resource management in FastAPI lifespan hooks. Redis clients, database engines/pools, pub/sub tasks, and background consumers should be created and closed predictably rather than as unmanaged globals.
7. SQLAlchemy 2.x and psycopg 3 choices matter for async design. The local code currently uses sync SQLAlchemy `Session` dependencies inside async route functions; that can be acceptable for small apps but may block the event loop under load unless routed through threadpool patterns or migrated deliberately to async SQLAlchemy/async psycopg.
8. Browser WebSocket clients provide limited built-in backpressure control and no automatic reconnect. Server and client plans should define heartbeat/ping behavior, reconnect strategy, idempotent subscription semantics, and message schemas.

## 3. Recent/version-specific caveats to verify locally

- `pyproject.toml` uses open lower bounds such as `fastapi>=0.115.0`, `uvicorn[standard]>=0.30.0`, `redis>=7.4.0`, and `pydantic-settings>=2.14.1`; actual installed versions may be much newer than the minimums. Verify with the lockfile/environment before implementing version-sensitive APIs.
- Uvicorn WebSocket behavior depends on installed protocol packages and runtime settings. With `uvicorn[standard]`, protocol support is normally present, but production settings such as workers, proxy headers, timeouts, and WebSocket backend should be checked locally.
- FastAPI/Pydantic v2 is the local baseline, so any examples from older FastAPI/Pydantic v1 tutorials may use stale model/config idioms.
- Redis dependency naming/versioning should be confirmed in the local resolver/lockfile. The modern package is `redis`/redis-py; async APIs are under `redis.asyncio` in current redis-py lines.
- SlowAPI has integration limitations and order-sensitive decorator patterns in its docs; verify current behavior before assuming it covers websocket endpoints or app-wide limits.
- If the app is deployed behind a proxy/load balancer, confirm WebSocket upgrade headers, idle timeouts, sticky sessions, allowed origins, TLS termination, and max connection limits.

## 4. How this evidence should shape local planning

- Start implementation planning by classifying the change as single-process/local-only versus production/cross-worker. If the feature requires reliable project-wide notifications, include a broker/backplane design before changing the in-memory manager.
- Preserve FastAPI/Starlette WebSocket idioms: accept only after validation, handle disconnects and send failures, close with appropriate codes, and define message schemas rather than arbitrary JSON blobs.
- Avoid widening scope into AI agents or background-job architecture unless the requested feature explicitly needs it. The repository already has multiple relevant subsystems; changes should be tied to a concrete task/workflow/WebSocket behavior.
- Verify installed dependency versions and run existing tests before coding. Version drift is likely because dependencies use broad `>=` ranges.
- Plan tests around connection lifecycle, project subscription isolation, broadcast behavior, disconnect cleanup, and failure of one client not breaking all broadcasts. If cross-process behavior is required, add integration tests or isolate the broker interface for testing.

## 5. Remaining clarification questions that matter before planning/implementation

1. What exact behavior is the future implementation meant to add or change: task event notifications, job progress streaming, chat-like messaging, admin monitoring, or something else?
2. Is the target deployment single-process development only, or production with multiple Uvicorn workers/containers?
3. Do WebSocket clients authenticate today, and should subscriptions be authorized by `project_id`?
4. Are messages expected to be persisted/replayed, or are they best-effort live notifications only?
5. Should Redis already in dependencies be used as the cross-process pub/sub/job backend, or is PostgreSQL-only preferred?
6. What client environment should be supported: browser native WebSocket, Python client, frontend framework, or all of these?

## Acceptance report

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Created only the requested external-context research markdown file; did not modify application/source files or broaden into an unstated implementation feature."
    }
  ],
  "changedFiles": [
    "/Users/ashleighhewitt/websocket_ap/context-gathering/researcher-external-context.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "Read local manifest/context files via available file-read tool: README.md, pyproject.toml, app/main.py, app/core/websockets.py, app/rate_limiting.py, app/tasks/router.py, app/jobs/router.py",
      "result": "passed",
      "summary": "Identified FastAPI, Starlette WebSockets, Uvicorn, SQLAlchemy, Pydantic v2, Redis, psycopg, Alembic, SlowAPI, pytest/httpx/ruff as relevant ecosystem context."
    },
    {
      "command": "Write requested research brief via available file-write tool",
      "result": "passed",
      "summary": "Wrote /Users/ashleighhewitt/websocket_ap/context-gathering/researcher-external-context.md."
    }
  ],
  "validationOutput": [],
  "residualRisks": [
    "No web_search tool was available in this subagent runtime, so links are based on authoritative known primary documentation rather than live search-result retrieval.",
    "No shell/git tool was available to inspect lockfiles, installed versions, or staged changes; no files were intentionally staged."
  ],
  "noStagedFiles": true,
  "notes": "Scope was limited to external ecosystem context plus minimal local manifest/framework clues, as requested."
}
```
