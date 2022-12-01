from flask_restx import Resource, fields, marshal_with
from app.services.user import user_service
from app.daos import feature1d_dao, feature2d_dao, regionset_dao
from .. import api, ma
from flask import Blueprint, request, g
from flask.json import jsonify
from flask import current_app
from flask_restx import Resource, fields, Api, marshal_with, Namespace
import marshmallow as mm
from .. import api, ma

basefeatureset_model_dict = {
    'id': fields.Integer(),
    'name': fields.String(),
    'owner': fields.Integer(),
    
    # TODO how to handle nested objects e.g. files, user_ids or tags?
}

class BaseFeatureSetAPI(Resource):
    dao = None
    def get(self):
        return self.dao.get_all()
    def post(self):
        raise NotImplementedError
    def delete(self):
        raise NotImplementedError
    def put(self):
        raise NotImplementedError

ns_regionset = Namespace('region', 'Routes for RegionSet datasets.')
@ns_regionset.route('/')
class RegionSetAPI(BaseFeatureSetAPI):
    dao = regionset_dao
    pass

ns_feature1d = Namespace('feature1d', 'Routes for Feature1D (bigwig) datasets.')
@ns_feature1d.route('/')
class RegionSetAPI(BaseFeatureSetAPI):
    dao = feature1d_dao
    pass

ns_feature2d = Namespace('feature2d', 'Routes for Feature2D (HiC) datasets.')
@ns_feature2d.route('/')
class RegionSetAPI(BaseFeatureSetAPI):
    dao = feature2d_dao
    pass

api.add_namespace(ns_regionset)
api.add_namespace(ns_feature1d)
api.add_namespace(ns_feature2d)


# user_fields = {
#     'id': fields.Integer(description="Unique identifying user id", readonly=True),
#     'username': fields.String(required=True, description="Nickname used for login."),
#     'email': fields.String(required=True, description="Email used for login."),
# }

# class BaseSchema(ma.Schema):
    
#     pass

# class UserSchemaResponseSchema(ma.Schema):
#     # id = ma.fields.Int(dump_only=True)
#     # username = ma.fields.String()
#     # email = ma.fields.String()
    
#     class Meta:
#         fields = ("id", "username", "email")

# class UserSchemaRequest(ma.Schema):
#     class Meta:
#         fields = ("id", "username", "email", "password")




# @api.route('/user')
# class UserAPI(Resource):
#     @marshal_with(user_fields, envelope='user')
#     def get(self):
#         user = user_dao.get_all()
#         return user_service.get_by_name_and_pw('dev', 'asdf')
#     def post(self):
#         return "test"
#         pass

# @api.route('/user/<int:id>')
# class UserIdAPI(Resource):
#     @marshal_with(user_fields, envelope='user')
#     def get(self, id):
#         user = user_dao.get_by_id(id)
#         return user
#     def post(self, id):
#         return "test"
#         pass
