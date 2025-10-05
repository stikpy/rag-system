"""
Récupérateur vectoriel utilisant Supabase pour la recherche de similarité.
"""

import json
import logging
from typing import Any, Dict, List, Optional
import numpy as np
from supabase import Client, create_client
from mistralai import Mistral

from ..embeddings import EmbeddingProvider
from ..utils.config import config

logger = logging.getLogger(__name__)

class VectorRetriever:
    """
    Récupérateur vectoriel utilisant Supabase comme base de données vectorielle.
    """
    
    def __init__(self):
        """Initialise le récupérateur vectoriel."""
        self.supabase = self._init_supabase()
        self.mistral = Mistral(api_key=config.mistral_api_key)
        logger.info("VectorRetriever initialisé")
    
    def _init_supabase(self) -> Client:
        """Initialise le client Supabase."""
        try:
            # Utiliser les nouvelles clés API si disponibles
            if config.supabase_publishable_key and config.supabase_secret_key:
                return create_client(config.supabase_url, config.supabase_secret_key)
            elif config.supabase_key:
                return create_client(config.supabase_url, config.supabase_key)
            else:
                raise ValueError("Aucune clé API Supabase configurée")
        except Exception as e:
            logger.error(f"Erreur d'initialisation Supabase: {e}")
            raise
    
    def retrieve(self, query: str, max_results: int = None, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Récupère les documents les plus pertinents pour une requête.
        
        Args:
            query: La requête de recherche
            max_results: Nombre maximum de résultats à retourner
            filters: Filtres optionnels pour la recherche
            
        Returns:
            Liste des documents récupérés avec leurs scores
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self._get_embedding(query)
            
            # Recherche dans la base de données
            max_results = max_results or config.max_retrieved_chunks
            
            # Utiliser la fonction de recherche vectorielle de Supabase
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': config.similarity_threshold,
                    'match_count': max_results
                }
            ).execute()
            
            documents = []
            for row in response.data:
                documents.append({
                    'content': row.get('content', ''),
                    'metadata': row.get('metadata', {}),
                    'similarity_score': row.get('similarity', 0.0)
                })
            
            logger.info(f"Récupéré {len(documents)} documents pour la requête")
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération: {e}")
            # Fallback: recherche textuelle simple
            return self._fallback_search(query, max_results)
    
    def _get_embedding(self, text: str) -> List[float]:
        """
        Génère un embedding pour le texte donné.
        
        Args:
            text: Le texte à encoder
            
        Returns:
            L'embedding vectoriel
        """
        try:
            response = self.mistral.embeddings(
                model="mistral-embed",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Erreur lors de la génération d'embedding: {e}")
            # Retourner un embedding de zéros en cas d'erreur
            return [0.0] * config.vector_dimension
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Ajoute un document à la base vectorielle.
        
        Args:
            content: Le contenu du document
            metadata: Métadonnées du document
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            # Générer l'embedding du contenu
            embedding = self._get_embedding(content)
            
            # Insérer dans la base de données
            self.supabase.table('documents').insert({
                'content': content,
                'metadata': metadata or {},
                'embedding': embedding
            }).execute()
            
            logger.info("Document ajouté à la base vectorielle")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du document: {e}")
            return False
    
    def _fallback_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Recherche de fallback en cas d'erreur avec les embeddings.
        
        Args:
            query: La requête de recherche
            max_results: Nombre maximum de résultats
            
        Returns:
            Liste des documents trouvés
        """
        try:
            # Recherche textuelle simple
            response = self.supabase.table('documents').select('*').ilike('content', f'%{query}%').limit(max_results).execute()
            
            documents = []
            for row in response.data:
                documents.append({
                    'content': row.get('content', ''),
                    'metadata': row.get('metadata', {}),
                    'similarity_score': 0.5  # Score par défaut
                })
            
            logger.info(f"Fallback: récupéré {len(documents)} documents")
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche de fallback: {e}")
            return []
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Récupère un document par son ID.
        
        Args:
            document_id: L'ID du document
            
        Returns:
            Le document ou None si non trouvé
        """
        try:
            response = self.supabase.table('documents').select('*').eq('id', document_id).execute()
            
            if response.data:
                return response.data[0]
            return None
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du document {document_id}: {e}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """
        Supprime un document de la base vectorielle.
        
        Args:
            document_id: L'ID du document à supprimer
            
        Returns:
            True si la suppression a réussi, False sinon
        """
        try:
            self.supabase.table('documents').delete().eq('id', document_id).execute()
            logger.info(f"Document {document_id} supprimé")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document {document_id}: {e}")
            return False