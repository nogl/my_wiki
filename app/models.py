from . import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import DateTime


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(DateTime, default=datetime.utcnow)
    updated = db.Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get(id)


class User(BaseModel):
    __tablename__ = 'users'

    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    status = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


# Tabla de asociación para tags
namespace_tags = db.Table('namespace_tags',
                          db.Column('namespace_id', db.Integer, db.ForeignKey('namespaces.id'), primary_key=True),
                          db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True)
                          )


class Tag(BaseModel):
    __tablename__ = 'tags'

    name = db.Column(db.String(50), unique=True, nullable=False)


class Namespace(BaseModel):
    __tablename__ = 'namespaces'

    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    md_content = db.Column(db.Text, nullable=False)
    status = db.Column(db.Integer, default=1)
    active = db.Column(db.Boolean, default=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User',
                           backref=db.backref('namespaces', lazy=True)
                           )
    tags = db.relationship('Tag',
                           secondary=namespace_tags,
                           lazy='subquery',
                           backref=db.backref('namespaces', lazy=True)
                           )
