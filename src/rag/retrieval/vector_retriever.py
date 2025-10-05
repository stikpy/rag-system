"""
Module de récupération vectorielle avec Supabase
===============================================

Ce module implémente la récupération vectorielle en utilisant Supabase
comme base de données vectorielle.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from supabase import create_client, Client
import logging
from ..utils.config import config
from ..embeddings import EmbeddingProvider

logger = logging.getLogger(__name__)


class VectorRetriever:
    """Récupérateur vectoriel utilisant Supabase"""
    
    def __init__(
        self, 
        supabase_url: str = None,
        supabase_key: str = None,
        supabase_publishable_key: str = None,
        supabase_secret_key: str = None,
        embedding_provider: EmbeddingProvider = None,
        table_name: str = "documents"
    ):
        """
        Initialise le récupérateur vectoriel
        
        Args:
            supabase_url: URL Supabase (optionnel)
            supabase_key: Clé Supabase (ancien format, optionnel)
            supabase_publishable_key: Clé publique Supabase (nouveau format, optionnel)
            supabase_secret_key: Clé secrète Supabase (nouveau format, optionnel)
            embedding_provider: Fournisseur d'embeddings (optionnel)
            table_name: Nom de la table Supabase
        """
        self.supabase_url = supabase_url or config.supabase_url
        self.embedding_provider = embedding_provider
        self.table_name = table_name
        
        # Initialiser le client Supabase (Nouveau format avec fallback)
        if supabase_publishable_key and supabase_secret_key:
            # Nouveau format
            self.supabase: Client = create_client(
                self.supabase_url,
                supabase_publishable_key,
                supabase_secret_key
            )
        elif supabase_key:
            # Ancien format (compatibilité)
            self.supabase: Client = create_client(self.supabase_url, supabase_key)
        elif config.supabase_publishable_key and config.supabase_secret_key:
            # Nouveau format depuis la config
            self.supabase: Client = create_client(
                self.supabase_url,
                config.supabase_publishable_key,
                config.supabase_secret_key
            )
        elif config.supabase_key:
            # Ancien format depuis la config
            self.supabase: Client = create_client(self.supabase_url, config.supabase_key)
        else:
            raise ValueError("Configuration Supabase manquante. Configurez SUPABASE_PUBLISHABLE_KEY et SUPABASE_SECRET_KEY ou SUPABASE_KEY")
        
        # Vérifier la connexion
        self._verify_connection()
    
    def _verify_connection(self):
        """Vérifie la connexion à Supabase"""
        try:
            # Test simple de connexion
            result = self.supabase.table(self.table_name).select("id").limit(1).execute()
            logger.info("Connexion à Supabase établie avec succès")
        except Exception as e:
            logger.error(f"Erreur de connexion à Supabase: {str(e)}")
            raise
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        batch_size: int = 100
    ) -> List[str]:
        """
        Ajoute des documents à la base vectorielle
        
        Args:
            documents: Liste des documents avec embeddings
            batch_size: Taille des batches pour l'insertion
            
        Returns:
            Liste des IDs des documents ajoutés
        """
        document_ids = []
        
        # Traiter par batches
        for i in range(0, len(documents), batch_size):
            batch = documents[i:i + batch_size]
            
            try:
                # Préparer les données pour l'insertion
                insert_data = []
                for doc in batch:
                    # Générer l'embedding si pas déjà présent
                    if 'embedding' not in doc and self.embedding_provider:
                        doc['embedding'] = self.embedding_provider.embed_text(doc['content'])
                    
                    insert_data.append({
                        'content': doc['content'],
                        'embedding': doc['embedding'],
                        'metadata': doc.get('metadata', {}),
                        'source': doc.get('source', 'unknown'),
                        'chunk_id': doc.get('chunk_id', 0),
                        'document_id': doc.get('document_id', ''),
                        'created_at': doc.get('created_at')
                    })
                
                # Insérer dans Supabase
                result = self.supabase.table(self.table_name).insert(insert_data).execute()
                
                # Collecter les IDs
                for row in result.data:
                    document_ids.append(row['id'])
                
                logger.info(f"Batch {i//batch_size + 1} inséré: {len(batch)} documents")
                
            except Exception as e:
                logger.error(f"Erreur lors de l'insertion du batch {i//batch_size + 1}: {str(e)}")
                raise
        
        return document_ids
    
    def search_similar(
        self, 
        query: str, 
        top_k: int = None,
        similarity_threshold: float = None,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Recherche des documents similaires
        
        Args:
            query: Requête de recherche
            top_k: Nombre de résultats à retourner
            similarity_threshold: Seuil de similarité
            filters: Filtres additionnels
            
        Returns:
            Liste des documents similaires
        """
        top_k = top_k or config.max_retrieved_chunks
        similarity_threshold = similarity_threshold or config.similarity_threshold
        
        try:
            # Générer l'embedding de la requête
            if self.embedding_provider:
                query_embedding = self.embedding_provider.embed_text(query)
            else:
                raise ValueError("Aucun fournisseur d'embeddings configuré")
            
            # Construire la requête Supabase
            query_builder = self.supabase.table(self.table_name)
            
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
                "id, content, metadata, source, chunk_id, document_id, created_at"
            ).execute()
            
            # Calculer les similarités (simulation - en production, utiliser pgvector)
            documents = result.data
            similarities = []
            
            for doc in documents:
                if 'embedding' in doc:
                    # Calculer la similarité cosinus
                    similarity = self._cosine_similarity(
                        query_embedding, 
                        doc['embedding']
                    )
                    
                    if similarity >= similarity_threshold:
                        doc['similarity_score'] = similarity
                        similarities.append(doc)
            
            # Trier par similarité
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            # Retourner les top_k résultats
            return similarities[:top_k]
            
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            raise
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calcule la similarité cosinus entre deux vecteurs"""
        try:
            vec1_np = np.array(vec1)
            vec2_np = np.array(vec2)
            
            dot_product = np.dot(vec1_np, vec2_np)
            norm1 = np.linalg.norm(vec1_np)
            norm2 = np.linalg.norm(vec2_np)
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return dot_product / (norm1 * norm2)
        except Exception as e:
            logger.error(f"Erreur lors du calcul de similarité: {str(e)}")
            return 0.0
    
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
            return True
        except Exception as e:
            logger.error(f"Erreur lors du vidage de la base: {str(e)}")
            return False
