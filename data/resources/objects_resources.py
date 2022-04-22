from flask import jsonify
from flask_restful import Resource, abort

from data.comments import Comments
from data.db_session import create_session
from data.objects import Object
from data.reg_parse_object import parser


def abort_if_object_not_found(object_id):
    session = create_session()
    object = session.query(Object).get(object_id)
    if not object:
        abort(404, message=f"Object {object_id} not found")


class ObjectsResource(Resource):
    def get(self, object_id):
        abort_if_object_not_found(object_id)
        session = create_session()
        object = session.query(Object).get(object_id)
        return jsonify({'Objects': object.to_dict(
            only=('id', 'name', 'region_id', 'meaning_id', 'type_id',
                  'is_unesco', 'description', 'video_path', 'picture_path'))})

    def delete(self, object_id):
        import os
        abort_if_object_not_found(object_id)
        db_sess = create_session()
        obj = db_sess.query(Object).get(object_id)
        if obj.picture_path != 'static/media/img/default_pic.png':
            os.remove(obj.picture_path)
        if obj.video_path:
            os.remove(obj.video_path)
        db_sess.query(Comments).filter(Comments.post_id == obj.id).delete()
        db_sess.delete(obj)
        db_sess.commit()
        return jsonify({'success': 'OK'})


class ObjectsListResource(Resource):
    def get(self):
        session = create_session()
        objects = session.query(Object).all()
        return jsonify({'Objects': [item.to_dict(
            only=('id', 'name', 'region_id', 'meaning_id', 'type_id',
                  'is_unesco', 'description', 'video_path', 'picture_path'))
            for item in objects]})

    def post(self):
        args = parser.parse_args()
        session = create_session()
        if session.query(Object).filter(Object.id == args['id']).first():
            return jsonify({'error': 'Object with that id already exists'})
        video = args['video'] if 'video' in args else None
        picture = args['picture'] if 'picture' in args else None
        object = Object(
            id=args['id'],
            name=args['name'],
            region_id=args['region_id'],
            meaning_id=args['meaning_id'],
            type_id=args['type_id'],
            is_unesco=args['is_unesco'],
            description=args['description']
        )
        object.set_paths(video, picture)
        session.add(object)
        session.commit()
        return jsonify({'success': 'OK'})
