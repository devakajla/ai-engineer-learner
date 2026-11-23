COLLECTION = {"list": "GET", "create": "POST"}
ITEM = {"read": "GET", "replace": "PUT", "update": "PATCH", "delete": "DELETE"}


def rest_endpoint(action, resource, item_id=None):
    if action in COLLECTION:
        return COLLECTION[action], f"/{resource}"
    if action in ITEM:
        if item_id is None:
            raise ValueError(f"{action} needs an item_id")
        return ITEM[action], f"/{resource}/{item_id}"
    raise ValueError(f"unknown action: {action}")
