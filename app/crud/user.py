# app/crud/user.py

from app.schemas.user import UserCreate, User
from app.db.postgres_database import get_db_connector

def create_user(user: UserCreate, role: str) -> User:
    db_connector = get_db_connector()
    insert_user_query = """
    INSERT INTO "users" ("email", "name", "password", "role") 
    VALUES (%s, %s, %s, %s) RETURNING *;
    """
    values = (user.email, user.name, user.password, role)
    db_connector.run_sql_execute(insert_user_query, values)
    new_user = db_connector._cur.fetchone()
    return User(**new_user)

def get_user_by_email(email: str):
    db_connector = get_db_connector()
    select_user_query = """
    SELECT * FROM "users" WHERE "email" = %s;
    """
    db_connector.run_sql_execute(select_user_query, (email,))
    user_record = db_connector._cur.fetchone()
    if user_record:
        return User(**user_record)
    return None
