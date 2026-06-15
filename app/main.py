from fastapi import FastAPI, WebSocket, APIRouter
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from .rate_limiting import limiter 
import uvicorn

from app.tasks.router import task_router

app = FastAPI()

app.include_router(task_router, prefix="/tasks")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def start_app(): 
    return {"App": "Is Running"}

if __name__ == "__main__": 
    uvicorn.run("app.main:app", port=8000, reload=True)
