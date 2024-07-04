import json
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from linkinpark.lib.common.logger import getLogger
from jubollm.base_service import BaseService
import requests

APP_ENV = os.environ.get("APP_ENV", "dev")
GENERATION_LOGGER = getLogger(
    name="ai-llm-generation",
    labels={"env": APP_ENV}
)

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
        url = "http://192.168.128.138:8000/initial-layer"  # Replace with your POST endpoint
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
