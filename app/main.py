import psycopg2
import time
from fastapi import FastAPI
from . import models
from .database import engine
from .routers import post, user

# Create db tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


while True:
    try:
        conn = psycopg2.connect(
            host="winhost", database="fastapi", user="postgres", password="postgres"
        )
        cursor = conn.cursor()
        print("Database connected!")
        break
    except Exception as error:
        print("Could not connect to database, error:", error)
        time.sleep(5)

my_posts = [
    {
        "id": 1,
        "title": "title of post 1",
        "content": "content of post 1",
    },
    {
        "id": 2,
        "title": "i am post2",
        "content": "i love pizza",
    },
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


# Set up routers
app.include_router(post.router)
app.include_router(user.router)


@app.get("/")
def root():
    return {"message": "Hello World"}
