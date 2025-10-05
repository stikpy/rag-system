#!/usr/bin/env python3
"""
Script de configuration Supabase simple
=======================================

Ce script configure Supabase de manière interactive et simple.
"""

import os
import sys
from pathlib import Path

def main():
    """Configuration Supabase simple"""
    print("🔑 Configuration Supabase - Nouveau Format")
    print("=" * 50)
    
    # Vérifier si le fichier .env existe
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ Fichier .env non trouvé")
        print("💡 Créez d'abord le fichier .env : cp env.example .env")
        return False
    
    print("✅ Fichier .env trouvé")
    
    # Demander les informations Supabase
    print("\n📋 Configuration Supabase")
    print("-" * 30)
    print("1. Allez sur https://supabase.com/dashboard")
    print("2. Sélectionnez votre projet")
    print("3. Allez dans 'Settings' > 'API Keys'")
    print("4. Copiez les valeurs suivantes :")
    print()
    
    url = input("URL Supabase (https://xxx.supabase.co): ").strip()
    if not url:
        print("❌ URL obligatoire")
        return False
    
    publishable_key = input("Publishable Key (sb_publishable_xxx): ").strip()
    if not publishable_key:
        print("❌ Publishable Key obligatoire")
        return False
    
    secret_key = input("Secret Key (sb_secret_xxx): ").strip()
    if not secret_key:
        print("❌ Secret Key obligatoire")
        return False
    
    # Mettre à jour le fichier .env
    print("\n📝 Mise à jour du fichier .env...")
    
    try:
        # Lire le fichier actuel
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les valeurs
        replacements = {
            "your_supabase_url_here": url,
            "your_supabase_anon_key_here": publishable_key,
            "your_supabase_service_role_key_here": secret_key,
        }
        
        # Appliquer les remplacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Ajouter le nouveau format si pas présent
        if "SUPABASE_PUBLISHABLE_KEY" not in content:
            # Ajouter après SUPABASE_URL
            content = content.replace(
                f"SUPABASE_URL={url}",
                f"SUPABASE_URL={url}\nSUPABASE_PUBLISHABLE_KEY={publishable_key}\nSUPABASE_SECRET_KEY={secret_key}"
            )
        
        # Écrire le fichier mis à jour
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier .env mis à jour")
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour : {e}")
        return False
    
    # Test de la configuration
    print("\n🧪 Test de la configuration...")
    
    try:
        from supabase import create_client
        
        # Test de connexion
        supabase = create_client(url, publishable_key, secret_key)
        
        # Test simple
        response = supabase.table("documents").select("id").limit(1).execute()
        
        print("✅ Connexion Supabase réussie !")
        print(f"📋 Réponse: {response}")
        
        print("\n🎉 Configuration Supabase terminée avec succès !")
        print("\n🚀 Prochaines étapes :")
        print("1. python3 examples/basic_rag_example.py")
        print("2. python3 examples/advanced_rag_example.py")
        print("3. Consultez SUPABASE_SETUP_GUIDE.md pour plus d'informations")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        print("\n💡 Vérifiez :")
        print("- L'URL Supabase est correcte")
        print("- Les clés API sont correctes")
        print("- Le projet Supabase est actif")
        print("- La table 'documents' existe")
        
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
