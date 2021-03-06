import os

import sqlalchemy
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from .tools.hash import generate_hash


class Object(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'objects'
    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    region_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)
    meaning_id = sqlalchemy.Column(sqlalchemy.Integer,
                                   sqlalchemy.ForeignKey("meanings.id"),
                                   nullable=False)
    meaning = orm.relation('Meaning')

    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("types.id"),
                                nullable=False)
    type = orm.relation('Type')

    comments = orm.relation('Comments', back_populates='obj')

    is_unesco = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    video_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    picture_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    _hash = None

    def __hash__(self):
        if self._hash is None:
            self._hash = generate_hash()
        return self._hash

    def set_video_path(self, path):
        from main import app
        if path.filename == '':
            self.video_path = None
            return
        self.video_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'vid/' + self.__hash__() + path.filename[-4:]
        path.save(self.video_path)

    def set_picture_path(self, path):
        from main import app
        if path.filename == '':
            self.picture_path = os.path.join(
                app.config[
                    'UPLOAD_FOLDER']
            ) + 'img/' + 'default_pic.png'
            return

        self.picture_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'img/' + self.__hash__() + path.filename[-4:]
        path.save(self.picture_path)

    def set_paths(self, video_path, picture_path):
        self.set_video_path(video_path)
        self.set_picture_path(picture_path)
