from .. import schemas, utils, oauth2
from fastapi import FastAPI, Response, status, HTTPException, APIRouter, Depends
from fastapi.params import Body
from typing import List, Optional
from random import randrange
from psycopg2.extras import RealDictCursor
from ..database import get_db

# cursor, conn = get_db()
router = APIRouter(
    prefix="/posts", 
    tags=["Posts"]
)

# @router.get("/")
@router.get("/", response_model=List[schemas.PostOut])
def get_posts(current_user: int = Depends(oauth2.get_current_user), \
    limit: int = 10, skip: int = 0, search: Optional[str] = '', db = Depends(get_db)):
    cursor, conn = db
    # print("""SELECT * FROM posts JOIN users ON posts.user_id=users.id LIMIT %s OFFSET %s WHERE title LIKE '%%%s%%';""" % (limit,skip,search))
    cursor.execute("""SELECT posts.title, posts.content, posts.published, posts.id, posts.created_at,\
        posts.user_id,users.email, users.created_at, COUNT(votes.user_id) AS votes\
        FROM posts \
        LEFT JOIN users on posts.user_id=users.id\
        LEFT JOIN votes on posts.id=votes.post_id\
        WHERE posts.title LIKE %s\
        GROUP BY posts.id, users.id\
        LIMIT %s OFFSET %s;""",("%"+search+"%",limit,skip,))
    # cursor.execute("""SELECT posts.*, COUNT(votes.post_id) AS votes FROM posts LEFT JOIN votes ON posts.id=votes.post_id WHERE posts.title LIKE %s GROUP BY posts.id LIMIT %s OFFSET %s;""",("%"+search+"%",limit,skip,))
    posts = cursor.fetchall()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user),\
    db = Depends(get_db)):
    cursor, conn = db
    # not using fstring because they are vulnerable to sql injection.
    cursor.execute(""" INSERT INTO posts (title, content, published, user_id) VALUES (%s, %s, %s, %s) RETURNING *;""",(post.title, post.content, post.published, current_user['id']))
    new_post = cursor.fetchone()
    conn.commit()
    # Returning post details along with user details
    cursor.execute("""SELECT * FROM posts JOIN users ON posts.user_id=users.id WHERE posts.id = %s""",(new_post['id'],))
    post_user_data = cursor.fetchone()
    return post_user_data

@router.get("/{id}",response_model=schemas.PostOut)
def get_post(id: int, current_user: int = Depends(oauth2.get_current_user), db = Depends(get_db)):
    cursor, conn = db
    cursor.execute("""SELECT posts.title, posts.content, posts.published, posts.id, posts.created_at,\
        posts.user_id,users.email, users.created_at, COUNT(votes.user_id) AS votes\
        FROM posts \
        LEFT JOIN users on posts.user_id=users.id\
        LEFT JOIN votes on posts.id=votes.post_id\
        WHERE posts.id = %s
        GROUP BY posts.id, users.id;""",(str(id),))
    # cursor.execute("""SELECT * FROM posts JOIN users ON posts.user_id=users.id WHERE posts.id = %s""",(str(id),))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail=f"Post with id: {id} was not found")
    return post

@router.delete("/{id}", status_code = status.HTTP_204_NO_CONTENT)
def delete_post(id: int, current_user: int = Depends(oauth2.get_current_user), db = Depends(get_db)):
    cursor, conn = db
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""",(str(id),))
    deleted_post = cursor.fetchone()

    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Post with id: {id} was not found.")

    if deleted_post['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to perform requested action")

    cursor.execute("""DELETE FROM posts WHERE id = %s;""",(str(id),))
    conn.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostOut)
def update_post(id: int, post: schemas.PostCreate, current_user: int = Depends(oauth2.get_current_user),\
    db = Depends(get_db)):
    cursor, conn = db
    cursor.execute("""SELECT * FROM posts WHERE id = %s;""",(str(id),))
    found_post = cursor.fetchone()
    
    if found_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
        detail=f"Post with id: {id} was not found.")

    if found_post['user_id'] != current_user['id']:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not Authorized to perform requested action")
    
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",(post.title,post.content,post.published, str(id)))
    conn.commit()

    cursor.execute("""SELECT posts.title, posts.content, posts.published, posts.id, posts.created_at,\
        posts.user_id,users.email, users.created_at, COUNT(votes.user_id) AS votes\
        FROM posts \
        LEFT JOIN users on posts.user_id=users.id\
        LEFT JOIN votes on posts.id=votes.post_id\
        WHERE posts.id = %s
        GROUP BY posts.id, users.id;""",(str(id),))

    updated_post = cursor.fetchone()
    return updated_post