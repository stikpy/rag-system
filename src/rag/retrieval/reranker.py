"""
Module de reranking avec Cohere
===============================

Ce module implémente le reranking des résultats de récupération
en utilisant l'API Cohere pour améliorer la pertinence des documents.
"""

import cohere
from typing import List, Dict, Any, Tuple
import logging
from ..utils.config import config

logger = logging.getLogger(__name__)


class CohereReranker:
    """Reranker utilisant l'API Cohere pour améliorer la pertinence des résultats"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialise le reranker Cohere
        
        Args:
            api_key: Clé API Cohere (optionnel, utilise la config par défaut)
            model: Modèle de reranking (optionnel, utilise la config par défaut)
        """
        self.api_key = api_key or config.cohere_api_key
        self.model = model or config.cohere_rerank_model
        self.client = cohere.Client(self.api_key)
        
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank les documents par rapport à la requête
        
        Args:
            query: Requête de l'utilisateur
            documents: Liste des documents à reranker
            top_k: Nombre de documents à retourner (optionnel)
            
        Returns:
            Liste des documents rerankés avec scores
        """
        if not documents:
            return []
            
        top_k = top_k or config.rerank_top_k
        
        try:
            # Appel à l'API Cohere pour le reranking
            response = self.client.rerank(
                model=self.model,
                query=query,
                documents=documents,
                top_k=min(top_k, len(documents))
            )
            
            # Formatage des résultats
            reranked_results = []
            for result in response.results:
                reranked_results.append({
                    'document': documents[result.index],
                    'score': result.relevance_score,
                    'index': result.index,
                    'original_rank': result.index
                })
            
            logger.info(f"Reranking terminé: {len(reranked_results)} documents rerankés")
            return reranked_results
            
        except Exception as e:
            logger.error(f"Erreur lors du reranking: {str(e)}")
            # En cas d'erreur, retourner les documents dans l'ordre original
            return [
                {
                    'document': doc,
                    'score': 0.5,  # Score par défaut
                    'index': i,
                    'original_rank': i
                }
                for i, doc in enumerate(documents[:top_k])
            ]
    
    def rerank_with_metadata(
        self, 
        query: str, 
        documents_with_metadata: List[Dict[str, Any]], 
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        Rerank les documents avec métadonnées
        
        Args:
            query: Requête de l'utilisateur
            documents_with_metadata: Liste des documents avec métadonnées
            top_k: Nombre de documents à retourner
            
        Returns:
            Liste des documents rerankés avec métadonnées et scores
        """
        if not documents_with_metadata:
            return []
            
        # Extraire les textes des documents
        documents = [doc.get('content', doc.get('text', '')) for doc in documents_with_metadata]
        
        # Reranker
        reranked_results = self.rerank(query, documents, top_k)
        
        # Réassocier les métadonnées
        final_results = []
        for result in reranked_results:
            original_doc = documents_with_metadata[result['original_rank']]
            final_result = {
                **original_doc,
                'rerank_score': result['score'],
                'rerank_rank': result['index']
            }
            final_results.append(final_result)
            
        return final_results
    
    def batch_rerank(
        self, 
        queries: List[str], 
        documents_batches: List[List[str]], 
        top_k: int = None
    ) -> List[List[Dict[str, Any]]]:
        """
        Rerank en batch pour plusieurs requêtes
        
        Args:
            queries: Liste des requêtes
            documents_batches: Liste des batches de documents
            top_k: Nombre de documents par requête
            
        Returns:
            Liste des résultats rerankés pour chaque requête
        """
        results = []
        for query, documents in zip(queries, documents_batches):
            reranked = self.rerank(query, documents, top_k)
            results.append(reranked)
            
        return results


class HybridReranker:
    """Reranker hybride combinant scores vectoriels et de reranking"""
    
    def __init__(self, cohere_reranker: CohereReranker = None):
        """
        Initialise le reranker hybride
        
        Args:
            cohere_reranker: Instance du reranker Cohere
        """
        self.cohere_reranker = cohere_reranker or CohereReranker()
        
    def hybrid_rerank(
        self, 
        query: str, 
        documents_with_scores: List[Dict[str, Any]], 
        alpha: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Reranking hybride combinant scores vectoriels et de reranking
        
        Args:
            query: Requête de l'utilisateur
            documents_with_scores: Documents avec scores vectoriels
            alpha: Poids du score de reranking (0-1)
            
        Returns:
            Documents avec scores hybrides
        """
        if not documents_with_scores:
            return []
            
        # Extraire les documents pour le reranking
        documents = [doc.get('content', doc.get('text', '')) for doc in documents_with_scores]
        
        # Reranker avec Cohere
        reranked_results = self.cohere_reranker.rerank(query, documents)
        
        # Créer un mapping des scores de reranking
        rerank_scores = {result['original_rank']: result['score'] for result in reranked_results}
        
        # Calculer les scores hybrides
        hybrid_results = []
        for i, doc in enumerate(documents_with_scores):
            vector_score = doc.get('score', 0.0)
            rerank_score = rerank_scores.get(i, 0.0)
            
            # Score hybride : combinaison pondérée
            hybrid_score = (1 - alpha) * vector_score + alpha * rerank_score
            
            hybrid_doc = {
                **doc,
                'vector_score': vector_score,
                'rerank_score': rerank_score,
                'hybrid_score': hybrid_score
            }
            hybrid_results.append(hybrid_doc)
        
        # Trier par score hybride
        hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        return hybrid_results
