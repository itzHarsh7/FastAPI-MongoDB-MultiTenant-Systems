from fastapi import APIRouter, Request, Query
from database import users
from .utils import create_access_token, verify_password, create_refresh_token,get_password_hash
from .serializer import LoginData, loginSerializer, userSerializer, RegisterData
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from .permissions import IsAdmin, IsTenant, IsAdminOrTenant
from bson import ObjectId


router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()


@router.post("/login")
async def login(login_data: LoginData):
    user = await users.find_one({"email":login_data.email})
    if not user:
        return JSONResponse(
            {"data": [], "message": "Invalid email or password", "success": False},
            status_code=401
        )
    if not verify_password(login_data.password, user.get("password")):
        return JSONResponse(
            {"data": [], "message": "Invalid email or password", "success": False},
            status_code=401
        )
    access_token = create_access_token({"sub": str(user["_id"]), "tenant_id": str(user["tenant"])})
    user_Data = await loginSerializer(user)
    refresh_token = create_refresh_token({"sub": str(user["_id"]), "tenant_id": str(user["tenant"])})
    return JSONResponse(
        {"data":{"user":user_Data, "access_token":access_token,"refresh_token":refresh_token}, "message": "Logged In Successfully", "success": True},
            status_code=200
        )

@router.post("/register")
async def register(request: Request, register_data: RegisterData, user_id: str = Query(..., description="Tenant ID for new user"), credentials: HTTPAuthorizationCredentials = Security(security)):
    if not await IsAdminOrTenant(request):
        return JSONResponse(
            {"data": [], "message": "Unauthorized", "success": False},
            status_code=403
            )
    role = request.state.role
    if role["name"] == "Admin":
        if not user_id:
            return JSONResponse(
                {"data": [], "message": "Tenant ID is required", "success": False},
                status_code=400
            )
        user = await users.find_one({"_id":ObjectId(user_id)})
        create_user = await users.insert_one({
            "first_name": register_data.first_name,
            "last_name": register_data.last_name,
            "email": register_data.email,
            "username": register_data.username,
            "password": get_password_hash(register_data.password),
            "role": user["role"],
            "tenant": user["tenant"],
            "profile":None,
            "is_active":True
            })
    else:
        create_user = await users.insert_one({
            "first_name": register_data.first_name,
            "last_name": register_data.last_name,
            "email": register_data.email,
            "username": register_data.username,
            "password": get_password_hash(register_data.password),
            "role": request.state.role["_id"],
            "tenant": request.state.tenant["_id"],
            "profile":None,
            "is_active":True
        })
    return JSONResponse(
        {"data": [], "message": "User Registered successfully", "success": True},
        status_code=200
    )

@router.get("/me")
async def get_me(request: Request ,credentials: HTTPAuthorizationCredentials = Security(security)):
    user = request.state.user
    user_data = await userSerializer(request)
    return JSONResponse(
        {"data": user_data, "message": "User fetched successfully", "success": True},
        status_code=200
    )