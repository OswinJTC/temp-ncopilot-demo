import os
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from jubollm.jubo_agent.lib.service import Service 
from jubollm.common.utils import load_yaml_with_environment

# Initialize the FastAPI app
app = FastAPI()

class QueryInput(BaseModel):
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

# Load configuration
APP_ENV = os.environ.get("APP_ENV", "dev")
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, "..", "config", "server_init_local.yaml")
if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

server_init_config = load_yaml_with_environment(config_path, {'APP_ENV': APP_ENV})

# Initialize the Service
service = Service(server_init_config)

@app.post("/process-input")
def process_input(input: QueryInput):
    tools = """
    [{
        "interface_type": "vitalsigns",
        "fullName": "用戶的全名",
        "retrieve": ["所需的數據字段，例如: 血壓：SYS, 脈搏：PR, 體溫：TP, 血氧：SPO2"],
        "conditions": {
            "duration": "持續時間（天）",
            "sortby": {"排序字段": "排序方式"},
            "limit": "限制數量"
        }
    }]
    """

    try:
        print(f"Received input: {input.input_text}")

        response = service.generate(tools, input.input_text)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error in post_response: {response.status_code}, {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.text)
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
