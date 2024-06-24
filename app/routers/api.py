from google.cloud import secretmanager
from fastapi import APIRouter, HTTPException
from app.models.request_models import RequestParams
from app.interfaces.data_interfaces import DataInterfaceFactory
import json
from datetime import datetime, timedelta
import logging
from app.db.database import get_mongo_collections
from typing import List, Dict, Any

router = APIRouter()


@router.post("/initial-layer")
async def execute_queries(my_params: RequestParams):
    results = []
    try:
        for query in my_params.queries:
            query_dict = {}
            if query.lastName and query.firstName:
                query_dict["lastName"] = query.lastName
                query_dict["firstName"] = query.firstName

            if query.timeframe:
                end_date = datetime.now()
                start_date = end_date - timedelta(days=query.timeframe)
                query_dict["createdDate"] = {"$gte": start_date, "$lte": end_date}

            print(query_dict)

            projection = {var: 1 for var in query.variables}
            projection["_id"] = 0  # Exclude the _id field from the results

            interface = DataInterfaceFactory().get_interface(query.interface_type, query_dict, projection, query.sort_field, query.limit)
            result = interface.execute()
            results.extend(result)

        logging.info(f"Final results: {results}")
        return json.loads(json.dumps(results, default=str))
    except Exception as e:
        logging.error(f"Error executing queries: {e}")
        raise HTTPException(status_code=500, detail=str(e))




#測試用
collections = get_mongo_collections()
collection2 = collections["vitalsigns"]
@router.get("/list-vital", response_model=List[Dict[str, Any]])
async def list_vital():
    try:
        vitals = list(collection2.find({}, {"_id": 0}))  # Exclude the _id field
        if vitals:
            logging.info(f"Listing all vitals: {vitals}")
        else:
            logging.info("No vitals found")
        return json.loads(json.dumps(vitals, default=str))
    except Exception as e:
        logging.error(f"Error listing vitals: {e}")
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
