import psycopg2
import time
from psycopg2.extras import RealDictCursor
from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
from sqlalchemy.orm import Session
from . import models
from .database import engine, SessionLocal, get_db

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


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


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # Using raw SQL
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()

    # Using ORM
    posts = db.query(models.Post).all()

    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # Using raw SQL
    # cursor.execute(
    #     """INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #     (post.title, post.content, post.published),
    # )
    # new_post = cursor.fetchone()
    # conn.commit()

    # Using ORM
    print(post)
    print(post.model_dump())
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    cursor.execute("""SELECT * from posts WHERE id = %s """, str(id))
    post = cursor.fetchone()

    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id: {id} was not found",
        )
    return {"post_detail": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("""DELETE FROM posts WHERE id = %s RETURNING * """, str(id))
    deleted_post = cursor.fetchone()
    conn.commit()

    if deleted_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING *""",
        (post.title, post.content, post.published, str(id)),
    )
    updated_post = cursor.fetchone()
    conn.commit()

    if updated_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"post with id {id} does not exist",
        )

    return {"data": updated_post}


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def find_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i
