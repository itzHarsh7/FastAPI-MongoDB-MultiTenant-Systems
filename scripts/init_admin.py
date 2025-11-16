import asyncio
from database import db
from authentication.utils import get_password_hash
from datetime import datetime, UTC


async def create_default_admin():
    user_collection = db["users"]
    tenants_collection = db["tenants"]
    roles_collection = db["roles"]

    existing_tenant = await tenants_collection.find_one({"name": "local"})
    existing_role = await roles_collection.find_one({"name":"Admin"})

    user_detail = {
        "first_name":"Super",
        "last_name":"Admin",
        "email":"admin@gmail.com",
        "username":"SuperAdmin",
        "is_active":True,
        "password": get_password_hash("Dev2024##"),
        "created_at": datetime.now(UTC),
        "tenant": existing_tenant["_id"],
        "role":existing_role["_id"]
    }
    user = await user_collection.find_one({"email":user_detail.get("email")})
    if not user:
        await user_collection.insert_one(user_detail)
        print("SuperAdmin Created Successfully")
    else:
        print("SuperAdmin Already Exists")
    
if __name__ == "__main__":
    asyncio.run(create_default_admin())
