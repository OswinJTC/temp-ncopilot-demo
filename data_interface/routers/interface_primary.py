# app/routers/api.py
from fastapi import HTTPException
from data_interface.factory import DataInterfaceFactory
import json
import logging 

def parse_query(query):
    query_dict = {}
    if query["patientName"]:
        query_dict["patientName"] = query["patientName"]

    projection = {var: 1 for var in query["retrieve"]}
    projection["_id"] = 0  # Exclude the _id field from the results

    conditions = {
        "duration": query["conditions"]["duration"] if query["conditions"] else None,
        "sortby": query["conditions"]["sortby"] if query["conditions"] else None,
        "limit": query["conditions"]["limit"] if query["conditions"] else None
    }

    return query_dict, projection, conditions

def execute_queries(my_params):
    results = []
    try:
        for query in my_params["queries"]:
            query_dict, projection, conditions = parse_query(query)
            logging.info(f"Parsed query: {query_dict}, Projection: {projection}, Conditions: {conditions}")
            interface = DataInterfaceFactory().get_interface(query["interface_type"], query_dict, projection, conditions)
            result = interface.execute()
            results.extend(result)

        logging.info(f"Final results: {results}")
        return json.loads(json.dumps(results, default=str))
    except Exception as e:
        logging.error(f"Error executing queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))
