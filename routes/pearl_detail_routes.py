import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from bson import ObjectId
from models.pearl_detail_model import PearlDetailModel

# Initialize Blueprint
pearl_detail_bp = Blueprint("pearl_detail_bp", __name__)

# Instantiate the model
pearl_detail_model = None

# Set the image folder path
image_folder = os.path.join(os.path.dirname(__file__), '../uploads')

def create_pearl_detail_routes(db):
    global pearl_detail_model
    pearl_detail_model = PearlDetailModel(db)

    # Fetch details using pearl_id from the `pearls` collection
    @pearl_detail_bp.route("/pearl/<pearl_id>/details", methods=["GET"])
    def get_details_by_pearl_id(pearl_id):
        try:
            # Validate pearl_id
            if not ObjectId.is_valid(pearl_id):
                return jsonify({"message": "Invalid pearl_id"}), 400

            # Fetch the pearl document from the pearls collection
            pearl = db.pearls.find_one({"_id": ObjectId(pearl_id)})
            if not pearl:
                return jsonify({"message": "Pearl not found"}), 404

            # Fetch associated details from the detail_pearl collection
            details = list(db.detail_pearl.find({"pearl_id": pearl_id}))
            for detail in details:
                detail["_id"] = str(detail["_id"])  # Convert ObjectId to string for JSON serialization

            # Convert pearl `_id` to string for serialization
            pearl["_id"] = str(pearl["_id"])

            return jsonify({"pearl": pearl, "details": details}), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching pearl details: {str(e)}"}), 500

    # Create a new pearl detail
    @pearl_detail_bp.route("/pearl/<pearl_id>/detail", methods=["POST"])
    def create_pearl_detail(pearl_id):
        try:
            if not ObjectId.is_valid(pearl_id):
                return jsonify({"message": "Invalid pearl_id"}), 400

            name = request.form.get("name")
            origin = request.form.get("origin")
            carat = request.form.get("carat")
            per_carat_price = request.form.get("per_carat_price")
            total_price = request.form.get("total_price")
            image = request.files.get("image")

            if not all([name, origin, carat, per_carat_price, total_price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            filename = secure_filename(image.filename)
            image_path = os.path.join(image_folder, filename)
            image.save(image_path)

            inserted_id = pearl_detail_model.create_pearl_detail(
                pearl_id, name, origin, carat, per_carat_price, total_price, filename
            )

            return jsonify({"message": "Pearl detail created", "id": inserted_id}), 201
        except Exception as e:
            return jsonify({"message": f"Error creating pearl detail: {str(e)}"}), 500

    # Get all pearl details
    @pearl_detail_bp.route("/pearl_detail", methods=["GET"])
    def get_pearl_details():
        try:
            details = pearl_detail_model.get_pearl_details()
            return jsonify(details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching pearl details: {str(e)}"}), 500

    # Get a single pearl detail by its ID
    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["GET"])
    def get_pearl_detail(detail_id):
        try:
            detail = pearl_detail_model.get_pearl_detail_by_id(detail_id)
            if detail:
                return jsonify(detail), 200
            return jsonify({"message": "Pearl detail not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error fetching pearl detail: {str(e)}"}), 500

    # Update a pearl detail
    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["PUT"])
    def update_pearl_detail(detail_id):
        try:
            updated_data = {key: request.form.get(key) for key in request.form}
            if not updated_data:
                return jsonify({"message": "No data provided for update"}), 400

            # Handle image update if necessary
            if "image" in request.files:
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(image_folder, filename)
                image.save(image_path)
                updated_data["image"] = filename

            success = pearl_detail_model.update_pearl_detail(detail_id, updated_data)
            if success:
                return jsonify({"message": "Pearl detail updated"}), 200
            return jsonify({"message": "No changes made or pearl detail not found"}), 400
        except Exception as e:
            return jsonify({"message": f"Error updating pearl detail: {str(e)}"}), 500

    # Delete a pearl detail
    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["DELETE"])
    def delete_pearl_detail(detail_id):
        try:
            success = pearl_detail_model.delete_pearl_detail(detail_id)
            if success:
                return jsonify({"message": "Pearl detail deleted"}), 200
            return jsonify({"message": "Pearl detail not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error deleting pearl detail: {str(e)}"}), 500

    # Serve image files
    @pearl_detail_bp.route('/images/<filename>', methods=['GET'])
    def get_image(filename):
        try:
            return send_from_directory(image_folder, filename)
        except Exception as e:
            return jsonify({"message": f"Error fetching image: {str(e)}"}), 500

    return pearl_detail_bp
