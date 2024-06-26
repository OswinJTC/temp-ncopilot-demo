import logging
from app.interfaces.base import DataInterface
from app.db.database import get_mongo_collections
from datetime import datetime, timedelta

class FindVitalsignsInterface(DataInterface):
    def __init__(self, query, projection, conditions=None):
        collections = get_mongo_collections()
        self.patientFullName_collection = collections["patientFullName"]
        self.vitalsigns_collection = collections["vitalsigns"]
        self.query = query
        self.projection = projection
        self.conditions = conditions

    def execute(self):
        # Step 1: Find the patient
        patientFullName = self.patientFullName_collection.find_one(
            {"fullName": self.query["patientName"]}
        )

        if not patientFullName:
            logging.info("No matching patient found for name: {}".format(self.query["patientName"]))
            return []

        patient_id = patientFullName["patient"]
        logging.info(f"Found Patient ID: {patient_id}")

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
                if value.lower() == "descending":
                    sort_fields.append((key, -1))
                elif value.lower() == "ascending":
                    sort_fields.append((key, 1))
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
