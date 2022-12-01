from flask_restx import Resource, fields, marshal_with
from app.services.user import user_service
from app.daos import user_dao
from .. import api, ma

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




@api.route('/user')
class UserAPI(Resource):
    @marshal_with(user_fields, envelope='user')
    def get(self):
        user = user_dao.get_all()
        return user_service.get_by_name_and_pw('dev', 'asdf')
    def post(self):
        return "test"
        pass

@api.route('/user/<int:id>')
class UserIdAPI(Resource):
    @marshal_with(user_fields, envelope='user')
    def get(self, id):
        user = user_dao.get_by_id(id)
        return user
    def post(self, id):
        return "test"
        pass
