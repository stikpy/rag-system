#!/usr/bin/env python3
"""
Script final pour tester la connexion Supabase avec Prisma.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from prisma import Prisma

async def test_final_connection():
    """Teste la connexion finale avec Prisma."""
    try:
        print("🚀 Test final de la connexion Supabase avec Prisma")
        print("=" * 60)
        
        # Charger les variables d'environnement
        from dotenv import load_dotenv
        load_dotenv('.env.local')
        
        # Vérifier que DATABASE_URL est définie
        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            print("❌ DATABASE_URL n'est pas définie dans .env.local")
            return False
        
        print(f"📡 URL de base de données: {database_url}")
        
        # Initialiser Prisma
        prisma = Prisma()
        
        # Se connecter
        await prisma.connect()
        print("✅ Connexion à la base de données réussie!")
        
        # Test de requête simple
        result = await prisma.query_raw("SELECT version() as version")
        print(f"📊 Version PostgreSQL: {result[0]['version']}")
        
        # Test de création d'une table si elle n'existe pas
        await prisma.query_raw("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        print("✅ Table de test créée/vérifiée")
        
        # Test d'insertion
        await prisma.query_raw("""
            INSERT INTO test_table (name) VALUES ('Test RAG System')
            ON CONFLICT DO NOTHING
        """)
        print("✅ Insertion de test réussie")
        
        # Test de sélection
        result = await prisma.query_raw("SELECT * FROM test_table LIMIT 5")
        print(f"📋 Données récupérées: {len(result)} enregistrements")
        for row in result:
            print(f"   - ID: {row['id']}, Name: {row['name']}, Created: {row['created_at']}")
        
        # Fermer la connexion
        await prisma.disconnect()
        print("✅ Connexion fermée proprement")
        
        print("\n🎉 Tous les tests sont passés avec succès!")
        print("🔧 Prisma Studio est disponible sur http://localhost:5555")
        print("📚 Votre système RAG est prêt à être utilisé!")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale."""
    success = await test_final_connection()
    if success:
        print("\n✅ Configuration terminée avec succès!")
    else:
        print("\n❌ Des problèmes ont été détectés.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
