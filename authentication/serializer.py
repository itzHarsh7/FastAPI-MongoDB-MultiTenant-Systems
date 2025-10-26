from pydantic import BaseModel, EmailStr, validator
from database import roles, tenants
from datetime import datetime
import re

async def serialize_datetime(dt):
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt

class LoginData(BaseModel):
    email: EmailStr
    password: str


class RegisterData(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    username: str
    password: str
    confirm_password: str
    @validator("password")
    def validate_password_complexity(cls, value):
        """
        Password must have:
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character
        - Minimum 8 characters
        """
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", value):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", value):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", value):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise ValueError("Password must contain at least one special character")
        return value

    @validator("confirm_password")
    def passwords_match(cls, value, values):
        """
        Check that confirm_password matches password
        """
        password = values.get("password")
        if password and value != password:
            raise ValueError("Passwords do not match")
        return value

async def loginSerializer(user):
    role = await roles.find_one({"_id": user["role"]})
    tenant = await tenants.find_one({"_id": user["tenant"]})
    login_dict = {
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "username": user["username"],
            "role": role["name"] if role else None,
            "tenant": tenant["name"] if tenant else None,
        }
    
    return login_dict

async def userSerializer(request):
    user = request.state.user
    role = request.state.role
    tenant = request.state.tenant
    user_dict = {
            "id": str(user["_id"]),
            "first_name": user["first_name"],
            "last_name": user["last_name"],
            "email": user["email"],
            "username": user["username"],
            "role": role["name"] if role else None,
            "tenant": tenant["name"] if tenant else None,
            "profile": user.get("profile", None),
            "created_at": await serialize_datetime(user.get("created_at")),
        }
    
    return user_dict