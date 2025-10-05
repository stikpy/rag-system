"""
Système RAG principal - Orchestrateur du système de génération augmentée par récupération.
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import asyncio

from ..retrieval.vector_retriever import VectorRetriever
from ..retrieval.reranker import CohereReranker
from ..generation.mistral_generator import MistralGenerator
from ..generation.openai_generator import OpenAIGenerator
from ..utils.config import config
from ..utils.text_processing import TextProcessor

logger = logging.getLogger(__name__)

class RAGSystem:
    """
    Système RAG principal qui orchestre la récupération et la génération.
    """
    
    def __init__(self):
        """Initialise le système RAG."""
        self.retriever = VectorRetriever()
        self.reranker = CohereReranker() if config.enable_reranking else None
        self.mistral_generator = MistralGenerator()
        self.openai_generator = OpenAIGenerator()
        self.text_processor = TextProcessor()
        
        logger.info("Système RAG initialisé avec succès")
    
    def query(self, question: str, max_chunks: int = None) -> str:
        """
        Traite une requête utilisateur et retourne une réponse générée.
        
        Args:
            question: La question de l'utilisateur
            max_chunks: Nombre maximum de chunks à récupérer
            
        Returns:
            La réponse générée par le système RAG
        """
        try:
            logger.info(f"Traitement de la requête: {question}")
            
            # 1. Récupération des documents pertinents
            retrieved_docs = self.retriever.retrieve(question, max_chunks or config.max_retrieved_chunks)
            
            if not retrieved_docs:
                return "Aucun document pertinent trouvé dans la base de données."
            
            # 2. Reranking si activé
            if self.reranker and len(retrieved_docs) > 1:
                retrieved_docs = self.reranker.rerank(question, retrieved_docs)
            
            # 3. Construction du contexte
            context = self._build_context(retrieved_docs)
            
            # 4. Génération de la réponse
            response = self._generate_response(question, context)
            
            logger.info("Requête traitée avec succès")
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement de la requête: {e}")
            return f"Erreur lors du traitement de votre question: {str(e)}"
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """
        Construit le contexte à partir des documents récupérés.
        
        Args:
            documents: Liste des documents récupérés
            
        Returns:
            Le contexte formaté
        """
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')
            metadata = doc.get('metadata', {})
            title = metadata.get('title', f'Document {i}')
            
            context_parts.append(f"Document {i} ({title}):\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _generate_response(self, question: str, context: str) -> str:
        """
        Génère une réponse basée sur la question et le contexte.
        
        Args:
            question: La question de l'utilisateur
            context: Le contexte récupéré
            
        Returns:
            La réponse générée
        """
        # Utiliser Mistral par défaut, avec fallback sur OpenAI
        try:
            return self.mistral_generator.generate(question, context)
        except Exception as e:
            logger.warning(f"Erreur avec Mistral, tentative avec OpenAI: {e}")
            try:
                return self.openai_generator.generate(question, context)
            except Exception as e2:
                logger.error(f"Erreur avec OpenAI: {e2}")
                return "Erreur lors de la génération de la réponse. Veuillez réessayer."
    
    def add_document(self, content: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Ajoute un document à la base de connaissances.
        
        Args:
            content: Le contenu du document
            metadata: Métadonnées du document
            
        Returns:
            True si l'ajout a réussi, False sinon
        """
        try:
            # Découper le document en chunks
            chunks = self.text_processor.split_into_chunks(content, metadata or {})
            
            # Ajouter chaque chunk à la base vectorielle
            for chunk in chunks:
                self.retriever.add_document(chunk['content'], chunk['metadata'])
            
            logger.info(f"Document ajouté avec {len(chunks)} chunks")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du document: {e}")
            return False