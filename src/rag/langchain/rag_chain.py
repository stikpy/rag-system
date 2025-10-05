"""
Intégration Langchain pour le système RAG
==========================================

Ce module implémente des chaînes Langchain avancées pour le RAG :
- RAG chains avec Mistral et OpenAI
- Agents conversationnels
- Memory management
- Document processing chains
"""

from typing import List, Dict, Any, Optional, Union
import logging
from langchain.chains import RetrievalQA, ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory, ConversationSummaryMemory
from langchain.prompts import PromptTemplate
from langchain.schema import BaseRetriever, Document
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.mistralai import MistralAI
from langchain_openai import OpenAI
from langchain_cohere import CohereRerank
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_community.embeddings import MistralAIEmbeddings, OpenAIEmbeddings

from ..utils.config import config

logger = logging.getLogger(__name__)


class RAGChain:
    """Chaîne RAG avec Langchain"""
    
    def __init__(
        self,
        llm_provider: str = "mistral",
        embedding_provider: str = "mistral",
        use_memory: bool = True,
        memory_type: str = "buffer"
    ):
        """
        Initialise la chaîne RAG Langchain
        
        Args:
            llm_provider: Fournisseur LLM ("mistral" ou "openai")
            embedding_provider: Fournisseur d'embeddings
            use_memory: Utiliser la mémoire conversationnelle
            memory_type: Type de mémoire ("buffer" ou "summary")
        """
        self.llm_provider = llm_provider
        self.embedding_provider = embedding_provider
        self.use_memory = use_memory
        
        # Initialiser les composants
        self._init_llm()
        self._init_embeddings()
        self._init_memory(memory_type)
        self._init_retriever()
        self._init_chain()
    
    def _init_llm(self):
        """Initialise le modèle de langage"""
        if self.llm_provider == "mistral":
            self.llm = MistralAI(
                model=config.mistral_generation_model,
                temperature=config.temperature,
                api_key=config.mistral_api_key
            )
        elif self.llm_provider == "openai":
            self.llm = OpenAI(
                model=config.openai_generation_model,
                temperature=config.temperature,
                api_key=config.openai_api_key
            )
        else:
            raise ValueError(f"Fournisseur LLM non supporté: {self.llm_provider}")
    
    def _init_embeddings(self):
        """Initialise les embeddings"""
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
        else:
            raise ValueError(f"Fournisseur d'embeddings non supporté: {self.embedding_provider}")
    
    def _init_memory(self, memory_type: str):
        """Initialise la mémoire conversationnelle"""
        if not self.use_memory:
            self.memory = None
            return
        
        if memory_type == "buffer":
            self.memory = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        elif memory_type == "summary":
            self.memory = ConversationSummaryMemory(
                llm=self.llm,
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        else:
            raise ValueError(f"Type de mémoire non supporté: {memory_type}")
    
    def _init_retriever(self):
        """Initialise le récupérateur"""
        # Note: Dans un vrai projet, vous configureriez SupabaseVectorStore ici
        # Pour l'instant, nous utilisons un récupérateur factice
        self.retriever = None
        logger.warning("Récupérateur non configuré - utilisez set_retriever()")
    
    def _init_chain(self):
        """Initialise la chaîne RAG"""
        if self.memory:
            self.chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=self.retriever,
                memory=self.memory,
                return_source_documents=True
            )
        else:
            self.chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=self.retriever,
                return_source_documents=True
            )
    
    def set_retriever(self, retriever: BaseRetriever):
        """Définit le récupérateur"""
        self.retriever = retriever
        self._init_chain()
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Pose une question à la chaîne RAG
        
        Args:
            question: Question à poser
            
        Returns:
            Réponse avec sources
        """
        try:
            if self.memory:
                result = self.chain({"question": question})
            else:
                result = self.chain({"query": question})
            
            return {
                "answer": result["answer"],
                "source_documents": result.get("source_documents", []),
                "chat_history": result.get("chat_history", [])
            }
        except Exception as e:
            logger.error(f"Erreur lors de la requête: {str(e)}")
            raise
    
    def clear_memory(self):
        """Efface la mémoire conversationnelle"""
        if self.memory:
            self.memory.clear()


class RAGAgent:
    """Agent RAG avec outils Langchain"""
    
    def __init__(self, rag_chain: RAGChain):
        """
        Initialise l'agent RAG
        
        Args:
            rag_chain: Chaîne RAG à utiliser
        """
        self.rag_chain = rag_chain
        self._init_tools()
        self._init_agent()
    
    def _init_tools(self):
        """Initialise les outils de l'agent"""
        self.tools = [
            Tool(
                name="RAG Search",
                description="Recherche dans la base de connaissances",
                func=self._rag_search
            ),
            Tool(
                name="Memory Clear",
                description="Efface la mémoire conversationnelle",
                func=self._clear_memory
            )
        ]
    
    def _init_agent(self):
        """Initialise l'agent"""
        # Prompt pour l'agent
        agent_prompt = PromptTemplate.from_template("""
        Tu es un assistant IA spécialisé dans la recherche d'informations.
        Tu as accès aux outils suivants:
        
        {tools}
        
        Utilise ces outils pour répondre aux questions de l'utilisateur.
        Si tu ne trouves pas d'information pertinente, dis-le clairement.
        
        Question: {input}
        {agent_scratchpad}
        """)
        
        self.agent = create_react_agent(
            llm=self.rag_chain.llm,
            tools=self.tools,
            prompt=agent_prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def _rag_search(self, query: str) -> str:
        """Outil de recherche RAG"""
        try:
            result = self.rag_chain.query(query)
            return result["answer"]
        except Exception as e:
            return f"Erreur lors de la recherche: {str(e)}"
    
    def _clear_memory(self, _: str) -> str:
        """Outil pour effacer la mémoire"""
        self.rag_chain.clear_memory()
        return "Mémoire effacée"
    
    def run(self, query: str) -> Dict[str, Any]:
        """
        Exécute l'agent avec une requête
        
        Args:
            query: Requête de l'utilisateur
            
        Returns:
            Résultat de l'agent
        """
        try:
            result = self.agent_executor.invoke({"input": query})
            return {
                "output": result["output"],
                "intermediate_steps": result.get("intermediate_steps", [])
            }
        except Exception as e:
            logger.error(f"Erreur lors de l'exécution de l'agent: {str(e)}")
            raise


class DocumentProcessingChain:
    """Chaîne de traitement de documents avec Langchain"""
    
    def __init__(self, llm_provider: str = "mistral"):
        """
        Initialise la chaîne de traitement
        
        Args:
            llm_provider: Fournisseur LLM
        """
        self.llm_provider = llm_provider
        self._init_llm()
        self._init_prompts()
    
    def _init_llm(self):
        """Initialise le LLM"""
        if self.llm_provider == "mistral":
            self.llm = MistralAI(
                model=config.mistral_generation_model,
                temperature=config.temperature,
                api_key=config.mistral_api_key
            )
        elif self.llm_provider == "openai":
            self.llm = OpenAI(
                model=config.openai_generation_model,
                temperature=config.temperature,
                api_key=config.openai_api_key
            )
    
    def _init_prompts(self):
        """Initialise les prompts de traitement"""
        self.summarize_prompt = PromptTemplate.from_template("""
        Résume le document suivant en {max_words} mots maximum:
        
        Document: {document}
        
        Résumé:
        """)
        
        self.extract_keywords_prompt = PromptTemplate.from_template("""
        Extrait les mots-clés principaux du document suivant:
        
        Document: {document}
        
        Mots-clés (séparés par des virgules):
        """)
        
        self.classify_prompt = PromptTemplate.from_template("""
        Classe le document suivant dans une des catégories suivantes:
        - technologie
        - science
        - histoire
        - littérature
        - autres
        
        Document: {document}
        
        Catégorie:
        """)
    
    def summarize_document(self, document: str, max_words: int = 100) -> str:
        """Résume un document"""
        try:
            prompt = self.summarize_prompt.format(
                document=document,
                max_words=max_words
            )
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Erreur lors du résumé: {str(e)}")
            raise
    
    def extract_keywords(self, document: str) -> List[str]:
        """Extrait les mots-clés d'un document"""
        try:
            prompt = self.extract_keywords_prompt.format(document=document)
            response = self.llm.invoke(prompt)
            keywords = response.content.strip().split(',')
            return [kw.strip() for kw in keywords if kw.strip()]
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction des mots-clés: {str(e)}")
            raise
    
    def classify_document(self, document: str) -> str:
        """Classe un document"""
        try:
            prompt = self.classify_prompt.format(document=document)
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Erreur lors de la classification: {str(e)}")
            raise


class RAGWithReranking:
    """RAG avec reranking Cohere intégré"""
    
    def __init__(self, rag_chain: RAGChain):
        """
        Initialise le RAG avec reranking
        
        Args:
            rag_chain: Chaîne RAG de base
        """
        self.rag_chain = rag_chain
        self.reranker = CohereRerank(
            model=config.cohere_rerank_model,
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
            # Récupération initiale
            result = self.rag_chain.query(question)
            
            # Reranking des documents sources
            if result.get("source_documents"):
                reranked_docs = self.reranker.compress_documents(
                    result["source_documents"],
                    question
                )
                result["reranked_documents"] = reranked_docs
            
            return result
        except Exception as e:
            logger.error(f"Erreur lors du reranking: {str(e)}")
            raise
