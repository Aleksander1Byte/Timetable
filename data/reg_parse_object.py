from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('id', required=False)
parser.add_argument('name', required=True)
parser.add_argument('region_id', required=True)
parser.add_argument('meaning_id', required=True)
parser.add_argument('type_id', required=True)
parser.add_argument('is_unesco', required=False)
parser.add_argument('description', required=False)
parser.add_argument('video_path', required=False)
parser.add_argument('picture_path', required=False)
