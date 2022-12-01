from werkzeug.security import generate_password_hash, check_password_hash
from ..daos import user_dao
from ..models import User

class UserAuthenticationException(Exception):
    pass

class UserService:
    def check_password(self, user_id, password):
        user = user_dao.get_by_id(user_id)
        if user is None or not check_password_hash(user.password, password):
            return False
        return True
    
#    def generate_auth_token(self, user_id, secret_key, expiration):
        #return Serializer(secret_key, expires_in=expiration).dumps({"user_id": user_id}).decode('utf-8')

    def add(self, username, password, email):
        password_hash=generate_password_hash(password)
        user = user_dao.add(username, password_hash, email)
        return user
    
user_service = UserService()