# Research: Practical tradeoffs for FastAPI job-status updates

## Summary
For this app, the lowest-risk next move is **A: keep the in-memory WebSocket manager while stabilizing HTTP/Celery/tests**, but explicitly treat it as single-process/dev-only and avoid relying on Celery-originated pushes yet. **B: Redis pub/sub now** solves real multi-process and worker-originated notification gaps, but adds distributed-system failure modes and harder tests before the base app is mature. **C: polling** is the simplest and most testable fallback for job status, but postpones learning and validation of WebSocket lifecycle behavior.

## Findings
1. **In-memory WebSocket managers are simple but process-local** — FastAPI’s WebSocket examples keep active connections in a Python list/dict in the application process; this is easy to reason about and valuable for learning connection lifecycle, disconnect handling, and test setup, but it does not cross Uvicorn/Gunicorn workers or Celery worker processes. Starlette/FastAPI expose WebSocket accept/send/receive primitives, but do not make in-memory connection state distributed. [FastAPI WebSockets](https://fastapi.tiangolo.com/advanced/websockets/) [Starlette WebSockets](https://www.starlette.io/websockets/)

2. **Option A has the best maintenance-to-learning ratio if scoped honestly** — Keeping the in-memory manager lets the team stabilize HTTP endpoints, Celery task creation/result flow, auth/session assumptions, and async tests without adding Redis message routing. Main risks: false confidence if deployed with multiple web workers, missed notifications from Celery unless routed through HTTP/app process, race conditions around disconnects, and brittle tests if WebSocket state leaks between tests. Mitigation: document single-process limitation, gate WebSocket push as best-effort, and expose polling/status endpoint as source of truth.

3. **Redis pub/sub is the right architecture for cross-process notifications, but validation difficulty rises sharply** — Redis Pub/Sub supports publish/subscribe messaging across processes, which fits Celery-worker-to-FastAPI-server notification paths. However, Redis Pub/Sub is transient: subscribers must be connected to receive messages, so clients can miss updates unless the system also stores canonical job state somewhere durable. This adds edge cases: reconnect/resubscribe, duplicate/out-of-order delivery handling, backpressure, Redis outages, task completion before WebSocket subscription, and integration-test orchestration. [Redis Pub/Sub](https://redis.io/docs/latest/develop/pubsub/) [Celery calling/tasks result docs](https://docs.celeryq.dev/en/stable/userguide/calling.html)

4. **Celery already pushes the app toward a durable status source independent of WebSockets** — Celery task states/results are generally retrieved through a result backend or app-maintained status store; WebSockets should be a notification layer, not the only record of truth. If Redis is already used as Celery broker/result backend, reusing Redis may reduce infrastructure count, but it still expands application semantics from request/response plus tasks into distributed event delivery. [Celery result backends](https://docs.celeryq.dev/en/stable/userguide/tasks.html#result-backends) [Celery states](https://docs.celeryq.dev/en/stable/reference/celery.states.html)

5. **Polling is boring but easiest to validate** — Polling a `/jobs/{id}/status` endpoint keeps state retrieval HTTP-only, avoids persistent connection lifecycle bugs, and is straightforward to test with normal FastAPI/TestClient or async HTTP tests. Costs: more request traffic, delayed UX versus push, less opportunity to validate WebSocket behavior now, and potential later refactor if clients are built around polling semantics. For early-stage reliability, polling is often a useful fallback even if WebSockets remain enabled. [FastAPI testing](https://fastapi.tiangolo.com/tutorial/testing/) [HTTP polling concept, MDN 202 Accepted pattern](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/202)

6. **Testing maturity should drive the sequence** — Async WebSocket tests require deterministic event ordering, cleanup, and timeouts; Celery integration tests add worker/broker orchestration; Redis pub/sub adds another asynchronous boundary. Pytest-asyncio and FastAPI testing support exist, but the combined stack is harder to make non-flaky than HTTP status polling. [pytest-asyncio](https://pytest-asyncio.readthedocs.io/) [FastAPI testing WebSockets](https://fastapi.tiangolo.com/advanced/testing-websockets/)

## Option comparison

| Option | Main upside | Main risks / edge cases | Maintenance cost | Validation difficulty | Learning value |
|---|---|---|---|---|---|
| A. In-memory WS manager now | Fast to keep; teaches WS lifecycle; minimal new infra | Single-process only; no direct Celery-worker push; disconnect cleanup; state leakage in tests | Low | Medium | High for FastAPI/WS basics |
| B. Redis pub/sub now | Supports multi-process and Celery-originated notifications | Missed transient messages; reconnects; ordering/duplicates; Redis outage; integration-test complexity | Medium-high | High | High for distributed messaging, but may distract |
| C. Polling first | Reliable source-of-truth path; easiest tests | Worse UX latency; more HTTP load; postpones WS validation; later client refactor | Low | Low | Low-medium |

## Recommended next move
Choose **A + a polling fallback**, not full B yet: keep the in-memory WebSocket manager only as an opportunistic single-process notification layer while making the HTTP job-status endpoint and Celery state flow the canonical source of truth. Add Redis pub/sub later when tests can prove: task lifecycle persistence, client reconnect behavior, missed-message recovery from status endpoint, and multi-worker deployment expectations.

Practical next steps:
1. Mark in-memory WS manager as non-production/multi-worker unsafe in code/docs.
2. Ensure every job status transition is persisted and retrievable via HTTP polling.
3. Add deterministic tests for task creation, status polling, WebSocket connect/disconnect, and cleanup.
4. Defer Redis pub/sub until there is a failing or explicit requirement for multi-process/Celery-originated live notifications.

## Confidence level
**Medium-high.** The architectural constraints are well supported by FastAPI/Starlette, Redis, and Celery docs. Confidence is lower on app-specific recommendation details because no local code inspection or live web-search tool was available.

## Sources
- Kept: FastAPI WebSockets (https://fastapi.tiangolo.com/advanced/websockets/) — primary framework docs showing in-process WebSocket connection-manager pattern.
- Kept: Starlette WebSockets (https://www.starlette.io/websockets/) — underlying ASGI/WebSocket API behavior used by FastAPI.
- Kept: Redis Pub/Sub (https://redis.io/docs/latest/develop/pubsub/) — primary source for pub/sub semantics and transient delivery model.
- Kept: Celery calling/tasks docs (https://docs.celeryq.dev/en/stable/userguide/calling.html) — primary source for task invocation and async task result patterns.
- Kept: Celery result backends/tasks docs (https://docs.celeryq.dev/en/stable/userguide/tasks.html#result-backends) — supports treating durable task status as separate from notification delivery.
- Kept: FastAPI testing docs (https://fastapi.tiangolo.com/tutorial/testing/) and WebSocket testing docs (https://fastapi.tiangolo.com/advanced/testing-websockets/) — relevant for validation effort.
- Kept: pytest-asyncio docs (https://pytest-asyncio.readthedocs.io/) — relevant to async test complexity.
- Dropped: Blog/tutorial commentary — excluded to avoid stale or SEO-heavy advice where primary docs cover the relevant behavior.

## Gaps
- No local file inspection was performed, per task instruction; exact current architecture, broker/backend configuration, and test maturity are unknown.
- No runtime `web_search` tool was available, so this brief relies on known stable primary documentation URLs rather than freshly fetched search results.
- Need confirmation of intended deployment model: single Uvicorn worker, multiple workers, containers, or horizontally scaled app instances.
- Need confirmation whether Redis is already required for Celery broker/result backend; if so, incremental infrastructure cost for pub/sub is lower, though semantic/test cost remains.

## Supervisor coordination
No blocker requiring supervisor decision.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Created the requested concise research brief only, at context/parallel-research/practical-tradeoffs.md, and updated progress.md; no application code or tests were modified."
    }
  ],
  "changedFiles": [
    "/Users/ashleighhewitt/websocket_ap/progress.md",
    "/Users/ashleighhewitt/websocket_ap/context/parallel-research/practical-tradeoffs.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "write progress.md and practical-tradeoffs.md via available file tool",
      "result": "passed",
      "summary": "Both requested files were written successfully."
    }
  ],
  "validationOutput": [],
  "residualRisks": [
    "No web_search tool was available in this runtime, so sources were not freshly fetched; brief cites stable primary documentation URLs from known official docs.",
    "No git status command/tool was available, so noStagedFiles is based on not running staging commands rather than repository inspection."
  ],
  "noStagedFiles": true,
  "notes": "No local project files were inspected, consistent with the instruction."
}
```
