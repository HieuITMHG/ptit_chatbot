import math
from core.database import db
from model.retrieval_result import RetrievalResult

resuls_collection = db["retrieval_results"]

class RetrievalMetric:
    def __init__(self, rag_engine, data_config, top_k):
        self.rag_engine = rag_engine
        self.top_k = top_k

        self.qrels_collection = db[data_config["qrels_col_name"]]
        self.queries_collection = db[data_config["queries_col_name"]]

        self.qrels_map = {}
        for rel in self.qrels_collection.find({}, {"_id": 0}):
            qid = rel["query_id"]
            cid = rel["chunk_id"]
            score = rel["relevance_score"]

            if qid not in self.qrels_map:
                self.qrels_map[qid] = {}

            self.qrels_map[qid][cid] = score

    def _prepare_eval_data(self, query_id, results):
        rel_map = self.qrels_map.get(query_id, {})
        rel_ids = set(rel_map.keys())

        result_ids = [r["id"] for r in results[: self.top_k]]

        total_rel = len(rel_ids)

        intersection = len(set(result_ids) & rel_ids)

        return {
            "rel_ids": rel_ids,
            "rel_map": rel_map,
            "result_ids": result_ids,
            "total_rel": total_rel,
            "intersection": intersection
        }

    def precision_recall(self, eval_data):
        total_rel = eval_data["total_rel"]
        result_len = len(eval_data["result_ids"])
        intersection = eval_data["intersection"]

        if total_rel == 0 or result_len == 0:
            return 0.0, 0.0

        precision = intersection / result_len
        recall = intersection / total_rel

        return precision, recall

    def ndcg(self, eval_data):
        rel_ids = eval_data["rel_ids"]
        result_ids = eval_data["result_ids"]

        dcg = 0.0
        for i, doc_id in enumerate(result_ids):
            if doc_id in rel_ids:
                dcg += 1 / math.log2(i + 2)

        ideal_hits = min(len(rel_ids), len(result_ids))

        idcg = sum(
            1 / math.log2(i + 2)
            for i in range(ideal_hits)
        )

        if idcg == 0:
            return 0.0

        return dcg / idcg
    
    def mrr(self, eval_data):
        rel_ids = eval_data["rel_ids"]
        result_ids = eval_data["result_ids"]

        for i, doc_id in enumerate(result_ids):
            if doc_id in rel_ids:
                return 1 / (i + 1)

        return 0.0
    
    def hit(self, eval_data):
        return eval_data["intersection"] >= 1

    def evaluate(self):
        query_lst = list(self.queries_collection.find({}, {"_id": 0}))

        precision_lst = []
        recall_lst = []
        ndcg_lst = []
        mrr_lst = []
        hit_lst = []

        for idx, query in enumerate(query_lst):
            
            results = self.rag_engine.retrieve(
                query=query["query_content"],
                top_k=self.top_k
            )

            eval_data = self._prepare_eval_data(
                query_id=query["id"],
                results=results
            )

            precision, recall = self.precision_recall(eval_data)
            ndcg = self.ndcg(eval_data)
            mrr = self.mrr(eval_data)
            hit = self.hit(eval_data)

            print(f"precision@{self.top_k} query {idx}: {precision}")
            
            precision_lst.append(precision)
            recall_lst.append(recall)
            ndcg_lst.append(ndcg)
            mrr_lst.append(mrr)
            hit_lst.append(hit)

        precision = sum(precision_lst) / len(precision_lst)
        recall = sum(recall_lst) / len(recall_lst)
        hit = sum(hit_lst) / len(hit_lst)
        ndcg = sum(ndcg_lst) / len(ndcg_lst)
        mrr = sum(mrr_lst) / len(mrr_lst)

        result = RetrievalResult(precision=precision,
                                 recall=recall,
                                 hit=hit,
                                 ndcg=ndcg,
                                 mrr=mrr,
                                 top_k=self.top_k)
        
        resuls_collection.insert_one(result.model_dump())

        metrics = [
            f"\nprecision@{self.top_k}: {sum(precision_lst) / len(precision_lst)}",
            f"\nrecall@{self.top_k}: {sum(recall_lst) / len(recall_lst)}",
            f"\nhit@{self.top_k}: {sum(hit_lst) / len(hit_lst)}",
            f"\nndcg@{self.top_k}: {sum(ndcg_lst) / len(ndcg_lst)}",
            f"\nMRR: {sum(mrr_lst) / len(mrr_lst)}",
        ]

        return metrics