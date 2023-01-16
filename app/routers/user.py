from .. import schemas, utils
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from fastapi.params import Body
from typing import List
from random import randrange
from psycopg2.extras import RealDictCursor
from ..database import get_db


router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db = Depends(get_db)):
    cursor, conn = db
    # hash password 
    user.password = utils.hash(user.password)
    cursor.execute("""  INSERT INTO users (email, password) VALUES (%s, %s) RETURNING *;""", (user.email, user.password))
    new_user = cursor.fetchone()
    conn.commit()
    return new_user

@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db = Depends(get_db)):
    cursor, conn = db
    cursor.execute("""SELECT * FROM users WHERE id = %s""",(str(id),))
    user = cursor.fetchone()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"User with id: {id} was not found")

    return user