import os
import requests
from jose import JWTError, jwt
from jose.jwk import RSAKey
from jose.utils import base64url_decode
from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import List
from .settings import settings

AUTH0_DOMAIN = settings.auth0_domain
API_IDENTIFIER = settings.api_identifier
ALGORITHMS = ["RS256"]
HTTP_SCHEME = HTTPBearer()

class TokenData(BaseModel):
    sub: str
    permissions: List[str]

def get_public_key(token: str):
    jwks_url = f"https://{AUTH0_DOMAIN}/.well-known/jwks.json"
    jwks = requests.get(jwks_url).json()
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    for key in jwks["keys"]:
        if key["kid"] == unverified_header["kid"]:
            rsa_key = {
                "kty": key["kty"],
                "kid": key["kid"],
                "use": key["use"],
                "n": key["n"],
                "e": key["e"]
            }
            break
    if not rsa_key:
        raise HTTPException(status_code=401, detail="Public key not found.")
    return RSAKey(key=rsa_key, algorithm=ALGORITHMS[0])

def get_jwt_token(auth: HTTPAuthorizationCredentials = Security(HTTP_SCHEME)) -> TokenData:
    try:
        payload = jwt.decode(auth.credentials, get_public_key(auth.credentials), algorithms=ALGORITHMS, audience=API_IDENTIFIER)
        return TokenData(sub=payload.get("sub"), permissions=payload.get("permissions", []))
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Could not validate credentials: {str(e)}")



def require_permission(permission: str):
    async def permission_checker(token: TokenData = Depends(get_jwt_token)):
        if permission not in token.permissions:
            raise HTTPException(status_code=403, detail="Permission denied")
        return token
    return permission_checker
