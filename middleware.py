from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from jose import jwt, JWTError
from starlette import status
from database import db
from settings import SECRET_KEY, ALGORITHM
from bson import ObjectId

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/favicon.ico","/auth/login"]:
                return await call_next(request)

            host = request.headers.get("host")
            if not host:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Missing Host header"}
                )

            tenant = await db.tenants.find_one({"host": host})
            if not tenant:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": f"No tenant found for host: {host}"}
                )
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

            user = await db.users.find_one({"_id": ObjectId(user_id), "tenant": ObjectId(token_tenant_id)})
            if not user:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "User not found or unauthorized for this tenant"}
                )

            request.state.user = user
            request.state.tenant = tenant
            request.state.role = await db.roles.find_one({"_id": user["role"]})

            response = await call_next(request)
            return response

        except Exception as e:
            # Catch all other exceptions and return a proper JSON response
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": str(e)}
            )
