from flask import Blueprint, request, jsonify
from models.login_model import LoginModel

# Blueprint setup
login_bp = Blueprint("login", __name__)

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
            # Serialize ObjectId to string
            user["_id"] = str(user["_id"])
            return jsonify({"message": "Login successful", "user": user}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 400

    return login_bp
