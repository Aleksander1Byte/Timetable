import sqlalchemy
import os
from flask_login import UserMixin
from sqlalchemy import orm
from sqlalchemy_serializer import SerializerMixin

from .db_session import SqlAlchemyBase
from .tools.hash import generate_hash


class Object(SqlAlchemyBase, UserMixin, SerializerMixin):
    PREVIEW_SIZE = (400, 600)
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
    is_unesco = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    video_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    picture_path = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    __hash__ = generate_hash()

    def set_video_path(self, path):
        from main import app
        self.video_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'vid/' + self.__hash__ + path.filename[-4:]
        path.save(self.video_path)

    def set_picture_path(self, path):
        from main import app
        self.picture_path = os.path.join(
            app.config[
                'UPLOAD_FOLDER']
        ) + 'img/' + self.__hash__ + path.filename[-4:]
        path.save(self.picture_path)

    def set_paths(self, video_path, picture_path):
        self.set_video_path(video_path)
        self.set_picture_path(picture_path)
