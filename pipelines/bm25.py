from core.database import db
import re, string
from pyvi.ViTokenizer import tokenize
import math
import pickle

enrich_hybrids_collection = db["enrich_hybrids"]

with open("pipelines/vietnamese-stopwords.txt", "r", encoding="utf-8") as f:
    list_stopwords = {line.strip() for line in f if line.strip()}

BM25_INDEX_PATH = "pipelines/bm25_index.pkl"

def clean_text(text):
    text = re.sub('<.*?>', '', text).strip()
    text = re.sub(r'(\s)+', r'\1', text)
    return text

def normalize_text(text):
    listpunctuation = string.punctuation.replace('_', '')
    for i in listpunctuation:
        text = text.replace(i, ' ')
    return text.lower()

def remove_stopword(text):
    words = text.split()
    filtered = [word for word in words if word not in list_stopwords]
    return " ".join(filtered)


def word_segment(sent):
    sent = tokenize(sent.encode('utf-8').decode('utf-8'))
    return sent


def preprocess(text):
    text = clean_text(text)
    text = normalize_text(text)
    text = word_segment(text)
    text = remove_stopword(text)
    return text


def get_docs():
    docs = []
    raw_docs = []

    doc_lst = list(enrich_hybrids_collection.find({}, {"_id": 0}))

    for doc in doc_lst:
        if len(doc["chunk_content"]) < 500:
            continue

        content = preprocess(doc["chunk_content"])

        docs.append(content)
        raw_docs.append(doc)

    return docs, raw_docs


class BM25:

    def __init__(self, k1=1.5, b=0.75):
        self.b = b
        self.k1 = k1

    def fit(self, corpus):

        tf = []
        df = {}
        idf = {}
        doc_len = []
        corpus_size = 0

        for document in corpus:
            corpus_size += 1
            doc_len.append(len(document))

            frequencies = {}
            for term in document:
                frequencies[term] = frequencies.get(term, 0) + 1

            tf.append(frequencies)

            for term in frequencies:
                df[term] = df.get(term, 0) + 1

        for term, freq in df.items():
            idf[term] = math.log(1 + (corpus_size - freq + 0.5) / (freq + 0.5))

        self.tf_ = tf
        self.df_ = df
        self.idf_ = idf
        self.doc_len_ = doc_len
        self.corpus_ = corpus
        self.corpus_size_ = corpus_size
        self.avg_doc_len_ = sum(doc_len) / corpus_size

        return self

    def search(self, query_tokens):

        scores = [self._score(query_tokens, idx) for idx in range(self.corpus_size_)]
        return scores

    def _score(self, query, index):

        score = 0.0
        doc_len = self.doc_len_[index]
        frequencies = self.tf_[index]

        for term in query:

            if term not in frequencies:
                continue

            freq = frequencies[term]

            numerator = self.idf_[term] * freq * (self.k1 + 1)

            denominator = freq + self.k1 * (
                1 - self.b + self.b * doc_len / self.avg_doc_len_
            )

            score += numerator / denominator

        return score


if __name__ == "__main__":

    print("Building BM25 index...")

    docs, raw_docs = get_docs()

    texts = [
        [word for word in document.split()]
        for document in docs
    ]

    bm25 = BM25()
    bm25.fit(texts)

    with open(BM25_INDEX_PATH, "wb") as f:
        pickle.dump(
        {
            "bm25": bm25,
            "docs": docs,
            "texts": texts,
            "raw_docs": raw_docs
        },
        f
        )

    print("BM25 index saved!")