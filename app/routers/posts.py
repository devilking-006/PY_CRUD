from fastapi import Response, status, HTTPException, Depends, APIRouter
from .. import models, schemas, oauth2
from sqlalchemy.orm import Session
from ..database import get_db
from typing import List, Optional

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

@router.get("/", response_model=List[schemas.PostRes])
def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user), limit: Optional[int] = None, offset: Optional[int] = None, search: Optional[str] = ""): # Added for using SQLAlchemy, OAuth2, along with the query parameters.

    posts = db.query(models.Post_table).filter(models.Post_table.title.contains(search)).limit(limit).offset(offset).all()
    return posts

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.PostRes)
def create_posts(post: schemas.Post, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    new_post = models.Post_table(owner_id = current_user.id, **post.model_dump()) # Unpack the model's fields automatically, instead of doing that manually, as in SQL Query.
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.PostRes)
def get_post(id: int, db: Session = Depends(get_db)):

    post = db.query(models.Post_table).filter(models.Post_table.id == id).first() # Returns the first instance of instance match.
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} was not found")
    return post

@router.delete("/{id}")
def delete_post(id: int, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post_table).filter(models.Post_table.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} does not exist")

    post_ = post_query.first()

    if post_.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the requested action!")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    # We aren't expected to send any data back when we use this 204 code
    return Response(status_code = status.HTTP_204_NO_CONTENT)

@router.put("/{id}", response_model=schemas.PostRes)
def update_post(id: int, post: schemas.Post, db: Session = Depends(get_db), current_user: models.User = Depends(oauth2.get_current_user)):
    
    post_query = db.query(models.Post_table).filter(models.Post_table.id == id)

    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail = f"post with id: {id} does not exist")

    post_ = post_query.first()

    if post_.owner_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to perform the requested action!")

    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()

    return post_