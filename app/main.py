from fastapi import FastAPI, WebSocket, APIRouter
import uvicorn

from app.tasks.router import task_router

app = FastAPI()

app.include_router(task_router, prefix="/tasks")


@app.get("/")
async def start_app(): 
    return {"App": "Is Running"}

if __name__ == "__main__": 
    uvicorn.run("app.main:app", port=8000, reload=True)

 