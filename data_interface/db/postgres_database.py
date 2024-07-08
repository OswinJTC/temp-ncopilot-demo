import logging
from linkinpark.lib.common.postgres_connector import PostgresConnectorFactory
from fastapi import HTTPException
import psycopg2

DB_NAME = "Oswin-test"

# Global variable for PostgreSQL
db_connector = None

def startup_postgres_event():
    global db_connector
    try:
        logging.info("Attempting to connect to PostgreSQL...")
        db_connector = PostgresConnectorFactory.get_cloudsql_postgres_connector(DB_NAME)
        logging.info(f"Connected to PostgreSQL with database: {DB_NAME}")
    except psycopg2.OperationalError as e:
        logging.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

def get_db_connector():
    global db_connector
    if not db_connector:
        startup_postgres_event()
    return db_connector
