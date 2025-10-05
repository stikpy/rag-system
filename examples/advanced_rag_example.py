"""
Exemple avancé du système RAG
============================

Cet exemple montre des fonctionnalités avancées :
- Reranking hybride
- Traitement par lots
- Gestion des métadonnées
- Optimisation des performances
"""

import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.core import RAGSystem
from rag.embeddings import HybridEmbeddingProvider, EmbeddingManager
from rag.retrieval import HybridReranker
from rag.ocr import DocumentOCRProcessor
from rag.utils import TextProcessor, create_splitter
from rag.utils.config import config


def advanced_rag_setup():
    """Configuration avancée du système RAG"""
    
    print("🚀 Configuration avancée du système RAG...")
    
    # 1. Fournisseur d'embeddings hybride
    hybrid_embedding = HybridEmbeddingProvider(
        primary_provider="mistral"
    )
    
    # 2. Gestionnaire d'embeddings avec cache
    embedding_manager = EmbeddingManager(hybrid_embedding)
    
    # 3. Reranker hybride
    hybrid_reranker = HybridReranker()
    
    # 4. Processeur de texte avancé
    advanced_splitter = create_splitter("sentence", chunk_size=512, chunk_overlap=100)
    text_processor = TextProcessor(splitter=advanced_splitter)
    
    # 5. Processeur OCR avancé
    ocr_processor = DocumentOCRProcessor()
    
    # 6. Système RAG complet
    rag_system = RAGSystem(
        embedding_provider=embedding_manager,
        reranker=hybrid_reranker,
        text_processor=text_processor,
        ocr_processor=ocr_processor.ocr_processor,
        generation_provider="mistral"
    )
    
    return rag_system


def batch_document_processing(rag_system: RAGSystem):
    """Traitement par lots de documents"""
    
    print("\n📚 Traitement par lots de documents...")
    
    # Documents de test
    documents = [
        {
            "content": "L'intelligence artificielle transforme de nombreux secteurs d'activité. Elle permet d'automatiser des tâches complexes et d'améliorer la prise de décision.",
            "metadata": {"category": "technologie", "language": "fr", "source": "article_1"}
        },
        {
            "content": "Le machine learning utilise des algorithmes pour apprendre à partir de données. Il est particulièrement efficace pour la reconnaissance d'images et le traitement du langage naturel.",
            "metadata": {"category": "technologie", "language": "fr", "source": "article_2"}
        },
        {
            "content": "Les réseaux de neurones profonds ont révolutionné l'IA. Ils permettent de résoudre des problèmes qui étaient auparavant impossibles à traiter.",
            "metadata": {"category": "technologie", "language": "fr", "source": "article_3"}
        },
        {
            "content": "L'éthique de l'IA est un enjeu majeur. Il faut s'assurer que les systèmes d'IA sont équitables, transparents et respectueux de la vie privée.",
            "metadata": {"category": "éthique", "language": "fr", "source": "article_4"}
        },
        {
            "content": "L'IA générative comme ChatGPT peut créer du contenu textuel de qualité. Elle ouvre de nouvelles possibilités créatives et professionnelles.",
            "metadata": {"category": "applications", "language": "fr", "source": "article_5"}
        }
    ]
    
    # Ajouter les documents
    start_time = time.time()
    document_ids = rag_system.add_documents(documents)
    processing_time = time.time() - start_time
    
    print(f"✅ {len(document_ids)} documents traités en {processing_time:.2f}s")
    return document_ids


def advanced_querying(rag_system: RAGSystem):
    """Requêtes avancées avec différents paramètres"""
    
    print("\n🔍 Requêtes avancées...")
    
    queries = [
        {
            "query": "Quels sont les avantages de l'intelligence artificielle ?",
            "top_k": 3,
            "use_reranking": True
        },
        {
            "query": "Comment fonctionne le machine learning ?",
            "top_k": 2,
            "use_reranking": False
        },
        {
            "query": "Quels sont les enjeux éthiques de l'IA ?",
            "top_k": 2,
            "use_reranking": True
        }
    ]
    
    for i, query_config in enumerate(queries, 1):
        print(f"\n📝 Requête {i}: {query_config['query']}")
        
        try:
            start_time = time.time()
            
            # Récupération avec paramètres
            documents = rag_system.retrieve_documents(
                query_config['query'],
                top_k=query_config['top_k'],
                use_reranking=query_config['use_reranking']
            )
            
            retrieval_time = time.time() - start_time
            
            print(f"📚 {len(documents)} documents récupérés en {retrieval_time:.2f}s")
            
            # Afficher les scores de similarité
            for j, doc in enumerate(documents):
                score = doc.get('similarity_score', doc.get('rerank_score', 0))
                source = doc.get('source', 'unknown')
                print(f"  📄 Document {j+1}: {source} (score: {score:.3f})")
            
            # Génération de réponse
            start_time = time.time()
            response = rag_system.generate_response(query_config['query'], documents)
            generation_time = time.time() - start_time
            
            print(f"💬 Réponse ({generation_time:.2f}s): {response}")
            
        except Exception as e:
            print(f"❌ Erreur lors de la requête {i}: {str(e)}")


def performance_analysis(rag_system: RAGSystem):
    """Analyse des performances du système"""
    
    print("\n📊 Analyse des performances...")
    
    # Test de performance avec différentes tailles de requêtes
    test_queries = [
        "Qu'est-ce que l'IA ?",
        "Expliquez le machine learning et ses applications",
        "Quels sont les défis éthiques de l'intelligence artificielle dans la société moderne ?"
    ]
    
    results = []
    
    for query in test_queries:
        start_time = time.time()
        
        try:
            # Récupération
            documents = rag_system.retrieve_documents(query, top_k=3)
            retrieval_time = time.time() - start_time
        
            # Génération
            start_gen = time.time()
            response = rag_system.generate_response(query, documents)
            generation_time = time.time() - start_gen
            
            total_time = time.time() - start_time
            
            results.append({
                'query': query,
                'query_length': len(query),
                'retrieval_time': retrieval_time,
                'generation_time': generation_time,
                'total_time': total_time,
                'response_length': len(response),
                'num_documents': len(documents)
            })
            
        except Exception as e:
            print(f"❌ Erreur lors du test de performance: {str(e)}")
    
    # Afficher les résultats
    print("\n📈 Résultats de performance:")
    print(f"{'Requête':<20} {'Temps total':<12} {'Récupération':<12} {'Génération':<12} {'Documents':<10}")
    print("-" * 80)
    
    for result in results:
        print(f"{result['query'][:18]:<20} "
              f"{result['total_time']:.2f}s{'':<8} "
              f"{result['retrieval_time']:.2f}s{'':<8} "
              f"{result['generation_time']:.2f}s{'':<8} "
              f"{result['num_documents']:<10}")


def metadata_filtering_example(rag_system: RAGSystem):
    """Exemple de filtrage par métadonnées"""
    
    print("\n🔍 Exemple de filtrage par métadonnées...")
    
    # Simuler un récupérateur avec filtres
    if hasattr(rag_system.vector_retriever, 'search_similar'):
        try:
            # Recherche avec filtre par catégorie
            documents = rag_system.vector_retriever.search_similar(
                "intelligence artificielle",
                top_k=5,
                filters={"metadata->category": "technologie"}
            )
            
            print(f"📚 {len(documents)} documents trouvés dans la catégorie 'technologie'")
            
            for doc in documents:
                metadata = doc.get('metadata', {})
                category = metadata.get('category', 'unknown')
                source = metadata.get('source', 'unknown')
                print(f"  📄 {source} (catégorie: {category})")
                
        except Exception as e:
            print(f"ℹ️  Filtrage par métadonnées non disponible: {str(e)}")


def main():
    """Fonction principale de l'exemple avancé"""
    
    print("🎯 Système RAG Avancé - Mistral, OpenAI, Supabase, Cohere")
    print("=" * 70)
    
    try:
        # Configuration avancée
        rag_system = advanced_rag_setup()
        print("✅ Système RAG avancé initialisé")
        
        # Traitement par lots
        document_ids = batch_document_processing(rag_system)
        
        # Requêtes avancées
        advanced_querying(rag_system)
        
        # Analyse des performances
        performance_analysis(rag_system)
        
        # Filtrage par métadonnées
        metadata_filtering_example(rag_system)
        
        # Informations du système
        print("\n📊 Informations du système:")
        system_info = rag_system.get_system_info()
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        
        print("\n🎉 Exemple avancé terminé avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        print("💡 Vérifiez votre configuration et vos clés API")


if __name__ == "__main__":
    main()
