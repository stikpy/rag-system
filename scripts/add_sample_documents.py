#!/usr/bin/env python3
"""
Script pour ajouter des documents de test à la base de données RAG.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

from prisma import Prisma

async def add_sample_documents():
    """Ajoute des documents de test à la base de données."""
    try:
        print("📄 Ajout de documents de test à la base de données...")
        print("=" * 60)
        
        # Initialiser Prisma
        prisma = Prisma()
        await prisma.connect()
        
        print("✅ Connexion à la base de données réussie!")
        
        # Documents de test
        sample_documents = [
            {
                "content": "L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des machines capables de simuler l'intelligence humaine. Elle inclut l'apprentissage automatique, le traitement du langage naturel, et la vision par ordinateur.",
                "metadata": {
                    "title": "Introduction à l'Intelligence Artificielle",
                    "type": "documentation",
                    "category": "IA",
                    "source": "sample"
                }
            },
            {
                "content": "Le machine learning est une sous-discipline de l'IA qui permet aux ordinateurs d'apprendre et de s'améliorer automatiquement à partir de l'expérience, sans être explicitement programmés pour chaque tâche.",
                "metadata": {
                    "title": "Machine Learning",
                    "type": "documentation", 
                    "category": "ML",
                    "source": "sample"
                }
            },
            {
                "content": "Les systèmes RAG (Retrieval-Augmented Generation) combinent la recherche d'informations avec la génération de texte pour produire des réponses plus précises et contextuelles.",
                "metadata": {
                    "title": "Systèmes RAG",
                    "type": "documentation",
                    "category": "RAG",
                    "source": "sample"
                }
            },
            {
                "content": "Supabase est une plateforme backend-as-a-service qui fournit une base de données PostgreSQL, l'authentification, et des APIs en temps réel pour les applications modernes.",
                "metadata": {
                    "title": "Supabase Platform",
                    "type": "documentation",
                    "category": "Backend",
                    "source": "sample"
                }
            },
            {
                "content": "Les embeddings vectoriels sont des représentations numériques de texte qui permettent de mesurer la similarité sémantique entre différents contenus. Ils sont essentiels pour la recherche vectorielle.",
                "metadata": {
                    "title": "Embeddings Vectoriels",
                    "type": "documentation",
                    "category": "Vectors",
                    "source": "sample"
                }
            }
        ]
        
        # Ajouter les documents
        added_count = 0
        for doc in sample_documents:
            try:
                # Vérifier si le document existe déjà
                existing = await prisma.query_raw(
                    "SELECT id FROM documents WHERE content = $1",
                    doc["content"]
                )
                
                if not existing:
                    await prisma.query_raw(
                        "INSERT INTO documents (content, metadata) VALUES ($1, $2)",
                        doc["content"],
                        doc["metadata"]
                    )
                    added_count += 1
                    print(f"✅ Document ajouté: {doc['metadata']['title']}")
                else:
                    print(f"⚠️  Document déjà existant: {doc['metadata']['title']}")
                    
            except Exception as e:
                print(f"❌ Erreur lors de l'ajout du document {doc['metadata']['title']}: {e}")
        
        # Vérifier le nombre total de documents
        total_docs = await prisma.query_raw("SELECT COUNT(*) as count FROM documents")
        print(f"\n📊 Total de documents dans la base: {total_docs[0]['count']}")
        
        # Afficher quelques exemples
        print("\n📋 Exemples de documents:")
        print("-" * 40)
        
        examples = await prisma.query_raw(
            "SELECT content, metadata FROM documents ORDER BY id DESC LIMIT 3"
        )
        
        for i, example in enumerate(examples, 1):
            title = example['metadata'].get('title', 'Sans titre') if example['metadata'] else 'Sans titre'
            content_preview = example['content'][:100] + "..." if len(example['content']) > 100 else example['content']
            print(f"{i}. {title}")
            print(f"   {content_preview}")
            print()
        
        await prisma.disconnect()
        print(f"✅ {added_count} nouveaux documents ajoutés avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de l'ajout des documents: {e}")
        return False
    
    return True

async def main():
    """Fonction principale."""
    success = await add_sample_documents()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
