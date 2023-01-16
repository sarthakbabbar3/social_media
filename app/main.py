from fastapi import FastAPI, status
from .routers import post, user, auth, votes
from .config import settings

app = FastAPI()

app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(votes.router)

@app.get("/")
async def root():
    return {"message": "Home Page!"}



