# FastAPI Multi Tenant System using MongoDB

To Run This project:

1. You should have docker install on your system.

2. Run This command:

    `docker-compose up --build`

This will install images and setup the default Roles and Tenant and SuperAdmin in the system.


## Example ENV
```
MONGO_URI="mongodb://mongodb:27017/"
DATABASE_NAME="multitenant_db"
SECRET_KEY="YOUR SECRET"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=600
REFRESH_TOKEN_EXPIRE_MINUTES=1200
REDIS_HOST=redis
REDIS_PORT=6379
DEFAULT_HOST="localhost:8000"
```

To Generate a Secure Secret, Use this python code:

```
import secrets

secret_key = secrets.token_bytes(16)

print(secret)
```