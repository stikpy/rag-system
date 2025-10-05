#!/usr/bin/env python3
"""
Script de mise à jour du mot de passe Supabase
============================================

Ce script vous aide à mettre à jour le mot de passe dans le fichier .env.
"""

import os
import sys
from pathlib import Path

def update_password():
    """Met à jour le mot de passe dans le fichier .env"""
    print("🔑 Mise à jour du mot de passe Supabase")
    print("=" * 50)
    
    # Demander le nouveau mot de passe
    new_password = input("Entrez le nouveau mot de passe Supabase: ").strip()
    
    if not new_password:
        print("❌ Mot de passe vide")
        return False
    
    # Lire le fichier .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer le mot de passe dans les URLs
    content_updated = content.replace('[1Arene2Folie]', new_password)
    
    # Écrire le fichier mis à jour
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content_updated)
    
    print("✅ Mot de passe mis à jour dans le fichier .env")
    return True

def test_connection():
    """Teste la connexion avec le nouveau mot de passe"""
    print("\n🧪 Test de la connexion...")
    
    try:
        import subprocess
        
        # Test avec npx prisma db pull
        result = subprocess.run(["npx", "prisma", "db", "pull"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connexion réussie !")
            return True
        else:
            print(f"❌ Erreur de connexion: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔑 Script de mise à jour du mot de passe Supabase")
    print("=" * 60)
    
    # Mettre à jour le mot de passe
    if not update_password():
        return False
    
    # Tester la connexion
    if not test_connection():
        print("\n❌ Test de connexion échoué")
        print("💡 Vérifiez que le mot de passe est correct")
        return False
    
    print("\n🎉 Configuration terminée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. npx prisma db push")
    print("2. npx prisma studio")
    print("3. python examples/basic_rag_example.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
