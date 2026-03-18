from .fixed_chunker import FixedSizeChunker
from .semantic_chunker import SemanticChunker
from .hybrid_chunker import HybridChunker
from enums.chunk_type import ChunkType

def build_chunker(config, embedder):

    chunk_type = config["type"]

    if chunk_type == ChunkType.FIXED.value:
        return FixedSizeChunker(
            tokenizer=config["tokenizer"],
            chunk_size=config["chunk_size"],
            chunk_overlap=config["overlap"])
    if chunk_type == ChunkType.SEMANTIC.value:
        return  SemanticChunker(tokenizer=config["tokenizer"],
                                embedder=embedder,
                                chunk_size=config["chunk_size"],
                                chunk_overlap=config["overlap"])
    if chunk_type == ChunkType.HYBRID.value:
        return HybridChunker(embedder=embedder,
                            tokenizer=config["tokenizer"],
                            chunk_size=config["chunk_size"],
                            chunk_overlap=config["overlap"])
    
    raise ValueError(f"Unknown chunker type: {chunk_type}")