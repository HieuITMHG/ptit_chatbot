from .etl.save_raw_html import crawl_raw_html
from .etl.parse_data import parse_data
from core.config_loader import PipelineConfig
from core.config import settings
from rag.enums.rag_type import RagType
from FlagEmbedding import BGEM3FlagModel
from .build_index import IndexBuilder

def run(rag, crawl=False, parse=False, chunk=False, embed=False):
    if (chunk or embed) and not rag:
        print("Phải chọn loại rag cho chunk và embed")
        return
    print(f"rag: {rag}")
    if rag:
        if rag == RagType.HYBRID.value:
            config = PipelineConfig("configs/hybrid_rag.yaml")
        elif rag == RagType.NAIVE.value:
            config = PipelineConfig("configs/naive_rag.yaml")
        elif rag == RagType.RERANK.value:
            config = PipelineConfig("configs/rerank_rag.yaml")

        embedder = BGEM3FlagModel(config.embedding["model"])
        
        index_builder = IndexBuilder(config=config, embedder=embedder)
    need_parse = None
    url_lst = None
    chunk_lst = None

    if crawl:
        need_parse = crawl_raw_html(settings.sitemap_index_url)
    if parse:
        url_lst = parse_data(need_parse)
    if chunk:
        chunk_lst = index_builder.chunking_pipeline(url_lst=url_lst)
    if embed:
        index_builder.embedding_pipeline(chunk_lst=chunk_lst)

    if not (crawl or parse or chunk or embed):
        print("Không có tác vụ nào được chọn")