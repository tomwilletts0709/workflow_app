# LangChain / LangGraph AI Agent Plan

## Purpose

Add AI to the app in a way that fits the current direction:

- **DB-first jobs** for long-running work.
- **Activity Feed / events** as the durable record of what happened.
- **WebSockets / Pub/Sub** for live delivery, not source of truth.
- **FastAPI router → service → repo** structure for application logic.
- **Celery + Redis** for background execution.

The goal is not to add a vague “AI agent” immediately. The goal is to build a safe foundation where AI can help with project/task workflows without bypassing the app’s domain rules.

---

## Research Summary

### External evidence

Authoritative docs point to this approach:

- FastAPI should not run long AI workflows directly in request handlers.
- Celery is suitable for long-running/retryable background jobs.
- LangGraph is a better fit than plain LangChain when workflows need state, branching, checkpointing, human approval, or resumability.
- LangChain is useful for model/tool integrations and structured outputs.
- Redis Pub/Sub is ephemeral live fanout; it is not durable history.
- Redis Streams are useful when replayable event delivery is needed.
- Postgres should remain the source of truth for app state and audit/history.

Useful primary docs:

- FastAPI background tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- Celery docs: https://docs.celeryq.dev/en/stable/
- LangChain docs: https://python.langchain.com/docs/introduction/
- LangGraph docs: https://langchain-ai.github.io/langgraph/
- LangGraph persistence: https://langchain-ai.github.io/langgraph/concepts/persistence/
- LangGraph human-in-the-loop: https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/
- LangGraph multi-agent concepts: https://langchain-ai.github.io/langgraph/concepts/multi_agent/
- Redis Pub/Sub: https://redis.io/docs/latest/develop/pubsub/
- Redis Streams: https://redis.io/docs/latest/develop/data-types/streams/
- OWASP LLM Top 10: https://owasp.org/www-project-top-10-for-large-language-model-applications/

---

## Local Codebase Implications

The app already has pieces that support an event-led AI design:

- `app/tasks/` has task creation and status transitions.
- `app/projects/` is becoming the project domain anchor.
- `app/jobs/` is intended to track background work.
- `app/workers.py` is the likely Celery worker entry point.
- `app/core/websockets.py` already has project-scoped WebSocket broadcasting.
- `plan.md` already proposes an Activity Feed with system-generated events.

Important current constraints:

- Project/task relationship work should be stabilized before project-scoped AI features.
- Jobs and worker code need to import cleanly before AI jobs can run.
- Activity Feed should be durable before WebSocket/Pub/Sub AI progress is treated as product behavior.
- Current WebSocket manager is in-memory, so it is not multi-process safe without Redis Pub/Sub/Streams or similar fanout.

---

## Recommended AI Product Direction

The app is moving toward:

> A collaborative project/task workspace with realtime updates and AI assistance.

The best AI uses are those that help users understand, organize, and act on project activity.

Recommended first AI capabilities:

1. **Project activity summary**
   - Summarize what changed in a project over a time period.
   - Input: Activity Feed events.
   - Output: concise summary + notable blockers/changes.

2. **Task suggestion from project goal**
   - User gives a goal.
   - AI suggests tasks, but does not create them automatically at first.

3. **Blocker detection**
   - AI reviews activity/tasks and suggests likely blockers.

4. **Task prioritization draft**
   - AI suggests ordering/reasons, but user decides.

Avoid initially:

- Autonomous database writes.
- Multi-agent/subagent systems.
- AI directly editing projects/tasks without user approval.
- Using WebSockets as the only place AI progress/result exists.

---

## Architecture Recommendation

Use this architecture for AI work:

```text
User request
  ↓
FastAPI route
  ↓
Create DB job / AI run row
  ↓
Create Activity Feed event: ai_run_requested
  ↓
Enqueue Celery task with run_id or job_id
  ↓
Celery worker starts
  ↓
LangChain/LangGraph executes AI workflow
  ↓
Worker writes result to Postgres
  ↓
Worker creates Activity Feed event: ai_run_completed / ai_run_failed
  ↓
Optional Redis Pub/Sub notification
  ↓
WebSocket clients receive live update
```

Core rule:

> Postgres stores truth. Redis transports messages. Celery executes work. LangChain/LangGraph performs AI reasoning. Activity Feed records what happened.

---

## LangChain vs LangGraph Decision

### Use simple LangChain / direct LLM calls first when:

- The task is one-shot.
- The output can be schema-validated.
- There is no branching or tool loop.
- The user only needs a result, not an interactive workflow.

Examples:

- Summarize recent activity.
- Suggest 5 tasks from a goal.
- Generate a project status update.
- Extract blockers from task descriptions.

### Use LangGraph when:

- The workflow has multiple steps.
- The agent needs tools.
- The workflow may pause for user approval.
- The work should be resumable/checkpointed.
- The graph needs branching or retries.

Examples:

- Analyze project → suggest task changes → wait for approval → apply changes.
- Summarize project → detect blockers → ask user whether to create follow-up tasks.
- Multi-step planning with human-in-the-loop.

Recommended path:

1. Start with simple async AI jobs.
2. Add structured outputs.
3. Add approval before writes.
4. Introduce LangGraph only once workflows need state/branching.

---

## Should This App Use Agents?

Yes, eventually — but not first.

A useful agent in this app should have a clear job:

- Read project/task/activity context.
- Produce structured suggestions.
- Ask for approval before mutating data.
- Record its actions in Activity Feed.

The first “agent” should probably be a constrained workflow, not a fully autonomous agent.

Example first agent:

```text
Project Summary Agent
  Input: project_id, date range
  Reads: project, tasks, activity feed
  Produces:
    - summary
    - changed tasks
    - blockers
    - suggested next actions
  Writes:
    - AI job result
    - Activity Feed event
```

---

## Would Subagents Be Useful?

Subagents can be useful later, but they add complexity.

### Avoid subagents early because they introduce:

- Coordination overhead.
- Higher token cost.
- Conflicting outputs.
- More complex debugging.
- Harder audit trails.

### Subagents may become useful when roles are clearly separable:

1. **Summarizer subagent**
   - Condenses activity and comments.

2. **Planner subagent**
   - Suggests tasks/milestones.

3. **Risk/blocker subagent**
   - Looks for delays, blockers, stale tasks.

4. **Reviewer subagent**
   - Checks proposed AI changes before user approval.

Recommended approach:

```text
Single constrained agent first
↓
Measure where it fails
↓
Only add subagents for clearly distinct responsibilities
```

If subagents are added, each should produce persisted intermediate outputs so users can understand why the final recommendation was made.

---

## Event-Led Structure

AI should fit into the same event-led model as Activity Feed.

Initial AI event types could be:

```text
ai_run_requested
ai_run_started
ai_run_completed
ai_run_failed
ai_suggestion_created
ai_suggestion_approved
ai_suggestion_rejected
```

These should be Activity Feed records, not just WebSocket messages.

Example event:

```json
{
  "project_id": 1,
  "type": "ai_run_completed",
  "message": "AI generated a project activity summary.",
  "data": {
    "job_id": 42,
    "agent_type": "project_summary",
    "model": "...",
    "prompt_version": "project-summary-v1"
  }
}
```

Important design point:

> Store concise rationale, sources, model name, prompt version, and output. Do not store hidden chain-of-thought.

---

## Suggested Data Concepts

Do not implement all of this immediately. These are planning concepts.

### `jobs`

Existing DB-first job table remains useful for background execution.

Possible job types:

```text
project_activity_summary
suggest_project_tasks
detect_project_blockers
prioritize_tasks
```

### Possible future `ai_runs`

If AI grows beyond simple jobs, add a dedicated table:

```text
ai_runs
- id
- project_id
- job_id
- type
- status
- input
- result
- error
- model
- prompt_version
- created_at
- started_at
- completed_at
```

Do not add this until jobs become too generic.

### Activity Feed

Activity remains the durable project history and AI memory source.

AI should read from activity, not scrape arbitrary app state without boundaries.

---

## First AI Vertical Slice

Recommended first slice:

> Async project activity summary.

### User flow

```http
POST /projects/{project_id}/ai/summary
```

Response:

```json
{
  "job_id": 42,
  "status": "pending"
}
```

Then:

```http
GET /jobs/42
```

returns final result.

### Worker flow

```text
Load job by id
↓
Read project activity feed
↓
Call LLM with bounded prompt
↓
Validate structured output
↓
Store result on job
↓
Create activity event
```

### Example result schema

```json
{
  "summary": "This week the project moved from setup to API implementation.",
  "notable_changes": [
    "Tasks API was created",
    "Project model relationship was added"
  ],
  "blockers": [
    "Jobs worker imports are not stable yet"
  ],
  "suggested_next_steps": [
    "Finish project router",
    "Add activity feed events for task transitions"
  ]
}
```

Why this slice first:

- It uses Activity Feed.
- It avoids autonomous writes.
- It fits DB-first jobs.
- It can run through Celery.
- It provides immediate user value.
- It prepares for LangGraph later.

---

## Pub/Sub Plan Preview

Pub/Sub should be treated as delivery, not truth.

### Recommended first Pub/Sub use

After writing an Activity Feed row:

```text
Activity row saved in Postgres
↓
Publish lightweight Redis Pub/Sub message
↓
FastAPI WebSocket process receives message
↓
Loads or forwards event to connected clients
```

Message shape:

```json
{
  "project_id": 1,
  "activity_id": 123,
  "type": "activity.created"
}
```

The Pub/Sub message should contain IDs, not the entire source of truth.

### Redis Pub/Sub is enough if:

- Missed realtime messages can be recovered by REST fetch.
- Activity Feed is stored in Postgres.
- Reconnect clients call `GET /projects/{id}/activity`.

### Redis Streams may be better if:

- Multiple services need durable replay.
- WebSocket workers need consumer groups.
- You need pending message inspection.
- You want at-least-once event processing outside Postgres.

Recommended path:

1. Build Activity Feed in Postgres.
2. Add REST retrieval.
3. Add Redis Pub/Sub for live WebSocket fanout.
4. Only consider Redis Streams if Pub/Sub lossiness becomes a real product problem.

---

## Safety and Trust Rules

AI features should follow these rules:

1. **No silent writes**
   - AI can suggest changes before it can apply changes.

2. **Human approval for mutations**
   - Creating/updating/deleting tasks should require approval at first.

3. **Structured outputs only**
   - Validate AI output with Pydantic/schema before storing.

4. **Permission-scoped context**
   - AI should only read data the user/project is allowed to access.

5. **Traceability**
   - Store model, prompt version, job id, and source activity ids.

6. **Retry/idempotency**
   - Celery retries must not duplicate task creations or activity events.

7. **No hidden chain-of-thought storage**
   - Store concise rationale and citations/provenance instead.

---

## Staged Implementation Plan

### Stage 0: Stabilize foundations

Before AI implementation:

- Finish project/task relationships.
- Finish jobs and Celery worker import path.
- Finish Activity Feed plan/implementation.
- Ensure migrations cover projects, tasks, jobs, and activity.

### Stage 1: Add AI configuration

Add environment/config planning for:

- AI provider API key.
- Default model.
- Prompt version.
- AI timeout.
- AI max tokens/cost limits.
- Optional LangSmith tracing.

### Stage 2: First async AI job

Implement project activity summary as a DB-first job.

No LangGraph yet unless needed.

### Stage 3: Structured outputs

Use schema-validated results for summaries/suggestions.

### Stage 4: Activity Feed integration

Record AI lifecycle events:

- requested
- started
- completed
- failed
- suggestion created

### Stage 5: WebSocket/Pub/Sub progress

Publish AI progress/activity notifications after DB commits.

### Stage 6: LangGraph workflows

Introduce LangGraph when workflows need:

- multiple steps
- checkpointing
- human approval
- retries/resume
- tool use

### Stage 7: Subagents

Only add subagents after one-agent workflows show clear limitations.

---

## Validation Strategy

### Unit tests

- Prompt assembly.
- Output schema validation.
- Activity event creation.
- Permission-scoped retrieval.
- Idempotency keys.

### Integration tests

- Job creation → Celery worker → job completed.
- AI job failure → job failed + activity event.
- Activity Feed retrieval after AI run.
- WebSocket reconnect catches up through REST.

### AI evaluation

- Golden examples for project summaries.
- Replay historical Activity Feed events.
- Compare AI summaries to expected summaries.
- Track accepted/rejected suggestions.

### Security tests

- Prompt injection from task descriptions/comments.
- Cross-project data leakage.
- Unauthorized project access.
- Malformed AI output.

---

## Key Decisions Still Needed

1. Which AI provider/model should be used first?
2. Should the first AI feature be project summary or task suggestions?
3. Should AI results live only in `jobs.result`, or should there be a dedicated `ai_runs` table later?
4. Should LangSmith or another tracing tool be used from the start?
5. Should Pub/Sub use Redis Pub/Sub first, or jump directly to Redis Streams?
6. What AI actions require user approval?
7. Should AI be allowed to create tasks, or only suggest them initially?

---

## Recommended Next Move

Do not add LangGraph immediately.

Recommended order:

1. Finish Activity Feed.
2. Stabilize jobs/Celery worker.
3. Add a simple async AI summary job using structured output.
4. Record AI lifecycle events in Activity Feed.
5. Add Redis Pub/Sub for live Activity Feed/WebSocket delivery.
6. Introduce LangGraph only when workflows need multi-step state or approval.

This keeps the app coherent: event-led first, AI-assisted second, agentic later.
