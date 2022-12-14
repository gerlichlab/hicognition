import marshal
from flask import Blueprint, request, g
from flask.json import jsonify
from flask import current_app
from flask_restx import Resource, fields, Api, marshal_with, Namespace
import marshmallow as mm
from app.services.file import file_service
from app.daos import file_dao
from .. import api, ma

file_ns = Namespace('file', 'File related endpoints.')
file_model = file_ns.model('File', {
    "id": fields.Integer(),
    "md5": fields.String(),
    "user_id": fields.String(),
    "name": fields.String(),
})

class FilePostSchema(ma.Schema):
    file = mm.fields.Raw(type='file')
file_post_schema = FilePostSchema()


file_post_model = file_ns.model('FileCreate', {
    #"name": fields.String,,
    "hash": fields.Integer(),
    "user_id": fields.String(),
    "file": fields.Raw('file')
})

@file_ns.route('/')
class FileAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self):
        return file_dao.get_all()

@file_ns.route('/<string:hash>')
class FileHashAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self, hash):
        user_id = 1 # TODO get logged in
        return file_dao.get_by_hash_userid(hash, user_id)

    @file_ns.expect(file_post_model)
    @file_ns.marshal_with(file_model)
    def post(self, hash: str):
        """Used to send files to the server.
        Files can only be created if the user has sent an md5 hash first and got the okay.

        Args:
            hash (str): Hash of the uploaded file

        Returns:
            File: newly created file object
        """
       #=file_post_schema.load(request.files)
        data = request.files['data']
        user_id = request.form.get('user_id')
        file_name=data.filename
        file_stream=data.stream
        return file_service.create(hash, file_stream, file_name, 1), 201 # g.current_user.id), 201 # USER ID NOT SET YET

@file_ns.route('/<int:id>')
class FileIdAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self, id):
        return file_dao.get_by_id(id)
    
    # TODO what to give back here
    def delete(self):
        # update file entry
        pass
    
api.add_namespace(file_ns)