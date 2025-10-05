"""
Module Langchain pour le système RAG
====================================

Ce module contient les intégrations Langchain :
- RAGChain : Chaînes RAG avec Langchain
- RAGAgent : Agents conversationnels
- DocumentProcessingChain : Traitement de documents
- RAGWithReranking : RAG avec reranking Cohere
"""

from .rag_chain import (
    RAGChain,
    RAGAgent, 
    DocumentProcessingChain,
    RAGWithReranking
)

__all__ = [
    "RAGChain",
    "RAGAgent",
    "DocumentProcessingChain", 
    "RAGWithReranking"
]
