import json
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_agent.base_service import BaseService
from data_interface.routers.api import execute_queries

INIT_SYSTEM_PROMPT = "你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。"

def classify_query(query):
    if any(keyword in query for keyword in ["血壓", "脈搏", "體溫", "血氧"]):
        return "vitalsigns"
    elif any(keyword in query for keyword in ["預約", "會議", "安排"]):
        return "appointments"
    else:
        return "default"

class Service(BaseService):
    def __init__(self, llm_config):
        super().__init__(**llm_config)

    def build_prompt(self, tools: str, user_input: str, base_prompt: str) -> str:
        template = ChatPromptTemplate.from_template(INIT_SYSTEM_PROMPT + "\n" + base_prompt)
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
                logging.error(f"Error decoding JSON: {e}")
                logging.error(f"Raw JSON string: {json_str}")
                return {}
        else:
            logging.error("No JSON object found in the response")
            logging.error(f"Raw response: {response}")
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

    def generate(self, tools: str, user_input: str, base_prompt: str) -> dict:
        formatted_prompt = self.build_prompt(tools, user_input, base_prompt)

        logging.debug(f"現在來 Formatted Prompt: {formatted_prompt}")

        chain = self.llm | StrOutputParser()
        summary = chain.invoke(formatted_prompt) #最希望這邊給出來就是完美的

        logging.debug(f"Raw response from LLM: {summary}")

        raw_json_output = self.parse_response(summary.strip())
        logging.debug(f"Parsed JSON output: {raw_json_output}")

        cleaned_json_output = self.clean_json_output(raw_json_output)
        logging.debug(f"Cleaned JSON output: {cleaned_json_output}")

        queries = self.split_queries(cleaned_json_output)
        logging.info(f"Split queries: {queries}")

        # Directly call the execute_queries function with the queries
        results = execute_queries({"queries": queries})
        
        return results
