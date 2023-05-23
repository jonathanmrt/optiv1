# /root/app/utils/auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..models.user import UserCreate
from typing import Optional, Any
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from ..utils.database import get_mongo_client_sync
import os

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_USERS', 'users')
MONGO_DB_NAME = "optitasks"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserCreate:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    client = get_mongo_client_sync()
    user = client[MONGO_DB_NAME][COLLECTION_NAME].users.find_one({"email": token_data.email})
    if user is None:
        raise credentials_exception
    return UserCreate(**user)

def get_user_name(email: str):
    client = get_mongo_client_sync()
    user = client[MONGO_DB_NAME][COLLECTION_NAME].find_one({"email": email})
    if user:
        return user["first_name"] + " " + user["last_name"]
    return None

def get_authenticated_user(request: Request):
    # Check if user is logged in
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    # Get the user's name
    user_name = get_user_name(request.session["user"]["email"])
    return user_name

def get_user_session(request: Request):
    # Check if user is logged in
    if "user" not in request.session:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return request.session["user"]

def get_user_name_from_session(user_session: dict):
    # Get the user's name
    user_name = get_user_name(user_session["email"])
    return user_name



