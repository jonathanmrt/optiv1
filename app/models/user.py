# /root/app/models/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    organization: str

class UserInDB(UserCreate):
    hashed_password: str
    id: Optional[str] = None

class TokenData(BaseModel):
    access_token: str
    token_type: str


