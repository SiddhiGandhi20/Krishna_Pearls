from werkzeug.security import check_password_hash, generate_password_hash
from bson import ObjectId

class AdminModel:
    def __init__(self, db):
        self.collection = db.admins  # You can create a separate collection for admins

    def is_email_registered(self, email):
        """Check if the email is already registered."""
        return self.collection.find_one({"email": email})

    def create_admin(self, name, email, password):
        """Insert a new admin into the database."""
        hashed_password = generate_password_hash(password)
        admin_data = {
            "name": name,
            "email": email,
            "password": hashed_password
        }
        self.collection.insert_one(admin_data)
        return True

    def validate_admin_login(self, email, password):
        """Validate admin login credentials."""
        admin = self.collection.find_one({"email": email})
        if admin and check_password_hash(admin["password"], password):
            return admin  # Return admin data if authentication is successful
        return None  # Return None if authentication fails
