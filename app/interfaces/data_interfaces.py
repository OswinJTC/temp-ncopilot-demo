import logging
from typing import Dict, Optional
from app.db.database import get_mongo_collections

class DataInterface:
    def execute(self, *args, **kwargs):
        raise NotImplementedError("This method should be overridden by subclasses")

class FindPatientInfoInterface(DataInterface):
    def __init__(self, query, projection):
        collections = get_mongo_collections()
        self.collection = collections["patients"]  # Get the patients collection
        self.query = query
        self.projection = projection

    def execute(self):
        logging.info(f"Executing query: {self.query} with projection: {self.projection}")
        patient = self.collection.find_one(self.query, self.projection)
        if not patient:
            return []
        return [patient]

class FindVitalsignsInterface(DataInterface):
    def __init__(self, query, projection, sort_field=None, limit=None):
        collections = get_mongo_collections()
        self.patients_collection = collections["patients"]  # Get the patients collection
        self.vitalsigns_collection = collections["vitalsigns"]  # Get the vitalsigns collection
        self.query = query
        self.projection = projection
        self.sort_field = sort_field
        self.limit = limit


    def execute(self):
        patient = self.patients_collection.find_one(
            {"lastName": self.query["lastName"], "firstName": self.query["firstName"]},
            {"_id": 1}
        )


        if not patient:
            logging.info("No matching patient found")
            return []

        patient_id = patient["_id"]
        logging.info(f"Found Patient ID: {patient_id}")

        vitalsigns_query = {
            "patient": patient_id,
            **({"createdDate": self.query["createdDate"]} if "createdDate" in self.query else {})
        }

        logging.info(f"Vitalsigns Query: {vitalsigns_query}")

        cursor = self.vitalsigns_collection.find(vitalsigns_query, self.projection)
        if self.sort_field:
            cursor = cursor.sort(self.sort_field, -1)  # Sort in descending order
        if self.limit:
            cursor = cursor.limit(self.limit)

        results = list(cursor)
        return results


class DataInterfaceFactory:
    def get_interface(self, interface_type: str, query: Dict, projection: Dict = None, sort_field: Optional[str] = None, limit: Optional[int] = None) -> DataInterface:
        if interface_type == "patient_info":
            return FindPatientInfoInterface(query, projection)
        elif interface_type == "vitalsigns":
            return FindVitalsignsInterface(query, projection, sort_field, limit)
        elif interface_type == "complex_vitalsigns":
            return FindComplexVitalsignsInterface(query, projection, sort_field, limit)
        else:
            raise ValueError(f"Unknown interface type: {interface_type}")





#研發中
class FindComplexVitalsignsInterface(DataInterface):
    def __init__(self, query, projection, sort_field=None, limit=None, start_date=None, end_date=None):
        collections = get_mongo_collections()
        self.patients_collection = collections["patients"]
        self.vitalsigns_collection = collections["vitalsigns"]
        self.query = query
        self.projection = projection
        self.sort_field = sort_field
        self.limit = limit
        self.start_date = start_date
        self.end_date = end_date

    def execute(self):
        # Step 1: Find the patient
        patient = self.patients_collection.find_one(
            {"lastName": self.query["lastName"], "firstName": self.query["firstName"]},
            {"_id": 1}
        )

        if not patient:
            logging.info("No matching patient found")
            return []

        patient_id = patient["_id"]
        logging.info(f"Found Patient ID: {patient_id}")

        # Step 2: Find historical 3 lowest TP values
        vitalsigns_query = {"patient": patient_id}
        cursor = self.vitalsigns_collection.find(vitalsigns_query, {"TP": 1}).sort("TP", 1).limit(3)
        lowest_tp_values = [record["TP"] for record in cursor]
        logging.info(f"Lowest 3 TP values: {lowest_tp_values}")

        if len(lowest_tp_values) < 3:
            logging.info("Not enough TP records found")
            return []

        # Step 3: Find the second highest temperature in the recent half year
        vitalsigns_query = {
            "patient": patient_id,
            "createdDate": {"$gte": self.start_date, "$lte": self.end_date}
        }

        logging.info(f"Vitalsigns Query: {vitalsigns_query}")

        cursor = self.vitalsigns_collection.find(vitalsigns_query, {"temperature": 1}).sort("temperature", -1).limit(2)
        highest_temps = [record["temperature"] for record in cursor]
        logging.info(f"Highest temperatures in recent half year: {highest_temps}")

        if len(highest_temps) < 2:
            logging.info("Not enough temperature records found")
            return []

        second_highest_temp = highest_temps[1]
        logging.info(f"Second highest temperature: {second_highest_temp}")

        # Step 4: Sum the 4 values and return the result
        sum_values = sum(lowest_tp_values) + second_highest_temp
        logging.info(f"Sum of the 4 values: {sum_values}")

        return {"sum": sum_values}

