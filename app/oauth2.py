from datetime import datetime, timedelta, UTC
import jwt
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import schemas, database, models
from .config import settings

# Use the command 'openssl rand -hex 32' in terminal to generate the random long secret key.

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

def create_access_tokens(data: dict):
    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    # pyjwt expects the payload, key, and algorithm
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt

def verify_access_token(token: str, credentials_exception):

    try:
        # Decodes using pyjwt
        payload = jwt.decode(jwt=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        
        id: str = payload.get("user_id")
    
        if id is None:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
        
    except jwt.PyJWTError:
        raise credentials_exception

    return token_data

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    # The idea behind this function and not directly using it in the verify_access_token function is that after the later returns the token data, this function should fetch the user from the Database. So that way, we can attach the user to any path operation and perform any necessary logic. Though this can be implemented by the path operations themselves too, that would just be another way of doing so.
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, 
        detail="Couldn't validate credentials", 
        headers={"WWW-Authenticate": "Bearer"}
    )

    token_ = verify_access_token(token, credentials_exception)

    user = db.query(models.User).filter(models.User.id == token_.id).first()

    return user