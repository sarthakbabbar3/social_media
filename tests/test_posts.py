from app import schemas
from jose import jwt
from app.config import settings
import pytest

def test_get_all_posts(authorized_client, test_posts):
    res = authorized_client.get("/posts/")
    assert res.status_code == 200
    assert len(res.json()) == len(test_posts)

def test_unauthorized_user_get_all_posts(client, test_posts):
    res = client.get("/posts/")
    assert res.status_code == 401

def test_unauthorized_user_get_one_posts(client, test_posts):
    res = client.get(f"/posts/{test_posts[0]['id']}")
    assert res.status_code == 401

def test_get_one_not_exist(authorized_client, test_posts):
    res = authorized_client.get(f"/posts/88888")
    assert res.status_code == 404

def test_get_one_post(authorized_client, test_posts):
    res =  authorized_client.get(f"/posts/{test_posts[0]['id']}")
    post = schemas.PostOut(**res.json())
    assert post.id == test_posts[0]['id']
    assert post.content == test_posts[0]["content"]


def test_create_post(authorized_client, test_user, test_posts):
    res = authorized_client.post("/posts/", json = {"title":"first title", "content": "new content",\
        "published": True})
    created_post = schemas.Post(**res.json())
    assert res.status_code == 201
    assert created_post.title == "first title"