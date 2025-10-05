"""Embedding providers for the RAG system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Sequence

from mistralai import Mistral
from openai import OpenAI

from ..utils.config import config


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers."""

    def __init__(self, model: str | None = None) -> None:
        self.model = model

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Generate an embedding for a single text snippet."""

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        """Generate embeddings for a sequence of texts."""

        return [self.embed_text(text) for text in texts]


class MistralEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by Mistral's embedding API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        super().__init__(model or config.mistral_embedding_model)
        self.api_key = api_key or config.mistral_api_key
        self.client = Mistral(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        embedding = response.data[0].embedding
        return list(embedding)

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [list(item.embedding) for item in response.data]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider backed by OpenAI's embedding API."""

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        super().__init__(model or config.openai_embedding_model)
        self.api_key = api_key or config.openai_api_key
        self.client = OpenAI(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        embedding = response.data[0].embedding
        return list(embedding)

    def embed_documents(self, texts: Sequence[str]) -> List[List[float]]:
        response = self.client.embeddings.create(model=self.model, input=list(texts))
        return [list(item.embedding) for item in response.data]


__all__ = [
    "EmbeddingProvider",
    "MistralEmbeddingProvider",
    "OpenAIEmbeddingProvider",
]
