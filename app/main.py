from fastapi import FastAPI
from app.routers import api

app = FastAPI()

app.include_router(api.router)

@app.get("/home")
async def read_home():
    return {"message": "Welcome to the nis-llm-data-interface"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
