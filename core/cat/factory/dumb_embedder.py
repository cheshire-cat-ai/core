import string
from typing import List
from itertools import combinations
from sklearn.feature_extraction.text import CountVectorizer
from langchain.embeddings.base import Embeddings


class DumbEmbedder(Embeddings):

    def __init__(self):
        # Get all printable characters numbers excluded and make everything lowercase
        chars = [p.lower() for p in string.printable[10:]]

        # Make the vocabulary with all possible combinations of 2 characters
        voc = {f"{k[0]}{k[1]}": v for v, k in enumerate(combinations(chars, 2))}

        # Re-index the tokens
        for i, k in enumerate(voc.keys()):
            voc[k] = i

        # Naive embedder that counts occurrences of couple of characters in text
        self.embedder = CountVectorizer(vocabulary=voc, analyzer="char_wb", ngram_range=(2, 2))

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        return self.embedder.transform(texts).astype(float).todense().tolist()

    def embed_query(self, text: str) -> List[float]:
        # Embeds the input text
        return self.embedder.transform([text]).astype(float).todense().tolist()[0]
