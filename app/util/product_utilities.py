import os


def convert_dollar_to_cents(price):
    return int(price) * 100


def get_inventory_with_valid_image_value(inventory):
    for item in inventory:
        item["image"] = os.getenv("STRAPI_SERVICE_URL") + item["image"]["url"]
    return inventory


def validate_cart_items(inventory, cart_details):
    """
    Arguments:
        inventory: products list from trusted source (from Strapi cms)
        cart_details: user's cart details coming from UI

    Returns:
        Stripe Lines Items in a List
        Example: [{
            "price": 1000 (or could be stripe's price id. not in our case though),
            "quantity": 1
        }],
    """
    validated_items = []
    for item_id in cart_details:
        product = cart_details[item_id]

        # use item_id to find existence of product in inventory
        inventory_item = next(
            filter(lambda i: i["id"] == int(item_id), inventory), None
        )

        if not inventory_item:
            raise Exception(f"Product {item_id} not found!")

        item = {
            "price_data": {
                "currency": inventory_item["currency"],
                "unit_amount": convert_dollar_to_cents(inventory_item["price"]),
                "product_data": {"name": inventory_item["name"]},
            },
            "quantity": product["quantity"],
        }

        if "description" in inventory_item:
            item["price_data"]["product_data"]["description"] = inventory_item[
                "description"
            ]

        if "image" in inventory_item:
            item["price_data"]["product_data"]["images"] = [inventory_item["image"]]

        if "price_data" in inventory_item:
            item["price_data"] = {item["price_data"], inventory_item["price_data"]}

        if "product_data" in inventory_item:
            item["price_data"]["product_data"] = {
                item["price_data"]["product_data"],
                inventory_item["product_data"],
            }

        validated_items.append(item)

    return validated_items
