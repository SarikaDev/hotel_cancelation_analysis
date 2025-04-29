# we are reading .env files with load_dotenv fuction from dotenv package
import os
import psycopg2
from dotenv import load_dotenv

# we are using in-built py-module to get data from .env files
load_dotenv()
# it's started reading .env files


def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
        )
        # We are connecting PostgreSQL DB with Python
        print("Connected to the database successfully!")
        return conn
    except Exception as e:
        print("Error connecting to the database:", e)
        return None


if __name__ == "__main__":
    get_db_connection()
