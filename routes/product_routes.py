from bson.objectid import ObjectId
from flask import Blueprint, request, jsonify, current_app
from pymongo.synchronous import collection
from werkzeug.utils import secure_filename
import os
from models.product_model import ProductModel

# Blueprint setup
product_bp = Blueprint("product", __name__)

def create_product_routes(db, upload_folder):
    product_model = ProductModel(db, upload_folder)

    # Create a folder for images if it doesn't exist
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Allowed file extensions for image upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    def allowed_file(filename):
        """Check if the uploaded file has an allowed extension."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    # Add product route
    @product_bp.route("/admin/product/add", methods=["POST"])
    def add_product():
        """API endpoint to add a product with image and details."""
        data = request.form  # To handle form data (text + image)

        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        image = request.files.get("image")  # This will be the uploaded image file

        # Input validation
        if not (name and description and price and image):
            return jsonify({"error": "All fields are required"}), 400

        if not allowed_file(image.filename):
            return jsonify({"error": "Invalid image format. Allowed formats are: png, jpg, jpeg, gif."}), 400

        # Secure the filename to prevent security issues
        filename = secure_filename(image.filename)

        # Save the image to the upload folder
        image_path = os.path.join(upload_folder, filename)
        image.save(image_path)

        # Store the product in the database
        product_model.create_product(name, description, price, filename)

        return jsonify({"message": "Product added successfully"}), 201

    # Get all products route
    @product_bp.route("/admin/products", methods=["GET"])
    def get_all_products():
        """Retrieve all products from the database."""
        products = product_model.get_all_products()

        # Convert ObjectId to string for all products
        for product in products:
            product['_id'] = str(product['_id'])

        return jsonify({"products": products}), 200

    # Get product by name route
    @product_bp.route("/admin/product/update/<name>", methods=["PUT"])
    def update_product(name):
        """API endpoint to update a product by its name."""
        updated_data = request.get_json()

        # Validate that data is provided
        if not updated_data:
            return jsonify({"error": "No data provided for update"}), 400

        # Reference the correct collection
        product_collection = db["products"]  # Ensure this matches your actual collection name

        # Perform the update (case-insensitive match for the name)
        result = product_collection.update_one(
            {"name": {"$regex": f"^{name}$", "$options": "i"}},  # Query for case-insensitive name match
            {"$set": updated_data}  # Update operation
        )

        # Handle update result
        if result.matched_count == 0:
            return jsonify({"error": "Product not found"}), 404
        elif result.modified_count == 0:
            return jsonify({"message": "No changes were made"}), 200
        else:
            return jsonify({"message": "Product updated successfully"}), 200


    # Delete product by name route
    @product_bp.route("/admin/product/delete/<name>", methods=["DELETE"])
    def delete_product(name):
        """API endpoint to delete a product by its name."""
        if product_model.delete_product_by_name(name):
            return jsonify({"message": "Product deleted successfully"}), 200
        else:
            return jsonify({"error": "Product not found"}), 404

    return product_bp
