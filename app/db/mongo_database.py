# app/db/mongo_database.py
import logging
from linkinpark.lib.common.mongo_connector import MongodbReadOnly

# Global variables for MongoDB
client = None
db = None
collections = {}

def startup_mongo_event():
    global client, db, collections
    # Initialize MongoDB
    client = MongodbReadOnly(env="dev")
    db = client["release"]
    read_only_db_develop = MongodbReadOnly(env="dev")
    collections['patients'] = read_only_db_develop['patients']
    collections['vitalsigns'] = read_only_db_develop['vitalsigns']

    logging.info("Connected to MongoDB with database: release")

def get_mongo_collections():
    global collections
    if not collections:
        startup_mongo_event()  # Ensure collections are initialized
    return collections
