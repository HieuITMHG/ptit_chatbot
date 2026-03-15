from .fixed_chunker import FixedSizeChunker
from .semantic_chunker import SemanticChunker
from .enrich_hybrid import EnrichHybrid
from enums.chunk_type import ChunkType
from .helpers import length_function, encoding, embedder

def build_chunker(config):

    chunk_type = config["type"]

    if chunk_type == ChunkType.FIXED.value:
        return FixedSizeChunker(
            encoding=encoding,
            chunk_size=config["chunk_size"],
            chunk_overlap=config["overlap"],
            length_function=length_function
        )
    if chunk_type == ChunkType.SEMANTIC.value:
        return  SemanticChunker(encoding=encoding,
                                embedder=embedder,
                                chunk_size=config["chunk_size"],
                                chunk_overlap=config["overlap"],
                                length_function=length_function)
    if chunk_type == ChunkType.ENRICHHYBRID.value:
        return EnrichHybrid(embedder=embedder,
                            encoding=encoding,
                            chunk_size=config["chunk_size"],
                            chunk_overlap=config["overlap"],
                            length_function=length_function)
    
    raise ValueError(f"Unknown chunker type: {chunk_type}")