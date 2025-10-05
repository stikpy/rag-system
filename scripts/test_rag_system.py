#!/usr/bin/env python3
"""
Script de test pour vérifier que le système RAG fonctionne correctement.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

def test_rag_system():
    """Test du système RAG."""
    try:
        print("🧪 Test du système RAG...")
        print("=" * 50)
        
        # Test 1: Import des modules
        print("1️⃣ Test des imports...")
        try:
            from rag.core.rag_system import RAGSystem
            from rag.retrieval.vector_retriever import VectorRetriever
            from rag.retrieval.reranker import CohereReranker
            from rag.utils.config import config
            print("✅ Imports réussis")
        except ImportError as e:
            print(f"❌ Erreur d'import: {e}")
            return False
        
        # Test 2: Initialisation du système RAG
        print("\n2️⃣ Test d'initialisation du système RAG...")
        try:
            rag = RAGSystem()
            print("✅ Système RAG initialisé")
        except Exception as e:
            print(f"❌ Erreur d'initialisation: {e}")
            return False
        
        # Test 3: Test d'une requête simple
        print("\n3️⃣ Test d'une requête...")
        try:
            question = "Qu'est-ce que l'intelligence artificielle ?"
            print(f"Question: {question}")
            
            response = rag.query(question)
            print(f"Réponse: {response}")
            print("✅ Requête traitée avec succès")
            
        except Exception as e:
            print(f"❌ Erreur lors de la requête: {e}")
            return False
        
        print("\n🎉 Tous les tests sont passés !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_system()
    if not success:
        sys.exit(1)
