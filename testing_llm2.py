import json
import requests
import logging
import os
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from langchain_community.llms import HuggingFaceEndpoint
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from linkinpark.lib.common.postgres_connector import PostgresConnectorFactory
import psycopg2

class QueryInput(BaseModel):
    input_text: str

class QueryOutput(BaseModel):
    output_text: str

class DbOutput(BaseModel):
    DbOutput: list

class RequestBody(BaseModel):
    input_text: str
    dboutput: DbOutput

# Initialize the FastAPI app
app = FastAPI()

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

# Initialize the HuggingFaceEndpoint
llm = HuggingFaceEndpoint(
    endpoint_url="http://127.0.0.1:5566/",  # LLM endpoint running on GPU server
    max_new_tokens=512,
    temperature=0.5,
    top_k=50,
    top_p=0.95,
    repetition_penalty=1.05,
    huggingfacehub_api_token="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",
)

# System prompt initialization
INIT_SYSTEM_PROMPT = "你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。"

# Adjusted prompt template
BASIC_PROMPT1 = """
你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。
以下是可以使用的工具選項schema規定:
{tools}
###
question: {user_input}
data: {db_output}

請根據上面的資料生成自然語言回覆，結果請遵守下面規則：
- 以親切的語氣向用戶回覆
- 只能使用定義的參數，不可以自行增加
- 按照schema輸出string
- data: {db_output} 代表獲得的數據，請全部輸出
- 只回傳 data: {db_output} 的數據
- 血壓：SYS
- 體溫：TP
- 血氧：SPO2
- 脈搏：PR


OUTPUT: string
"""

tools = """
[{
    "response": "親愛的用戶您好，"名字"過去"時間範圍"的"數據類型"為 "獲得的數據"。謝謝您!"
}]
"""

def build_prompt(tools: str, user_input: str, db_output: str) -> str:
    template = ChatPromptTemplate.from_template(
        INIT_SYSTEM_PROMPT + "\n" + BASIC_PROMPT1
    )
    formatted_prompt = template.format_prompt(tools=tools, user_input=user_input, db_output=db_output)
    return formatted_prompt.to_string()

@app.post("/query", response_model=QueryOutput)
def process(request: RequestBody):
    try:
        input_text = request.input_text
        db_output = request.dboutput.DbOutput
        print(f"Received input: {input_text}")
        print(f"Received dboutput: {db_output}")

        # Convert dboutput to string for prompt
        db_output_str = json.dumps(db_output)

        # Build prompt with data and user input
        formatted_prompt = build_prompt(tools, input_text, db_output_str)

        chain = llm | StrOutputParser()
        summary = chain.invoke(formatted_prompt).strip()

        # Ensure response is well-formatted and meaningful
        if not summary or summary.lower() == 'none':
            raise ValueError("Received an invalid response from the LLM")

        # Attempt to extract and format the response
        if summary.startswith('"') and summary.endswith('"'):
            summary = summary[1:-1]

        return {"output_text": summary}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to process the request. Please try again.")
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
