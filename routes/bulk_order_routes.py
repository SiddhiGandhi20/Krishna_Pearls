from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import os
from bson import ObjectId

def create_bulk_order_routes(db, upload_folder):
    bulk_order_bp = Blueprint('bulk_order', __name__)

    # Helper function to serialize ObjectId
    def serialize_objectid(obj):
        """Convert ObjectId to string for JSON serialization"""
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj

    # POST: Create a new Pearl
    @bulk_order_bp.route("/bulk_order", methods=["POST"])
    def create_pearl():
        try:
            # Extract form-data
            pearl_id = request.form.get("id")  # Custom ID
            name = request.form.get("name")
            origin = request.form.get("origin")
            per_carat_price = request.form.get("per_carat_price")
            image = request.files.get("image")  # Extract image file

            # Check if all required fields are present
            if not all([pearl_id, name, origin, per_carat_price, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Save image file
            filename = secure_filename(image.filename)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)

            # Prepare data to insert into MongoDB (only storing the filename)
            pearl_data = {
                "id": pearl_id,  # Use custom ID
                "name": name,
                "origin": origin,
                "per_carat_price": per_carat_price,
                "image": filename  # Store only the filename in the DB
            }

            # Insert into MongoDB
            result = db.bulk_order.insert_one(pearl_data)

            # Convert the result ObjectId to string
            pearl_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string

            # Return the pearl data
            return jsonify(serialize_objectid(pearl_data)), 201  # Return the created pearl

        except Exception as e:
            return jsonify({"message": f"Error creating pearl: {str(e)}"}), 500

    # GET: Fetch all pearls
    @bulk_order_bp.route("/bulk_order", methods=["GET"])
    def get_all_pearls():
        try:
            pearls = list(db.bulk_order.find())  # Fetch all pearls from MongoDB
            # Ensure all ObjectId fields are serialized
            for pearl in pearls:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
            return jsonify(pearls)

        except Exception as e:
            return jsonify({"message": f"Error fetching pearls: {str(e)}"}), 500

    # GET: Fetch a single pearl by custom ID
    @bulk_order_bp.route("/bulk_order/<id>", methods=["GET"])
    def get_pearl_by_id(id):
        try:
            pearl = db.bulk_order.find_one({"id": id})  # Fetch by custom id
            if pearl:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
                return jsonify(pearl)
            return jsonify({"message": "Pearl not found"}), 404

        except Exception as e:
            return jsonify({"message": f"Error fetching pearl: {str(e)}"}), 500

    # PUT: Update a pearl by custom ID
    @bulk_order_bp.route("/bulk_order/<id>", methods=["PUT"])
    def update_pearl(id):
        try:
            pearl = db.bulk_order.find_one({"id": id})
            if not pearl:
                return jsonify({"message": "Pearl not found"}), 404

            # Get data to update
            updated_data = request.form.to_dict()
            if "image" in request.files:
                # Handle image update
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(upload_folder, filename)
                image.save(image_path)
                updated_data["image"] = filename  # Store only filename

            # Update the pearl in the database
            result = db.bulk_order.update_one({"id": id}, {"$set": updated_data})
            if result.modified_count > 0:
                return jsonify({"message": "Pearl updated successfully"})
            return jsonify({"message": "No changes made"}), 400

        except Exception as e:
            return jsonify({"message": f"Error updating pearl: {str(e)}"}), 500

    # DELETE: Delete a pearl by custom ID
    @bulk_order_bp.route("/bulk_order/<id>", methods=["DELETE"])
    def delete_pearl(id):
        try:
            result = db.bulk_order.delete_one({"id": id})
            if result.deleted_count > 0:
                return jsonify({"message": "Pearl deleted successfully"})
            return jsonify({"message": "Pearl not found"}), 404

        except Exception as e:
            return jsonify({"message": f"Error deleting pearl: {str(e)}"}), 500

    # Serve images from the 'uploads' directory
    @bulk_order_bp.route('/images_bulk/<filename>', methods=['GET'])
    def get_image(filename):
        try:
            # Return image from the provided image folder
            return send_from_directory(upload_folder, filename)
        except Exception as e:
            return jsonify({"message": f"Error fetching image: {str(e)}"}), 500

    return bulk_order_bp