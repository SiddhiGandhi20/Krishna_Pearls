import jwt
import datetime
from flask import Blueprint, request, jsonify
from models.login_model import LoginModel

# Blueprint setup
login_bp = Blueprint("login", __name__)

# Secret key for signing JWT tokens (store securely, e.g., in environment variables)
SECRET_KEY = "your_secret_key"

def create_login_routes(db):
    login_model = LoginModel(db)

    @login_bp.route("/login", methods=["POST"])
    def login():
        """API endpoint to login an existing user."""
        data = request.get_json()

        # Extract data from request
        email = data.get("email")
        password = data.get("password")

        # Input validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Validate user credentials
        user = login_model.validate_user_login(email, password)
        if user:
            # Generate JWT token
            payload = {
                "id": str(user["_id"]),  # Serialize ObjectId to string
                "email": user["email"],
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),  # Token expiration time
            }
            token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

            return jsonify({"message": "Login successful", "token": token}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 400

    return login_bp
