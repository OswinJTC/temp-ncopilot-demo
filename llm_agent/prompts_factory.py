import logging
from server.postgres_database import get_db_connector

def get_tools_1(query_type: str):

    db_connector = get_db_connector()
    
    try:
        columns, _ = db_connector.get_columns('llm_tools')
        all_data = db_connector.select_values('llm_tools', columns)
        tools_content_list = [row['content'] for row in all_data if row['query_type'] == query_type]
        
        return tools_content_list if tools_content_list else None
    except Exception as e:
        logging.error(f"Error fetching tools: {e}")
        return None
    

def get_base_prompt_1(query_type: str):
    
    db_connector = get_db_connector()
    
    try:
        
        columns, _ = db_connector.get_columns('llm_base_prompts')
        all_data = db_connector.select_values('llm_base_prompts', columns)
        prompt = next((row['content'] for row in all_data if row['query_type'] == query_type), None)
        
        if prompt is None:
            logging.error(f"No base prompt found for query type: {query_type}")
            return None
        
        return prompt
    except Exception as e:
        logging.error(f"Error fetching base prompt: {e}")
        return None

#-----

def get_tools_2(query_type: str):

    db_connector = get_db_connector()
    
    try:
        columns, _ = db_connector.get_columns('llm_tools_2')
        all_data = db_connector.select_values('llm_tools_2', columns)
        tools_content_list = [row['content'] for row in all_data if row['query_type'] == query_type]
        
        return tools_content_list if tools_content_list else None
    except Exception as e:
        logging.error(f"Error fetching tools: {e}")
        return None
    

def get_base_prompt_2(query_type: str):
    
    db_connector = get_db_connector()
    
    try:
        
        columns, _ = db_connector.get_columns('llm_base_prompts_2')
        all_data = db_connector.select_values('llm_base_prompts_2', columns)
        prompt = next((row['content'] for row in all_data if row['query_type'] == query_type), None)
        
        if prompt is None:
            logging.error(f"No base prompt found for query type: {query_type}")
            return None
        
        return prompt
    except Exception as e:
        logging.error(f"Error fetching base prompt: {e}")
        return None

