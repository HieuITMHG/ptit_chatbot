from core.database import db

users_collection = db["users"]

def get_user(username: str):
    user_lst = users_collection.find_one({"username": username})
    return user_lst
    
    
