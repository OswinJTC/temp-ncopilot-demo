import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from server.postgres_database import startup_postgres_event
from data_interface.db.mongo_database import startup_mongo_event
from llm_agent.llm import process_input_text
from data_interface.routers import RBAC_test

from auth0.auth import check_permission
from auth0.models import TokenData

app = FastAPI()

class InputData(BaseModel):
    input_text: str

# Allow CORS for specific origins
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow only specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Initialize the databases
startup_postgres_event()
startup_mongo_event()

app.include_router(RBAC_test.router)


@app.post("/main-processing")
def agent_main(input_data: InputData, token_data: TokenData = Depends(check_permission("juboAgent_submit:query"))):
    try:
        response = process_input_text(input_data.input_text)
        
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
