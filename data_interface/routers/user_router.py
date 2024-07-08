# app/routers/user_router.py

import logging
from fastapi import APIRouter, HTTPException
from data_interface.schemas import user as schemas_user
from data_interface.crud import user as crud_user
from data_interface.utils.auth0 import create_auth0_user, assign_auth0_role

router = APIRouter()

# Configure logging
logging.basicConfig(level=logging.INFO)

@router.post("/register", response_model=schemas_user.User)
async def register_user(user: schemas_user.UserCreate):
    logging.info(f"Received registration request for email: {user.email}")

    existing_user = crud_user.get_user_by_email(user.email)
    if existing_user:
        logging.warning(f"User already registered: {user.email}")
        raise HTTPException(status_code=400, detail="User already registered")

    role = "admin" if user.email == "admin@example.com" else "guest"
    new_user = create_and_assign_role(user.email, user.password, user.name, role)
    logging.info(f"User created and role assigned: {new_user.email}")
    return new_user

def create_and_assign_role(email: str, password: str, name: str, role: str):
    logging.info(f"Creating user in Auth0: {email}")
    auth0_user = create_auth0_user(email, password, name)
    user_id = auth0_user["user_id"]
    logging.info(f"User created in Auth0 with ID: {user_id}")

    logging.info(f"Assigning role {role} to user {email}")
    assign_auth0_role(user_id, role)
    
    user = schemas_user.UserCreate(email=email, name=name, password=password)
    new_user = crud_user.create_user(user, role)  # Pass the role here
    return new_user
