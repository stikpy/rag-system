#!/usr/bin/env python3
"""
Script pour corriger la connexion à la base de données Supabase.
"""

import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

def fix_database_connection():
    """Corrige la configuration de la base de données."""
    print("🔧 Correction de la connexion à la base de données...")
    print("=" * 60)
    
    # Vérifier les variables d'environnement
    database_url = os.getenv("DATABASE_URL")
    direct_url = os.getenv("DIRECT_URL")
    
    print(f"📊 DATABASE_URL: {database_url}")
    print(f"📊 DIRECT_URL: {direct_url}")
    
    if not database_url or "your_" in database_url or "password" in database_url:
        print("❌ DATABASE_URL n'est pas configurée correctement")
        print("🔧 Veuillez configurer les vraies valeurs dans .env.local")
        return False
    
    if not direct_url or "your_" in direct_url or "password" in direct_url:
        print("❌ DIRECT_URL n'est pas configurée correctement")
        print("🔧 Veuillez configurer les vraies valeurs dans .env.local")
        return False
    
    # Tester la connexion avec Prisma
    try:
        from prisma import Prisma
        import asyncio
        
        async def test_connection():
            prisma = Prisma()
            try:
                await prisma.connect()
                print("✅ Connexion à la base de données réussie!")
                
                # Test simple
                result = await prisma.query_raw("SELECT 1 as test;")
                print(f"📊 Test de requête: {result}")
                
                await prisma.disconnect()
                return True
            except Exception as e:
                print(f"❌ Erreur de connexion: {e}")
                return False
        
        success = asyncio.run(test_connection())
        return success
        
    except ImportError as e:
        print(f"❌ Erreur d'import Prisma: {e}")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

def show_config_instructions():
    """Affiche les instructions de configuration."""
    print("\n📋 Instructions de configuration:")
    print("=" * 40)
    print("1. Ouvrez votre projet Supabase")
    print("2. Allez dans Settings > Database")
    print("3. Copiez les informations de connexion:")
    print("   - Host: aws-1-eu-west-3.pooler.supabase.com")
    print("   - Database: postgres")
    print("   - Username: postgres")
    print("   - Password: [votre mot de passe]")
    print("4. Mettez à jour .env.local avec:")
    print("   DATABASE_URL=\"postgresql://postgres:[password]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres?pgbouncer=true\"")
    print("   DIRECT_URL=\"postgresql://postgres:[password]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres\"")

if __name__ == "__main__":
    success = fix_database_connection()
    if not success:
        show_config_instructions()
        sys.exit(1)
    else:
        print("\n🎉 Configuration de la base de données correcte!")
