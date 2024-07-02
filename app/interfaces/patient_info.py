import logging
from .base import DataInterface
from app.db.mongo_database import get_mongo_collections

class FindPatientInfoInterface(DataInterface):
    def __init__(self, query, projection):
        collections = get_mongo_collections()
        self.collection = collections["patients"]
        self.query = query
        self.projection = projection

    def execute(self):
        logging.info(f"Executing query: {self.query} with projection: {self.projection}")
        patient = self.collection.find_one(self.query, self.projection)
        if not patient:
            return []
        return [patient]
