from dataclasses import dataclass
from enum import StrEnum, auto

from app.tasks.flows import StateMachine


class TaskStatus(StrEnum):
    TODO = auto()
    IN_PROGRESS = auto()
    BLOCKED = auto() 
    COMPLETED = auto()
    CANCELLED = auto()

class TaskEvent(StrEnum):
    START_TASK = auto() 
    BLOCK_TASK = auto()
    COMPLETE_TASK = auto()
    UNBLOCK_TASK = auto()
    REOPEN_TASK = auto()
    CANCEL_TASK = auto() 

@dataclass(frozen=True)
class TaskCtx:
    task_id: int
    name: str
    
 
#Task States for transition of tasks. 

task_state: StateMachine[TaskStatus, TaskEvent, TaskCtx] = StateMachine()

@task_state.transition(TaskStatus.TODO, TaskEvent.START_TASK, TaskStatus.IN_PROGRESS)
def begin_tasl(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} started: {ctx.name}"

@task_state.transition(
    (TaskStatus.TODO, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED),
    TaskEvent.CANCEL_TASK,
    TaskStatus.CANCELLED,
)
def cancel_task_todo(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} cancelled: {ctx.name}"

@task_state.transition(TaskStatus.IN_PROGRESS, TaskEvent.COMPLETE_TASK, TaskStatus.COMPLETED)
def complete_task(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} completted: {ctx.name}"

@task_state.transition(TaskStatus.IN_PROGRESS, TaskEvent.BLOCK_TASK, TaskStatus.BLOCKED)
def block_task(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} blocked: {ctx.name}"

@task_state.transition(TaskStatus.BLOCKED, TaskEvent.UNBLOCK_TASK, TaskStatus.IN_PROGRESS)
def unblock_task(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} unblocked: {ctx.name}"


@task_state.transition(TaskStatus.COMPLETED, TaskEvent.REOPEN_TASK, TaskStatus.TODO)
def reopen_task(ctx: TaskCtx) -> str: 
    return f"Task {ctx.task_id} reopened: {ctx.name}"

