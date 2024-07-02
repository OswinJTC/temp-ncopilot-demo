from fastapi import FastAPI
from app.routers import api, user_router
from app.db.postgres_database import startup_postgres_event
from app.db.mongo_database import startup_mongo_event
from app.settings import settings  # Update import statement

app = FastAPI()

# Initialize the databases
startup_postgres_event()
startup_mongo_event()

# Include routers
app.include_router(api.router)
app.include_router(user_router.router)

@app.get("/home")
async def read_home():
    return {"message": "Welcome to the nis-llm-data-interface"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
