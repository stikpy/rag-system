#!/usr/bin/env python3
"""
Script pour tester la connexion à Supabase avec différents mots de passe.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from prisma import Prisma

async def test_connection(password: str, connection_type: str = "pooler"):
    """Teste une connexion avec un mot de passe donné."""
    try:
        if connection_type == "pooler":
            # Connexion via pooler (port 6543)
            database_url = f"postgresql://postgres.nlunnxppbraflzyublfg:{password}@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
        else:
            # Connexion directe (port 5432)
            database_url = f"postgresql://postgres.nlunnxppbraflzyublfg:{password}@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
        
        print(f"\n🔍 Test de connexion avec le mot de passe: {password}")
        print(f"📡 Type de connexion: {connection_type}")
        print(f"🔗 URL: {database_url}")
        
        # Définir la variable d'environnement
        os.environ["DATABASE_URL"] = database_url
        
        # Initialiser Prisma
        prisma = Prisma()
        
        # Tenter de se connecter
        await prisma.connect()
        
        # Test simple de requête
        result = await prisma.query_raw("SELECT 1 as test")
        print(f"✅ Connexion réussie! Résultat du test: {result}")
        
        # Fermer la connexion
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Échec de la connexion: {e}")
        return False

async def main():
    """Fonction principale pour tester les connexions."""
    passwords = ["1Arene2Folie", "1Arene2Folie!"]
    connection_types = ["pooler", "direct"]
    
    print("🚀 Test des connexions Supabase")
    print("=" * 50)
    
    for password in passwords:
        for conn_type in connection_types:
            success = await test_connection(password, conn_type)
            if success:
                print(f"\n🎉 Connexion réussie avec le mot de passe: {password}")
                print(f"📊 Type de connexion: {conn_type}")
                return
    
    print("\n❌ Aucune connexion n'a réussi avec les mots de passe fournis.")

if __name__ == "__main__":
    asyncio.run(main())
