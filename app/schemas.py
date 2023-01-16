from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from pydantic.types import conint

class PostBase(BaseModel):
    title: str 
    content: str
    published: bool = True

class PostOut(PostBase):
    id: int
    created_at: datetime
    user_id: int
    votes: int
    created_at: datetime
    user_id: int
    email: EmailStr

class PostCreate(PostBase):
    pass

# User response
class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

# schema for response
class Post(PostBase):
    created_at: datetime
    user_id: int
    email: EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str 

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
    post_id: int
    dir: conint(le=1)