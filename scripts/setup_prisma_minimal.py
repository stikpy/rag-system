#!/usr/bin/env python3
"""
Configuration Prisma minimale avec Supabase
==========================================

Ce script configure Prisma avec Supabase de manière minimale.
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_minimal_schema():
    """Configure le schéma Prisma minimal"""
    print("🔧 Configuration du schéma Prisma minimal...")
    
    # Copier le schéma minimal
    minimal_schema = Path("prisma/schema_minimal.prisma")
    main_schema = Path("prisma/schema.prisma")
    
    if minimal_schema.exists():
        # Remplacer le schéma principal par le schéma minimal
        with open(minimal_schema, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(main_schema, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Schéma Prisma minimal configuré")
        return True
    else:
        print("❌ Schéma minimal non trouvé")
        return False

def generate_client():
    """Génère le client Prisma"""
    print("🔧 Génération du client Prisma...")
    try:
        result = subprocess.run(["npx", "prisma", "generate"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Client Prisma généré")
            return True
        else:
            print(f"❌ Erreur lors de la génération: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

def push_schema():
    """Applique le schéma à la base de données"""
    print("📊 Application du schéma à la base de données...")
    try:
        result = subprocess.run(["npx", "prisma", "db", "push"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Schéma appliqué à la base de données")
            return True
        else:
            print(f"❌ Erreur lors de l'application: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False

def test_connection():
    """Teste la connexion"""
    print("🧪 Test de la connexion...")
    try:
        result = subprocess.run(["npx", "prisma", "db", "pull"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connexion testée avec succès")
            return True
        else:
            print(f"❌ Erreur lors du test: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def create_test_script():
    """Crée un script de test minimal"""
    print("🧪 Création du script de test minimal...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test minimal de Prisma avec Supabase
===================================
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

async def test_prisma():
    """Test minimal de Prisma"""
    try:
        from prisma import Prisma
        
        prisma = Prisma()
        await prisma.connect()
        
        # Test simple
        documents = await prisma.document.find_many()
        print(f"✅ Connexion Prisma réussie")
        print(f"📊 Documents trouvés: {len(documents)}")
        
        # Test de création d'un document
        print("📄 Test de création d'un document...")
        document = await prisma.document.create({
            "content": "Test document for RAG system",
            "metadata": {"test": True}
        })
        print(f"✅ Document créé: {document.id}")
        
        # Test de création d'un chunk
        print("📝 Test de création d'un chunk...")
        chunk = await prisma.documentchunk.create({
            "documentId": document.id,
            "content": "Test chunk content",
            "chunkIndex": 0,
            "metadata": {"chunk_type": "test"}
        })
        print(f"✅ Chunk créé: {chunk.id}")
        
        # Test de création d'une requête
        print("❓ Test de création d'une requête...")
        query = await prisma.query.create({
            "query": "What is RAG?",
            "response": "RAG is Retrieval-Augmented Generation",
            "metadata": {"test": True}
        })
        print(f"✅ Requête créée: {query.id}")
        
        await prisma.disconnect()
        print("🎉 Tous les tests sont passés avec succès !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_prisma())
    sys.exit(0 if success else 1)
'''
    
    test_file = Path("scripts/test_prisma_minimal.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # Rendre le script exécutable
    test_file.chmod(0o755)
    
    print("✅ Script de test créé: scripts/test_prisma_minimal.py")
    return True

def main():
    """Fonction principale"""
    print("🗄️ Configuration Prisma minimale avec Supabase")
    print("=" * 60)
    
    # Configurer le schéma minimal
    if not setup_minimal_schema():
        return False
    
    # Générer le client
    if not generate_client():
        return False
    
    # Appliquer le schéma
    if not push_schema():
        return False
    
    # Tester la connexion
    if not test_connection():
        return False
    
    # Créer le script de test
    if not create_test_script():
        return False
    
    print("\n🎉 Configuration Prisma minimale terminée !")
    print("\n📋 Prochaines étapes :")
    print("1. python scripts/test_prisma_minimal.py")
    print("2. python examples/basic_rag_example.py")
    print("3. Consultez docs/PRISMA_SUPABASE_SETUP.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
