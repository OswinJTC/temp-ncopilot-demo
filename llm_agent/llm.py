from fastapi import HTTPException, Depends
import logging
import json
from llm_agent.config_utils import server_init_config
from llm_agent.prompts_factory import get_base_prompt, get_tools 
from llm_agent.service import Service, classify_query 
from auth0.auth import check_role
from auth0.models import TokenData

def process_input_text(input_text: str):
    try:
        # Classify the query to determine which prompt and tools to fetch
        query_type = classify_query(input_text)


        #base_prompt = get_base_prompt(query_type)

        base_prompt = """
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
- 將使用者的請求解析為全名（fullName）、需要檢索的欄位（retrieve）、以及條件（conditions）
- 條件包括限制（limit）、排序（sortby）和時間範圍（duration）。
- 只做我叫你做的事情
- 將日期都轉換成天數
- 血壓：SYS
- 體溫：TP
- 血氧：SPO2
- 脈搏：PR

OUTPUT: json
"""

        #tools = get_tools(query_type)

        tools = """
            {
                "interface_type": "vitalsigns",
                "patientName": "名字",
                "retrieve": ["所需關鍵字"],
                "conditions": {
                    "duration": "持續時間（天）",
                    "sortby": {"排序字段": "排序方式"},
                    "limit": "限制數量"
                }

            }
    """

        logging.debug(f"Classified query type: {query_type}")
        

        if not base_prompt or not tools:
            raise HTTPException(status_code=500, detail="Failed to retrieve prompt or tools from the database")

        service = Service(llm_config=server_init_config)
        response = service.generate(tools, input_text, base_prompt)
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


#哈囉你好。可以麻煩請你給我憨斑斑三個月內前三高的體溫嗎？謝謝喔感恩你～～～