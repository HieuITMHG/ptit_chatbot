import yaml
from qdrant_client.models import VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Distance

from core.qdrant import client
from core.database import db

quoties_collection = db["quoties"]

def load_config(path):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
    
def embed_quote(config):
    col_name = config["col_name"]
    encoder = SentenceTransformer(config["model_name"])
    quoties = list(quoties_collection.find({},{"_id": 0}))
    

    print(encoder.get_sentence_embedding_dimension())

    if not client.collection_exists(col_name):
        client.create_collection(
            collection_name = col_name,
            vectors_config = VectorParams(size=encoder.get_sentence_embedding_dimension(),
                                          distance = Distance.COSINE)
        )
        print(f"Đã tạo thành công collection {col_name} !!")
    else:
        print(f"Collection {col_name} đã tồn tại !!")
    
    #Upload data
    print("Đang upload vector")

    BATCH_SIZE = 100

    for i in range(0, len(quoties), BATCH_SIZE):
        batch_quotes = quoties[i:i + BATCH_SIZE]
        
        texts_to_encode = [quote["quote_content"] for quote in batch_quotes]
        batch_vectors = encoder.encode(texts_to_encode).tolist()
        
        points = []
        for j, quote in enumerate(batch_quotes):
            global_idx = i + j 
            points.append(
                PointStruct(id=global_idx, vector=batch_vectors[j], payload=quote)
            )
        
        client.upload_points(
            collection_name=col_name,
            points=points,
            wait=True 
        )
        
        print(f"Đã cập nhật lên DB xong {i + len(batch_quotes)} / {len(quoties)} points")

    print("Đã upload xong data")

if __name__ == "__main__":
    config = load_config("embedding_eval/eval_pipeline/model_config.yaml")
    print(config["m-e5-base"])
    embed_quote(config=config["m-e5-base"])