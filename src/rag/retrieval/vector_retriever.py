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
    
    def retrieve(self, query: str, max_results: int = None) -> List[Dict[str, Any]]:
        """
        Récupère les documents les plus pertinents pour une requête.
        
        Args:
            query: La requête de recherche
            max_results: Nombre maximum de résultats à retourner
            
        Returns:
            Liste des documents récupérés avec leurs scores
        """
        try:
            # Générer l'embedding de la requête
            query_embedding = self._get_embedding(query)
            
            # Recherche dans la base de données
            max_results = max_results or config.max_retrieved_chunks
            
<<<<<<< HEAD
            # Utiliser la fonction de recherche vectorielle de Supabase
            response = self.supabase.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': config.similarity_threshold,
                    'match_count': max_results
                }
=======
            # Appliquer les filtres si présents
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query_builder = query_builder.in_(key, value)
                    else:
                        query_builder = query_builder.eq(key, value)
            
            # Utiliser la fonction de similarité vectorielle de Supabase
            # Note: Cette fonction nécessite l'extension pgvector
            result = query_builder.select(
                "id, content, embedding, metadata, source, chunk_id, document_id, created_at"
>>>>>>> origin/codex/review-code-for-complete-rag
            ).execute()
            
            documents = []
            for row in response.data:
                documents.append({
                    'content': row.get('content', ''),
                    'metadata': row.get('metadata', {}),
                    'similarity_score': row.get('similarity', 0.0)
                })
            
<<<<<<< HEAD
            logger.info(f"Récupéré {len(documents)} documents pour la requête")
            return documents
=======
            for doc in documents:
                embedding = self._normalize_embedding(doc.get('embedding'))
                if embedding is None:
                    continue

                # Calculer la similarité cosinus
                similarity = self._cosine_similarity(
                    query_embedding,
                    embedding
                )

                if similarity >= similarity_threshold:
                    doc['similarity_score'] = similarity
                    similarities.append(doc)
            
            # Trier par similarité
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Retourner les top_k résultats
            return similarities[:top_k]
>>>>>>> origin/codex/review-code-for-complete-rag
            
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
            
<<<<<<< HEAD
            # Insérer dans la base de données
            self.supabase.table('documents').insert({
                'content': content,
                'metadata': metadata or {},
                'embedding': embedding
            }).execute()
            
            logger.info("Document ajouté à la base vectorielle")
=======
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            return 0.0

    def _normalize_embedding(self, raw_embedding: Any) -> Optional[List[float]]:
        """Convertit une représentation d'embedding en liste de flottants."""

        if raw_embedding is None:
            return None

        if isinstance(raw_embedding, dict):
            if 'data' in raw_embedding and isinstance(raw_embedding['data'], list):
                raw_embedding = raw_embedding['data']
            else:
                logger.warning("Embedding Supabase au format inattendu (dict)")
                return None

        if isinstance(raw_embedding, str):
            try:
                raw_embedding = json.loads(raw_embedding)
            except json.JSONDecodeError:
                logger.warning("Impossible de décoder l'embedding Supabase en JSON")
                return None

        try:
            return [float(value) for value in raw_embedding]
        except (TypeError, ValueError):
            logger.warning("Embedding Supabase au format inattendu (non convertible en float)")
            return None
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """Récupère un document par son ID"""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("id", document_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Erreur lors de la récupération du document {document_id}: {str(e)}")
            return None
    
    def delete_document(self, document_id: str) -> bool:
        """Supprime un document par son ID"""
        try:
            result = self.supabase.table(self.table_name).delete().eq("id", document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Erreur lors de la suppression du document {document_id}: {str(e)}")
            return False
    
    def update_document(
        self, 
        document_id: str, 
        updates: Dict[str, Any]
    ) -> bool:
        """Met à jour un document"""
        try:
            result = self.supabase.table(self.table_name).update(updates).eq("id", document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du document {document_id}: {str(e)}")
            return False
    
    def get_documents_by_source(self, source: str) -> List[Dict[str, Any]]:
        """Récupère tous les documents d'une source"""
        try:
            result = self.supabase.table(self.table_name).select("*").eq("source", source).execute()
            return result.data
        except Exception as e:
            logger.error(f"Erreur lors de la récupération des documents de la source {source}: {str(e)}")
            return []
    
    def get_document_count(self) -> int:
        """Retourne le nombre total de documents"""
        try:
            result = self.supabase.table(self.table_name).select("id", count="exact").execute()
            return result.count
        except Exception as e:
            logger.error(f"Erreur lors du comptage des documents: {str(e)}")
            return 0
    
    def clear_database(self) -> bool:
        """Vide la base de données (ATTENTION: supprime tout)"""
        try:
            result = self.supabase.table(self.table_name).delete().neq("id", "").execute()
            logger.warning("Base de données vidée")
>>>>>>> origin/codex/review-code-for-complete-rag
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