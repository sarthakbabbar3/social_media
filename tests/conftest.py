from fastapi.testclient import TestClient
from app.main import app
import psycopg2
from psycopg2.extras import RealDictCursor
import time
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from app.config import settings
from app.database import get_db
import pytest
from app.oauth2 import create_access_token


# Keep retrying connection
while True:
    try:
        conn = psycopg2.connect(host=settings.database_hostname, port = settings.database_port,\
        database=settings.database_name+'_test', user=settings.database_username,\
        password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection to Test Database was successfull!")
        break

    except Exception as error:
        print("Connection to Test Database Failed")
        print("Error: ", error)
        time.sleep(2)

# CREATE TABLES
def create_tables():
    # users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id SERIAL PRIMARY KEY,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """)
    conn.commit()

    # posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS posts(
        id serial PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL, 
        published BOOL NOT NULL DEFAULT true,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        user_id INTEGER NOT NULL,
        CONSTRAINT fk_user
            FOREIGN KEY(user_id)
            REFERENCES users(id)
            ON DELETE CASCADE
    );
    """)
    conn.commit()

    # votes table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS votes(
        post_id INT NOT NULL, 
        user_id INT NOT NULL,
        PRIMARY KEY(post_id, user_id),
        CONSTRAINT fk_post_id
            FOREIGN KEY(post_id)
            REFERENCES posts(id)
            ON DELETE CASCADE,
        CONSTRAINT fk_user_id
            FOREIGN KEY(user_id)
            REFERENCES users(id)
            ON DELETE CASCADE 
    );
    """)
    conn.commit()

def drop_tables():
    cursor.execute("""
    DROP TABLE IF EXISTS votes;
    DROP TABLE IF EXISTS posts;
    DROP TABLE IF EXISTS users;
    """)
    conn.commit()


@pytest.fixture()
def client():
    drop_tables()
    create_tables()

    def override_get_db():
        return cursor, conn
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)

@pytest.fixture
def test_user(client):
    user_data = {"email": "sarthak@gmail.com", "password": "hello1234"}
    res = client.post("/users/", json=user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user['password'] = user_data['password']
    return new_user

@pytest.fixture
def token(test_user):
    return create_access_token({"user_id": test_user['id']})

@pytest.fixture
def authorized_client(client, token):
    client.headers = {
        **client.headers, 
        "Authorization": f"Bearer {token}"
    }
    return client

@pytest.fixture
def test_posts(test_user):
    cursor.execute("DELETE FROM posts;")
    conn.commit()

    post_data = [
        {
            "title": "first title",
            "content": "good content",
            "user_id": test_user['id']
        },
        {
            "title": "2nd title", 
            "content": "some more good content", 
            "user_id": test_user['id']
        }
    ]
    
    for post in post_data:
        cursor.execute("""
        INSERT INTO posts (title, content, user_id)
        VALUES (%s, %s, %s) RETURNING *;""",
        (post['title'], post['content'], post['user_id'],))
        conn.commit()
        
    cursor.execute("""
    SELECT * FROM posts;
    """)
    posts = cursor.fetchall()
    return posts
    