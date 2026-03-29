# from pymongo import MongoClient
# from core.config import settings 
# from core.database import db, local_db

# documents_collection = local_db["documents"]

# def sync_cloud_to_local(batch_size=1000):
#     # Lấy danh sách tất cả các collection đang có trên Cloud
#     collections = db.list_collection_names()
    
#     print(f"Tìm thấy {len(collections)} collections. Bắt đầu đồng bộ...\n")

#     for coll_name in collections:
#         print(f"⏳ Đang xử lý collection: '{coll_name}'...")
#         cloud_collection = db[coll_name]
#         local_collection = local_db[coll_name]

#         # LƯU Ý: Xóa sạch dữ liệu cũ của collection này ở local trước khi copy 
#         # để tránh lỗi trùng lặp _id (DuplicateKeyError)
#         local_collection.drop() 

#         # Lấy dữ liệu từ cloud
#         cursor = cloud_collection.find()
        
#         batch = []
#         total_inserted = 0

#         # Duyệt qua từng bản ghi và gom thành từng đợt (batch)
#         for doc in cursor:
#             batch.append(doc)
            
#             # Đủ số lượng batch_size thì tiến hành insert 1 lần
#             if len(batch) == batch_size:
#                 local_collection.insert_many(batch)
#                 total_inserted += len(batch)
#                 batch = [] # Làm trống batch để hứng đợt tiếp theo

#         # Insert những bản ghi còn sót lại (nếu tổng số không chia hết cho batch_size)
#         if batch:
#             local_collection.insert_many(batch)
#             total_inserted += len(batch)

#         print(f"✅ Hoàn tất '{coll_name}'! Đã copy {total_inserted} bản ghi.\n")

#     print("🎉 TẤT CẢ DỮ LIỆU ĐÃ ĐƯỢC ĐỒNG BỘ VỀ LOCAL THÀNH CÔNG!")

# if __name__ == "__main__":
#     sync_cloud_to_local()