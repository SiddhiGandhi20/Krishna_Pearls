import re
from flask import Blueprint, request, jsonify
from flask_cors import CORS  # Import CORS
from models.user_model import UserModel

# Blueprint setup
auth_bp = Blueprint("auth", __name__)
CORS(auth_bp)  # Enable CORS for this blueprint

def create_auth_routes(db):
    user_model = UserModel(db)

    @auth_bp.route("/signup", methods=["POST"])
    def signup():
        """API endpoint to register a new user."""
        data = request.get_json()

        # Extract data from request
        name = data.get("name")
        email = data.get("email")
        mobile = data.get("mobile")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Input validation
        if not (name and email and mobile and password and confirm_password):
            return jsonify({"error": "All fields are required"}), 400

        if not re.match(r"^[0-9]{10}$", mobile):
            return jsonify({"error": "Invalid mobile number"}), 400

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return jsonify({"error": "Invalid email address"}), 400

        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check for duplicate email and mobile
        if user_model.is_email_registered(email):
            return jsonify({"error": "Email already registered"}), 400

        if user_model.is_mobile_registered(mobile):
            return jsonify({"error": "Mobile number already registered"}), 400

        # Create new user
        user_model.create_user(name, email, mobile, password)
        return jsonify({"message": "User registered successfully"}), 201

    return auth_bp
