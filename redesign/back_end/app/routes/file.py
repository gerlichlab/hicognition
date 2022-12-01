import marshal
from flask import Blueprint, request, g
from flask.json import jsonify
from flask import current_app
from flask_restx import Resource, fields, Api, marshal_with, Namespace
import marshmallow as mm
from app.services.file import file_service
from app.daos import file_dao
from .. import api, ma
import app.routes.models as rx_models

file_ns = Namespace('file', 'File related endpoints.')
file_model = rx_models.file_model(file_ns)

class FilePostSchema(ma.Schema):
    file = mm.fields.Raw(type='file')
file_post_schema = FilePostSchema()


file_post_model = file_ns.model('FileCreate', {
    #"name": fields.String,
    "file": fields.Raw('file')
})

@file_ns.route('/')
class FileAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self):
        return file_dao.get_all()
    
    @file_ns.expect(file_post_model)
    @file_ns.marshal_with(file_model)
    @marshal_with(file_model)
    def post(self):
        data=file_post_schema.load(request.files)
        file_name=data['file'].filename
        file_stream=data['file'].stream
        return file_service.create(file_stream, file_name, 1), 201 # g.current_user.id), 201

@file_ns.route('/<int:id>')
class FileIdAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self, id):
        return file_dao.get_by_id(id)
    
    # TODO what to give back here
    def delete(self):
        # update file entry
        pass
    
@file_ns.route('/<string:md5>')
class FileHashAPI(Resource):
    @file_ns.marshal_with(file_model)
    def get(self, md5):
        return file_dao.get_by_hash(md5)
    
api.add_namespace(file_ns)