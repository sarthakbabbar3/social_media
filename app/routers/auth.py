from fastapi import APIRouter, Depends, status, HTTPException, Response
from .. import database, schemas, utils, oauth2
from fastapi.security.oauth2 import OAuth2PasswordRequestForm #built in utility in fastapi to get login credentials
from ..database import get_db

router = APIRouter(
    tags=['Authentication']
)

@router.post('/login', response_model=schemas.Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    cursor, conn = db
    cursor.execute("""SELECT * FROM users WHERE email = %s;""",(str(user_credentials.username),))
    user = cursor.fetchone()

    if not user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials")

    # Verify Password
    if not utils.verify(user_credentials.password, user['password']):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Invalid Credentials"
        )
    
    # Create a token
    access_token = oauth2.create_access_token(data = {"user_id": user['id']})
    return {"access_token" : access_token, "token_type": "bearer"}

