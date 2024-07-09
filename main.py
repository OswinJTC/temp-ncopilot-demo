import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

from postgres_database import startup_postgres_event
from data_interface.db.mongo_database import startup_mongo_event
from llm_agent.llm import process_input_text

# Initialize the FastAPI app
app = FastAPI()

class InputData(BaseModel):
    input_text: str

# CORS configuration
origins = [
    "http://localhost:3000",  # Frontend URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the databases
startup_postgres_event()
startup_mongo_event()

@app.post("/main-input-processing")
def agent_main(input_data: InputData):
    try:
        response = process_input_text(input_data.input_text)
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
