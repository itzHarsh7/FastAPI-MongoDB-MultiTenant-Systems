from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from starlette import status
from database import db
from settings import SECRET_KEY, ALGORITHM, redis, DEFAULT_HOST
from bson import ObjectId
import json

from bson import ObjectId
from datetime import datetime

def serialize_document(doc):
    """Recursively convert MongoDB documents for JSON serialization."""
    if isinstance(doc, dict):
        return {k: serialize_document(v) for k, v in doc.items()}
    elif isinstance(doc, list):
        return [serialize_document(i) for i in doc]
    elif isinstance(doc, ObjectId):
        return str(doc)
    elif isinstance(doc, datetime):
        return doc.isoformat()
    else:
        return doc
    

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            host = request.headers.get("host")
            if not host:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Host header"}
                )
            
            if not host == DEFAULT_HOST and request.url.path in ["/", "/docs", "/openapi.json", "/favicon.ico"]:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "You are not alllowed to Access this platform"}
                )
            
            if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/favicon.ico","/auth/login"]:
                return await call_next(request)

            

            tenant_key = f"tenant:{host}"
            tenant_json = await redis.get(tenant_key)
            if tenant_json:
                tenant = json.loads(tenant_json)
            else:
                # Fallback to DB
                tenant = await db.tenants.find_one({"host": host})
                if not tenant:
                    return JSONResponse(
                        status_code=status.HTTP_403_FORBIDDEN,
                        content={"detail": f"No tenant found for host: {host}"}
                    )
                tenant["_id"] = str(tenant["_id"])

                # Store permanently (no TTL)
                tenant = serialize_document(tenant)
                await redis.set(tenant_key, json.dumps(tenant), ex=300)

            if tenant and not tenant.get("is_active", True):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Tenant is inactive"}
                )

            auth_header = request.headers.get("Authorization")
            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing or invalid Authorization header"}
                )

            token = auth_header.split(" ")[1]

            try:
                payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            except JWTError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Token is invalid or expired"}
                )

            user_id = payload.get("sub")
            token_tenant_id = payload.get("tenant_id")

            if not user_id or not token_tenant_id:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid token payload"}
                )

            if str(tenant["_id"]) != str(token_tenant_id):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Token tenant mismatch with host"}
                )
            user_key = f"user:{token_tenant_id}:{user_id}"
            user_json = await redis.get(user_key)
            if user_json:
                user = json.loads(user_json)
            else:
                # Fetch from Mongo
                user = await db.users.find_one({
                    "_id": ObjectId(user_id),
                    "tenant": ObjectId(token_tenant_id)
                })

                if not user:
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "User not found or unauthorized"}
                    )
                
                user = serialize_document(user)
                await redis.set(user_key, json.dumps(user), ex=300)


            role_id = str(user["role"])
            role_key = f"role:{role_id}"
            role_json = await redis.get(role_key)
            if role_json:
                role = json.loads(role_json)
            else:
                role = await db.roles.find_one({"_id": ObjectId(user["role"])})
                if role:
                    # role["_id"] = str(role["_id"])
                    role = serialize_document(role)
                    await redis.set(role_key, json.dumps(role),ex=300)


            request.state.user = user
            request.state.tenant = tenant
            request.state.role = role

            response = await call_next(request)
            return response

        except Exception as e:
            # Catch all other exceptions and return a proper JSON response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)}
            )
