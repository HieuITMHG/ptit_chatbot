from core.database import db
import re
import unicodedata

documents_collection = db["documents"]

output_path = "data_ingestion/etl/data_eval_result.txt"

if __name__ == "__main__":
    docs = documents_collection.find({})
    count = 0
    for doc in docs:
        
        text = re.sub(r"\n+", " ", doc["content"]).strip()
        text = unicodedata.normalize("NFC", text)

        documents_collection.update_one(
            {"_id": doc["_id"]},
            {"$set": {"content": text}}
        )
        print(count)
        count += 1
        

