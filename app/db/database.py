import logging
from linkinpark.lib.common.mongo_connector import MongodbReadOnly

client = None
db = None
collections = {}

def startup_event():
    global client, db, collections
    client = MongodbReadOnly(env="dev")
    db = client["release"]
    read_only_db_develop = MongodbReadOnly(env="dev")

    collections['patients'] = read_only_db_develop['patients']
    collections['vitalsigns'] = read_only_db_develop['vitalsigns']
    collections['patientFullName'] = read_only_db_develop['patientFullName']
    logging.info("Connected to MongoDB with database: release")

   

def get_mongo_collections():
    global collections
    if not collections:
        startup_event()  # Ensure collections are initialized
    return collections
