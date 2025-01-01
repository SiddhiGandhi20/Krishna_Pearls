from flask import Blueprint, request, jsonify,current_app as app
from bson import ObjectId
from werkzeug.utils import secure_filename
import os
from models.cart_model import CartModel

def create_cart_routes(db):
    cart_bp = Blueprint('cart', __name__)
    cart_model = CartModel(db)

    @cart_bp.route('/cart', methods=['POST'])
    def add_to_cart():
        try:
            # Get data from form fields
            pearl_id = request.form.get('pearl_id')
            quantity = request.form.get('quantity', type=int)  # Convert to int for quantity
            file = request.files.get('image')  # Get the image file

            if not pearl_id or quantity <= 0:
                return jsonify({"message": "Invalid pearl ID or quantity"}), 400

            image_url = None
            if file:
                # Ensure safe file saving
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Now call the add_to_cart method with the correct number of arguments
            cart_model.add_to_cart(pearl_id, quantity, image_url)
            return jsonify({"message": "Pearl added to cart successfully"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500


    # Other routes...
    @cart_bp.route('/cart', methods=['GET'])
    def get_cart():
        try:
            cart_items = cart_model.get_cart_items()
            total_price = 0  # Initialize total price

            # Add details for each item in the cart and calculate the total price
            for item in cart_items['items']:
                pearl = cart_model.collection.database.detail_pearl.find_one({"_id": ObjectId(item["pearl_id"])})
                if pearl:
                    item["name"] = pearl["name"]
                    item["origin"] = pearl["origin"]
                    item["carat"] = float(pearl["carat"])  # Ensure carat is a float
                    item["per_carat_price"] = float(pearl["per_carat_price"])  # Ensure price is a float
                    item["quantity"] = item["quantity"]  # Ensure quantity is an integer
                    item["total_price"] = int(item["quantity"] * item["per_carat_price"] * item["carat"])  # Calculate total price

                    item["image_url"] = item.get("image_url")  # Ensure image_url is correct

                    # Add item total_price to the cart total, keeping it an integer
                    total_price += item["total_price"]

            # Return the cart items with the total price
            return jsonify({
                "items": cart_items["items"],
                "total_price": total_price  # Total price as integer
            }), 200

        except Exception as e:
            return jsonify({"message": str(e)}), 500


    @cart_bp.route('/cart/<pearl_id>', methods=['PUT'])
    def update_cart(pearl_id):
        try:
            # Get quantity and image from the request
            quantity = request.form.get('quantity')
            file = request.files.get('image')

            # Validate quantity
            if not quantity or int(quantity) <= 0:
                return jsonify({"message": "Invalid quantity"}), 400

            # Fetch the pearl details from 'detail_pearl' collection
            pearl = cart_model.collection.database.detail_pearl.find_one({"_id": ObjectId(pearl_id)})
            if not pearl:
                return jsonify({"message": "Pearl not found"}), 404

            # Calculate total price: (quantity * per_carat_price * carat)
            carat = float(pearl["carat"])  # Ensure carat is a float
            per_carat_price = float(pearl["per_carat_price"])  # Ensure price is a float
            total_price = int(int(quantity) * per_carat_price * carat)  # Use int to get total price

            # Handle image file if present
            image_url = None
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(os.getcwd(), 'uploads', filename))
                image_url = os.path.join('uploads', filename)

            # Update the cart item with quantity, image_url, and total_price
            updated = cart_model.update_cart_item(pearl_id, int(quantity), image_url, total_price)
            if updated:
                return jsonify({"message": "Cart item updated successfully"}), 200
            else:
                return jsonify({"message": "Cart item not found"}), 404
        except Exception as e:
            return jsonify({"message": str(e)}), 500
        

    @cart_bp.route('/cart/<pearl_id>', methods=['DELETE'])
    def remove_from_cart(pearl_id):
        try:
            if cart_model.remove_from_cart(pearl_id):
                return jsonify({"message": "Pearl removed from cart"}), 200
            else:
                return jsonify({"message": "Pearl not found in cart"}), 404
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    @cart_bp.route('/cart/clear', methods=['DELETE'])
    def clear_cart():
        try:
            cart_model.clear_cart()
            return jsonify({"message": "Cart cleared successfully"}), 200
        except Exception as e:
            return jsonify({"message": str(e)}), 500

    return cart_bp
