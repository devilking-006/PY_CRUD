from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db

router = APIRouter(
    prefix="/users",
    tags=['Users']
)

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserRes)
def create_user(user: schemas.UserDetails, db: Session = Depends(get_db)):
    # hash the password - user.password
    hashed_password = utils.hash(user.password) # Hash it and store
    user.password = hashed_password # Set the password to the hashed one

    new_user = models.User(**user.model_dump()) # Unpack the model's fields automatically, instead of doing that manually.
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Retireve information about a specific User based on their ID:
@router.get('/{id}', response_model=schemas.UserRes)
def get_user(id: int, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == id).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with {id} does not exist")

    return user