from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP
from sqlalchemy.sql.expression import null, text
# from sqlalchemy.sql import text

class Post_table(Base): # Table for all the posts.
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(
        Enum(
            "Music", "Dance", "Drama", "Travel", "Politics", 
            "Educational", "Food", "Technology", "Geography", 
            "Geopolitics", "History", "Sci-fi",
            name="post_category_enum" # Required for PostgreSQL to create the type object
        ), 
        nullable=False
    )
    is_published = Column(Boolean, server_default='FALSE', nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text('now()')
    )

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text('now()')
    )
