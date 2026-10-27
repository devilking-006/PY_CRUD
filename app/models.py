from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, Enum, TIMESTAMP, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship

class Post_table(Base): # Table for all the posts.
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    category = Column(
        Enum(
            "Music", "Dance", "Drama", "Travel", "Politics", 
            "Educational", "Food", "Technology", "Geography", 
            "Geopolitics", "History", "Sci-fi", "Movies", "Justice",
            "Law", "Memes", "Science", "Astronomy", "Nostalgia", 
            "80s", "90s", "AI", "Robotics", "EVs", "Drones", "Sports",
            "National", "Asian Games", "Olympics", "Paralympics",
            name="post_category_enum" # Required for PostgreSQL to create the type object
        ), 
        nullable=False
    )
    is_published = Column(Boolean, server_default='FALSE', nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), 
        nullable=False, 
        server_default=text('now()')
    )

    owner = relationship("User") # Fetches the user details for a post

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

class Votes(Base):
    __tablename__ = "votes"

    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    post_id = Column(Integer, ForeignKey(
        "posts.id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)