from pymongo import MongoClient
from pwdlib import PasswordHash
from app.schemas.user import UserInDB
# Import collection hoặc tự tạo tạm thời để insert
# Nếu repo của bạn đang dùng 'mongo:27017', hãy tạo client mới ở đây để ghi đè

def run_insert():
    # 1. Kết nối tới localhost vì bạn đang chạy ngoài Docker
    # Thay admin/password123 bằng thông tin bạn đã set trong docker-compose
    uri = "mongodb://admin:admin123@localhost:27017/admin"
    client = MongoClient(uri)
    db = client["PTITBOT"] # Tên database của bạn
    users_collection = db["users"]

    password_hash = PasswordHash.recommended()

    # 2. Dữ liệu user
    raw_password = "123456"
    user_data = {
        "username": "huuhieu",
        "email": "danghuuhieu038@gmail.com",
        "full_name": "Dang Huu Hieu",
        "disabled": False
    }

    # 3. Hash và Validate
    hashed_password = password_hash.hash(raw_password)
    user_in_db = UserInDB(**user_data, hashed_password=hashed_password)

    # 4. Thực hiện Insert
    try:
        # Kiểm tra xem user đã tồn tại chưa để tránh trùng lặp
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