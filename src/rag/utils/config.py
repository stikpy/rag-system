"""
Configuration du système RAG
===========================

Gestion centralisée de la configuration pour le système RAG.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()


class RAGConfig(BaseSettings):
    """Configuration du système RAG"""
    
    # API Keys
    mistral_api_key: str = Field(..., env="MISTRAL_API_KEY")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    cohere_api_key: str = Field(..., env="COHERE_API_KEY")
    
    # Supabase Configuration (Nouveau Format)
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_publishable_key: Optional[str] = Field(None, env="SUPABASE_PUBLISHABLE_KEY")
    supabase_secret_key: Optional[str] = Field(None, env="SUPABASE_SECRET_KEY")
    
    # Ancien format (pour compatibilité)
    supabase_key: Optional[str] = Field(None, env="SUPABASE_KEY")
    supabase_service_role_key: Optional[str] = Field(None, env="SUPABASE_SERVICE_ROLE_KEY")
    
    # Database Configuration
    database_url: Optional[str] = Field(None, env="DATABASE_URL")
    direct_url: Optional[str] = Field(None, env="DIRECT_URL")
    
    # Optional: Other vector databases
    pinecone_api_key: Optional[str] = Field(None, env="PINECONE_API_KEY")
    pinecone_environment: Optional[str] = Field(None, env="PINECONE_ENVIRONMENT")
    
    # RAG Parameters
    chunk_size: int = Field(1024, env="CHUNK_SIZE")
    chunk_overlap: int = Field(200, env="CHUNK_OVERLAP")
    max_tokens: int = Field(4096, env="MAX_TOKENS")
    temperature: float = Field(0.7, env="TEMPERATURE")
    
    # Embedding Models
    mistral_embedding_model: str = "mistral-embed"
    openai_embedding_model: str = "text-embedding-3-small"
    
    # Generation Models
    mistral_generation_model: str = "mistral-large-latest"
    openai_generation_model: str = "gpt-4"
    
    # Vector Database Settings
    vector_dimension: int = 1024  # Mistral embeddings dimension
    similarity_threshold: float = 0.7
    max_retrieved_chunks: int = 5
    
    # Reranking Settings
    cohere_rerank_model: str = "rerank-multilingual-v3.0"
    rerank_top_k: int = 3
    enable_reranking: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_config() -> RAGConfig:
    """Obtenir la configuration du système RAG"""
    return RAGConfig()


# Instance globale de configuration
config = get_config()
