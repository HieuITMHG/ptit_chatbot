from .base_chunker import BaseChunker
import re
from core.database import db
from .fixed_chunker import FixedSizeChunker
from sklearn.metrics.pairwise import paired_cosine_distances
from sentence_transformers import SentenceTransformer
from .helpers import length_function, encoding

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
                 drop = 0.12,
                 min_chunk_size = 100):
        super().__init__(encoding, chunk_size, chunk_overlap, length_function)
        self.threshold = threshold
        self.embedder = SentenceTransformer(embedder)
        self.drop = drop
        self.fixed_chunk_split = FixedSizeChunker(encoding=self.encoding,
                                                  chunk_size=self.chunk_size,
                                                  chunk_overlap=self.chunk_overlap,
                                                  length_function=length_function)
        self.min_chunk_size = min_chunk_size

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
    
    def merge_small_chunks(self, chunks):
        if not chunks:
            return chunks
        
        merged = []
        buffer = chunks[0]

        for chunk in chunks[1:]:
            if buffer["token_count"] < self.min_chunk_size:

                text_combined = buffer["text"] + " " + chunk["text"]

                token_count_combined = buffer["token_count"] + chunk["token_count"]
                combined = {"text": text_combined, "token_count": token_count_combined}

                if token_count_combined <= self.chunk_size:
                    buffer = combined
                else:
                    merged.append(buffer)
                    buffer = chunk
            else:
                merged.append(buffer)
                buffer = chunk

        merged.append(buffer)
        return merged
        
    def split_text(self, text):
        sentences = self.split_into_sentences(text)
        if not sentences:
            return []
            
        vectors = self.embedder.encode(sentences)
        
        # Tính độ dài (token count) cho từng câu con
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

            # Xử lý khi một câu dài hơn giới hạn chunk_size
            if sen_len >= self.chunk_size:
                if chunk_sentences:
                    chunk_text = " ".join(chunk_sentences)
                    # Tính chính xác token_count của chunk sau khi nối
                    token_count = self.length_function(chunk_text)[1]
                    chunks.append({
                        "text": chunk_text, 
                        "token_count": token_count
                    })
                    
                    chunk_sentences = []
                    current_chunk_length = 0
                
                sub_chunks = self.fixed_chunk_split.split_text(sentence)
                # Xử lý kèm token_count cho các đoạn bị cắt ép (fixed split)
                for sc in sub_chunks:
                    sc_token_count = self.length_function(sc)[1]
                    chunks.append({
                        "text": sc, 
                        "token_count": sc_token_count
                    })
                
                last_score = 1.0
                continue

            # Bắt đầu một chunk mới
            if not chunk_sentences:
                chunk_sentences.append(sentence)
                current_chunk_length = sen_len
                if i < len(sentences) - 1:
                    last_score = sim_scores[i]
                continue
                
            cscore = sim_scores[i - 1]
            cdrop = last_score - cscore
            
            # Cắt chunk dựa trên điểm ngắt ngữ nghĩa (semantic threshold/drop)
            if cdrop > self.drop or cscore < self.threshold:
                chunk_text = " ".join(chunk_sentences)
                token_count = self.length_function(chunk_text)[1]
                chunks.append({
                    "text": chunk_text, 
                    "token_count": token_count
                })
                
                chunk_sentences = [sentence]
                current_chunk_length = sen_len
            else:
                # Cắt chunk dựa trên giới hạn kích thước (chunk_size)
                if current_chunk_length + sen_len + 1 > self.chunk_size:
                    chunk_text = " ".join(chunk_sentences)
                    token_count = self.length_function(chunk_text)[1]
                    chunks.append({
                        "text": chunk_text, 
                        "token_count": token_count
                    })
                    
                    chunk_sentences = [sentence]
                    current_chunk_length = sen_len
                else:
                    chunk_sentences.append(sentence)
                    current_chunk_length += (sen_len + 1)
            
            last_score = cscore

        # Xử lý chunk cuối cùng còn sót lại sau khi kết thúc vòng lặp
        if chunk_sentences:
            chunk_text = " ".join(chunk_sentences)
            token_count = self.length_function(chunk_text)[1]
            chunks.append({
                "text": chunk_text, 
                "token_count": token_count
            })

        chunks = self.merge_small_chunks(chunks)

        return chunks

# if __name__ == "__main__":
#     embedder = SentenceTransformer("BAAI/bge-m3")
#     doc = documents_collection.find_one({"source_url": "/sinh-vien/hoat-dong-ngoai-khoa/sinh-vien-hoc-vien-cn-bcvt-voi-dot-trai-cua-tap-doan-vnpt.html"})
#     chunker = SemanticChunker(chunk_size=500, 
#                                chunk_overlap=50, 
#                                length_function=length_function, 
#                                encoding=encoding, 
#                                threshold=0.7, 

#                                embedder="BAAI/bge-m3")
#     chunks = chunker.split_text(doc["content"])
#     for chunk in chunks:
#         print(chunk)    

    
    
