from flask import Blueprint, request, jsonify
from models.pearl_detail_model import PearlDetailModel
from bson import ObjectId

# Initialize Blueprint
pearl_detail_bp = Blueprint("pearl_detail_bp", __name__)

# Instantiate the model
pearl_detail_model = None

def create_pearl_detail_routes(db):
    global pearl_detail_model
    pearl_detail_model = PearlDetailModel(db)

    @pearl_detail_bp.route("/pearl/<pearl_id>/detail", methods=["POST"])
    def create_pearl_detail(pearl_id):
        try:
            # Validate `pearl_id`
            if not ObjectId.is_valid(pearl_id):
                return jsonify({"message": "Invalid pearl_id"}), 400

            # Parse form data
            name = request.form.get("name")
            origin = request.form.get("origin")
            carat = request.form.get("carat")
            weight = request.form.get("weight")
            per_carat_price = request.form.get("per_carat_price")
            total_price = request.form.get("total_price")
            image = request.form.get("image")

            # Check for missing fields
            if not all([name, origin, carat, weight, per_carat_price, total_price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Call the model to create the detail
            inserted_id = pearl_detail_model.create_pearl_detail(
                pearl_id, name, origin, carat, weight, per_carat_price, total_price, image
            )
            return jsonify({"message": "Pearl detail created", "id": inserted_id}), 201
        except Exception as e:
            return jsonify({"message": f"Error creating pearl detail: {str(e)}"}), 500

    @pearl_detail_bp.route("/pearl_detail", methods=["GET"])
    def get_pearl_details():
        try:
            details = pearl_detail_model.get_pearl_details()
            return jsonify(details), 200
        except Exception as e:
            return jsonify({"message": f"Error fetching pearl details: {str(e)}"}), 500

    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["GET"])
    def get_pearl_detail(detail_id):
        try:
            detail = pearl_detail_model.get_pearl_detail_by_id(detail_id)
            if detail:
                return jsonify(detail), 200
            return jsonify({"message": "Pearl detail not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error fetching pearl detail: {str(e)}"}), 500

    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["PUT"])
    def update_pearl_detail(detail_id):
        try:
            updated_data = {key: request.form.get(key) for key in request.form}
            if not updated_data:
                return jsonify({"message": "No data provided for update"}), 400

            success = pearl_detail_model.update_pearl_detail(detail_id, updated_data)
            if success:
                return jsonify({"message": "Pearl detail updated"}), 200
            return jsonify({"message": "No changes made or pearl detail not found"}), 400
        except Exception as e:
            return jsonify({"message": f"Error updating pearl detail: {str(e)}"}), 500

    @pearl_detail_bp.route("/pearl_detail/<detail_id>", methods=["DELETE"])
    def delete_pearl_detail(detail_id):
        try:
            success = pearl_detail_model.delete_pearl_detail(detail_id)
            if success:
                return jsonify({"message": "Pearl detail deleted"}), 200
            return jsonify({"message": "Pearl detail not found"}), 404
        except Exception as e:
            return jsonify({"message": f"Error deleting pearl detail: {str(e)}"}), 500

    return pearl_detail_bp
