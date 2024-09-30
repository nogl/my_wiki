from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table, Boolean
from sqlalchemy.orm import relationship, declarative_base, backref

from app import db_session

from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now())
    updated = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    @classmethod
    def get_by_id(cls, id):
        cls: Base
        return cls.query.get(id)


class User(BaseModel):
    __tablename__ = 'users'

    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    status = Column(Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


namespace_tags = Table('namespace_tags', Base.metadata,
                       Column('namespace_id', Integer, ForeignKey('namespaces.id'), primary_key=True),
                       Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
                       )


class Tag(BaseModel):
    __tablename__ = 'tags'

    name = Column(String(50), unique=True, nullable=False)


class Book(BaseModel):
    __tablename__ = 'books'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)


class Namespace(BaseModel):
    __tablename__ = 'namespaces'

    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    md_content = Column(Text, nullable=False)
    status = Column(Integer, default=1)
    active = Column(Boolean, default=True)

    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user = relationship('User',
                        backref=backref('namespaces', lazy=True)
                        )

    tags = relationship('Tag',
                        secondary=namespace_tags,
                        lazy='subquery',
                        backref=backref('namespaces', lazy=True)
                        )

    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    book = relationship('Book', backref='namespaces')


class Post(BaseModel):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)

    namespace_id = Column(Integer,
                          ForeignKey('namespaces.id'),
                          nullable=False)
    namespace = relationship('Namespace',
                             backref='posts')

    user_id = Column(Integer,
                     ForeignKey('users.id'),
                     nullable=False)

    user = relationship('User',
                        backref='posts')
