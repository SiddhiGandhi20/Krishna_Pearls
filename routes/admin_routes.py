from flask import Blueprint, request, jsonify
from models.admin_model import AdminModel

# Blueprint setup
admin_bp = Blueprint("admin", __name__)

def create_admin_routes(db):
    admin_model = AdminModel(db)

    # Admin Registration Route
    @admin_bp.route("/admin/signup", methods=["POST"])
    def admin_signup():
        """API endpoint to register a new admin."""
        data = request.get_json()

        # Extract data from request
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        # Input validation
        if not (name and email and password and confirm_password):
            return jsonify({"error": "All fields are required"}), 400

        if password != confirm_password:
            return jsonify({"error": "Passwords do not match"}), 400

        # Check for duplicate email
        if admin_model.is_email_registered(email):
            return jsonify({"error": "Email already registered"}), 400

        # Create new admin
        admin_model.create_admin(name, email, password)
        return jsonify({"message": "Admin registered successfully"}), 201

    # Admin Login Route
    @admin_bp.route("/admin/login", methods=["POST"])
    def admin_login():
        """API endpoint to login an existing admin."""
        data = request.get_json()

        # Extract data from request
        email = data.get("email")
        password = data.get("password")

        # Input validation
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        # Validate admin credentials
        admin = admin_model.validate_admin_login(email, password)
        if admin:
            # Serialize ObjectId to string
            admin["_id"] = str(admin["_id"])
            return jsonify({"message": "Login successful", "admin": admin}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 400

    return admin_bp
