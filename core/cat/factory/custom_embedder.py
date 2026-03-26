import re
import os
import string
import json
from typing import List
from itertools import combinations
from sklearn.feature_extraction.text import CountVectorizer
from langchain_core.embeddings import Embeddings
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
        voc = []
        for k in combinations(chars, 2):
            voc.append(f"{k[0]}{k[1]}")
        voc = sorted(set(voc))

        # Naive embedder that counts occurrences of couple of characters in text
        self.embedder = CountVectorizer(
            vocabulary=voc, analyzer=lambda s: re.findall("..", s), binary=True
        )

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of text and returns the embedding vectors that are lists of floats."""
        return self.embedder.transform(texts).astype(float).todense().tolist()

    def embed_query(self, text: str) -> List[float]:
        """Embed a string of text and returns the embedding vector as a list of floats."""
        return self.embed_documents([text])[0]


class CustomOpenAIEmbeddings(Embeddings):
    """Use LLAMA2 as embedder by calling a self-hosted lama-cpp-python instance."""

    def __init__(self, url):
        self.url = os.path.join(url, "v1/embeddings")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = json.dumps({"input": texts})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return [e["embedding"] for e in ret.json()["data"]]

    def embed_query(self, text: str) -> List[float]:
        payload = json.dumps({"input": text})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()["data"][0]["embedding"]


class MiniMaxEmbeddings(Embeddings):
    """MiniMax Embeddings using the embo-01 model.

    Calls MiniMax's native embedding API at https://api.minimax.io/v1/embeddings.
    Supports both 'db' (for indexing) and 'query' (for search) embedding types.
    """

    def __init__(self, minimax_api_key: str, model: str = "embo-01", embed_type: str = "db"):
        self.api_key = minimax_api_key
        self.model = model
        self.embed_type = embed_type
        self.url = "https://api.minimax.io/v1/embeddings"

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = json.dumps({
            "model": self.model,
            "texts": texts,
            "type": "db",
        })
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        ret = httpx.post(self.url, data=payload, headers=headers, timeout=None)
        ret.raise_for_status()
        data = ret.json()
        if data.get("vectors") is None:
            raise ValueError(f"MiniMax embedding API error: {data.get('base_resp', {}).get('status_msg', 'unknown error')}")
        return data["vectors"]

    def embed_query(self, text: str) -> List[float]:
        payload = json.dumps({
            "model": self.model,
            "texts": [text],
            "type": "query",
        })
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        ret = httpx.post(self.url, data=payload, headers=headers, timeout=None)
        ret.raise_for_status()
        data = ret.json()
        if data.get("vectors") is None:
            raise ValueError(f"MiniMax embedding API error: {data.get('base_resp', {}).get('status_msg', 'unknown error')}")
        return data["vectors"][0]


class CustomOllamaEmbeddings(Embeddings):
    """Use Ollama to serve embedding models."""

    def __init__(self, base_url, model):
        self.url = os.path.join(base_url, "api/embed")
        self.model = model

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = json.dumps({"model": self.model , "input": texts})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()["embeddings"]

    def embed_query(self, text: str) -> List[float]:
        payload = json.dumps({"model": self.model , "input": text})
        ret = httpx.post(self.url, data=payload, timeout=None)
        ret.raise_for_status()
        return ret.json()["embeddings"][0]
