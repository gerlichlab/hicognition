from flask_restx import Resource, fields, marshal_with, Namespace
from app.services.user import user_service
from app.daos import user_dao
from .. import api, ma

user_ns = Namespace('user', 'User related endpoints.')


user_fields = {
    'id': fields.Integer(description="Unique identifying user id", readonly=True),
    'username': fields.String(required=True, description="Nickname used for login."),
    'email': fields.String(required=True, description="Email used for login."),
}

class BaseSchema(ma.Schema):
    
    pass

class UserSchemaResponseSchema(ma.Schema):
    # id = ma.fields.Int(dump_only=True)
    # username = ma.fields.String()
    # email = ma.fields.String()
    
    class Meta:
        fields = ("id", "username", "email")

class UserSchemaRequest(ma.Schema):
    class Meta:
        fields = ("id", "username", "email", "password")




@user_ns.route('/')
class UserAPI(Resource):
    @marshal_with(user_fields, envelope='user')
    def get(self):
        user = user_dao.get_all()
        return user
    def post(self):
        return "test"
        pass

@user_ns.route('/<int:id>')
class UserIdAPI(Resource):
    @marshal_with(user_fields, envelope='user')
    def get(self, id):
        user = user_dao.get_by_id(id)
        #return user_service.check_password('dev')
        return user
    def post(self, id):
        return "test"
        pass

api.add_namespace(user_ns) 