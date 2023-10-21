import os
import string
import json
from typing import List
from itertools import combinations
from sklearn.feature_extraction.text import CountVectorizer
from langchain.embeddings.base import Embeddings
import httpx


class DumbEmbedder(Embeddings):
    """Default Dumb Embedder.

    This is the default embedder used for testing purposes
    and to replace official embedders when they are not available.

    Notes
    -----
    This class relies on the `CountVectorizer`[1]_ offered by Scikit-learn.
    This embedder uses a naive approach to extract features from a text and build an embedding vector.
    Namely, it looks for pairs of characters in text starting form a vocabulary with all possible pairs of
    printable characters, digits excluded.

    """

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
        """Embed a list of text and returns the embedding vectors that are lists of floats."""
        return self.embedder.transform(texts).astype(float).todense().tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a string of text and returns the embedding vector as a list of floats."""
        return self.embedder.transform([text]).astype(float).todense().tolist()[0]


class CustomOpenAIEmbeddings(Embeddings):
    """Use LLAMA2 as embedder by calling a self-hosted lama-cpp-python instance.
    """
    
    def __init__(self, url):
        self.url = os.path.join(url, "v1/embeddings")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = json.dumps({"input": texts})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return  [e['embedding'] for e in ret.json()['data']]
    
    def embed_query(self, text: str) -> List[float]:
        payload = json.dumps({"input": text})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()['data'][0]['embedding']

class CustomFastembedEmbeddings(Embeddings):
    """Use Fastembed for embedding.
    """
    def __init__(self, url, model,max_length) -> None:
        self.url = url
        output = httpx.post(f"{url}/embeddings", json={"model": model, "max_length": max_length})
        output.raise_for_status()
        
    
    def embed_documents(self, texts: List[str]):
        payload = json.dumps({"document": texts})
        ret = httpx.post(f"{self.url}/embeddings/document", data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()
    
    def embed_query(self, text: str) -> List[float]:
        payload = json.dumps({"prompt": text})
        ret = httpx.post(f"{self.url}/embeddings/prompt", data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()