"""
Exemple d'utilisation basique du système RAG
============================================

Cet exemple montre comment utiliser le système RAG avec :
- Mistral pour les embeddings et la génération
- Supabase comme base de données vectorielle
- Cohere pour le reranking
- OCR pour les documents scannés
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.core import RAGSystem
from rag.embeddings import MistralEmbeddingProvider
from rag.retrieval import VectorRetriever, CohereReranker
from rag.ocr import OCRProcessor
from rag.utils import TextProcessor
from rag.utils.config import config


def main():
    """Exemple principal d'utilisation du système RAG"""
    
    print("🚀 Initialisation du système RAG...")
    
    # 1. Initialiser les composants
    embedding_provider = MistralEmbeddingProvider()
    vector_retriever = VectorRetriever(embedding_provider=embedding_provider)
    reranker = CohereReranker()
    ocr_processor = OCRProcessor()
    text_processor = TextProcessor()
    
    # 2. Créer le système RAG
    rag_system = RAGSystem(
        embedding_provider=embedding_provider,
        vector_retriever=vector_retriever,
        reranker=reranker,
        text_processor=text_processor,
        ocr_processor=ocr_processor,
        generation_provider="mistral"
    )
    
    print("✅ Système RAG initialisé avec succès")
    
    # 3. Ajouter des documents texte
    print("\n📄 Ajout de documents texte...")
    text_documents = [
        {
            "content": "L'intelligence artificielle est une technologie qui permet aux machines d'apprendre et de prendre des décisions de manière autonome.",
            "metadata": {"title": "Introduction IA", "type": "article"}
        },
        {
            "content": "Le machine learning est une sous-discipline de l'IA qui se concentre sur l'apprentissage automatique à partir de données.",
            "metadata": {"title": "Machine Learning", "type": "article"}
        },
        {
            "content": "Les réseaux de neurones artificiels sont inspirés du fonctionnement du cerveau humain et permettent de résoudre des problèmes complexes.",
            "metadata": {"title": "Réseaux de neurones", "type": "article"}
        }
    ]
    
    document_ids = rag_system.add_documents(text_documents)
    print(f"✅ {len(document_ids)} documents texte ajoutés")
    
    # 4. Ajouter des documents avec OCR (si fichiers disponibles)
    print("\n🔍 Traitement de documents avec OCR...")
    # Exemple avec des fichiers (à adapter selon vos fichiers)
    ocr_files = []
    # ocr_files = ["documents/scan.pdf", "documents/image.png"]  # Décommentez si vous avez des fichiers
    
    if ocr_files:
        ocr_document_ids = rag_system.add_documents_with_ocr(ocr_files)
        print(f"✅ {len(ocr_document_ids)} documents OCR ajoutés")
    else:
        print("ℹ️  Aucun fichier OCR à traiter")
    
    # 5. Tester le système avec des requêtes
    print("\n❓ Test du système RAG...")
    
    queries = [
        "Qu'est-ce que l'intelligence artificielle ?",
        "Comment fonctionne le machine learning ?",
        "Expliquez les réseaux de neurones"
    ]
    
    for query in queries:
        print(f"\n🔍 Requête: {query}")
        
        try:
            # Récupérer les documents pertinents
            documents = rag_system.retrieve_documents(query, top_k=2)
            print(f"📚 {len(documents)} documents récupérés")
            
            # Générer une réponse
            response = rag_system.generate_response(query, documents)
            print(f"💬 Réponse: {response}")
            
        except Exception as e:
            print(f"❌ Erreur lors du traitement de la requête: {str(e)}")
    
    # 6. Afficher les informations du système
    print("\n📊 Informations du système:")
    system_info = rag_system.get_system_info()
    for key, value in system_info.items():
        print(f"  {key}: {value}")


def example_with_different_providers():
    """Exemple avec différents fournisseurs"""
    
    print("\n🔄 Exemple avec différents fournisseurs...")
    
    # Système avec OpenAI
    from rag.embeddings import OpenAIEmbeddingProvider
    
    openai_embedding = OpenAIEmbeddingProvider()
    
    rag_system_openai = RAGSystem(
        embedding_provider=openai_embedding,
        generation_provider="openai"
    )
    
    print("✅ Système RAG avec OpenAI initialisé")
    
    # Test avec OpenAI
    try:
        response = rag_system_openai.query("Qu'est-ce que l'IA ?")
        print(f"🤖 Réponse OpenAI: {response['response']}")
    except Exception as e:
        print(f"❌ Erreur avec OpenAI: {str(e)}")


def example_ocr_processing():
    """Exemple de traitement OCR"""
    
    print("\n🔍 Exemple de traitement OCR...")
    
    ocr_processor = OCRProcessor(ocr_engine="hybrid")
    
    # Exemple avec une image (à adapter)
    # image_path = "examples/test_image.png"
    # if os.path.exists(image_path):
    #     result = ocr_processor.extract_text_from_image(image_path)
    #     print(f"📄 Texte extrait: {result['text'][:100]}...")
    #     print(f"🎯 Confiance: {result['confidence']:.2f}")
    # else:
    #     print("ℹ️  Aucune image de test disponible")
    
    print("ℹ️  Placez une image dans examples/ pour tester l'OCR")


if __name__ == "__main__":
    print("🎯 Système RAG avec Mistral, OpenAI, Supabase et Cohere")
    print("=" * 60)
    
    try:
        main()
        example_with_different_providers()
        example_ocr_processing()
        
        print("\n🎉 Exemple terminé avec succès !")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {str(e)}")
        print("💡 Assurez-vous d'avoir configuré vos clés API dans le fichier .env")
