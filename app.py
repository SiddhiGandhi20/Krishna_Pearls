from flask import Flask
from flask_pymongo import PyMongo
from config import Config

from routes.user_routes import create_auth_routes
from routes.login_routes import create_login_routes
from routes.admin_routes import create_admin_routes
from routes.product_routes import create_product_routes

app = Flask(__name__)

# Load MongoDB configuration
app.config.from_object(Config)
mongo = PyMongo(app)

app.register_blueprint(create_auth_routes(mongo.db))
app.register_blueprint(create_login_routes(mongo.db))
app.register_blueprint(create_admin_routes(mongo.db))
app.register_blueprint(create_product_routes(mongo.db, app.config["UPLOAD_FOLDER"]))


if __name__ == "__main__":
    app.run(debug=True)