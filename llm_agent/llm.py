from fastapi import HTTPException
import logging
import json
from llm_agent.config_utils import server_init_config
from llm_agent.prompts_factory import get_base_prompt_1, get_tools_1, get_base_prompt_2, get_tools_2
from llm_agent.service import Service, classify_query
from llm_agent.service2 import Service2 
from pydantic import BaseModel
from auth0.models import TokenData
from llm_agent.models import HeHeDbOutput, RequestBody

def process_input_text(input_text: str, token_data: TokenData):
    try:
        query_type = classify_query(input_text)
        base_prompt = get_base_prompt_1(query_type)
        tools_from_db = get_tools_1(query_type)
        print("前1")
        print(tools_from_db)
        tools_content = json.loads(tools_from_db[0].strip().replace('\n', '').replace('\r', ''))
        tools = json.dumps(tools_content, indent=4, ensure_ascii=False)
        print("後1")
        print(tools_from_db)

        print(base_prompt)
        print(tools)

        #logging.debug(f"Classified query type: {query_type}")

        if not base_prompt or not tools:
            raise HTTPException(status_code=500, detail="Failed to retrieve prompt or tools from the database")

        service = Service(llm_config=server_init_config)
        response = service.generate(tools, input_text, base_prompt, token_data)
        return response
    except HTTPException as e:
        logging.error(f"An error occurred during input processing: {e.detail}")
        raise e  # Re-raise the HTTPException to propagate it back to the client
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))



 
#===


BASIC_PROMPT1 = """
你是一個人工智慧助理。請依照使用者提出的需求輸出對應的結果。
以下是可以使用的工具選項schema規定:
{tool2}
###
question: {user_input}
data: {db_output}
link: {link}

請根據上面的資料生成自然語言回覆，結果請遵守下面規則：
- 以親切的語氣向用戶回覆
- 只能使用定義的參數，不可以自行增加
- 按照schema輸出string
- data: {db_output} 代表獲得的數據，請全部輸出
- 只回傳 data: {db_output} 的數據，和 link: {link}
- 血壓：SYS
- 體溫：TP
- 血氧：SPO2
- 脈搏：PR

OUTPUT: string
"""

tool2 = """
[{
    "response": "親愛的用戶您好，"名字"過去"時間範圍"的"數據類型"為 "獲得的數據"。謝謝您!"資料連結""
}]
"""

def convert_to_nl(input_text: str, request: RequestBody):
    try:

        query_type = classify_query(input_text)
        print("嗨嗨嗨二")
        print(query_type)
        BASIC_PROMPT1 = get_base_prompt_2(query_type)
        print(BASIC_PROMPT1)
        
        tool2_from_db = get_tools_2(query_type)
        print("前2")
        print(tool2_from_db)
        tools_content = json.loads(tool2_from_db[0].strip().replace('\n', '').replace('\r', ''))
        tool2 = json.dumps(tools_content, indent=4, ensure_ascii=False)
        print("後2")
        print(tool2)

  
        if not BASIC_PROMPT1 or not tool2:
            raise HTTPException(status_code=500, detail="Failed to retrieve prompt or tool2 from the database")

        service = Service2(llm_config=server_init_config)
        response = service.generate(tool2, BASIC_PROMPT1, request)
        return response
    except HTTPException as e:
        logging.error(f"An error occurred during input processing: {e.detail}")
        raise e  # Re-raise the HTTPException to propagate it back to the client
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
