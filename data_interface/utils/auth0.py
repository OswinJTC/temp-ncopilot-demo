# app/utils/auth0.py

import requests
from data_interface.settings import settings

AUTH0_DOMAIN = settings.auth0_domain
AUTH0_CLIENT_ID = settings.auth0_client_id
AUTH0_CLIENT_SECRET = settings.auth0_client_secret

def get_auth0_token():
    url = f"https://{AUTH0_DOMAIN}/oauth/token"
    payload = {
        "client_id": AUTH0_CLIENT_ID,
        "client_secret": AUTH0_CLIENT_SECRET,
        "audience": f"https://{AUTH0_DOMAIN}/api/v2/",
        "grant_type": "client_credentials"
    }
    headers = {"content-type": "application/json"}
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def create_auth0_user(email: str, password: str, name: str):
    url = f"https://{AUTH0_DOMAIN}/api/v2/users"
    username = email.split('@')[0]  # Generate a username based on the email
    payload = {
        "email": email,
        "password": password,
        "name": name,
        "connection": "Username-Password-Authentication",
        "username": username  # Add the username field
    }
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {get_auth0_token()}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

def assign_auth0_role(user_id: str, role_name: str):
    role_id_for_admin = "rol_UtkmNRKLIyDv8ZCN"
    role_id_for_guest = "rol_y78TwmaAYQSlFFQF"

    role_id = role_id_for_admin if role_name == "admin" else role_id_for_guest
    
    url = f"https://{AUTH0_DOMAIN}/api/v2/users/{user_id}/roles"
    payload = {"roles": [role_id]}
    headers = {
        "content-type": "application/json",
        "authorization": f"Bearer {get_auth0_token()}"
    }
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
