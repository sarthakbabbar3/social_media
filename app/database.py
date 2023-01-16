import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

# Keep retrying connection
while True:
    try:
        conn = psycopg2.connect(host=settings.database_hostname, port = settings.database_port,\
        database=settings.database_name, user=settings.database_username,\
        password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection to Database was successfull!")
        break

    except Exception as error:
        print("Connection to Database Failed")
        print("Error: ", error)
        time.sleep(2)

def get_db():
    return cursor, conn