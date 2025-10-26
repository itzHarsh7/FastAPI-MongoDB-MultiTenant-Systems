from motor.motor_asyncio import AsyncIOMotorClient
from settings import MONGO_URI, DATABASE_NAME
from datetime import timezone

client = AsyncIOMotorClient(MONGO_URI, tz_aware=True, tzinfo=timezone.utc)
db = client[DATABASE_NAME]

users = db.users
tenants = db.tenants
roles = db.roles