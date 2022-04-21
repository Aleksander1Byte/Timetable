import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase


class Object(SqlAlchemyBase, UserMixin, SerializerMixin):
    PREVIEW_SIZE = (400, 600)
    __tablename__ = 'objects'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    id_region = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    meaning_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("meanings.id"),
                                   nullable=False)
    meaning = orm.relation('Meaning')

    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("types.id"),
                                nullable=False)
    type = orm.relation('Type')

    is_unesco = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)

    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
