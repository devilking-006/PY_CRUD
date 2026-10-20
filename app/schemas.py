from pydantic import BaseModel, Field, EmailStr
from typing import Literal, Annotated, Optional
from datetime import datetime

class UserDetails(BaseModel): # User model for validating the details provided by the user. At new account creation time.
    username: str
    email: EmailStr
    password: str

class UserRes(BaseModel): # User response model for viewing the required details only, to the user, and hiding sensitive details in order to safeguard his personal information.
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    class Config: # SQL Alchemy model to Pydantic model conversion.
        from_attributes = True # Earlier 'orm_mode = True'

class UserLogin(BaseModel): # User Login model to check for authentic user before sharing the required data.
    email: EmailStr
    password: str

class Post(BaseModel): # Post Model, for creation of new post and also updation of an existing post.
    title : Annotated[str, Field(..., description="The Title of the post", example="The Bahamas")]
    content : Annotated[str, Field(..., description="Post Content, what the user wants to describe about the post")]
    category : Annotated[
        Literal[
            "Music", "Dance", "Drama", "Travel", "Politics",
            "Educational", "Food", "Technology", "Geography",
            "Geopolitics", "History", "Sci-fi", "Movies", "Justice",
            "Law", "Memes", "Science", "Astronomy", "Nostalgia", 
            "80s", "90s", "AI", "Robotics", "EVs", "Drones", "Sports",
            "National", "Asian Games", "Olympics", "Paralympics"
        ], Field(..., description="Category of the post")
    ]
    is_published : Annotated[bool, Field(..., description="Is the post published (True) or in a Draft (False)")] = False

class PostRes(Post): # Response Model, contains the fields to be shown to the user, on requirement.
    created_at: datetime
    owner_id: int
    owner: UserRes

    class Config: # SQL Alchemy model to Pydantic model conversion.
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int] = None