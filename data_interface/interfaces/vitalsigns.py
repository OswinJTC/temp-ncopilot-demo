from datetime import datetime, timedelta
from bson import ObjectId, errors
from data_interface.db.mongo_database import get_mongo_collections
from data_interface.db.postgres_database import get_db_connector
import logging

class FindVitalsignsInterface:
    def __init__(self, query, projection, conditions=None):
        self.query = query
        self.projection = projection
        self.conditions = conditions
        self.db_connector = get_db_connector()
        self.vitalsigns_collection = get_mongo_collections()["vitalsigns"]

    def execute(self):
        try:
            # Step 1: Find the patient from PostgreSQL
            query = 'SELECT * FROM "dev_nis_patient_fullname" WHERE "fullname" = %s'
            values = (self.query["patientName"],)
            
            self.db_connector.run_sql_execute(query, values)
            patient_fullname = self.db_connector._cur.fetchone()
            
            if not patient_fullname:
                logging.info(f"No matching patient found for name: {self.query['patientName']}")
                return []

            patient_id_str = patient_fullname["patient_id"]
            logging.info(f"Found patient ID string: {patient_id_str}")

            try:
                patient_id = ObjectId(patient_id_str)
                logging.info(f"Converted patient ID to ObjectId: {patient_id}")
            except errors.InvalidId as e:
                logging.error(f"Invalid ObjectId format: {patient_id_str}")
                return []

            # Step 2: Construct the vitalsigns query
            vitalsigns_query = {"patient": patient_id}

            # Add time range to the query if duration is specified
            if self.conditions and self.conditions.get("duration"):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(self.conditions["duration"]))
                vitalsigns_query["createdDate"] = {"$gte": start_date, "$lte": end_date}
                logging.info(f"Time range: start_date = {start_date}, end_date = {end_date}")

            logging.info(f"Vitalsigns Query: {vitalsigns_query}")

            # Perform the query with the constructed conditions
            cursor = self.vitalsigns_collection.find(vitalsigns_query, self.projection)

            # Apply sorting if specified
            if self.conditions and self.conditions.get("sortby"):
                sort_fields = []
                for key, value in self.conditions["sortby"].items():
                    sort_order = -1 if value.lower() == "descending" else 1
                    sort_fields.append((key, sort_order))
                cursor = cursor.sort(sort_fields)
                logging.info(f"Sort fields: {sort_fields}")

            # Apply limiting if specified
            if self.conditions and self.conditions.get("limit"):
                cursor = cursor.limit(int(self.conditions["limit"]))
                logging.info(f"Limit: {self.conditions['limit']}")

            # Fetch the results and filter out documents without required fields
            results = [doc for doc in cursor if all(field in doc for field in self.projection.keys() if self.projection[field] == 1)]
            logging.info(f"Results: {results}")
            return results

        except Exception as e:
            logging.error(f"An error occurred during execution: {str(e)}")
            return []
