from flask import Flask, jsonify, send_from_directory
from flask_pymongo import PyMongo
from config import Config
from flask_cors import CORS  # Import CORS
from routes.user_routes import create_auth_routes
from routes.login_routes import create_login_routes
from routes.admin_routes import create_admin_routes
from routes.product_routes import create_product_routes
from routes.pearls_routes import create_pearl_routes
from routes.pearl_detail_routes import create_pearl_detail_routes
from routes.bulk_order_routes import create_bulk_order_routes
import os

# Initialize Flask app
app = Flask(__name__)

# Enable CORS (Cross-Origin Resource Sharing) for all routes
# You can specify origins instead of '*' for more security
CORS(app, resources={r"/*": {"origins": "*"}})

# Load MongoDB configuration
app.config.from_object(Config)
mongo = PyMongo(app)

# Endpoint to serve image from uploads folder
@app.route('/uploads/<filename>')
def get_image(filename):
    try:
        # Construct file path and check if the file exists
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        else:
            return jsonify({"message": "Image not found"}), 404
    except Exception as e:
        return jsonify({"message": f"Error fetching image: {str(e)}"}), 500
    


# Register route blueprints for different parts of your app
app.register_blueprint(create_auth_routes(mongo.db))
app.register_blueprint(create_login_routes(mongo.db))
app.register_blueprint(create_admin_routes(mongo.db))
app.register_blueprint(create_product_routes(mongo.db, app.config["UPLOAD_FOLDER"]))
app.register_blueprint(create_pearl_routes(mongo.db, app.config["UPLOAD_FOLDER"]))
app.register_blueprint(create_pearl_detail_routes(mongo.db))
app.register_blueprint(create_bulk_order_routes(mongo.db, app.config["UPLOAD_FOLDER"]))

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
