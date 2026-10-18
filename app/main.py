from fastapi import FastAPI
# from fastapi.params import Body
import psycopg2
# from psycopg.rows import dict_row => For psycopg3 only.
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models
from .database import engine
from .routers import posts, users, auth

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

'''
while True:

    try:
        conn = psycopg2.connect(
            host='localhost', 
            dbname='fastapi', 
            user='postgres', 
            password='debraj006',
            cursor_factory=RealDictCursor
        )
        cursor = conn.cursor()
        print("Connection established successfully!")
        break
    
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
        time.sleep(2)
'''

app.include_router(posts.router)
app.include_router(users.router)
app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Hello World"}