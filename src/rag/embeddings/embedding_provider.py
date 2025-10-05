"""
Module de génération d'embeddings
=================================

Ce module implémente la génération d'embeddings avec :
- Mistral AI
- OpenAI
- Support pour différents modèles
"""

import numpy as np
from typing import List, Dict, Any, Optional, Union
from abc import ABC, abstractmethod
import logging
from mistralai import Mistral
from openai import OpenAI
from ..utils.config import config

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Classe abstraite pour les fournisseurs d'embeddings"""
    
    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """Génère un embedding pour un texte"""
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings pour plusieurs textes"""
        pass


class MistralEmbeddingProvider(EmbeddingProvider):
    """Fournisseur d'embeddings Mistral AI"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialise le fournisseur Mistral
        
        Args:
            api_key: Clé API Mistral (optionnel)
            model: Modèle d'embedding (optionnel)
        """
        self.api_key = api_key or config.mistral_api_key
        self.model = model or config.mistral_embedding_model
        self.client = Mistral(api_key=self.api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """Génère un embedding pour un texte avec Mistral"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding Mistral: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings pour plusieurs textes avec Mistral"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings Mistral: {str(e)}")
            raise


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Fournisseur d'embeddings OpenAI"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialise le fournisseur OpenAI
        
        Args:
            api_key: Clé API OpenAI (optionnel)
            model: Modèle d'embedding (optionnel)
        """
        self.api_key = api_key or config.openai_api_key
        self.model = model or config.openai_embedding_model
        self.client = OpenAI(api_key=self.api_key)
    
    def embed_text(self, text: str) -> List[float]:
        """Génère un embedding pour un texte avec OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding OpenAI: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings pour plusieurs textes avec OpenAI"""
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [data.embedding for data in response.data]
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embeddings OpenAI: {str(e)}")
            raise


class HybridEmbeddingProvider(EmbeddingProvider):
    """Fournisseur d'embeddings hybride combinant Mistral et OpenAI"""
    
    def __init__(
        self, 
        mistral_provider: MistralEmbeddingProvider = None,
        openai_provider: OpenAIEmbeddingProvider = None,
        primary_provider: str = "mistral"
    ):
        """
        Initialise le fournisseur hybride
        
        Args:
            mistral_provider: Fournisseur Mistral
            openai_provider: Fournisseur OpenAI
            primary_provider: Fournisseur principal ("mistral" ou "openai")
        """
        self.mistral_provider = mistral_provider or MistralEmbeddingProvider()
        self.openai_provider = openai_provider or OpenAIEmbeddingProvider()
        self.primary_provider = primary_provider
    
    def embed_text(self, text: str) -> List[float]:
        """Génère un embedding avec le fournisseur principal"""
        if self.primary_provider == "mistral":
            return self.mistral_provider.embed_text(text)
        else:
            return self.openai_provider.embed_text(text)
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings avec le fournisseur principal"""
        if self.primary_provider == "mistral":
            return self.mistral_provider.embed_texts(texts)
        else:
            return self.openai_provider.embed_texts(texts)
    
    def embed_texts_hybrid(self, texts: List[str]) -> Dict[str, List[List[float]]]:
        """Génère des embeddings avec les deux fournisseurs"""
        mistral_embeddings = self.mistral_provider.embed_texts(texts)
        openai_embeddings = self.openai_provider.embed_texts(texts)
        
        return {
            'mistral': mistral_embeddings,
            'openai': openai_embeddings
        }


class EmbeddingManager:
    """Gestionnaire d'embeddings avec cache et optimisation"""
    
    def __init__(self, provider: EmbeddingProvider = None):
        """
        Initialise le gestionnaire d'embeddings
        
        Args:
            provider: Fournisseur d'embeddings (optionnel)
        """
        self.provider = provider or MistralEmbeddingProvider()
        self.cache = {}  # Cache simple pour les embeddings
    
    def get_embedding(self, text: str, use_cache: bool = True) -> List[float]:
        """
        Obtient un embedding pour un texte
        
        Args:
            text: Texte à embedder
            use_cache: Utiliser le cache (optionnel)
            
        Returns:
            Embedding du texte
        """
        if use_cache and text in self.cache:
            return self.cache[text]
        
        embedding = self.provider.embed_text(text)
        
        if use_cache:
            self.cache[text] = embedding
        
        return embedding
    
    def get_embeddings(self, texts: List[str], use_cache: bool = True) -> List[List[float]]:
        """
        Obtient des embeddings pour plusieurs textes
        
        Args:
            texts: Liste des textes à embedder
            use_cache: Utiliser le cache (optionnel)
            
        Returns:
            Liste des embeddings
        """
        if not use_cache:
            return self.provider.embed_texts(texts)
        
        embeddings = []
        texts_to_embed = []
        indices_to_embed = []
        
        # Vérifier le cache
        for i, text in enumerate(texts):
            if text in self.cache:
                embeddings.append(self.cache[text])
            else:
                texts_to_embed.append(text)
                indices_to_embed.append(i)
                embeddings.append(None)  # Placeholder
        
        # Générer les embeddings manquants
        if texts_to_embed:
            new_embeddings = self.provider.embed_texts(texts_to_embed)
            
            # Mettre à jour le cache et les résultats
            for i, embedding in enumerate(new_embeddings):
                text = texts_to_embed[i]
                original_index = indices_to_embed[i]
                self.cache[text] = embedding
                embeddings[original_index] = embedding
        
        return embeddings
    
    def clear_cache(self):
        """Vide le cache des embeddings"""
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """Retourne la taille du cache"""
        return len(self.cache)


def create_embedding_provider(provider_type: str = "mistral", **kwargs) -> EmbeddingProvider:
    """
    Factory pour créer des fournisseurs d'embeddings
    
    Args:
        provider_type: Type de fournisseur ("mistral", "openai", "hybrid")
        **kwargs: Arguments additionnels
        
    Returns:
        Fournisseur d'embeddings
    """
    if provider_type == "mistral":
        return MistralEmbeddingProvider(**kwargs)
    elif provider_type == "openai":
        return OpenAIEmbeddingProvider(**kwargs)
    elif provider_type == "hybrid":
        return HybridEmbeddingProvider(**kwargs)
    else:
        raise ValueError(f"Type de fournisseur non supporté: {provider_type}")
