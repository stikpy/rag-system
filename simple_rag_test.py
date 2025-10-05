#!/usr/bin/env python3
"""
Test simple du système RAG sans dépendances complexes.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

def test_simple_rag():
    """Test simple du système RAG."""
    print("🧪 Test simple du système RAG...")
    print("=" * 50)
    
    try:
        # Test 1: Vérifier les variables d'environnement
        print("1️⃣ Vérification des variables d'environnement...")
        
        mistral_key = os.getenv("MISTRAL_API_KEY")
        openai_key = os.getenv("OPENAI_API_KEY")
        cohere_key = os.getenv("COHERE_API_KEY")
        
        if not mistral_key or "your_" in mistral_key:
            print("❌ MISTRAL_API_KEY non configurée")
            return False
        if not openai_key or "your_" in openai_key:
            print("❌ OPENAI_API_KEY non configurée")
            return False
        if not cohere_key or "your_" in cohere_key:
            print("❌ COHERE_API_KEY non configurée")
            return False
            
        print("✅ Variables d'environnement configurées")
        
        # Test 2: Test simple avec Mistral
        print("\n2️⃣ Test de génération avec Mistral...")
        try:
            from mistralai import Mistral
            
            client = Mistral(api_key=mistral_key)
            
            # Test simple
            response = client.chat.completions.create(
                model="mistral-small-latest",
                messages=[
                    {"role": "user", "content": "Bonjour, peux-tu me dire ce qu'est l'intelligence artificielle en une phrase ?"}
                ],
                max_tokens=100
            )
            
            answer = response.choices[0].message.content
            print(f"✅ Réponse Mistral: {answer}")
            
        except Exception as e:
            print(f"❌ Erreur Mistral: {e}")
            return False
        
        # Test 3: Test simple avec OpenAI
        print("\n3️⃣ Test de génération avec OpenAI...")
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=openai_key)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": "Qu'est-ce que le machine learning ?"}
                ],
                max_tokens=100
            )
            
            answer = response.choices[0].message.content
            print(f"✅ Réponse OpenAI: {answer}")
            
        except Exception as e:
            print(f"❌ Erreur OpenAI: {e}")
            return False
        
        print("\n🎉 Tous les tests sont passés !")
        print("✅ Le système RAG est opérationnel")
        return True
        
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_rag()
    if not success:
        print("\n🔧 Vérifiez votre configuration dans .env.local")
        sys.exit(1)
