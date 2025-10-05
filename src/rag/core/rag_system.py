"""
Système RAG principal
====================

Ce module implémente le système RAG complet avec :
- Support Mistral et OpenAI
- Récupération vectorielle avec Supabase
- Reranking avec Cohere
- Génération de réponses
"""

import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
from mistralai import Mistral
from openai import OpenAI

from ..embeddings import EmbeddingProvider, MistralEmbeddingProvider, OpenAIEmbeddingProvider
from ..retrieval import VectorRetriever, CohereReranker, HybridReranker
from ..ocr import OCRProcessor, DocumentOCRProcessor
from ..utils import TextProcessor, DocumentSplitter, CharacterSplitter
from ..utils.config import config

logger = logging.getLogger(__name__)


class RAGSystem:
    """Système RAG principal intégrant tous les composants"""
    
    def __init__(
        self,
        embedding_provider: EmbeddingProvider = None,
        vector_retriever: VectorRetriever = None,
        reranker: CohereReranker = None,
        text_processor: TextProcessor = None,
        ocr_processor: OCRProcessor = None,
        generation_provider: str = "mistral"
    ):
        """
        Initialise le système RAG
        
        Args:
            embedding_provider: Fournisseur d'embeddings
            vector_retriever: Récupérateur vectoriel
            reranker: Reranker pour améliorer les résultats
            text_processor: Processeur de texte
            ocr_processor: Processeur OCR pour documents scannés
            generation_provider: Fournisseur de génération ("mistral" ou "openai")
        """
        # Configuration des composants
        self.embedding_provider = embedding_provider or MistralEmbeddingProvider()
        self.vector_retriever = vector_retriever
        self.reranker = reranker or CohereReranker()
        self.text_processor = text_processor or TextProcessor()
        self.ocr_processor = ocr_processor or OCRProcessor()
        self.document_ocr_processor = DocumentOCRProcessor(self.ocr_processor)
        self.generation_provider = generation_provider
        
        # Initialiser les clients de génération
        self._init_generation_clients()
        
        # Vérifier la configuration
        self._verify_configuration()
    
    def _init_generation_clients(self):
        """Initialise les clients de génération"""
        if self.generation_provider == "mistral":
            self.mistral_client = Mistral(api_key=config.mistral_api_key)
            self.openai_client = None
        elif self.generation_provider == "openai":
            self.openai_client = OpenAI(api_key=config.openai_api_key)
            self.mistral_client = None
        else:
            # Support hybride
            self.mistral_client = Mistral(api_key=config.mistral_api_key)
            self.openai_client = OpenAI(api_key=config.openai_api_key)
    
    def _verify_configuration(self):
        """Vérifie la configuration du système"""
        if not self.embedding_provider:
            raise ValueError("Aucun fournisseur d'embeddings configuré")
        
        if not self.vector_retriever:
            logger.warning("Aucun récupérateur vectoriel configuré")
        
        logger.info(f"Système RAG initialisé avec {self.generation_provider}")
    
    def add_documents(
        self, 
        documents: List[Dict[str, Any]], 
        split_documents: bool = True
    ) -> List[str]:
        """
        Ajoute des documents au système RAG
        
        Args:
            documents: Liste des documents à ajouter
            split_documents: Découper les documents en chunks
            
        Returns:
            Liste des IDs des documents ajoutés
        """
        try:
            processed_documents = documents
            
            # Découper les documents si demandé
            if split_documents:
                processed_documents = self.text_processor.split_documents(documents)
                logger.info(f"Documents découpés en {len(processed_documents)} chunks")
            
            # Générer les embeddings
            for doc in processed_documents:
                if 'embedding' not in doc:
                    doc['embedding'] = self.embedding_provider.embed_text(doc['content'])
            
            # Ajouter à la base vectorielle
            if self.vector_retriever:
                document_ids = self.vector_retriever.add_documents(processed_documents)
                logger.info(f"{len(document_ids)} documents ajoutés au système")
                return document_ids
    
    def add_documents_with_ocr(
        self, 
        file_paths: List[Union[str, Path]], 
        metadata: List[Dict[str, Any]] = None,
        split_documents: bool = True
    ) -> List[str]:
        """
        Ajoute des documents en utilisant l'OCR si nécessaire
        
        Args:
            file_paths: Liste des chemins de fichiers
            metadata: Métadonnées pour chaque fichier (optionnel)
            split_documents: Découper les documents en chunks
            
        Returns:
            Liste des IDs des documents ajoutés
        """
        try:
            processed_documents = []
            metadata = metadata or [{}] * len(file_paths)
            
            for file_path, meta in zip(file_paths, metadata):
                file_path = Path(file_path)
                
                # Déterminer si l'OCR est nécessaire
                if self._needs_ocr(file_path):
                    logger.info(f"Traitement OCR pour {file_path}")
                    document = self.document_ocr_processor.process_document_for_rag(file_path, meta)
                else:
                    # Traitement normal pour les fichiers texte
                    logger.info(f"Traitement normal pour {file_path}")
                    document = self._process_text_file(file_path, meta)
                
                processed_documents.append(document)
            
            # Ajouter les documents traités
            return self.add_documents(processed_documents, split_documents)
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents avec OCR: {str(e)}")
            raise
    
    def _needs_ocr(self, file_path: Path) -> bool:
        """Détermine si un fichier nécessite l'OCR"""
        # Extensions nécessitant l'OCR
        ocr_extensions = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.bmp'}
        return file_path.suffix.lower() in ocr_extensions
    
    def _process_text_file(self, file_path: Path, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Traite un fichier texte normal"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                'content': content,
                'source': str(file_path),
                'file_type': file_path.suffix.lower(),
                'metadata': metadata
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du fichier texte {file_path}: {str(e)}")
            raise
    
    def retrieve_documents(
        self, 
        query: str, 
        top_k: int = None,
        use_reranking: bool = None
    ) -> List[Dict[str, Any]]:
        """
        Récupère les documents pertinents pour une requête
        
        Args:
            query: Requête de recherche
            top_k: Nombre de documents à récupérer
            use_reranking: Utiliser le reranking (optionnel)
            
        Returns:
            Liste des documents pertinents
        """
        if not self.vector_retriever:
            raise ValueError("Aucun récupérateur vectoriel configuré")
        
        top_k = top_k or config.max_retrieved_chunks
        use_reranking = use_reranking if use_reranking is not None else config.enable_reranking
        
        try:
            # Récupération vectorielle
            documents = self.vector_retriever.search_similar(query, top_k=top_k * 2)
            
            if not documents:
                logger.warning("Aucun document trouvé pour la requête")
                return []
            
            # Reranking si activé
            if use_reranking and self.reranker:
                documents = self.reranker.rerank_with_metadata(
                    query, 
                    documents, 
                    top_k=top_k
                )
                logger.info(f"Documents rerankés: {len(documents)} résultats")
            else:
                documents = documents[:top_k]
            
            return documents
            
        except Exception as e:
            logger.error(f"Erreur lors de la récupération: {str(e)}")
            raise
    
    def generate_response(
        self, 
        query: str, 
        context_documents: List[Dict[str, Any]] = None,
        model: str = None,
        temperature: float = None
    ) -> str:
        """
        Génère une réponse à partir d'une requête et d'un contexte
        
        Args:
            query: Requête de l'utilisateur
            context_documents: Documents de contexte (optionnel)
            model: Modèle à utiliser (optionnel)
            temperature: Température de génération (optionnel)
            
        Returns:
            Réponse générée
        """
        try:
            # Récupérer le contexte si pas fourni
            if context_documents is None:
                context_documents = self.retrieve_documents(query)
            
            # Construire le contexte
            context = self._build_context(context_documents)
            
            # Construire le prompt
            prompt = self._build_prompt(query, context)
            
            # Générer la réponse
            if self.generation_provider == "mistral":
                response = self._generate_with_mistral(prompt, model, temperature)
            elif self.generation_provider == "openai":
                response = self._generate_with_openai(prompt, model, temperature)
            else:
                # Utiliser Mistral par défaut
                response = self._generate_with_mistral(prompt, model, temperature)
            
            return response
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération: {str(e)}")
            raise
    
    def query(
        self, 
        query: str, 
        top_k: int = None,
        use_reranking: bool = None,
        model: str = None,
        temperature: float = None
    ) -> Dict[str, Any]:
        """
        Interface principale pour interroger le système RAG
        
        Args:
            query: Requête de l'utilisateur
            top_k: Nombre de documents à récupérer
            use_reranking: Utiliser le reranking
            model: Modèle de génération
            temperature: Température de génération
            
        Returns:
            Dictionnaire avec la réponse et les métadonnées
        """
        try:
            # Récupérer les documents pertinents
            documents = self.retrieve_documents(query, top_k, use_reranking)
            
            # Générer la réponse
            response = self.generate_response(
                query, 
                documents, 
                model, 
                temperature
            )
            
            return {
                'query': query,
                'response': response,
                'context_documents': documents,
                'num_context_docs': len(documents),
                'model_used': model or self.generation_provider
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
            raise
    
    def _build_context(self, documents: List[Dict[str, Any]]) -> str:
        """Construit le contexte à partir des documents"""
        if not documents:
            return ""
        
        context_parts = []
        for i, doc in enumerate(documents, 1):
            content = doc.get('content', '')
            source = doc.get('source', 'unknown')
            context_parts.append(f"[Document {i} - Source: {source}]\n{content}\n")
        
        return "\n".join(context_parts)
    
    def _build_prompt(self, query: str, context: str) -> str:
        """Construit le prompt pour la génération"""
        prompt = f"""Contexte informationnel :
---------------------
{context}
---------------------

Basé sur les informations ci-dessus et sans utiliser de connaissances préalables, réponds à la question suivante :

Question : {query}

Réponse :"""
        return prompt
    
    def _generate_with_mistral(
        self, 
        prompt: str, 
        model: str = None, 
        temperature: float = None
    ) -> str:
        """Génère une réponse avec Mistral"""
        model = model or config.mistral_generation_model
        temperature = temperature or config.temperature
        
        try:
            response = self.mistral_client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de la génération Mistral: {str(e)}")
            raise
    
    def _generate_with_openai(
        self, 
        prompt: str, 
        model: str = None, 
        temperature: float = None
    ) -> str:
        """Génère une réponse avec OpenAI"""
        model = model or config.openai_generation_model
        temperature = temperature or config.temperature
        
        try:
            response = self.openai_client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {str(e)}")
            raise
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retourne les informations sur le système"""
        info = {
            'embedding_provider': type(self.embedding_provider).__name__,
            'generation_provider': self.generation_provider,
            'has_vector_retriever': self.vector_retriever is not None,
            'has_reranker': self.reranker is not None,
            'has_text_processor': self.text_processor is not None
        }
        
        if self.vector_retriever:
            info['document_count'] = self.vector_retriever.get_document_count()
        
        return info
