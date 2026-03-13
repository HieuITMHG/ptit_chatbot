from .base_chunker import BaseChunker
import re
from core.database import db
from .fixed_chunker import FixedSizeChunker
from sklearn.metrics.pairwise import paired_cosine_distances
from sentence_transformers import SentenceTransformer

documents_collection = db["documents"]
semantic_chunk = db["semantic_chunks"]

class SemanticChunker(BaseChunker):
    def __init__(self, 
                 embedder:str, 
                 encoding, 
                 chunk_size = 500, 
                 chunk_overlap = 50, 
                 length_function = ..., 
                 threshold = 0.5,
                 drop = 0.12):
        super().__init__(encoding, chunk_size, chunk_overlap, length_function)
        self.threshold = threshold
        self.embedder = SentenceTransformer(embedder)
        self.drop = drop
        self.fixed_chunk_split = FixedSizeChunker(encoding=self.encoding,
                                                  chunk_size=self.chunk_size,
                                                  chunk_overlap=self.chunk_overlap,
                                                  length_function=length_function)

    def split_into_sentences(self, text: str) -> list[str]:

        abbreviations = [
            "Mr.", "Mrs.", "Ms.", "Dr.", "Prof.",
            "TP.", "Tp.", "ThS.", "TS.", "PGS.", "GS.",
            "VD.", "Th.S.", "v.v.", "GS.TS."
        ]

        placeholder = "<DOT>"

        for abbr in abbreviations:
            text = text.replace(abbr, abbr.replace(".", placeholder))

        sentences = re.split(r'(?<=[.!?])\s+(?=[A-ZÀ-Ỵ])', text)

        sentences = [
            s.replace(placeholder, ".").strip()
            for s in sentences if s.strip()
        ]

        return sentences    
    
    def split_text(self, text):
        sentences = self.split_into_sentences(text)
        if not sentences:
            return []
            
        vectors = self.embedder.encode(sentences)
        
        sen_lengths = [self.length_function(s)[1] for s in sentences]

        if len(sentences) > 1:
            sim_scores = 1.0 - paired_cosine_distances(vectors[:-1], vectors[1:])
        else:
            sim_scores = []

        chunks = []
        chunk_sentences = []
        
        current_chunk_length = 0 
        last_score = 1.0

        for i, sentence in enumerate(sentences):
            sen_len = sen_lengths[i]

            if sen_len >= self.chunk_size:
                if chunk_sentences:
                    chunks.append(" ".join(chunk_sentences))
                    chunk_sentences = []
                    current_chunk_length = 0
                
                sub_chunks = self.fixed_chunk_split(sentence)
                chunks.extend(sub_chunks)
                last_score = 1.0
                continue

            if not chunk_sentences:
                chunk_sentences.append(sentence)
                current_chunk_length = sen_len
                if i < len(sentences) - 1:
                    last_score = sim_scores[i]
                continue
                
            cscore = sim_scores[i - 1]
            cdrop = last_score - cscore
            
            if cdrop > self.drop or cscore < self.threshold:
            
                chunks.append(" ".join(chunk_sentences))
                chunk_sentences = [sentence]
                current_chunk_length = sen_len
            else:
                if current_chunk_length + sen_len + 1 > self.chunk_size:
                    chunks.append(" ".join(chunk_sentences))
                    chunk_sentences = [sentence]
                    current_chunk_length = sen_len
                else:
                    chunk_sentences.append(sentence)
                    current_chunk_length += (sen_len + 1)
            
            last_score = cscore

        if chunk_sentences:
            chunks.append(" ".join(chunk_sentences))

        return chunks

# if __name__ == "__main__":
#     embedder = SentenceTransformer("BAAI/bge-m3")
#     chunker = SemanticChunking(chunk_size=500, 
#                                chunk_overlap=50, 
#                                length_function=length_function, 
#                                encoding=encoding, 
#                                threshold=0.7, 
#                                embedder=embedder)
    

    
    
