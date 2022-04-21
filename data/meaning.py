import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Meaning(SqlAlchemyBase):
    __tablename__ = 'meanings'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    objects = orm.relation('Object', back_populates='meaning')


class Type(SqlAlchemyBase):
    __tablename__ = 'types'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    objects = orm.relation('Object', back_populates='type')
