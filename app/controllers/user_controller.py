# /root/app/controllers/user_controller.py
from ..utils.auth import create_access_token
from ..utils.database import get_mongo_client_sync
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, status, Form, Request
import os
from fastapi.responses import RedirectResponse

from fastapi.security import OAuth2PasswordRequestForm
from ..models.user import UserCreate, UserInDB, TokenData
from jose import JWTError
from datetime import timedelta

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

COLLECTION_NAME = os.getenv('MONGO_DB_COLLECTION_USERS', 'users')
MONGO_DB_NAME = "optitasks"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

@router.post("/register", response_model=UserInDB)
async def register(
    email: str = Form(...), 
    password: str = Form(...), 
    first_name: str = Form(...), 
    last_name: str = Form(...), 
    organization: str = Form(...)
):
    client = get_mongo_client_sync()
    if client[MONGO_DB_NAME][COLLECTION_NAME].find_one({"email": email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered",
        )
    hashed_password = pwd_context.hash(password)
    user_in = UserInDB(
        first_name=first_name, 
        last_name=last_name, 
        email=email, 
        hashed_password=hashed_password, 
        organization=organization
    )
    result = client[MONGO_DB_NAME][COLLECTION_NAME].insert_one(user_in.dict(exclude={"id"}))
    user_in.id = str(result.inserted_id)
    
    # return user_in
    # Redirect to the index page after successful registration
    return RedirectResponse(url='/login', status_code=status.HTTP_303_SEE_OTHER)

@router.post("/login", response_model=TokenData)
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    client = get_mongo_client_sync()
    user = client[MONGO_DB_NAME][COLLECTION_NAME].find_one({"email": form_data.username})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user_in_db = UserInDB(**user)
    password_valid = pwd_context.verify(form_data.password, user_in_db.hashed_password)
    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_in_db.email}, expires_delta=access_token_expires
    )

    # Store user's email and token in the session
    request.session["user"] = {"email": user_in_db.email, "token": access_token}

    return RedirectResponse(url='/tasks', status_code=status.HTTP_303_SEE_OTHER)


