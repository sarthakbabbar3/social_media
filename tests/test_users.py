from app import schemas
from jose import jwt
from app.config import settings
import pytest


def test_create_user(client):
    res = client.post("/users/", json={"email":"sbabbar008@gmail.com", "password":"hello1234"})
    new_user = schemas.UserOut(**res.json())
    # print(res)
    assert res.status_code == 201
    assert new_user.email == "sbabbar008@gmail.com"

def test_login_user(client, test_user):
    res = client.post(
        "/login", data={"username":test_user['email'], "password":test_user['password']}
    )
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token, settings.secret_key, algorithms=settings.algorithm)
    id: str =  payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == 'bearer'
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code",[
    ('wrongemail@gmail.com',"hello1234", 403),
    ("sarthak@gmail.com", "wrongPassword", 403),
    (None, "hello1234", 422),
    ("sarthak@gmail.com", None, 422)
])

def test_incorrect_login(client, test_user, email, password, status_code):
    res = client.post("/login", data={"username":email, "password":password})
    assert res.status_code == status_code




