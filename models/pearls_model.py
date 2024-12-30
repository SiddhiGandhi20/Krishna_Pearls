from bson import ObjectId

class PearlModel:
    def __init__(self, db):
        self.collection = db.pearls  # Access the 'pearls' collection

    def get_all_pearls(self):
        """Fetch all pearls from the collection."""
        try:
            pearls = list(self.collection.find())  # Get all documents in the collection
            # Convert ObjectId to string for JSON serialization
            for pearl in pearls:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
            return pearls
        except Exception as e:
            print(f"Error fetching data: {e}")
            return None
        
    def get_pearl_by_id(self, pearl_id):
        """Fetch a single pearl by its ID."""
        try:
            pearl = self.collection.find_one({"_id": ObjectId(pearl_id)})
            if pearl:
                pearl["_id"] = str(pearl["_id"])  # Convert ObjectId to string
            return pearl
        except Exception as e:
            print(f"Error fetching pearl: {e}")
            return None

    def create_pearl(self, data):
        """Create a new pearl in the collection."""
        try:
            result = self.collection.insert_one(data)  # Insert the new pearl
            return str(result.inserted_id)  # Return the inserted ID as a string
        except Exception as e:
            print(f"Error creating pearl: {e}")
            return None

    def update_pearl(self, pearl_id, data):
        """Update an existing pearl by its ID."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(pearl_id)}, {"$set": data}
            )
            return result.modified_count > 0  # Return True if update was successful
        except Exception as e:
            print(f"Error updating pearl: {e}")
            return False

    def delete_pearl(self, pearl_id):
        """Delete a pearl by its ID."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(pearl_id)})
            return result.deleted_count > 0  # Return True if deletion was successful
        except Exception as e:
            print(f"Error deleting pearl: {e}")
            return False
