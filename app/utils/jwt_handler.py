from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import HTTPException, Request
from fastapi.security import HTTPBearer
from typing import Optional

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"

def create_token(data: dict, expires_delta: Optional[int] = 60):
    to_encode = data.copy()
    if expires_delta is None:
        expires_delta = 60
    expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid Token")
    
import logging

logging.basicConfig(level=logging.DEBUG)
jwtbearer_logger = logging.getLogger("jwtbearer")
jwtbearer_logger.setLevel(logging.DEBUG)

class JWTBearer(HTTPBearer):
    def __init__(self, allowed_roles: list = None):
        if allowed_roles is None:
            allowed_roles = []
        # Normalize allowed roles to uppercase for case-insensitive comparison
        self.allowed_roles = [role.upper() for role in allowed_roles]
        super(JWTBearer, self).__init__()

    async def __call__(self, request: Request):
        credentials = await super().__call__(request)
        if not credentials:
            raise HTTPException(status_code=401, detail="Invalid authorization code.")
        try:
            payload = decode_token(credentials.credentials)
            jwtbearer_logger.debug(f"Decoded JWT payload: {payload}")
            jwtbearer_logger.debug(f"Allowed roles: {self.allowed_roles}")
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid Token")

        role = payload.get("role")
        jwtbearer_logger.debug(f"Role extracted from token: {role}")

        if not role:
            jwtbearer_logger.debug("Role not found in token payload")
            raise HTTPException(status_code=403, detail="Access Denied: Role not found")

        # Normalize role to uppercase for comparison
        if self.allowed_roles and role.upper() not in self.allowed_roles:
            jwtbearer_logger.debug(f"Access denied for role: {role}")
            raise HTTPException(status_code=403, detail="Access Denied")
        
        request.state.user = payload
        return credentials
