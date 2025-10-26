from pydantic import BaseModel, EmailStr, validator
from database import roles, tenants
import re

class TenantRegisterData(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    organisation: str
    host: str
