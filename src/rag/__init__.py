"""
Module RAG principal
===================

Ce module contient les composants principaux du système RAG :
- core : Logique principale du RAG
- embeddings : Génération d'embeddings avec Mistral et OpenAI
- retrieval : Système de récupération avec Supabase
- utils : Utilitaires et helpers
"""

from .core import RAGSystem
from .embeddings import EmbeddingProvider
from .retrieval import VectorRetriever

__all__ = ["RAGSystem", "EmbeddingProvider", "VectorRetriever"]
