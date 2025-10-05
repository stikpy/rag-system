#!/usr/bin/env python3
"""
Script de vérification des clés API
==================================

Ce script vérifie que toutes les clés API sont correctement configurées
et que les services sont accessibles.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import requests
import time

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def check_env_file():
    """Vérifie que le fichier .env existe"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Fichier .env non trouvé")
        print("💡 Copiez env.example vers .env : cp env.example .env")
        return False
    
    print("✅ Fichier .env trouvé")
    return True

def load_environment():
    """Charge les variables d'environnement"""
    try:
        load_dotenv()
        print("✅ Variables d'environnement chargées")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du chargement des variables : {e}")
        return False

def check_mistral_api():
    """Vérifie la clé API Mistral"""
    api_key = os.getenv("MISTRAL_API_KEY")
    
    if not api_key:
        print("❌ MISTRAL_API_KEY non définie")
        return False
    
    if api_key == "your_mistral_api_key_here":
        print("❌ MISTRAL_API_KEY non configurée (valeur par défaut)")
        return False
    
    # Test de la clé API
    try:
        from mistralai import Mistral
        client = Mistral(api_key=api_key)
        
        # Test simple
        response = client.chat.complete(
            model="mistral-small-latest",
            messages=[{"role": "user", "content": "Test"}]
        )
        
        print("✅ Mistral API fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Mistral API : {e}")
        return False

def check_openai_api():
    """Vérifie la clé API OpenAI"""
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        print("⚠️  OPENAI_API_KEY non définie (optionnel)")
        return True
    
    if api_key == "your_openai_api_key_here":
        print("⚠️  OPENAI_API_KEY non configurée (optionnel)")
        return True
    
    # Test de la clé API
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        
        # Test simple
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=10
        )
        
        print("✅ OpenAI API fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur OpenAI API : {e}")
        return False

def check_cohere_api():
    """Vérifie la clé API Cohere"""
    api_key = os.getenv("COHERE_API_KEY")
    
    if not api_key:
        print("❌ COHERE_API_KEY non définie")
        return False
    
    if api_key == "your_cohere_api_key_here":
        print("❌ COHERE_API_KEY non configurée")
        return False
    
    # Test de la clé API
    try:
        import cohere
        client = cohere.Client(api_key=api_key)
        
        # Test simple
        response = client.embed(
            texts=["Test"],
            model="embed-english-v3.0"
        )
        
        print("✅ Cohere API fonctionnelle")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Cohere API : {e}")
        return False

def check_supabase_config():
    """Vérifie la configuration Supabase"""
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        print("❌ Configuration Supabase incomplète")
        return False
    
    if url == "your_supabase_url_here" or key == "your_supabase_anon_key_here":
        print("❌ Configuration Supabase non configurée")
        return False
    
    # Test de la connexion Supabase
    try:
        from supabase import create_client
        supabase = create_client(url, key)
        
        # Test simple
        response = supabase.table("documents").select("id").limit(1).execute()
        
        print("✅ Supabase connecté")
        return True
        
    except Exception as e:
        print(f"❌ Erreur Supabase : {e}")
        print("💡 Vérifiez que la table 'documents' existe")
        return False

def check_optional_services():
    """Vérifie les services optionnels"""
    print("\n🔍 Vérification des services optionnels...")
    
    # Pinecone
    pinecone_key = os.getenv("PINECONE_API_KEY")
    if pinecone_key and pinecone_key != "your_pinecone_api_key_here":
        print("✅ Pinecone configuré")
    else:
        print("⚠️  Pinecone non configuré (optionnel)")
    
    # Database URL
    db_url = os.getenv("DATABASE_URL")
    if db_url and db_url != "postgresql://user:password@host:port/database":
        print("✅ Database URL configuré")
    else:
        print("⚠️  Database URL non configuré (optionnel)")

def check_system_requirements():
    """Vérifie les prérequis système"""
    print("\n🔍 Vérification des prérequis système...")
    
    # Python version
    python_version = sys.version_info
    if python_version >= (3, 8):
        print(f"✅ Python {python_version.major}.{python_version.minor} OK")
    else:
        print(f"❌ Python {python_version.major}.{python_version.minor} - Version 3.8+ requise")
        return False
    
    # Modules requis
    required_modules = [
        "mistralai", "openai", "cohere", "supabase", 
        "langchain", "prisma", "pytesseract", "easyocr"
    ]
    
    missing_modules = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module} installé")
        except ImportError:
            print(f"❌ {module} manquant")
            missing_modules.append(module)
    
    if missing_modules:
        print(f"\n💡 Installez les modules manquants :")
        print(f"pip install {' '.join(missing_modules)}")
        return False
    
    return True

def main():
    """Fonction principale de vérification"""
    print("🔑 Vérification des clés API du système RAG")
    print("=" * 50)
    
    # Vérifications de base
    if not check_env_file():
        return False
    
    if not load_environment():
        return False
    
    if not check_system_requirements():
        return False
    
    print("\n🔍 Vérification des clés API...")
    
    # Vérifications des services
    results = {
        "mistral": check_mistral_api(),
        "openai": check_openai_api(),
        "cohere": check_cohere_api(),
        "supabase": check_supabase_config()
    }
    
    # Vérifications optionnelles
    check_optional_services()
    
    # Résumé
    print("\n📊 Résumé de la configuration :")
    print("=" * 40)
    
    required_services = ["mistral", "cohere", "supabase"]
    optional_services = ["openai"]
    
    all_required_ok = all(results[service] for service in required_services)
    
    for service in required_services:
        status = "✅" if results[service] else "❌"
        print(f"{status} {service.upper()} : {'OK' if results[service] else 'ERREUR'}")
    
    for service in optional_services:
        status = "✅" if results[service] else "⚠️"
        print(f"{status} {service.upper()} : {'OK' if results[service] else 'OPTIONNEL'}")
    
    if all_required_ok:
        print("\n🎉 Configuration complète ! Vous pouvez utiliser le système RAG.")
        print("\n🚀 Pour tester le système :")
        print("python examples/basic_rag_example.py")
    else:
        print("\n❌ Configuration incomplète. Vérifiez les erreurs ci-dessus.")
        print("\n💡 Consultez docs/API_KEYS_SETUP.md pour plus d'informations.")
    
    return all_required_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
