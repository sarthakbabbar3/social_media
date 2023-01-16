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


@pytest.fixture(scope="module")
def client():
    drop_tables()
    create_tables()

    def override_get_db():
        return cursor, conn
    
    app.dependency_overrides[get_db] = override_get_db
    
    yield TestClient(app)
    