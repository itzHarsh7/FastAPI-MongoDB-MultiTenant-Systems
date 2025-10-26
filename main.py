from fastapi import FastAPI, HTTPException
from database import db
from fastapi import FastAPI, HTTPException
from authentication.views import router as user_routers
from tenant.views import router as tenant_routers
from middleware import AuthMiddleware
from fastapi.security import HTTPBearer


app = FastAPI(title="MultiTenant FastAPI Application")
app.add_middleware(AuthMiddleware)

security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "Welcome to MultiTenant FastAPI Application"}

app.include_router(user_routers, prefix="/auth")      # Authentication / Users routes
app.include_router(tenant_routers, prefix="/tenants")