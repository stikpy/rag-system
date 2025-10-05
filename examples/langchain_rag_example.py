"""
Exemple d'utilisation Langchain avec le système RAG
==================================================

Cet exemple montre comment utiliser Langchain selon la documentation officielle :
- Embeddings Mistral et OpenAI
- VectorStore Supabase
- RAG chains avec reranking
- Document processing
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.langchain.embeddings_integration import (
    LangchainEmbeddingProvider,
    LangchainVectorStore,
    LangchainRAGChain,
    LangchainDocumentProcessor,
    LangchainRAGWithReranking
)
from langchain_core.documents import Document
from rag.utils.config import config


def basic_langchain_example():
    """Exemple basique avec Langchain"""
    
    print("🚀 Exemple Langchain basique...")
    
    # 1. Initialiser le fournisseur d'embeddings Mistral
    mistral_embedding = LangchainEmbeddingProvider(
        provider="mistral",
        model="mistral-embed"
    )
    
    print("✅ Fournisseur Mistral initialisé")
    
    # 2. Tester l'embedding
    test_text = "L'intelligence artificielle transforme notre monde"
    embedding = mistral_embedding.embed_query(test_text)
    print(f"📊 Embedding généré: {len(embedding)} dimensions")
    
    # 3. Initialiser le VectorStore
    vector_store = LangchainVectorStore(
        embedding_provider=mistral_embedding
    )
    
    print("✅ VectorStore Supabase initialisé")
    
    # 4. Créer des documents
    documents = [
        Document(
            page_content="L'IA est une technologie révolutionnaire qui permet aux machines d'apprendre.",
            metadata={"source": "article_1", "category": "technology"}
        ),
        Document(
            page_content="Le machine learning utilise des algorithmes pour analyser des données.",
            metadata={"source": "article_2", "category": "technology"}
        ),
        Document(
            page_content="Les réseaux de neurones sont inspirés du cerveau humain.",
            metadata={"source": "article_3", "category": "science"}
        )
    ]
    
    # 5. Ajouter les documents au VectorStore
    try:
        doc_ids = vector_store.add_documents(documents)
        print(f"✅ {len(doc_ids)} documents ajoutés au VectorStore")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout des documents: {str(e)}")
        print("💡 Assurez-vous que Supabase est configuré correctement")
    
    # 6. Recherche de similarité
    try:
        results = vector_store.similarity_search(
            "Qu'est-ce que l'intelligence artificielle ?",
            k=2
        )
        print(f"🔍 {len(results)} documents trouvés")
        for i, doc in enumerate(results):
            print(f"  Document {i+1}: {doc.page_content[:50]}...")
    except Exception as e:
        print(f"⚠️  Erreur lors de la recherche: {str(e)}")


def advanced_rag_chain_example():
    """Exemple avancé avec chaîne RAG complète"""
    
    print("\n🔗 Exemple chaîne RAG avancée...")
    
    # 1. Initialiser la chaîne RAG
    rag_chain = LangchainRAGChain(
        embedding_provider="mistral",
        llm_provider="mistral",
        use_vector_store=True
    )
    
    print("✅ Chaîne RAG initialisée")
    
    # 2. Créer des documents avec le processeur
    processor = LangchainDocumentProcessor("mistral")
    
    texts = [
        "L'intelligence artificielle est une technologie qui permet aux machines d'apprendre et de prendre des décisions de manière autonome.",
        "Le machine learning est une sous-discipline de l'IA qui se concentre sur l'apprentissage automatique à partir de données.",
        "Les réseaux de neurones artificiels sont inspirés du fonctionnement du cerveau humain et permettent de résoudre des problèmes complexes."
    ]
    
    metadatas = [
        {"title": "Introduction IA", "category": "technology"},
        {"title": "Machine Learning", "category": "technology"},
        {"title": "Réseaux de neurones", "category": "science"}
    ]
    
    documents = processor.process_documents(texts, metadatas)
    print(f"📄 {len(documents)} documents traités")
    
    # 3. Ajouter les documents à la chaîne
    try:
        doc_ids = rag_chain.add_documents(documents)
        print(f"✅ {len(doc_ids)} documents ajoutés à la chaîne")
    except Exception as e:
        print(f"⚠️  Erreur lors de l'ajout: {str(e)}")
    
    # 4. Tester la chaîne RAG
    queries = [
        "Qu'est-ce que l'intelligence artificielle ?",
        "Comment fonctionne le machine learning ?",
        "Expliquez les réseaux de neurones"
    ]
    
    for query in queries:
        print(f"\n❓ Requête: {query}")
        try:
            result = rag_chain.query(query)
            print(f"💬 Réponse: {result['answer']}")
            print(f"📚 Sources: {len(result['source_documents'])} documents")
        except Exception as e:
            print(f"⚠️  Erreur lors de la requête: {str(e)}")


def reranking_example():
    """Exemple avec reranking Cohere"""
    
    print("\n🔄 Exemple avec reranking...")
    
    # 1. Initialiser la chaîne RAG
    rag_chain = LangchainRAGChain(
        embedding_provider="mistral",
        llm_provider="mistral"
    )
    
    # 2. Initialiser le RAG avec reranking
    rag_with_reranking = LangchainRAGWithReranking(rag_chain)
    
    print("✅ RAG avec reranking initialisé")
    
    # 3. Tester avec reranking
    query = "Quels sont les avantages de l'intelligence artificielle ?"
    print(f"\n❓ Requête: {query}")
    
    try:
        result = rag_with_reranking.query_with_reranking(query)
        print(f"💬 Réponse: {result['answer']}")
        print(f"🔄 Reranking: {result['reranked']}")
        print(f"📚 Documents rerankés: {len(result['source_documents'])}")
    except Exception as e:
        print(f"⚠️  Erreur lors du reranking: {str(e)}")


def multi_provider_example():
    """Exemple avec plusieurs fournisseurs"""
    
    print("\n🔄 Exemple multi-fournisseurs...")
    
    # Test avec différents fournisseurs d'embeddings
    providers = ["mistral", "openai"]
    
    for provider in providers:
        print(f"\n🔧 Test avec {provider}...")
        
        try:
            # Initialiser le fournisseur
            embedding_provider = LangchainEmbeddingProvider(provider)
            
            # Tester l'embedding
            test_text = "Test d'embedding avec " + provider
            embedding = embedding_provider.embed_query(test_text)
            print(f"✅ {provider}: {len(embedding)} dimensions")
            
        except Exception as e:
            print(f"⚠️  Erreur avec {provider}: {str(e)}")


def document_processing_example():
    """Exemple de traitement de documents"""
    
    print("\n📄 Exemple de traitement de documents...")
    
    # 1. Initialiser le processeur
    processor = LangchainDocumentProcessor("mistral")
    
    # 2. Documents de test
    texts = [
        "L'intelligence artificielle révolutionne la médecine en permettant un diagnostic plus précis.",
        "Les voitures autonomes utilisent l'IA pour naviguer de manière sécurisée.",
        "L'IA générative peut créer du contenu artistique et littéraire de qualité."
    ]
    
    metadatas = [
        {"category": "médecine", "language": "fr"},
        {"category": "transport", "language": "fr"},
        {"category": "créativité", "language": "fr"}
    ]
    
    # 3. Traiter les documents
    documents = processor.process_documents(texts, metadatas)
    print(f"📄 {len(documents)} documents traités")
    
    # 4. Ajouter les embeddings
    try:
        documents_with_embeddings = processor.embed_documents(documents)
        print(f"✅ Embeddings ajoutés aux documents")
        
        # Afficher les métadonnées
        for i, doc in enumerate(documents_with_embeddings):
            print(f"  Document {i+1}: {doc.metadata['category']} - {len(doc.metadata.get('embedding', []))} dimensions")
            
    except Exception as e:
        print(f"⚠️  Erreur lors de l'embedding: {str(e)}")


def main():
    """Fonction principale"""
    
    print("🎯 Système RAG avec Langchain - Exemples complets")
    print("=" * 60)
    
    try:
        # Exemples de base
        basic_langchain_example()
        
        # Exemples avancés
        advanced_rag_chain_example()
        
        # Exemples avec reranking
        reranking_example()
        
        # Exemples multi-fournisseurs
        multi_provider_example()
        
        # Exemples de traitement de documents
        document_processing_example()
        
        print("\n🎉 Tous les exemples Langchain terminés avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        print("💡 Vérifiez votre configuration et vos clés API")


if __name__ == "__main__":
    main()
