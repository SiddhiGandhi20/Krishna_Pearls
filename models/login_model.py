from werkzeug.security import check_password_hash

class LoginModel:
    def __init__(self, db):
        self.collection = db.signup

    def validate_user_login(self, email, password):
        """Validate user login credentials."""
        user = self.collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            return user  # Return user data if authentication is successful
        return None  # Return None if authentication fails
