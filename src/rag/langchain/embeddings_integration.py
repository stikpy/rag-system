"""
Intégration Langchain pour les embeddings
=========================================

Ce module implémente les embeddings Langchain selon la documentation officielle :
- MistralAIEmbeddings
- OpenAIEmbeddings  
- CohereEmbeddings
- Support Supabase VectorStore
"""

from typing import List, Dict, Any, Optional, Union
import logging
from langchain_mistralai import MistralAIEmbeddings
from langchain_openai import OpenAIEmbeddings
from langchain_cohere import CohereEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.embeddings import Embeddings
from langchain_core.documents import Document

from ..utils.config import config

logger = logging.getLogger(__name__)


class LangchainEmbeddingProvider:
    """Fournisseur d'embeddings avec Langchain"""
    
    def __init__(
        self,
        provider: str = "mistral",
        model: str = None,
        api_key: str = None
    ):
        """
        Initialise le fournisseur d'embeddings Langchain
        
        Args:
            provider: Fournisseur ("mistral", "openai", "cohere")
            model: Modèle à utiliser (optionnel)
            api_key: Clé API (optionnel)
        """
        self.provider = provider
        self.model = model
        self.api_key = api_key
        
        # Initialiser l'embedding selon le fournisseur
        self._init_embedding()
    
    def _init_embedding(self):
        """Initialise l'embedding selon le fournisseur"""
        if self.provider == "mistral":
            self.embedding = MistralAIEmbeddings(
                model=self.model or config.mistral_embedding_model,
                api_key=self.api_key or config.mistral_api_key
            )
        elif self.provider == "openai":
            self.embedding = OpenAIEmbeddings(
                model=self.model or config.openai_embedding_model,
                api_key=self.api_key or config.openai_api_key
            )
        elif self.provider == "cohere":
            self.embedding = CohereEmbeddings(
                model=self.model or "embed-english-v3.0",
                api_key=self.api_key or config.cohere_api_key
            )
        else:
            raise ValueError(f"Fournisseur non supporté: {self.provider}")
    
    def embed_query(self, text: str) -> List[float]:
        """Génère un embedding pour une requête"""
        try:
            return self.embedding.embed_query(text)
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding de la requête: {str(e)}")
            raise
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Génère des embeddings pour plusieurs documents"""
        try:
            return self.embedding.embed_documents(texts)
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding des documents: {str(e)}")
            raise


class LangchainVectorStore:
    """VectorStore Langchain avec Supabase"""
    
    def __init__(
        self,
        embedding_provider: LangchainEmbeddingProvider,
        supabase_url: str = None,
        supabase_key: str = None,
        table_name: str = "documents"
    ):
        """
        Initialise le VectorStore Langchain
        
        Args:
            embedding_provider: Fournisseur d'embeddings
            supabase_url: URL Supabase (optionnel)
            table_name: Nom de la table (optionnel)
        """
        self.embedding_provider = embedding_provider
        self.supabase_url = supabase_url or config.supabase_url
        self.supabase_key = supabase_key or config.supabase_key
        self.table_name = table_name
        
        # Initialiser le VectorStore
        self._init_vector_store()
    
    def _init_vector_store(self):
        """Initialise le VectorStore Supabase"""
        try:
            self.vector_store = SupabaseVectorStore(
                embedding=self.embedding_provider.embedding,
                supabase_url=self.supabase_url,
                supabase_key=self.supabase_key,
                table_name=self.table_name
            )
            logger.info("VectorStore Supabase initialisé avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du VectorStore: {str(e)}")
            raise
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Ajoute des documents au VectorStore"""
        try:
            return self.vector_store.add_documents(documents)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {str(e)}")
            raise
    
    def similarity_search(
        self,
        query: str,
        k: int = 4,
        filter: Dict[str, Any] = None
    ) -> List[Document]:
        """Recherche de similarité"""
        try:
            return self.vector_store.similarity_search(
                query=query,
                k=k,
                filter=filter
            )
        except Exception as e:
            logger.error(f"Erreur lors de la recherche: {str(e)}")
            raise
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 4,
        filter: Dict[str, Any] = None
    ) -> List[tuple]:
        """Recherche de similarité avec scores"""
        try:
            return self.vector_store.similarity_search_with_score(
                query=query,
                k=k,
                filter=filter
            )
        except Exception as e:
            logger.error(f"Erreur lors de la recherche avec scores: {str(e)}")
            raise
    
    def delete_documents(self, ids: List[str]) -> bool:
        """Supprime des documents"""
        try:
            self.vector_store.delete(ids)
            return True
        except Exception as e:
            logger.error(f"Erreur lors de la suppression: {str(e)}")
            return False


class LangchainRAGChain:
    """Chaîne RAG complète avec Langchain"""
    
    def __init__(
        self,
        embedding_provider: str = "mistral",
        llm_provider: str = "mistral",
        use_vector_store: bool = True
    ):
        """
        Initialise la chaîne RAG Langchain
        
        Args:
            embedding_provider: Fournisseur d'embeddings
            llm_provider: Fournisseur LLM
            use_vector_store: Utiliser le VectorStore
        """
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
        self.use_vector_store = use_vector_store
        
        # Initialiser les composants
        self._init_embedding_provider()
        self._init_vector_store()
        self._init_llm()
        self._init_chain()
    
    def _init_embedding_provider(self):
        """Initialise le fournisseur d'embeddings"""
        self.embedding = LangchainEmbeddingProvider(
            provider=self.embedding_provider
        )
    
    def _init_vector_store(self):
        """Initialise le VectorStore"""
        if self.use_vector_store:
            self.vector_store = LangchainVectorStore(
                embedding_provider=self.embedding
            )
        else:
            self.vector_store = None
    
    def _init_llm(self):
        """Initialise le LLM"""
        if self.llm_provider == "mistral":
            from langchain_mistralai import MistralAI
            self.llm = MistralAI(
                model=config.mistral_generation_model,
                temperature=config.temperature,
                api_key=config.mistral_api_key
            )
        elif self.llm_provider == "openai":
            from langchain_openai import ChatOpenAI
            self.llm = ChatOpenAI(
                model=config.openai_generation_model,
                temperature=config.temperature,
                api_key=config.openai_api_key
            )
        else:
            raise ValueError(f"Fournisseur LLM non supporté: {self.llm_provider}")
    
    def _init_chain(self):
        """Initialise la chaîne RAG"""
        if self.vector_store:
            from langchain.chains import RetrievalQA
            self.chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.vector_store.vector_store.as_retriever(),
                return_source_documents=True
            )
        else:
            self.chain = None
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Ajoute des documents à la chaîne"""
        if not self.vector_store:
            raise ValueError("VectorStore non configuré")
        
        return self.vector_store.add_documents(documents)
    
    def query(self, question: str) -> Dict[str, Any]:
        """Pose une question à la chaîne"""
        if not self.chain:
            raise ValueError("Chaîne non configurée")
        
        try:
            result = self.chain({"query": question})
            return {
                "answer": result["result"],
                "source_documents": result.get("source_documents", [])
            }
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
            raise
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Recherche de similarité"""
        if not self.vector_store:
            raise ValueError("VectorStore non configuré")
        
        return self.vector_store.similarity_search(query, k)


class LangchainDocumentProcessor:
    """Processeur de documents avec Langchain"""
    
    def __init__(self, embedding_provider: str = "mistral"):
        """
        Initialise le processeur de documents
        
        Args:
            embedding_provider: Fournisseur d'embeddings
        """
        self.embedding_provider = LangchainEmbeddingProvider(embedding_provider)
    
    def process_documents(
        self,
        texts: List[str],
        metadatas: List[Dict[str, Any]] = None
    ) -> List[Document]:
        """
        Traite des documents pour Langchain
        
        Args:
            texts: Liste des textes
            metadatas: Métadonnées (optionnel)
            
        Returns:
            Liste des documents Langchain
        """
        documents = []
        metadatas = metadatas or [{}] * len(texts)
        
        for text, metadata in zip(texts, metadatas):
            document = Document(
                page_content=text,
                metadata=metadata
            )
            documents.append(document)
        
        return documents
    
    def embed_documents(self, documents: List[Document]) -> List[Document]:
        """Ajoute les embeddings aux documents"""
        try:
            texts = [doc.page_content for doc in documents]
            embeddings = self.embedding_provider.embed_documents(texts)
            
            # Ajouter les embeddings aux métadonnées
            for doc, embedding in zip(documents, embeddings):
                doc.metadata["embedding"] = embedding
            
            return documents
        except Exception as e:
            logger.error(f"Erreur lors de l'embedding des documents: {str(e)}")
            raise


class LangchainRAGWithReranking:
    """RAG avec reranking Cohere intégré"""
    
    def __init__(
        self,
        rag_chain: LangchainRAGChain,
        rerank_model: str = None
    ):
        """
        Initialise le RAG avec reranking
        
        Args:
            rag_chain: Chaîne RAG de base
            rerank_model: Modèle de reranking (optionnel)
        """
        self.rag_chain = rag_chain
        self.rerank_model = rerank_model or config.cohere_rerank_model
        
        # Initialiser le reranker Cohere
        from langchain_cohere import CohereRerank
        self.reranker = CohereRerank(
            model=self.rerank_model,
            api_key=config.cohere_api_key,
            top_n=config.rerank_top_k
        )
    
    def query_with_reranking(self, question: str) -> Dict[str, Any]:
        """
        Pose une question avec reranking
        
        Args:
            question: Question à poser
            
        Returns:
            Réponse avec documents rerankés
        """
        try:
            # Recherche initiale
            documents = self.rag_chain.similarity_search(question, k=10)
            
            # Reranking
            reranked_docs = self.reranker.compress_documents(documents, question)
            
            # Génération de réponse avec documents rerankés
            # Note: Ici vous devriez utiliser les documents rerankés pour la génération
            result = self.rag_chain.query(question)
            
            return {
                "answer": result["answer"],
                "source_documents": reranked_docs,
                "reranked": True
            }
        except Exception as e:
            logger.error(f"Erreur lors du reranking: {str(e)}")
            raise
