from bson import ObjectId

class CartModel:
    def __init__(self, db):
        self.collection = db.cart  # Assuming the cart data is stored in a "cart" collection

    def add_to_cart(self, pearl_id, quantity, image_url=None):
        """Add a product to the cart or update its quantity if already present."""
        pearl = self.collection.database.detail_pearl.find_one({"_id": ObjectId(pearl_id)})

        if not pearl:
            raise ValueError("Pearl not found")

        # Ensure quantity, carat, and per_carat_price are numbers
        try:
            quantity = int(quantity)  # Ensure quantity is an integer
            carat = float(pearl["carat"])  # Ensure carat is a float
            per_carat_price = float(pearl["per_carat_price"])  # Ensure per_carat_price is a float
        except ValueError as e:
            raise ValueError("Invalid value for quantity, carat, or per_carat_price: " + str(e))

        # Calculate total price
        total_price = quantity * per_carat_price * carat

        existing_item = self.collection.find_one({"pearl_id": pearl_id})
        if existing_item:
            # Update quantity and total price
            new_quantity = existing_item["quantity"] + quantity
            total_price = new_quantity * per_carat_price * carat  # Update total price
            self.collection.update_one(
                {"pearl_id": pearl_id},
                {"$set": {
                    "quantity": new_quantity,
                    "total_price": total_price,
                    "image_url": image_url,
                    "name": pearl["name"],
                    "origin": pearl["origin"],
                    "carat": carat,
                    "per_carat_price": per_carat_price
                }}
            )
        else:
            # Add new item to the cart
            cart_item = {
                "pearl_id": pearl_id,
                "name": pearl["name"],
                "origin": pearl["origin"],
                "carat": carat,
                "per_carat_price": per_carat_price,
                "quantity": quantity,
                "total_price": total_price,
                "image_url": image_url
            }
            self.collection.insert_one(cart_item)

        return True


    def update_cart_item(self, pearl_id, quantity, image_url=None, total_price=None):
        # Ensure there's no conflict in the number of arguments
        cart_item = self.collection.find_one({"pearl_id": pearl_id})

        if cart_item:
            # Update the cart item with the new data
            updated_fields = {"quantity": quantity}
            if image_url:
                updated_fields["image_url"] = image_url
            if total_price:
                updated_fields["total_price"] = total_price

            self.collection.update_one(
                {"pearl_id": pearl_id},
                {"$set": updated_fields}
            )
            return True
        else:
            return False
        
    def get_cart_items(self):
        """Retrieve all items in the cart."""
        cart_items = list(self.collection.find())
        
        # Convert ObjectId to string for all fields
        for item in cart_items:
            item["_id"] = str(item["_id"])  # Convert the ObjectId to a string
            item["pearl_id"] = str(item["pearl_id"])  # Ensure product_id is also a string (if needed)
        
        total_price = sum(float(item["total_price"]) for item in cart_items)
        
        return {"items": cart_items, "total_price": total_price}


    def remove_from_cart(self, pearl_id):
        """Remove a product from the cart."""
        result = self.collection.delete_one({"pearl_id": pearl_id})
        return result.deleted_count > 0

    def clear_cart(self):
        """Remove all items from the cart."""
        self.collection.delete_many({})
        return True
