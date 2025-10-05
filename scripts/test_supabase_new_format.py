#!/usr/bin/env python3
"""
Script de test pour le nouveau format des clés API Supabase
==========================================================

Ce script teste la connexion Supabase avec le nouveau format des clés API.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

def test_new_format():
    """Teste le nouveau format des clés API Supabase"""
    print("🔑 Test du nouveau format Supabase")
    print("=" * 40)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier les variables d'environnement
    url = os.getenv("SUPABASE_URL")
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    
    print(f"URL: {url}")
    print(f"Publishable Key: {publishable_key[:20]}..." if publishable_key else "Non définie")
    print(f"Secret Key: {secret_key[:20]}..." if secret_key else "Non définie")
    
    if not url:
        print("❌ SUPABASE_URL non définie")
        return False
    
    if not publishable_key:
        print("❌ SUPABASE_PUBLISHABLE_KEY non définie")
        return False
    
    if not secret_key:
        print("❌ SUPABASE_SECRET_KEY non définie")
        return False
    
    # Test de connexion
    try:
        from supabase import create_client
        
        print("\n🔌 Test de connexion...")
        supabase = create_client(url, publishable_key, secret_key)
        
        # Test simple
        print("📊 Test de la table documents...")
        response = supabase.table("documents").select("id").limit(1).execute()
        
        print("✅ Connexion Supabase réussie (nouveau format)")
        print(f"📋 Réponse: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def test_old_format():
    """Teste l'ancien format des clés API Supabase"""
    print("\n🔑 Test de l'ancien format Supabase")
    print("=" * 40)
    
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier les variables d'environnement
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    print(f"URL: {url}")
    print(f"Key: {key[:20]}..." if key else "Non définie")
    print(f"Service Key: {service_key[:20]}..." if service_key else "Non définie")
    
    if not url or not key:
        print("❌ Configuration ancien format incomplète")
        return False
    
    # Test de connexion
    try:
        from supabase import create_client
        
        print("\n🔌 Test de connexion...")
        supabase = create_client(url, key)
        
        # Test simple
        print("📊 Test de la table documents...")
        response = supabase.table("documents").select("id").limit(1).execute()
        
        print("✅ Connexion Supabase réussie (ancien format)")
        print(f"📋 Réponse: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

def test_vector_retriever():
    """Teste le VectorRetriever avec le nouveau format"""
    print("\n🔍 Test du VectorRetriever")
    print("=" * 40)
    
    try:
        from rag.retrieval.vector_retriever import VectorRetriever
        from rag.embeddings import MistralEmbeddingProvider
        
        print("🔧 Initialisation du VectorRetriever...")
        
        # Test avec le nouveau format
        retriever = VectorRetriever()
        
        print("✅ VectorRetriever initialisé avec succès")
        
        # Test de récupération
        print("🔍 Test de récupération...")
        results = retriever.retrieve("test query", top_k=1)
        
        print(f"✅ Récupération réussie: {len(results)} résultats")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur VectorRetriever : {e}")
        return False

def main():
    """Fonction principale"""
    print("🧪 Test des clés API Supabase")
    print("=" * 50)
    
    # Test du nouveau format
    new_format_ok = test_new_format()
    
    # Test de l'ancien format
    old_format_ok = test_old_format()
    
    # Test du VectorRetriever
    retriever_ok = test_vector_retriever()
    
    # Résumé
    print("\n📊 Résumé des tests:")
    print("=" * 30)
    print(f"🆕 Nouveau format: {'✅' if new_format_ok else '❌'}")
    print(f"🔄 Ancien format: {'✅' if old_format_ok else '❌'}")
    print(f"🔍 VectorRetriever: {'✅' if retriever_ok else '❌'}")
    
    if new_format_ok or old_format_ok:
        print("\n🎉 Configuration Supabase fonctionnelle !")
        if new_format_ok:
            print("💡 Utilisez le nouveau format pour une meilleure sécurité")
        else:
            print("💡 Migrez vers le nouveau format quand possible")
    else:
        print("\n❌ Configuration Supabase incomplète")
        print("💡 Consultez docs/SUPABASE_NEW_API_FORMAT.md")
    
    return new_format_ok or old_format_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
