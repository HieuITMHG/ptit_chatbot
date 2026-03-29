import json

with open("evaluation/ds_gen/enrich_dataset.json", "r", encoding="utf-8") as f:
    query_lst = json.load(f)

pre_lst = []
top_k = 5

for query in query_lst:
    pre = len(query["relevant_chunks"]) / 5
    pre_lst.append(pre)
print(sum(pre_lst)/200)
