from fastapi import FastAPI
from app.routers import api

app = FastAPI()

app.include_router(api.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the nis-llm-data-interface"}