import os
class Config:
    MONGO_URI =  "mongodb+srv://siddhigandhi:Siddhi2013@cluster0.4yg1e.mongodb.net/krishna_pearls?retryWrites=true&w=majority&appName=Cluster0"

    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Folder to store images
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}  # Allowed file extensions for images
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Max upload size of 16MB