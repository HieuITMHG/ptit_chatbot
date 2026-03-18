from core.database import db
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.test_case import LLMTestCase
import time
from deepeval.models import GPTModel
from core.config import settings


class GenerationMetric:
    def __init__(self, rag_engine, data_config, top_k):
        self.rag_engine = rag_engine
        self.top_k = top_k

        self.qrels_collection = db[data_config["qrels_col_name"]]
        self.queries_collection = db[data_config["queries_col_name"]]

        self.model = GPTModel(
            model="gpt-4o-mini",
            api_key=settings.openai_key
        )

        self.answer_metric = AnswerRelevancyMetric(
            threshold=0.7,
            model=self.model
        )

        self.faithfulness_metric = FaithfulnessMetric(
            threshold=0.7,
            model=self.model,
            include_reason=True
        )

    def answer_relevancy(self, query, actual_res):
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_res
        )

        self.answer_metric.measure(test_case)

        return self.answer_metric.score, self.answer_metric.reason

    def faithfulness(self, query, actual_res, contexts):
        test_case = LLMTestCase(
            input=query,
            actual_output=actual_res,
            retrieval_context=contexts
        )

        self.faithfulness_metric.measure(test_case)

        return self.faithfulness_metric.score, self.faithfulness_metric.reason

    def evaluate(self):

        query_lst = [
            {"query_content": "tư vấn tuyển sinh đại học cao đẳng ptit 2014 2025"},
            {"query_content": "Chỉ tiêu đầu vào của chương trình CNTT chất lượng cao năm 2022 và phương thức xét tuyển các đợt 2016, 2022 có khác biệt gì?"},
            {"query_content": "Đối tượng nào được miễn giảm chi phí học tập năm 2025-2026, và ngành Marketing yêu cầu môn gì để vào học?"},
            {"query_content": "Yêu cầu hồ sơ để trở thành Master Trainer tại PTIT là gì và nếu muốn học ngành Công nghệ IoT thì tìm thông tin ở đề án 2019 có không?"},
            {"query_content": "Cơ sở vật chất của Ký túc xá tại Học viện Cơ sở có gì nổi bật và mức phí lưu trú hàng tháng là bao nhiêu?"},
        ]

        for query in query_lst:

            t0 = time.perf_counter()

            retrieved_contexts = self.rag_engine.retrieve(
                query=query["query_content"],
                top_k=self.top_k
            )

            context_texts = [c["chunk_content"] if isinstance(c, dict) else str(c) for c in retrieved_contexts]

            t1 = time.perf_counter()

            llm_response = self.rag_engine.generate(
                contexts=retrieved_contexts,
                query=query["query_content"]
            )

            t2 = time.perf_counter()

            ans_rel, ans_reason = self.answer_relevancy(
                query=query["query_content"],
                actual_res=llm_response
            )

            faith, faith_reason = self.faithfulness(
                query=query["query_content"],
                actual_res=llm_response,
                contexts=context_texts
            )

            t3 = time.perf_counter()

            retrieve_latency = t1 - t0
            generate_latency = t2 - t1
            judge_latency = t3 - t2
            total_latency = t3 - t0

            print("\n==============================")
            print("Query:", query["query_content"])
            print("\nAnswer:")
            print(llm_response)

            print("\nAnswer Relevancy:", ans_rel)
            print(ans_reason)

            print("\nFaithfulness:", faith)
            print(faith_reason)

            print("\nLatency")
            print("retrieve:", f"{retrieve_latency:.2f}s")
            print("generate:", f"{generate_latency:.2f}s")
            print("judge:", f"{judge_latency:.2f}s")
            print("total:", f"{total_latency:.2f}s")