from fastapi import APIRouter, Request, Query
from database import db
from authentication.utils import create_access_token, verify_password, create_refresh_token,get_password_hash
from .serializer import TenantRegisterData
from .utils import generate_random_password, generate_unique_username
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from authentication.permissions import IsAdmin, IsTenant, IsAdminOrTenant
from bson import ObjectId


router = APIRouter(tags=["Tenant"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


@router.post("/register")
async def register_tenant(request: Request, register_data: TenantRegisterData,  credentials: HTTPAuthorizationCredentials = Security(security)):
    try:
        if not await IsAdmin(request):
            return JSONResponse(
                {"data": [], "message": "Unauthorized", "success": False},
                status_code=403
                )
        if await db.tenants.find_one({"host": register_data.host}):
            return JSONResponse(
                {"data": [], "message": "Tenant with this host already exists", "success": False},
                status_code=400
            )
        tenant = await db.tenants.insert_one({
                "name": register_data.organisation,
                "host": register_data.host,
                "profile": None,
                "is_active": True})
        role = await db.roles.find_one({"name":"Tenant"})
        password = await generate_random_password()
        username = await generate_unique_username(first_name=register_data.first_name, last_name=register_data.last_name)
        user = await db.users.insert_one({
                "first_name": register_data.first_name,
                "last_name": register_data.last_name,
                "email": register_data.email,
                "username": username,
                "password": get_password_hash(password),
                "role": role["_id"],
                "tenant": tenant.inserted_id,
                "profile":None,
                "is_active":True
            })

        return JSONResponse(
            {"data": [], "message": "Tenant Registered successfully", "success": True},
            status_code=200
        )
    except Exception as e:
        return JSONResponse(
            {"data": [], "message": str(e), "success": False},
            status_code=500
        )


@router.get("/")
async def get_tenants(request: Request ,credentials: HTTPAuthorizationCredentials = Security(security)):
    if not await IsAdmin(request):
        return JSONResponse(
            {"data": [], "message": "Unauthorized", "success": False},
            status_code=403
            )
    tenants_cursor = db.tenants.find({})
    tenants_list = []
    async for tenant in tenants_cursor:
        tenants_list.append({
            "id": str(tenant["_id"]),
            "name": tenant["name"],
            "host": tenant["host"],
            "is_active": tenant.get("is_active", True),
            "profile": tenant.get("profile", None)
        })
    return JSONResponse(
        {"data": tenants_list, "message": "Tenants fetched successfully", "success": True},
        status_code=200
    )