from datetime import datetime, timedelta
from bson import ObjectId, errors
from data_interface.db.mongo_database import get_mongo_collections
from server.postgres_database import get_db_connector
import logging
from auth0.auth import check_organization_permission, check_patient_id_permission
from auth0.models import TokenData
from fastapi import HTTPException  # Ensure to import HTTPException


class FindVitalsignsInterface:
    def __init__(self, query, projection, conditions=None, token_data: TokenData = None):
        self.query = query
        self.projection = projection
        self.conditions = conditions
        self.token_data = token_data
        self.db_connector = get_db_connector()
        self.vitalsigns_collection = get_mongo_collections()["vitalsigns"]
        self.patient_info_collection = get_mongo_collections()["patients"]

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
                # 檢查機構
                check_organization_permission(self.token_data, patient_organization_str)
            except HTTPException as e:
                if e.status_code == 403:
                    try:
                        # 檢查家屬
                        check_patient_id_permission(self.token_data, patient_id_str)
                    except HTTPException as e:
                        if e.status_code == 403:
                            raise HTTPException(status_code=403, detail="根本沒存取權拍謝")
                        else:
                            logging.error(f"Unexpected error: {e.status_code}")
                            raise e
                else:
                    logging.error(f"Unexpected error: {e.status_code}")
                    raise e

            # Step 4: Construct the vitalsigns query
            vitalsigns_query = {"patient": patient_id}

            # Step 5: 處理時間
            if self.conditions and self.conditions.get("duration"):
                end_date = datetime.now()
                start_date = end_date - timedelta(days=int(self.conditions["duration"]))
                vitalsigns_query["createdDate"] = {"$gte": start_date, "$lte": end_date}
                logging.info(f"Time range: start_date = {start_date}, end_date = {end_date}")

            logging.info(f"Vitalsigns Query: {vitalsigns_query}")

            # Step 6: 準備開始找
            cursor = self.vitalsigns_collection.find(vitalsigns_query, self.projection)

            # Step 7: 有比較的話
            if self.conditions and self.conditions.get("sortby"):
                sort_fields = [(key, -1 if value.lower() == "descending" else 1) for key, value in self.conditions["sortby"].items()]
                cursor = cursor.sort(sort_fields)
                logging.info(f"Sort fields: {sort_fields}")

            # Step 8: 有限定的話
            if self.conditions and self.conditions.get("limit"):
                cursor = cursor.limit(int(self.conditions["limit"]))
                logging.info(f"Limit: {self.conditions['limit']}")

            # Step 9: 開始找
            results = [doc for doc in cursor if all(field in doc for field in self.projection.keys() if self.projection[field] == 1)]
            logging.info(f"Results: {results}")

            # Step 10: 附上連結
            if self.conditions.get("duration"):
                link_str = "https://smc.jubo.health/VitalSign/patient/" + patient_id_str + "?start=" + str(start_date)[:10]
                link = {"link":link_str}
            else:
                link_str = "https://smc.jubo.health/VitalSign/patient/" + patient_id_str
                link = {"link":link_str}

            logging.info(f"Link: {link}")
            results.append(link)
            return results

        except HTTPException as e:
            logging.error(f"An error occurred during execution: {e.detail}")
            raise e  # Re-raise the HTTPException to propagate it back to the client
        except Exception as e:
            logging.error(f"An error occurred during execution: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))  # Raise a new HTTPException to propagate the error
