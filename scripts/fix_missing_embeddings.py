#!/usr/bin/env python3
"""
Script pour générer les embeddings manquants dans la table documents.
"""

import os
import sys
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

load_dotenv('.env.local')

async def fix_embeddings():
    """Génère les embeddings manquants pour les documents."""
    print("🔧 Correction des embeddings manquants...")
    print("=" * 60)
    
    try:
        from prisma import Prisma
        from rag.embeddings import MistralEmbeddingProvider
        
        # Connexion à la base de données
        prisma = Prisma()
        await prisma.connect()
        print("✅ Connexion à la base de données réussie")
        
        # Récupérer les documents sans embeddings
        documents_without_embeddings = await prisma.query_raw("""
            SELECT id, content, metadata 
            FROM documents 
            WHERE embedding IS NULL
        """)
        
        print(f"📊 Documents sans embeddings trouvés: {len(documents_without_embeddings)}")
        
        if not documents_without_embeddings:
            print("✅ Tous les documents ont déjà des embeddings!")
            await prisma.disconnect()
            return
        
        # Initialiser le provider d'embeddings (OpenAI)
        from rag.embeddings import OpenAIEmbeddingProvider
        embedding_provider = OpenAIEmbeddingProvider()
        print("✅ Provider d'embeddings OpenAI initialisé")
        
        # Générer les embeddings pour chaque document
        for doc in documents_without_embeddings:
            doc_id = doc['id']
            content = doc['content']
            
            print(f"🔄 Génération d'embedding pour le document {doc_id}...")
            
            try:
                # Générer l'embedding
                embedding = embedding_provider.embed_text(content)
                print(f"✅ Embedding généré (dimension: {len(embedding)})")
                
                # Mettre à jour la base de données
                await prisma.execute_raw("""
                    UPDATE documents 
                    SET embedding = $1 
                    WHERE id = $2
                """, embedding, doc_id)
                
                print(f"✅ Document {doc_id} mis à jour avec succès")
                
            except Exception as e:
                print(f"❌ Erreur pour le document {doc_id}: {e}")
                continue
        
        # Vérifier le résultat
        final_count = await prisma.query_raw("SELECT COUNT(*) as count FROM documents WHERE embedding IS NOT NULL")
        total_count = await prisma.query_raw("SELECT COUNT(*) as count FROM documents")
        
        print(f"\n📊 Résultat final:")
        print(f"   • Documents avec embeddings: {final_count[0]['count']}")
        print(f"   • Total documents: {total_count[0]['count']}")
        
        await prisma.disconnect()
        print("\n🎉 Correction des embeddings terminée!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la correction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(fix_embeddings())
