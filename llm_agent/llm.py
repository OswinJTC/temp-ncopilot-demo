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
         
        tools_content = json.loads(tools_from_db[0].strip().replace('\n', '').replace('\r', ''))
        tools = json.dumps(tools_content, indent=4, ensure_ascii=False)
         

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



def convert_to_nl(input_text: str, request: RequestBody):
    try:

        query_type = classify_query(input_text)
        print(query_type)
        BASIC_PROMPT1 = get_base_prompt_2(query_type)
        print(BASIC_PROMPT1)
        
        tool2_from_db = get_tools_2(query_type)
         
        tools_content = json.loads(tool2_from_db[0].strip().replace('\n', '').replace('\r', ''))
        tool2 = json.dumps(tools_content, indent=4, ensure_ascii=False)
         

  
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
