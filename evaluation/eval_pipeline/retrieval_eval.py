from pipelines.naive_rag_pipeline import NaiveRag
from core.config_loader import PipelineConfig
from core.database import db
from .metrics import precision_recall

queries_collection = db["queries"]

if __name__ == "__main__":
    config = PipelineConfig("configs/base.yaml").embedding
    rag_engine = NaiveRag(embedding_model=config["model"],
                          collection_name=config["col_name"])
    query_lst = list(queries_collection.find({}))

    recall_lst = []
    precision_lst = []
    
    top_k = 10

    for query in query_lst:
        results = rag_engine.retriever(query=query["query_content"], top_k=top_k)

        precision, recall = precision_recall(query_id=query["id"], results=results, top_k=top_k)

        precision_lst.append(precision)
        recall_lst.append(recall)

        print(f"Recall query {query["id"]}: {recall}")
        print(f"Precision query {query["id"]}: {precision}")
    
    total_recall = sum(recall_lst)
    total_precision = sum(precision_lst)

    print(f"Tổng recall là {total_recall/len(query_lst)}")
    print(f"Tổng precision là {total_precision/len(query_lst)}")
    
    
