from bson import ObjectId

class PearlDetailModel:
    def __init__(self, db):
        self.collection = db.detail_pearl  # Use the 'detail_pearl' collection

    def create_pearl_detail(self, pearl_id, name, origin, carat, weight, per_carat_price, total_price, image):
        """Insert a new pearl detail document."""
        try:
            detail = {
                "pearl_id": pearl_id,
                "name": name,
                "origin": origin,
                "carat": carat,
                "weight": weight,
                "per_carat_price": per_carat_price,
                "total_price": total_price,
                "image": image,
            }
            result = self.collection.insert_one(detail)
            return str(result.inserted_id)  # Return the inserted ID as a string
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def get_pearl_details(self):
        """Fetch all pearl details."""
        try:
            details = list(self.collection.find())
            for detail in details:
                detail["_id"] = str(detail["_id"])  # Convert ObjectId to string
            return details
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def get_pearl_detail_by_id(self, detail_id):
        """Fetch a pearl detail by its ID."""
        try:
            detail = self.collection.find_one({"_id": ObjectId(detail_id)})
            if detail:
                detail["_id"] = str(detail["_id"])  # Convert ObjectId to string
            return detail
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def update_pearl_detail(self, detail_id, updated_data):
        """Update a pearl detail document."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(detail_id)}, {"$set": updated_data}
            )
            return result.modified_count > 0  # Return True if any document was updated
        except Exception as e:
            raise Exception(f"Database error: {e}")

    def delete_pearl_detail(self, detail_id):
        """Delete a pearl detail document."""
        try:
            result = self.collection.delete_one({"_id": ObjectId(detail_id)})
            return result.deleted_count > 0  # Return True if any document was deleted
        except Exception as e:
            raise Exception(f"Database error: {e}")
