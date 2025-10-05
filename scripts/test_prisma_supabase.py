#!/usr/bin/env python3
"""
Script de test pour Prisma avec Supabase
========================================

Ce script teste la configuration Prisma.
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.database.prisma_client import PrismaRAGClient, test_prisma_connection

async def test_full_functionality():
    """Test complet de la fonctionnalité Prisma"""
    print("🧪 Test complet de Prisma avec Supabase")
    print("=" * 50)
    
    client = PrismaRAGClient()
    
    try:
        await client.connect()
        print("✅ Connexion établie")
        
        # Test de création d'un document
        print("📄 Test de création d'un document...")
        document = await client.create_document(
            content="Ceci est un test de document pour le système RAG",
            metadata={"type": "test", "language": "fr"}
        )
        print(f"✅ Document créé: {document.id}")
        
        # Test de création d'un chunk
        print("📝 Test de création d'un chunk...")
        chunk = await client.create_document_chunk(
            document_id=document.id,
            content="Chunk de test",
            chunk_index=0,
            metadata={"chunk_type": "test"}
        )
        print(f"✅ Chunk créé: {chunk.id}")
        
        # Test de création d'une requête
        print("❓ Test de création d'une requête...")
        query = await client.create_query(
            query="Qu'est-ce que le RAG ?",
            response="Le RAG est un système de génération augmentée par récupération",
            document_id=document.id,
            chunk_id=chunk.id,
            metadata={"test": True}
        )
        print(f"✅ Requête créée: {query.id}")
        
        # Test de récupération
        print("🔍 Test de récupération...")
        documents = await client.prisma.document.find_many()
        chunks = await client.prisma.documentchunk.find_many()
        queries = await client.prisma.query.find_many()
        
        print(f"📊 Résultats:")
        print(f"  - Documents: {len(documents)}")
        print(f"  - Chunks: {len(chunks)}")
        print(f"  - Requêtes: {len(queries)}")
        
        await client.disconnect()
        print("✅ Test complet réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale"""
    print("🗄️ Test de Prisma avec Supabase")
    print("=" * 40)
    
    # Test de connexion
    if not await test_prisma_connection():
        return False
    
    # Test complet
    if not await test_full_functionality():
        return False
    
    print("\n🎉 Tous les tests sont passés avec succès !")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
