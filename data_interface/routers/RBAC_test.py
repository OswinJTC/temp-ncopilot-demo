from fastapi import APIRouter, Depends
from auth0.auth import check_role
from auth0.auth import check_permission
from auth0.models import TokenData

router = APIRouter()

@router.get("/admin")
async def admin_route(token_data: TokenData = Depends(check_role("pkce-demo-admin"))):
    return {"message": "Welcome, admin!"}

@router.get("/guest")
async def guest_route(token_data: TokenData = Depends(check_permission("ah:tai"))):
    return {"message": "Welcome, guest!"}


@router.get("/test")
async def test():
    return {"message": "Hello, world!"}
