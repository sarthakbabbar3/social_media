from .. import schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from fastapi.params import Body
from typing import List, Optional
from random import randrange
from ..database import get_db

router = APIRouter(
    prefix="/votes", 
    tags=["Vote"]
)

@router.post("/",status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, current_user: int = Depends(oauth2.get_current_user), db = Depends(get_db)):
    cursor, conn = db
    
    # voting on a post that doesnt exist
    cursor.execute("""SELECT * FROM posts WHERE id = %s""",(vote.post_id,))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Post with id {vote.post_id} does not exist.")

    cursor.execute("""SELECT * FROM votes WHERE post_id = %s AND user_id = %s""",(vote.post_id,\
            current_user["id"]))
    found_vote = cursor.fetchone()

    if vote.dir == 1:
        if found_vote:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"user {current_user['id']} has already voted on post {vote.post_id}")
        else:
            cursor.execute("""INSERT INTO votes (post_id, user_id) VALUES (%s, %s);""", (vote.post_id, current_user["id"]))
            conn.commit()
            return {"message": "successfully added vote"}
    else:
        if not found_vote:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vote does not exist.")

        else:
            cursor.execute("""DELETE FROM votes WHERE post_id = %s AND user_id = %s""",(vote.post_id,\
            current_user["id"]))
            conn.commit()
            return {"message": "successfuly deleted vote"}