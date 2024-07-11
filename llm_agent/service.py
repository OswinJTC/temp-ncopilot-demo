import json
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_agent.base_service import BaseService
from data_interface.routers.interface_primary import execute_query

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


     

    def generate(self, tools: str, user_input: str, base_prompt: str) -> dict:
        formatted_prompt = self.build_prompt(tools, user_input, base_prompt)

        logging.debug(f"餵給 LLM 的Formatted Prompt: {formatted_prompt}")

        chain = self.llm | StrOutputParser()
        summary = chain.invoke(formatted_prompt) #最希望這邊給出來就是完美的

        logging.debug(f"就是這個啦 Raw response from LLM: {summary}")


        raw_json_output = self.parse_response(summary.strip())

        results = execute_query(raw_json_output)
        
        return results
