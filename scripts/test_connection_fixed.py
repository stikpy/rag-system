#!/usr/bin/env python3
"""
Test de connexion corrigé à la base de données Supabase
======================================================

Ce script teste la connexion avec les URLs corrigées.
"""

import os
import sys
import psycopg2
from pathlib import Path

def load_env_variables():
    """Charge les variables d'environnement depuis .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Nettoyer les guillemets
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
    
    print("✅ Variables d'environnement chargées")
    return True

def fix_database_urls():
    """Corrige les URLs de base de données"""
    print("🔧 Correction des URLs de base de données...")
    
    # Récupérer les variables
    database_url = os.getenv('DATABASE_URL')
    direct_url = os.getenv('DIRECT_URL')
    
    if not database_url or not direct_url:
        print("❌ Variables d'environnement manquantes")
        return None, None
    
    # Corriger DATABASE_URL (enlever pgbouncer=true)
    if 'pgbouncer=true' in database_url:
        database_url_fixed = database_url.replace('?pgbouncer=true', '')
    else:
        database_url_fixed = database_url
    
    # Corriger DIRECT_URL (s'assurer que c'est le port 5432)
    if ':6543/' in direct_url:
        direct_url_fixed = direct_url.replace(':6543/', ':5432/')
    else:
        direct_url_fixed = direct_url
    
    print(f"📊 DATABASE_URL corrigée: {database_url_fixed[:50]}...")
    print(f"📊 DIRECT_URL corrigée: {direct_url_fixed[:50]}...")
    
    return database_url_fixed, direct_url_fixed

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")
    
    # Corriger les URLs
    database_url_fixed, direct_url_fixed = fix_database_urls()
    if not database_url_fixed or not direct_url_fixed:
        return False
    
    # Test avec DATABASE_URL (connection pooling)
    print("\n🔗 Test avec DATABASE_URL (connection pooling)...")
    try:
        conn = psycopg2.connect(database_url_fixed)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion DATABASE_URL réussie")
        print(f"📊 Version PostgreSQL: {version[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur DATABASE_URL: {e}")
        return False
    
    # Test avec DIRECT_URL (connexion directe)
    print("\n🔗 Test avec DIRECT_URL (connexion directe)...")
    try:
        conn = psycopg2.connect(direct_url_fixed)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion DIRECT_URL réussie")
        print(f"📊 Version PostgreSQL: {version[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur DIRECT_URL: {e}")
        return False
    
    return True

def test_prisma_connection():
    """Teste la connexion Prisma"""
    print("\n🔧 Test de connexion Prisma...")
    
    try:
        import subprocess
        
        # Test avec npx prisma db pull
        result = subprocess.run(["npx", "prisma", "db", "pull"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connexion Prisma réussie")
            return True
        else:
            print(f"❌ Erreur Prisma: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test Prisma: {e}")
        return False

def create_fixed_env_file():
    """Crée un fichier .env corrigé"""
    print("\n📝 Création du fichier .env corrigé...")
    
    # Lire le fichier .env actuel
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corriger les URLs
    content_fixed = content.replace('?pgbouncer=true', '')
    
    # Créer le fichier corrigé
    with open(".env.fixed", 'w', encoding='utf-8') as f:
        f.write(content_fixed)
    
    print("✅ Fichier .env corrigé créé: .env.fixed")
    return True

def main():
    """Fonction principale"""
    print("🔍 Test de connexion corrigé à la base de données Supabase")
    print("=" * 70)
    
    # Charger les variables d'environnement
    if not load_env_variables():
        return False
    
    # Tester la connexion à la base de données
    if not test_database_connection():
        print("\n❌ Test de connexion échoué")
        print("💡 Vérifiez vos identifiants de base de données")
        return False
    
    # Tester la connexion Prisma
    if not test_prisma_connection():
        print("\n⚠️  Connexion Prisma échouée")
        print("💡 Vérifiez la configuration Prisma")
        return False
    
    # Créer le fichier .env corrigé
    if not create_fixed_env_file():
        return False
    
    print("\n🎉 Tests de connexion terminés avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. npx prisma db push")
    print("2. npx prisma studio")
    print("3. python examples/basic_rag_example.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
