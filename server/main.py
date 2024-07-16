import uvicorn
import logging, json
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from server.postgres_database import startup_postgres_event
from data_interface.db.mongo_database import startup_mongo_event
from llm_agent.llm import process_input_text, convert_to_nl
from data_interface.routers import RBAC_test
from auth0.auth import check_permission, get_token_data
from auth0.models import TokenData
from llm_agent.models import HeHeDbOutput, RequestBody


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
def agent_main(input_data: InputData, token_data: TokenData = Depends(get_token_data)):
    try:
        response1 = process_input_text(input_data.input_text, token_data)

 
        print(response1)

        #取出連結，分頭傳遞
        temp_link = next((item for item in response1 if "link" in item), None)
        if temp_link:
            response1.remove(temp_link)

      
        #model construction
        db_output_obj = HeHeDbOutput(DbOutput=response1)
        request_body = RequestBody(input_text=input_data.input_text, dboutput=db_output_obj, link=temp_link["link"])
        formatted_request_body = json.dumps(request_body.dict(), indent=2, ensure_ascii=False)

        response2 = convert_to_nl(formatted_request_body)

        print(f"快結束了")
        print(response2)

        return response2
    
    except HTTPException as e:
        logging.error(f"回到最初的起點: {e.detail}")
        raise e  # Re-raise the HTTPException to propagate it back to the client
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)