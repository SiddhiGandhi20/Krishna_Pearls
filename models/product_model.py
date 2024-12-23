from werkzeug.utils import secure_filename
import os
from flask_pymongo import PyMongo
from bson import ObjectId

class ProductModel:
    def __init__(self, db, upload_folder):
        self.collection = db.products  # Assuming the product data is stored in a "products" collection
        self.upload_folder = upload_folder  # Directory for storing uploaded product images

    def create_product(self, name, description, price, image_filename):
        """Insert a new product into the database."""
        product_data = {
            "name": name,
            "description": description,
            "price": price,
            "image_url": image_filename  # Store the filename or URL for the image
        }
        self.collection.insert_one(product_data)
        return True

    def get_all_products(self):
        """Retrieve all products from the database."""
        # Fetch products from the database
        products = list(self.collection.find())
        return products

    def get_product_by_name(self, name):
        """Retrieve a product by its name."""
        return self.collection.find_one({"name": name})
    
    def update_product_by_name(self, name, updated_data):
        """Update a product's details by its name."""
        print(f"Attempting to update product with name: {name}")
        result = self.collection.update_one(
            {"name": name},
            {"$set": updated_data}
        )
        print(f"Matched count: {result.matched_count}, Modified count: {result.modified_count}")
        return result.modified_count > 0

    def delete_product_by_name(self, name):
        """Delete a product by its name."""
        result = self.collection.delete_one({"name": name})
        return result.deleted_count > 0  # Returns True if the product was deleted
