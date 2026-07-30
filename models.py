from flask_login import UserMixin


class AdminUser(UserMixin):
    def __init__(self, username):
        self.id = username
