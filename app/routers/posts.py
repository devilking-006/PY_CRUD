from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.PostRes])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)): # Added for using SQLAlchemy, OAuth2
    '''
    cursor.execute("""SELECT * FROM public.posts """)
    posts = cursor.fetchall() -> Used Psycopg2 methods.
    '''
    print(current_user.email)
    posts = db.query(models.Post_table).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostRes)
def create_posts(post: schemas.Post, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    # cursor.execute(f"INSERT INTO posts (title, content, category) VALUES ({post.title}, {post.content}, {post.category})") -> Has an issue of SQL Injection problem, hackers may modify the database by providing SQL codes in those places. Safe version below (Psycopg style):
    '''
    cursor.execute("""
                   INSERT INTO posts (title, content, category, is_published) VALUES
                   (%s, %s, %s, %s) RETURNING *
                   """, (post.title, post.content, post.category, post.is_published)
                   )
    new_post = cursor.fetchone()
    conn.commit()
    '''
    print(current_user.email)
    new_post = models.Post_table(**post.model_dump()) # Unpack the model's fields automatically, instead of doing that manually.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostRes)
def get_post(id: int, db: Session = Depends(get_db)):
    '''
    cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id),))
    post = cursor.fetchone()
    '''

    post = db.query(models.Post_table).filter(models.Post_table.id == id).first() # Returns the first instance of instance match.
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return post

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    # index = find_post_index(id)
    conn.commit()
    '''

    deleted_post = db.query(models.Post_table).filter(models.Post_table.id == id)

    if deleted_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} does not exist")
    
    deleted_post.delete(synchronize_session=False)
    db.commit()
    # We aren't expected to send any data back when we use this 204 code
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostRes)
def update_post(id: int, post: schemas.Post, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    '''
    cursor.execute("""UPDATE posts SET title = %s, content = %s, category = %s, isPublished = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.category, post.isPublished, str(id)))

    updated_post = cursor.fetchone()
    conn.commit()
    ''' 

    post_query = db.query(models.Post_table).filter(models.Post_table.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} does not exist")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_query.first()