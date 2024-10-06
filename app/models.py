from datetime import datetime
from app.db import db_session
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship, declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now)
    updated = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class User(BaseModel):
    __tablename__ = 'users_table'
    username = Column(String(64), unique=True, nullable=False)
    url_identifier = Column(String(64), unique=True, nullable=False)

    email = Column(String(128), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    status = Column(Integer, default=0)

    bio = Column(Text, nullable=True)

    namespaces = relationship('Namespace', back_populates='user', lazy='dynamic')
    pages = relationship('Page', back_populates='user', lazy='dynamic')
    sections = relationship('Section', back_populates='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Namespace(BaseModel):
    __tablename__ = 'namespaces_table'
    name = Column(String(64), nullable=False)
    url_identifier = Column(String(64), unique=True, nullable=False)

    md_content = Column(Text, nullable=True)
    status = Column(Integer, default=1)

    user_id = Column(Integer, ForeignKey('users_table.id'), nullable=False)
    user = relationship('User', back_populates='namespaces')
    pages = relationship('Page', back_populates='namespace', lazy='dynamic')

    def __repr__(self):
        return f'<Namespace {self.name}>'


class Page(BaseModel):
    __tablename__ = 'pages_table'
    title = Column(String(256), nullable=False)
    url_identifier = Column(String(64), unique=True, nullable=False)

    md_content = Column(Text, nullable=True)
    status = Column(Integer, default=1)

    namespace_id = Column(Integer, ForeignKey('namespaces_table.id'), nullable=False)
    namespace = relationship('Namespace', back_populates='pages')

    user_id = Column(Integer, ForeignKey('users_table.id'), nullable=False)
    user = relationship('User', back_populates='pages')

    sections = relationship('Section', back_populates='page', lazy='dynamic')

    def __repr__(self):
        return f'<Page {self.title}>'


class Section(BaseModel):
    __tablename__ = 'sections_table'
    title = Column(String(200), nullable=False)

    md_content = Column(Text, nullable=True)
    status = Column(Integer, default=1)

    page_id = Column(Integer, ForeignKey('pages_table.id'), nullable=False)
    page = relationship('Page', back_populates='sections')

    user_id = Column(Integer, ForeignKey('users_table.id'), nullable=False)
    user = relationship('User', back_populates='sections')

    def __repr__(self):
        return f'<Section {self.title}>'
