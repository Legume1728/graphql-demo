import graphene
# from graphene_sqlalchemy import SQLAlchemyObjectType

from sqlalchemy import String, Integer, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker, scoped_session

# Base class
class Base(DeclarativeBase):
    pass

# Define SQLAlchemy models
class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)

    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="user")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="commenter")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    content: Mapped[str] = mapped_column(String, nullable=False)

    user_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    user: Mapped["User"] = relationship("User", back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    text: Mapped[str] = mapped_column(String, nullable=False)

    post_id: Mapped[str] = mapped_column(String, ForeignKey('posts.id'), nullable=False)
    post: Mapped["Post"] = relationship("Post", back_populates="comments")

    commenter_id: Mapped[str] = mapped_column(String, ForeignKey('users.id'), nullable=False)
    commenter: Mapped["User"] = relationship("User", back_populates="comments")

# Database setup
engine = create_engine("sqlite:///example.db")  # SQLite for simplicity
SessionLocal = scoped_session(sessionmaker(bind=engine))

def get_db_session():
    return SessionLocal()
