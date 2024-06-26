from fastapi import APIRouter, HTTPException
from app.models.request_models import RequestParams
from app.factory import DataInterfaceFactory
import json
import logging

router = APIRouter()

def parse_query(query):
    query_dict = {}
    if query.patientName:
        query_dict["patientName"] = query.patientName

    projection = {var: 1 for var in query.retrieve}
    projection["_id"] = 0  # Exclude the _id field from the results

    conditions = {
        "duration": query.conditions.duration if query.conditions else None,
        "sortby": query.conditions.sortby if query.conditions else None,
        "limit": query.conditions.limit if query.conditions else None
    }

    return query_dict, projection, conditions
@router.post("/initial-layer")
async def execute_queries(my_params: RequestParams):
    results = []
    try:
        for query in my_params.queries:
            query_dict, projection, conditions = parse_query(query)
            logging.info(f"Parsed query: {query_dict}, Projection: {projection}, Conditions: {conditions}")
            interface = DataInterfaceFactory().get_interface(query.interface_type, query_dict, projection, conditions)
            result = interface.execute()
            results.extend(result)

        logging.info(f"Final results: {results}")
        return json.loads(json.dumps(results, default=str))
    except Exception as e:
        logging.error(f"Error executing queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/test-gcp-credentials")
async def test_gcp_credentials():
    try:
        client = secretmanager.SecretManagerServiceClient()
        secret_name = "projects/jubo-ai/secrets/mongodbUrlDEVAnalytics/versions/latest"
        response = client.access_secret_version(request={"name": secret_name})
        secret_data = response.payload.data.decode("UTF-8")
        return {"message": "Successfully accessed secret", "secret_data": secret_data}
    except Exception as e:
        return {"error": str(e)}
 