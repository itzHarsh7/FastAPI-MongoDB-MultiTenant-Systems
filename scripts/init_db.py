import asyncio
from database import db

async def create_default_tenants_roles():
    tenants_collection = db["tenants"]
    roles_collection = db["roles"]

    default_tenants = [
        {"name": "local", "host": "localhost:8000","profile":None,"is_active": True},
    ]
    for tenant in default_tenants:
        existing = await tenants_collection.find_one({"name": tenant["name"], "host": tenant["host"]})
        if not existing:
            await tenants_collection.insert_one(tenant)
            print(f"Tenant '{tenant['name']}' created")
        else:
            print(f"Tenant '{tenant['name']}' already exists")

    roles_list = ["Admin", "User", "Tenant"]
    for role_name in roles_list:
        existing = await roles_collection.find_one({"name": role_name})
        if not existing:
            await roles_collection.insert_one({"name": role_name})
            print(f"Role '{role_name}' created")
        else:
            print(f"Role '{role_name}' already exists")

if __name__ == "__main__":
    asyncio.run(create_default_tenants_roles())
