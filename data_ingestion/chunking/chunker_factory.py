from .fixed_chunker import FixedSizeChunker
from enums.chunk_type import ChunkType
from .helpers import length_function, encoding

def build_chunker(config):

    chunk_type = config["type"]

    if chunk_type == ChunkType.FIXED.value:
        return FixedSizeChunker(
            encoding=encoding,
            chunk_size=config["chunk_size"],
            chunk_overlap=config["overlap"],
            length_function=length_function
        )
    
    raise ValueError(f"Unknown chunker type: {chunk_type}")