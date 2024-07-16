# app/routers/api.py
from fastapi import HTTPException
from data_interface.factory import DataInterfaceFactory
import json
import logging 
from auth0.models import TokenData

def parse_query(query: dict):
    query_dict = {}
    if "patientName" in query and query["patientName"]:
        query_dict["patientName"] = query["patientName"]

    projection = {var: 1 for var in query["retrieve"]}
    projection["_id"] = 0  # Exclude the _id field from the results

    conditions = {
        "duration": query["conditions"]["duration"] if "duration" in query["conditions"] else None,
        "sortby": query["conditions"]["sortby"] if "sortby" in query["conditions"] else None,
        "limit": query["conditions"]["limit"] if "limit" in query["conditions"] else None
    }

    return query_dict, projection, conditions


def execute_query(query: dict, token_data: TokenData):
    try:
        query_dict, projection, conditions = parse_query(query)
        logging.info(f"Parsed query: {query_dict}, Projection: {projection}, Conditions: {conditions}")
        interface = DataInterfaceFactory().get_interface(query["interface_type"], query_dict, projection, conditions, token_data)
        result = interface.execute()
        logging.info(f"Result: {result}")
        return json.loads(json.dumps(result, default=str))
    except HTTPException as e:
        logging.error(f"An error occurred during query execution: {e.detail}")
        raise e  # Re-raise the HTTPException to propagate it back to the client
    except Exception as e:
        logging.error(f"Error executing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))





 