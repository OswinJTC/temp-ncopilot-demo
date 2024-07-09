from fastapi import HTTPException
import logging
import json
from llm_agent.config_utils import server_init_config
from llm_agent.tools_prompts.tools_prompts_CRUD import get_base_prompt, get_tools 
from llm_agent.service import Service, classify_query 

def process_input_text(input_text: str):
    try:
        # Classify the query to determine which prompt and tools to fetch
        query_type = classify_query(input_text)



        base_prompt = get_base_prompt(query_type)

         


        tools = get_tools(query_type)

        



        logging.debug(f"Classified query type: {query_type}")
        logging.debug(f"Base prompt: {base_prompt}")
        logging.debug(f"Tools: {tools}")

        if not base_prompt or not tools:
            raise HTTPException(status_code=500, detail="Failed to retrieve prompt or tools from the database")

        service = Service(llm_config=server_init_config)
        response = service.generate(tools, input_text, base_prompt)
        return response
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
