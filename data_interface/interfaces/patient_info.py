import logging
from .base import BaseInterface
from data_interface.db.mongo_database import get_mongo_collections
from server.postgres_database import get_db_connector
from auth0.auth import check_organization_permission, check_patient_id_permission
from auth0.models import TokenData
from fastapi import HTTPException
from bson import ObjectId
from pymongo import errors

class FindPatientInfoInterface(BaseInterface):
    def __init__(self, query, projection, conditions=None, token_data: TokenData = None):
        self.query = query
        self.projection = projection
        self.conditions = conditions
        self.token_data = token_data
        self.patient_info_collection = get_mongo_collections()["patients"]
        self.db_connector = get_db_connector()

    def execute(self):
        try:
            # Step 1: Find the patient from PostgreSQL
            query = 'SELECT * FROM "dev_nis_patient_fullname" WHERE "fullname" = %s'
            values = (self.query["patientName"],)
            self.db_connector.run_sql_execute(query, values)
            pg_patient_object = self.db_connector._cur.fetchone()

            if not pg_patient_object:
                logging.info(f"No matching patient found for name: {self.query['patientName']}")
                return []

            # Step 2: Get patient_id_str
            patient_id_str = pg_patient_object["patient_id"]
            logging.info(f"Found patient ID string: {patient_id_str}")

            try:
                patient_id = ObjectId(patient_id_str)
                logging.info(f"Converted patient ID to ObjectId: {patient_id}")
            except errors.InvalidId as e:
                logging.error(f"Invalid ObjectId format: {patient_id_str}")
                return []

            # Step 3: Get patient_organization_str and check metadata
            result = self.patient_info_collection.find_one({"_id": patient_id}, {"organization": 1, "_id": 0})

            if result and 'organization' in result and isinstance(result['organization'], ObjectId):
                result['organization'] = str(result['organization'])

            patient_organization_str = str(result.get('organization', ''))
            logging.info(f"Found patient organization string: {patient_organization_str}")

            logging.info(self.token_data)

            try:
                # Check organization
                check_organization_permission(self.token_data, patient_organization_str)
            except HTTPException as e:
                if e.status_code == 403:
                    try:
                        # Check patient ID permission
                        check_patient_id_permission(self.token_data, patient_id_str)
                    except HTTPException as e:
                        if e.status_code == 403:
                            raise HTTPException(status_code=403, detail="Access denied")
                        else:
                            logging.error(f"Unexpected error: {e.status_code}")
                            raise e
                else:
                    logging.error(f"Unexpected error: {e.status_code}")
                    raise e

            # Step 4: Construct the query for patient information
            patients_info_query = {"_id": patient_id}
             
            logging.info(f"MongoDB Query: {patients_info_query}, Projection: {self.projection}")

            result = []
            result.append(self.patient_info_collection.find_one(patients_info_query, self.projection))

            link_str = "https://smc.jubo.health/MyPatient/" + patient_id_str
            link = {"link":link_str}
            logging.info(f"Link: {link}")
            result.append(link)

            return result

        except HTTPException as e:
            logging.error(f"An error occurred during execution: {e.detail}")
            raise e  # Re-raise the HTTPException to propagate it back to the client
        except Exception as e:
            logging.error(f"An error occurred during execution: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))  # Raise a new HTTPException to propagate the error
