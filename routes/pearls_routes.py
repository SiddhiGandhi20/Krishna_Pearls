import os
from flask import Blueprint, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
from bson import ObjectId

def create_pearl_routes(db, upload_folder):
    pearl_bp = Blueprint('pearls', __name__)

    # Helper function to serialize ObjectId
    def serialize_objectid(obj):
        """Convert ObjectId to string for JSON serialization"""
        if isinstance(obj, ObjectId):
            return str(obj)
        return obj

    # Set the image folder path (relative to the project root directory)
    image_folder = os.path.join(os.path.dirname(__file__), '../uploads')

    # POST: Create a new Pearl
    @pearl_bp.route("/pearls", methods=["POST"])
    def create_pearl():
        try:
            # Extract form-data
            pearl_id = request.form.get("id")  # Custom ID
            name = request.form.get("name")
            origin = request.form.get("origin")
            carat = request.form.get("carat")
            image = request.files.get("image")  # Extract image file

            # Check if all required fields are present
            if not all([pearl_id, name, origin, carat, image]):
                return jsonify({"message": "Missing required fields"}), 400

            # Save image file
            filename = secure_filename(image.filename)
            image_path = os.path.join(image_folder, filename)
            image.save(image_path)

     

            # Prepare data to insert into MongoDB
            pearl_data = {
                "id": pearl_id,  # Use custom ID
                "name": name,
                "origin": origin,
                "carat": carat,
                "image": filename  # Store image filename instead of full path
            }

            # Insert into MongoDB
            result = db.pearls.insert_one(pearl_data)

            # Convert the result ObjectId to string
            pearl_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string

            # Return the pearl data
            return jsonify(serialize_objectid(pearl_data)), 201  # Return the created pearl

        except Exception as e:
            return jsonify({"message": f"Error creating pearl: {str(e)}"}), 500

    # GET: Fetch all pearls
    @pearl_bp.route("/pearls", methods=["GET"])
    def get_all_pearls():
        try:
            pearls = list(db.pearls.find())  # Fetch all pearls from MongoDB
            # Ensure all ObjectId fields are serialized
            for pearl in pearls:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
            return jsonify(pearls)

        except Exception as e:
            return jsonify({"message": f"Error fetching pearls: {str(e)}"}), 500

    # GET: Fetch a single pearl by custom ID
    @pearl_bp.route("/pearls/<id>", methods=["GET"])
    def get_pearl_by_id(id):
        try:
            pearl = db.pearls.find_one({"id": id})  # Fetch by custom id
            if pearl:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
                # Add the image URL (this could be your public image path)
                if 'image' in pearl:
                    pearl['image_url'] = f"/images/{pearl['image']}"  # Assuming you serve images from /images/<filename>
                return jsonify(pearl)
            return jsonify({"message": "Pearl not found"}), 404

        except Exception as e:
            return jsonify({"message": f"Error fetching pearl: {str(e)}"}), 500

    # PUT: Update a pearl by custom ID
    @pearl_bp.route("/pearls/<id>", methods=["PUT"])
    def update_pearl(id):
        try:
            pearl = db.pearls.find_one({"id": id})
            if not pearl:
                return jsonify({"message": "Pearl not found"}), 404

            # Get data to update
            updated_data = request.form.to_dict()
            if "image" in request.files:
                # Handle image update
                image = request.files.get("image")
                filename = secure_filename(image.filename)
                image_path = os.path.join(image_folder, filename)
                image.save(image_path)
                updated_data["image"] = filename

            # Update the pearl in the database
            result = db.pearls.update_one({"id": id}, {"$set": updated_data})
            if result.modified_count > 0:
                return jsonify({"message": "Pearl updated successfully"})
            return jsonify({"message": "No changes made"}), 400

        except Exception as e:
            return jsonify({"message": f"Error updating pearl: {str(e)}"}), 500

    # DELETE: Delete a pearl by custom ID
    @pearl_bp.route("/pearls/<id>", methods=["DELETE"])
    def delete_pearl(id):
        try:
            result = db.pearls.delete_one({"id": id})
            if result.deleted_count > 0:
                return jsonify({"message": "Pearl deleted successfully"})
            return jsonify({"message": "Pearl not found"}), 404

        except Exception as e:
            return jsonify({"message": f"Error deleting pearl: {str(e)}"}), 500

    # Serve the image from the uploads folder
    @pearl_bp.route('/images/<filename>', methods=['GET'])
    def get_image(filename):
        try:
            # Return image from the provided image folder
            return send_from_directory(image_folder, filename)
        except Exception as e:
            return jsonify({"message": f"Error fetching image: {str(e)}"}), 500

    return pearl_bp
