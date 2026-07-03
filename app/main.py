from fastapi import FastAPI, WebSocket, APIRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limiting import limiter 
import uvicorn

from app.tasks.router import task_router
from app.core.websockets import websocket_router
from app.jobs.router import job_router
from app.projects.router import project_router
from app.activity.router import activity_router
from app.search.router import search_router

app = FastAPI()

app.include_router(task_router, prefix="/tasks")
app.include_router(websocket_router)
app.include_router(job_router, prefix="/jobs")
app.include_router(project_router, prefix='/projects')
app.include_router(activity_router)
app.include_router(search_router, prefix='/search')

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/")
async def start_app(): 
    return {"App": "Is Running"}

if __name__ == "__main__": 
    uvicorn.run("app.main:app", port=8000, reload=True)
