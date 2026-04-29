from core.database import db

users_collection = db["users"]

def get_user(username: str):
    return users_collection.find_one({"username": username})


def create_user_if_not_exists(username: str, hashed_password: str):
    existing = users_collection.find_one({"username": username})
    if existing:
        print("Đã có test user")
        return existing

    user_doc = {
        "username": username,
        "hashed_password": hashed_password
    }
    users_collection.insert_one(user_doc)
    print("Đã tạo test user")
    return user_doc