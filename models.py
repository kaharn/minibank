class User:
    def __init__(self, username, password, full_name):
        self.username = username
        self.password = password
        self.full_name = full_name

    def to_dict(self):
        return {
            "username": self.username,
            "password": self.password,
            "full_name": self.full_name
        }