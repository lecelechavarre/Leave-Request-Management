from models.user_model import UserModel

class AuthController:
    @staticmethod
    def login(username, password):
        if UserModel.verify(username, password):
            return UserModel.get_user(username)
        return None

    @staticmethod
    def register(username, password, role='employee'):
        return UserModel.add_user(username, password, role)
