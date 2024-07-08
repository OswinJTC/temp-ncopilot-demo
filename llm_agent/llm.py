import os
import json
import uvicorn
import requests
import yaml
import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from linkinpark.lib.common.logger import getLogger
from linkinpark.lib.common.secret_accessor import SecretAccessor
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import HuggingFaceEndpoint

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

def interpolate(config, environment):
    for key, value in config.items():
        if isinstance(value, str):
            config[key] = value.format(**environment)
        elif isinstance(value, dict):
            interpolate(value, environment)

def load_yaml_with_environment(filename, environment):
    with open(filename, 'r') as file:
        config = yaml.safe_load(file)

    interpolate(config, environment)
    return config

# Load configuration
APP_ENV = os.environ.get("APP_ENV", "dev")

SERVICE_LOGGER = getLogger(
    name="ai-llm-service",
    labels={"env": APP_ENV}
)


current_dir = os.path.dirname(os.path.abspath(__file__))


config_path = os.path.join(current_dir, "config", "server_init_local.yaml")


if not os.path.exists(config_path):
    raise FileNotFoundError(f"Configuration file not found: {config_path}")

server_init_config = load_yaml_with_environment(config_path, {'APP_ENV': APP_ENV})



unsupported_params = ['max_new_tokens', 'repetition_penalty', 'temperature', 'top_k', 'top_p']
filtered_config = {k: v for k, v in server_init_config.items() if k not in unsupported_params}
print("Filtered configuration for HuggingFaceEndpoint:", filtered_config)  # Debug print


class BaseService:
    def __init__(self, service_name: str, llm_source: str = 'local', **kwargs):
        self.llm_source = llm_source
        self.generation_params = kwargs
        self.service_name = service_name
        self.service_id = uuid.uuid4().hex
        self.llm = HuggingFaceEndpoint(**self.generation_params)
        self.auth_token = self._get_token()
        self.auth_headers = {"Authorization": f"Bearer {self.auth_token}"}
        self.llm.client.headers = self.auth_headers
        self._log_service()

    def _get_token(self):
        url = "https://ai-model-dev.jubo.health/api/v1/get-token"
        username = SecretAccessor().access_secret('local-gpu-username')
        password = SecretAccessor().access_secret('local-gpu-password')
        data = {"username": username, "password": password}
        response = requests.post(url, data=json.dumps(data))
        return response.json()['token']

    def _log_service(self):
        llm_info_request = requests.get(
            url=self.generation_params['endpoint_url'] + '/info',
            headers=self.auth_headers
        )
        llm_info = llm_info_request.json()
        SERVICE_LOGGER.info({
            "message": f"initialized new local service: {self.service_name}",
            "metrics": {"called": 1},
            "labels": {
                'service_id': self.service_id,
                'service_name': self.service_name,
                'llm_source': self.llm_source, 
                'llm_info': json.dumps(llm_info),
                'generation_params': json.dumps(self.generation_params)
            }
        })

class Service(BaseService):
    def __init__(self, llm_config):
        super().__init__(**llm_config)

    def build_prompt(self, tools: str, user_input: str) -> str:
        template = ChatPromptTemplate.from_template(
            INIT_SYSTEM_PROMPT + "\n" + BASIC_PROMPT1
        )
        formatted_prompt = template.format_prompt(tools=tools, user_input=user_input)
        return formatted_prompt.to_string()

    def parse_response(self, response: str) -> dict:
        start_idx = response.find("{")
        end_idx = response.rfind("}") + 1
        if start_idx != -1 and end_idx != -1:
            json_str = response[start_idx:end_idx]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
                print(f"Raw JSON string: {json_str}")
                return {}
        else:
            print("No JSON object found in the response")
            print(f"Raw response: {response}")
            return {}

    def clean_json_output(self, json_output: dict) -> dict:
        retrieval_mapping = {
            "血壓": "SYS",
            "脈搏": "PR",
            "體溫": "TP",
            "血氧": "SPO2"
        }

        if "conditions" in json_output:
            conditions = json_output["conditions"]
            if "duration" in conditions and conditions["duration"] in ["0", 0]:
                conditions["duration"] = ""
            if "sortby" in conditions:
                sortby = conditions["sortby"]
                if isinstance(sortby, dict):
                    conditions["sortby"] = {retrieval_mapping.get(k.split("：")[0], k.split("：")[0]): v for k, v in sortby.items()}
                    conditions["sortby"] = {k: v for k, v in conditions["sortby"].items() if v in ["ascending", "descending"]}
                else:
                    conditions["sortby"] = ""
            if "limit" in conditions and conditions["limit"] in ["0", 0, "all"]:
                conditions["limit"] = ""

        if "retrieve" in json_output:
            json_output["retrieve"] = [retrieval_mapping.get(field.split("：")[0], field.split("：")[0]) for field in json_output["retrieve"]]

        if "lastName" in json_output and "firstName" in json_output:
            full_name = json_output.pop("lastName") + json_output.pop("firstName")
            json_output["fullName"] = full_name

        return json_output

    def split_queries(self, json_output: dict) -> list:
        queries = []
        conditions = json_output.get("conditions", {})
        duration = conditions.get("duration", "")
        sortby = conditions.get("sortby", {})
        limit = conditions.get("limit", "")

        for field in json_output["retrieve"]:
            query = {
                "interface_type": json_output["interface_type"],
                "patientName": json_output["fullName"],
                "retrieve": [field],
                "conditions": {
                    "duration": duration,
                    "sortby": {field: sortby[field]} if field in sortby and sortby[field] in ["ascending", "descending"] else "",
                    "limit": limit
                }
            }
            queries.append(query)

        return queries

    def send_post_request(self, queries):
        url = "http://127.0.0.1:8000/initial-layer"  # Replace with your POST endpoint
        headers = {"Content-Type": "application/json"}
        data = {"queries": queries}
        response = requests.post(url, headers=headers, json=data)
        return response

    def generate(self, tools: str, user_input: str) -> dict:
        formatted_prompt = self.build_prompt(tools, user_input)

        chain = self.llm | StrOutputParser()
        summary = chain.invoke(formatted_prompt)

        raw_json_output = self.parse_response(summary.strip())
        cleaned_json_output = self.clean_json_output(raw_json_output)
        queries = self.split_queries(cleaned_json_output)

        return self.send_post_request(queries)

# System prompt initialization
INIT_SYSTEM_PROMPT = "你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。"

# Basic prompt template
BASIC_PROMPT1 = """
以下是可以使用的工具選項schema規定:
{tools}
###
question: {user_input}

output的結果請遵守下面規則，如果沒有符合的工具請output none：
- 將可以解決問題的工具選項輸出成名稱以及參數的json格式
- 從question之中取得定義的參數填入json之中
- 只能使用定義的參數，不可以自行增加
- 只寫json的部分，不要有多餘的描述
- 按照schema輸出json格式
- 只做我叫你做的事情
- 將日期都轉換成天數

OUTPUT: json
"""

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

        service = Service(llm_config= filtered_config)
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
