from pymongo import MongoClient
from pwdlib import PasswordHash
from app.schemas.user import UserInDB

def run_insert():
    uri = "mongodb://admin:admin123@mongo:27017/admin"
    client = MongoClient(uri)
    db = client["PTITBOT"]
    users_collection = db["users"]

    password_hash = PasswordHash.recommended()

    raw_password = "123456"
    user_data = {
        "username": "huuhieu",
        "email": "danghuuhieu038@gmail.com",
        "full_name": "Dang Huu Hieu",
        "disabled": False
    }

    hashed_password = password_hash.hash(raw_password)
    user_in_db = UserInDB(**user_data, hashed_password=hashed_password)

    try:

        if users_collection.find_one({"username": user_data["username"]}):
            print("User này đã tồn tại rồi!")
        else:
            result = users_collection.insert_one(user_in_db.model_dump())
            print(f"Thành công! ID: {result.inserted_id}")
    except Exception as e:
        print(f"Lỗi: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    run_insert()