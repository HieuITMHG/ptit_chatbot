from .base_chunker import BaseChunker
import re
from .fixed_chunker import FixedSizeChunker
from sklearn.metrics.pairwise import paired_cosine_distances

class SemanticChunker(BaseChunker):
    def __init__(self, 
                 embedder:any, 
                 tokenizer: str, 
                 chunk_size = 500, 
                 chunk_overlap = 50, 
                 threshold = 0.5,
                 drop = 0.12,
                 min_chunk_size = 100):
        super().__init__(chunk_size, chunk_overlap)
        self.threshold = threshold
        self.embedder = embedder
        self.drop = drop
        self.fixed_chunk_split = FixedSizeChunker(tokenizer=tokenizer,
                                                  chunk_size=self.chunk_size,
                                                  chunk_overlap=self.chunk_overlap)
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
        
    def split_text(self, text, title):

        title = f"title: {title}"
        title_tokens = self.length_function(title)[1]

        max_content_tokens = self.chunk_size - title_tokens
        if max_content_tokens <= 0:
            raise ValueError("Title too long for chunk size")

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

            # sentence quá dài
            if sen_len >= max_content_tokens:

                if chunk_sentences:
                    chunk_text = title + "\n" + " ".join(chunk_sentences)
                    token_count = self.length_function(chunk_text)[1]

                    chunks.append({
                        "text": chunk_text,
                        "token_count": token_count
                    })

                    chunk_sentences = []
                    current_chunk_length = 0

                sub_chunks = self.fixed_chunk_split.split_text(sentence)

                for sc in sub_chunks:

                    sc_text = title + "\n" + sc
                    sc_token_count = self.length_function(sc_text)[1]

                    if sc_token_count > self.chunk_size:
                        sc = sc[:max_content_tokens]

                    chunks.append({
                        "text": sc_text,
                        "token_count": sc_token_count
                    })

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

            should_split = (cdrop > self.drop or cscore < self.threshold)

            if should_split:

                chunk_text = title + "\n" + " ".join(chunk_sentences)
                token_count = self.length_function(chunk_text)[1]

                chunks.append({
                    "text": chunk_text,
                    "token_count": token_count
                })

                chunk_sentences = [sentence]
                current_chunk_length = sen_len

            else:

                if current_chunk_length + sen_len > max_content_tokens:

                    chunk_text = title + "\n" + " ".join(chunk_sentences)
                    token_count = self.length_function(chunk_text)[1]

                    chunks.append({
                        "text": chunk_text,
                        "token_count": token_count
                    })

                    chunk_sentences = [sentence]
                    current_chunk_length = sen_len

                else:
                    chunk_sentences.append(sentence)
                    current_chunk_length += sen_len

            last_score = cscore

        if chunk_sentences:

            chunk_text = title + "\n" + " ".join(chunk_sentences)
            token_count = self.length_function(chunk_text)[1]

            chunks.append({
                "text": chunk_text,
                "token_count": token_count
            })

        chunks = self.merge_small_chunks(chunks)

        return chunks