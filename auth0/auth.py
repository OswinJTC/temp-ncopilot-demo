from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from auth0.utils import verify_jwt, get_user_roles, get_management_api_token
from auth0.models import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_token_data(token: str = Depends(oauth2_scheme)) -> TokenData:
    payload = verify_jwt(token)
    roles = payload.get("https://myapp.example.com/roles", [])
    
    if isinstance(roles, str):
        roles = [roles]
    
    access_token = get_management_api_token()
    user_roles = get_user_roles(payload.get("sub"), access_token)
    roles.extend([role['name'] for role in user_roles])

    return TokenData(
        sub=payload.get("sub"),
        permissions=payload.get("permissions", []),
        roles=roles
    )

def check_role(required_role: str):
    def role_checker(token_data: TokenData = Depends(get_token_data)):
        if required_role not in token_data.roles:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return token_data
    return role_checker

def check_permission(required_permission: str):
    def _check_permission(token_data: TokenData = Depends(get_token_data)):
        if required_permission not in token_data.permissions:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return token_data
    return _check_permission
