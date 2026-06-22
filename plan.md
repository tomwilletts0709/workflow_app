# Implementation Plan

## Goal
Design an Activity Feed vertical that records important project/task events in the database, exposes them through an API, and leaves a clean path for WebSocket broadcasting and future AI summaries.

## Tasks
1. **Confirm activity feed scope and first event types**: Keep the first slice system-generated only; do not allow users to manually create feed entries yet.
   - File: planning decision only
   - Changes: Agree the initial feed records these events: `project_created`, `task_created`, `task_status_changed`; defer comments, job events, AI events, and user-authored updates.
   - Acceptance: A reviewer can describe exactly which app actions create activity rows and which do not.

2. **Create an activity domain package**: Add a new module for the activity feed instead of mixing feed logic directly into tasks/projects.
   - File: `app/activity/`
   - Changes: Create package files for model/schema, enum, repo, service, and router.
   - Acceptance: Activity code has a clear home and follows the existing router → service → repo pattern.

3. **Define activity event types**: Use an enum for known activity types so event names stay consistent.
   - File: `app/activity/enums.py`
   - Changes: Define `ActivityType` with at least `PROJECT_CREATED`, `TASK_CREATED`, `TASK_STATUS_CHANGED`.
   - Acceptance: Activity rows cannot silently drift between string spellings such as `taskCreated`, `task_created`, and `TASK_CREATED`.

4. **Add the Activity database model and Pydantic schemas**: Store a project-scoped feed item with optional task context.
   - File: `app/activity/models.py`
   - Changes: Add SQLAlchemy `Activity` model with fields: `id`, `project_id`, `task_id`, `type`, `message`, `metadata`, `created_at`; add `ActivityRead` schema.
   - Acceptance: The model can represent project-only activity and task-related activity.

5. **Use conservative relationship rules**: Tie activity to projects, but do not let activity rows control task/project lifecycle.
   - File: `app/activity/models.py`
   - Changes: `project_id` should be a required `ForeignKey` to projects. `task_id` should be nullable because some events are project-level. Decide whether project deletion cascades activity deletion alongside tasks.
   - Acceptance: `project_created` can exist without a task, while `task_created` and `task_status_changed` can include a task id.

6. **Create an Alembic migration for activity**: Add the new table in the database.
   - File: `migrations/versions/<new_revision>_create_activity_table.py`
   - Changes: Create `activity` or `activities` table with indexes on `project_id` and `created_at`; include enum handling if using SQLAlchemy enum.
   - Acceptance: `alembic upgrade head` creates the activity table without manually editing the database.

7. **Build ActivityRepo**: Keep database access isolated in a repository.
   - File: `app/activity/repo.py`
   - Changes: Add methods `create(...)` and `list_for_project(project_id, limit, offset)` ordered newest-first or oldest-first by explicit decision.
   - Acceptance: No router directly creates activity rows through SQLAlchemy.

8. **Build ActivityService**: Centralize feed message construction and activity creation.
   - File: `app/activity/service.py`
   - Changes: Add methods like `project_created(project)`, `task_created(task)`, and `task_status_changed(task, old_status, new_status)` that call repo with consistent messages/metadata.
   - Acceptance: Task/project services can record activity by calling semantic methods instead of building raw dictionaries everywhere.

9. **Add ActivityRouter for project feed retrieval**: Expose feed reads through project-scoped endpoint.
   - File: `app/activity/router.py`
   - Changes: Add `GET /projects/{project_id}/activity` or mount an activity router with a project-scoped path; support basic pagination/limit.
   - Acceptance: API users can retrieve the activity feed for a project without querying tasks directly.

10. **Mount the activity endpoint**: Register the activity router in the FastAPI app.
   - File: `app/main.py`
   - Changes: Include the activity router with a route shape that does not conflict with `app/projects/router.py`.
   - Acceptance: The app imports and the activity endpoint is visible in FastAPI docs.

11. **Record project-created activity**: Hook activity creation into the project creation flow.
   - File: `app/projects/service.py`
   - Changes: After a project is created, create a `PROJECT_CREATED` activity row in the same request flow.
   - Acceptance: Creating a project creates exactly one project-created feed item.

12. **Record task-created activity**: Hook activity creation into the task creation flow.
   - File: `app/tasks/service.py`
   - Changes: After a task is created, create a `TASK_CREATED` activity row using `task.project_id` and `task.id`.
   - Acceptance: Creating a task under a project creates exactly one task-created feed item.

13. **Record task-status-changed activity**: Preserve the old task status before transition and record the change after persistence.
   - File: `app/tasks/service.py`
   - Changes: In `transition`, capture `old_status = task.status` before state-machine handling, then record `TASK_STATUS_CHANGED` after `repo.update_status(...)` succeeds.
   - Acceptance: A status transition feed item includes old status and new status in metadata.

14. **Keep WebSocket broadcast optional for the first slice**: Do not require realtime broadcast for the first implementation, but design the activity service so it can broadcast later.
   - File: `app/activity/service.py`, `app/core/websockets.py`
   - Changes: First implementation writes DB rows only. Later extension can broadcast the newly-created `ActivityRead` payload through `manager.broadcast_to_project(project_id, payload)`.
   - Acceptance: Activity Feed works through REST even if no WebSocket clients are connected.

15. **Add tests for the vertical**: Test feed creation and retrieval around the three initial event types.
   - File: `tests/test_activity.py` or related test files
   - Changes: Add tests for project creation activity, task creation activity, task status transition activity, and project feed ordering.
   - Acceptance: Tests prove the feed is system-generated and project-scoped.

16. **Validate app-level integration**: Run focused checks after implementation.
   - File: not applicable
   - Changes: Run `uv run pytest -q` if baseline permits; otherwise run focused tests for activity and document unrelated failures.
   - Acceptance: Activity implementation has evidence from tests or clear notes about pre-existing blockers.

## Files to Modify
- `app/main.py` - mount the activity feed router.
- `app/projects/service.py` - create activity after successful project creation.
- `app/tasks/service.py` - create activity after task creation and task status transitions.
- `app/projects/models.py` - may need final relationship/table-name consistency before activity foreign keys are reliable.
- `app/tasks/models.py` - may need final `project_id` foreign key consistency before task activity can be reliable.
- `pyproject.toml` - no new dependency expected for activity feed itself.

## New Files
- `app/activity/__init__.py` - package marker.
- `app/activity/enums.py` - `ActivityType` enum.
- `app/activity/models.py` - SQLAlchemy activity model and Pydantic schemas.
- `app/activity/repo.py` - activity persistence and feed queries.
- `app/activity/service.py` - semantic activity creation methods and future broadcast boundary.
- `app/activity/router.py` - project activity feed API endpoint.
- `migrations/versions/<revision>_create_activity_table.py` - database migration for activity table.
- `tests/test_activity.py` - focused tests for the activity vertical.

## Dependencies
- Task 4 depends on Task 3 because the model needs stable activity event types.
- Task 6 depends on Tasks 4 and 5 because the migration should match the final model and foreign key policy.
- Tasks 7 and 8 depend on Task 4 because repo/service need the model.
- Task 9 depends on Tasks 7 and 8 because the router should call the service/repo layer.
- Tasks 11-13 depend on Task 8 because project/task services should call semantic activity service methods.
- Task 15 depends on Tasks 9 and 11-13 because tests need the API and event hooks.
- Project/task model consistency is a prerequisite for reliable foreign keys and project-scoped activity.

## Risks
- The current project/task relationship is still in progress; `Project.__tablename__`, `Task.project_id` foreign key, and `relationship(back_populates=...)` must agree before activity foreign keys are dependable.
- Existing jobs/project code has import and naming issues in the broader app; full `pytest` may fail for unrelated reasons until those are cleaned up.
- `metadata` is a convenient activity field name, but SQLAlchemy declarative models can have naming conflicts around `metadata`; prefer a safer column attribute name such as `data` mapped to column name `metadata`, or `details`.
- If activity rows cascade-delete with projects, the feed is not a permanent audit log. If permanent audit history is desired, do not cascade-delete activities. This decision needs explicit confirmation.
- Creating activity rows inside the same service method as the domain action is simple, but not fully event-driven yet. A later event dispatcher can be introduced after the feed proves useful.
- WebSocket broadcasting should be deferred until DB-backed activity works; otherwise realtime messages may vanish without a persistent feed.
- If multiple side effects are added later, transaction boundaries matter: domain row creation and activity row creation should either both commit or have a clear failure policy.
