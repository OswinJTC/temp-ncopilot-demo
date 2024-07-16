import json
import logging
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from llm_agent.base_service import BaseService
from fastapi import HTTPException
from pydantic import BaseModel
from llm_agent.models import HeHeDbOutput, RequestBody


INIT_SYSTEM_PROMPT = "你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。"


class Service2(BaseService):
    def __init__(self, llm_config):
        super().__init__(**llm_config)

    def build_prompt(self, tool1: str, input_text: str, db_output: str, BASIC_PROMPT1: str, link: str) -> str:
        template = ChatPromptTemplate.from_template(
            INIT_SYSTEM_PROMPT + "\n" + BASIC_PROMPT1
        )
        formatted_prompt = template.format_prompt(tool1=tool1, user_input=input_text, db_output=db_output, link=link)
        print(formatted_prompt.to_string())
        return formatted_prompt.to_string()

    def generate(self, tool1: str, BASIC_PROMPT1: str, request: RequestBody):
        try:

            data = json.loads(request)
            input_text = data["input_text"]
            db_output = data["dboutput"]["DbOutput"]
            link = data["link"]
            print(f"Received input: {input_text}")
            print(f"Received dboutput: {db_output}")
            print(f"Received link: {link}")

            # Convert dboutput to string for prompt
            db_output_str = json.dumps(db_output)

          
            formatted_prompt = self.build_prompt(tool1, input_text, db_output_str, BASIC_PROMPT1, link)
            chain = self.llm | StrOutputParser()
            summary = chain.invoke(formatted_prompt).strip()

 
            if not summary or summary.lower() == 'none':
                raise ValueError("Received an invalid response from the LLM")

     
            if summary.startswith('"') and summary.endswith('"'):
                summary = summary[1:-1]

            return {"output_text": summary}
        except Exception as e:
            print(f"Error: {e}")
            raise HTTPException(status_code=500, detail="Failed to process the request. Please try again.")
