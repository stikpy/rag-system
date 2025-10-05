"""
Exemple de production RAG avec Langchain
========================================

Cet exemple montre un système RAG complet en production utilisant :
- Les meilleures pratiques Langchain
- Configuration optimisée
- Monitoring et observabilité
- Gestion d'erreurs robuste
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Imports Langchain
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.vectorstores import FAISS, Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mistralai import MistralAIEmbeddings, MistralAI
from langchain_cohere import CohereEmbeddings, CohereRerank
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.retrievers import BM25Retriever, EnsembleRetriever

# Imports du système RAG
from rag.utils.config import config
from rag.utils.logging import setup_logging

# Configuration du logging
logger = setup_logging(level="INFO", log_file="rag_production.log")


class ProductionRAGSystem:
    """Système RAG de production avec Langchain"""
    
    def __init__(
        self,
        embedding_provider: str = "mistral",
        llm_provider: str = "mistral",
        vector_store_type: str = "faiss",
        use_reranking: bool = True,
        use_memory: bool = True
    ):
        """
        Initialise le système RAG de production
        
        Args:
            embedding_provider: Fournisseur d'embeddings
            llm_provider: Fournisseur LLM
            vector_store_type: Type de vector store
            use_reranking: Utiliser le reranking
            use_memory: Utiliser la mémoire conversationnelle
        """
        self.embedding_provider = embedding_provider
        self.llm_provider = llm_provider
        self.vector_store_type = vector_store_type
        self.use_reranking = use_reranking
        self.use_memory = use_memory
        
        # Métriques
        self.metrics = {
            "queries_processed": 0,
            "total_retrieval_time": 0,
            "total_generation_time": 0,
            "cache_hits": 0,
            "errors": 0
        }
        
        # Initialiser les composants
        self._init_embeddings()
        self._init_llm()
        self._init_vector_store()
        self._init_reranker()
        self._init_memory()
        self._init_chain()
        
        logger.info(f"Système RAG de production initialisé: {self.llm_provider} + {self.embedding_provider}")
    
    def _init_embeddings(self):
        """Initialise les embeddings"""
        try:
            if self.embedding_provider == "mistral":
                self.embeddings = MistralAIEmbeddings(
                    model=config.mistral_embedding_model,
                    api_key=config.mistral_api_key
                )
            elif self.embedding_provider == "openai":
                self.embeddings = OpenAIEmbeddings(
                    model=config.openai_embedding_model,
                    api_key=config.openai_api_key
                )
            elif self.embedding_provider == "cohere":
                self.embeddings = CohereEmbeddings(
                    model="embed-english-v3.0",
                    api_key=config.cohere_api_key
                )
            else:
                raise ValueError(f"Fournisseur d'embeddings non supporté: {self.embedding_provider}")
            
            logger.info(f"Embeddings {self.embedding_provider} initialisés")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation des embeddings: {str(e)}")
            raise
    
    def _init_llm(self):
        """Initialise le LLM"""
        try:
            if self.llm_provider == "mistral":
                self.llm = MistralAI(
                    model=config.mistral_generation_model,
                    temperature=config.temperature,
                    api_key=config.mistral_api_key
                )
            elif self.llm_provider == "openai":
                self.llm = ChatOpenAI(
                    model=config.openai_generation_model,
                    temperature=config.temperature,
                    api_key=config.openai_api_key
                )
            else:
                raise ValueError(f"Fournisseur LLM non supporté: {self.llm_provider}")
            
            logger.info(f"LLM {self.llm_provider} initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du LLM: {str(e)}")
            raise
    
    def _init_vector_store(self):
        """Initialise le vector store"""
        try:
            if self.vector_store_type == "faiss":
                self.vector_store = None  # Sera créé lors de l'ajout de documents
            elif self.vector_store_type == "chroma":
                self.vector_store = None  # Sera créé lors de l'ajout de documents
            elif self.vector_store_type == "inmemory":
                self.vector_store = InMemoryVectorStore(embedding=self.embeddings)
            else:
                raise ValueError(f"Type de vector store non supporté: {self.vector_store_type}")
            
            logger.info(f"Vector store {self.vector_store_type} initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du vector store: {str(e)}")
            raise
    
    def _init_reranker(self):
        """Initialise le reranker"""
        if self.use_reranking:
            try:
                self.reranker = CohereRerank(
                    model=config.cohere_rerank_model,
                    api_key=config.cohere_api_key,
                    top_n=config.rerank_top_k
                )
                logger.info("Reranker Cohere initialisé")
            except Exception as e:
                logger.warning(f"Reranker non disponible: {str(e)}")
                self.reranker = None
        else:
            self.reranker = None
    
    def _init_memory(self):
        """Initialise la mémoire conversationnelle"""
        if self.use_memory:
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
            logger.info("Mémoire conversationnelle initialisée")
        else:
            self.memory = None
    
    def _init_chain(self):
        """Initialise la chaîne RAG"""
        if self.vector_store is None:
            logger.warning("Vector store non initialisé - chaîne non créée")
            self.chain = None
            return
        
        try:
            if self.memory:
                self.chain = ConversationalRetrievalChain.from_llm(
                    llm=self.llm,
                    retriever=self.vector_store.as_retriever(),
                    memory=self.memory,
                    return_source_documents=True
                )
            else:
                self.chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.vector_store.as_retriever(),
                    return_source_documents=True
                )
            
            logger.info("Chaîne RAG initialisée")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation de la chaîne: {str(e)}")
            self.chain = None
    
    def add_documents(self, documents: List[Document]) -> bool:
        """
        Ajoute des documents au système
        
        Args:
            documents: Liste des documents à ajouter
            
        Returns:
            True si succès, False sinon
        """
        try:
            if self.vector_store_type == "faiss":
                self.vector_store = FAISS.from_documents(documents, self.embeddings)
            elif self.vector_store_type == "chroma":
                self.vector_store = Chroma.from_documents(
                    documents=documents,
                    embedding=self.embeddings,
                    persist_directory="./chroma_db"
                )
            elif self.vector_store_type == "inmemory":
                self.vector_store.add_documents(documents)
            
            # Réinitialiser la chaîne avec le nouveau vector store
            self._init_chain()
            
            logger.info(f"{len(documents)} documents ajoutés au système")
            return True
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des documents: {str(e)}")
            self.metrics["errors"] += 1
            return False
    
    def query(self, question: str, use_reranking: bool = None) -> Dict[str, Any]:
        """
        Pose une question au système RAG
        
        Args:
            question: Question à poser
            use_reranking: Utiliser le reranking (optionnel)
            
        Returns:
            Dictionnaire avec la réponse et métadonnées
        """
        start_time = time.time()
        use_reranking = use_reranking if use_reranking is not None else self.use_reranking
        
        try:
            if not self.chain:
                raise ValueError("Chaîne RAG non initialisée")
            
            # Récupération
            retrieval_start = time.time()
            if use_reranking and self.reranker:
                # Récupération avec reranking
                retriever = self.vector_store.as_retriever(search_kwargs={"k": 10})
                documents = retriever.invoke(question)
                reranked_docs = self.reranker.compress_documents(documents, question)
                
                # Utiliser les documents rerankés
                context = "\n".join([doc.page_content for doc in reranked_docs])
                response = self._generate_with_context(question, context)
                source_documents = reranked_docs
            else:
                # Récupération standard
                if self.memory:
                    result = self.chain({"question": question})
                else:
                    result = self.chain({"query": question})
                
                response = result["answer"]
                source_documents = result.get("source_documents", [])
            
            retrieval_time = time.time() - retrieval_start
            
            # Génération
            generation_start = time.time()
            if not use_reranking or not self.reranker:
                # La génération a déjà été faite dans la chaîne
                generation_time = 0
            else:
                generation_time = time.time() - generation_start
            
            total_time = time.time() - start_time
            
            # Mettre à jour les métriques
            self.metrics["queries_processed"] += 1
            self.metrics["total_retrieval_time"] += retrieval_time
            self.metrics["total_generation_time"] += generation_time
            
            return {
                "answer": response,
                "source_documents": source_documents,
                "num_sources": len(source_documents),
                "retrieval_time": retrieval_time,
                "generation_time": generation_time,
                "total_time": total_time,
                "reranked": use_reranking and self.reranker is not None
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
            self.metrics["errors"] += 1
            return {
                "answer": f"Erreur lors du traitement: {str(e)}",
                "source_documents": [],
                "error": str(e)
            }
    
    def _generate_with_context(self, question: str, context: str) -> str:
        """Génère une réponse avec un contexte donné"""
        prompt = PromptTemplate.from_template("""
        Contexte: {context}
        
        Question: {question}
        
        Réponse basée sur le contexte:
        """)
        
        formatted_prompt = prompt.format(context=context, question=question)
        response = self.llm.invoke(formatted_prompt)
        return response.content
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retourne les métriques du système"""
        if self.metrics["queries_processed"] > 0:
            avg_retrieval_time = self.metrics["total_retrieval_time"] / self.metrics["queries_processed"]
            avg_generation_time = self.metrics["total_generation_time"] / self.metrics["queries_processed"]
        else:
            avg_retrieval_time = 0
            avg_generation_time = 0
        
        return {
            "queries_processed": self.metrics["queries_processed"],
            "avg_retrieval_time": avg_retrieval_time,
            "avg_generation_time": avg_generation_time,
            "cache_hits": self.metrics["cache_hits"],
            "errors": self.metrics["errors"],
            "error_rate": self.metrics["errors"] / max(self.metrics["queries_processed"], 1)
        }
    
    def clear_memory(self):
        """Efface la mémoire conversationnelle"""
        if self.memory:
            self.memory.clear()
            logger.info("Mémoire conversationnelle effacée")


def create_sample_documents() -> List[Document]:
    """Crée des documents d'exemple"""
    documents = [
        Document(
            page_content="L'intelligence artificielle est une technologie qui permet aux machines d'apprendre et de prendre des décisions de manière autonome.",
            metadata={"source": "article_1", "category": "technology", "language": "fr"}
        ),
        Document(
            page_content="Le machine learning est une sous-discipline de l'IA qui se concentre sur l'apprentissage automatique à partir de données.",
            metadata={"source": "article_2", "category": "technology", "language": "fr"}
        ),
        Document(
            page_content="Les réseaux de neurones artificiels sont inspirés du fonctionnement du cerveau humain et permettent de résoudre des problèmes complexes.",
            metadata={"source": "article_3", "category": "science", "language": "fr"}
        ),
        Document(
            page_content="L'IA générative comme ChatGPT peut créer du contenu textuel de qualité et ouvre de nouvelles possibilités créatives.",
            metadata={"source": "article_4", "category": "applications", "language": "fr"}
        ),
        Document(
            page_content="L'éthique de l'IA est un enjeu majeur qui nécessite une réflexion sur l'équité, la transparence et le respect de la vie privée.",
            metadata={"source": "article_5", "category": "ethics", "language": "fr"}
        )
    ]
    return documents


def test_production_rag():
    """Test du système RAG de production"""
    
    print("🚀 Test du système RAG de production...")
    
    # 1. Initialiser le système
    rag_system = ProductionRAGSystem(
        embedding_provider="mistral",
        llm_provider="mistral",
        vector_store_type="faiss",
        use_reranking=True,
        use_memory=True
    )
    
    # 2. Créer et ajouter des documents
    documents = create_sample_documents()
    success = rag_system.add_documents(documents)
    
    if not success:
        print("❌ Erreur lors de l'ajout des documents")
        return
    
    print(f"✅ {len(documents)} documents ajoutés")
    
    # 3. Tester différentes requêtes
    test_queries = [
        "Qu'est-ce que l'intelligence artificielle ?",
        "Comment fonctionne le machine learning ?",
        "Expliquez les réseaux de neurones",
        "Quels sont les enjeux éthiques de l'IA ?",
        "Qu'est-ce que l'IA générative ?"
    ]
    
    print("\n🔍 Test des requêtes...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Requête {i}: {query}")
        
        start_time = time.time()
        result = rag_system.query(query, use_reranking=True)
        total_time = time.time() - start_time
        
        print(f"💬 Réponse: {result['answer']}")
        print(f"📚 Sources: {result['num_sources']} documents")
        print(f"⏱️  Temps: {total_time:.2f}s")
        print(f"🔄 Reranking: {'Oui' if result.get('reranked', False) else 'Non'}")
        
        if 'error' in result:
            print(f"❌ Erreur: {result['error']}")
    
    # 4. Afficher les métriques
    print("\n📊 Métriques du système:")
    metrics = rag_system.get_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key}: {value:.3f}")
        else:
            print(f"  {key}: {value}")
    
    # 5. Test de la mémoire conversationnelle
    print("\n💭 Test de la mémoire conversationnelle...")
    
    # Première question
    result1 = rag_system.query("Qu'est-ce que l'IA ?")
    print(f"Réponse 1: {result1['answer'][:100]}...")
    
    # Question de suivi
    result2 = rag_system.query("Peux-tu me donner plus de détails ?")
    print(f"Réponse 2: {result2['answer'][:100]}...")
    
    # Effacer la mémoire
    rag_system.clear_memory()
    print("🧹 Mémoire effacée")


def benchmark_performance():
    """Benchmark des performances"""
    
    print("\n⚡ Benchmark des performances...")
    
    # Test avec différents fournisseurs
    providers = [
        ("mistral", "mistral"),
        ("openai", "openai"),
    ]
    
    for embedding_provider, llm_provider in providers:
        print(f"\n🔧 Test avec {embedding_provider} + {llm_provider}...")
        
        try:
            # Initialiser le système
            rag_system = ProductionRAGSystem(
                embedding_provider=embedding_provider,
                llm_provider=llm_provider,
                vector_store_type="inmemory",
                use_reranking=False,
                use_memory=False
            )
            
            # Ajouter des documents
            documents = create_sample_documents()
            rag_system.add_documents(documents)
            
            # Test de performance
            query = "Qu'est-ce que l'intelligence artificielle ?"
            times = []
            
            for _ in range(5):  # 5 tests
                start_time = time.time()
                result = rag_system.query(query)
                end_time = time.time()
                times.append(end_time - start_time)
            
            avg_time = sum(times) / len(times)
            print(f"  Temps moyen: {avg_time:.2f}s")
            print(f"  Réponse: {result['answer'][:50]}...")
            
        except Exception as e:
            print(f"  ❌ Erreur: {str(e)}")


def main():
    """Fonction principale"""
    
    print("🎯 Système RAG de Production avec Langchain")
    print("=" * 50)
    
    try:
        # Test principal
        test_production_rag()
        
        # Benchmark
        benchmark_performance()
        
        print("\n🎉 Tests terminés avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        logger.error(f"Erreur dans main: {str(e)}")


if __name__ == "__main__":
    main()
