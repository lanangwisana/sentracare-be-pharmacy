# pharmacy-service/auth.py
import os
from jose import jwt, JWTError
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "change-this-secret-in-prod")
ALGORITHM = "HS256"
ISSUER = os.getenv("AUTH_ISSUER", "sentracare-auth")
AUDIENCE = os.getenv("AUTH_AUDIENCE", "sentracare-services")

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            issuer=ISSUER,
            audience=AUDIENCE,
        )
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token tidak valid")
    return payload

def require_roles(allowed_roles: list):
    def _inner(user=Depends(get_current_user)):
        if user.get("role") not in allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Akses ditolak")
        return user
    return _inner