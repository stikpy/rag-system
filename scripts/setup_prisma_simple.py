#!/usr/bin/env python3
"""
Configuration Prisma simplifiée avec Supabase
=============================================

Ce script configure Prisma avec Supabase de manière simplifiée.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prisma_installed():
    """Vérifie si Prisma est installé"""
    try:
        result = subprocess.run(["npx", "prisma", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Prisma installé")
            return True
    except:
        pass
    
    print("❌ Prisma non installé")
    return False

def install_prisma():
    """Installe Prisma"""
    print("📦 Installation de Prisma...")
    try:
        subprocess.run(["npm", "install", "-g", "prisma"], check=True)
        print("✅ Prisma installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def setup_simple_schema():
    """Configure le schéma Prisma simplifié"""
    print("🔧 Configuration du schéma Prisma simplifié...")
    
    # Copier le schéma simplifié
    simple_schema = Path("prisma/schema_simple.prisma")
    main_schema = Path("prisma/schema.prisma")
    
    if simple_schema.exists():
        # Remplacer le schéma principal par le schéma simplifié
        with open(simple_schema, 'r', encoding='utf-8') as f:
            content = f.read()
        
        with open(main_schema, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Schéma Prisma simplifié configuré")
        return True
    else:
        print("❌ Schéma simplifié non trouvé")
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
    """Crée un script de test simple"""
    print("🧪 Création du script de test...")
    
    test_script = '''#!/usr/bin/env python3
"""
Test simple de Prisma avec Supabase
==================================
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

async def test_prisma():
    """Test simple de Prisma"""
    try:
        from prisma import Prisma
        
        prisma = Prisma()
        await prisma.connect()
        
        # Test simple
        documents = await prisma.document.find_many()
        print(f"✅ Connexion Prisma réussie")
        print(f"📊 Documents trouvés: {len(documents)}")
        
        await prisma.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_prisma())
    sys.exit(0 if success else 1)
'''
    
    test_file = Path("scripts/test_prisma_simple.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # Rendre le script exécutable
    test_file.chmod(0o755)
    
    print("✅ Script de test créé: scripts/test_prisma_simple.py")
    return True

def main():
    """Fonction principale"""
    print("🗄️ Configuration Prisma simplifiée avec Supabase")
    print("=" * 60)
    
    # Vérifier Prisma
    if not check_prisma_installed():
        if not install_prisma():
            return False
    
    # Configurer le schéma simplifié
    if not setup_simple_schema():
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
    
    print("\n🎉 Configuration Prisma simplifiée terminée !")
    print("\n📋 Prochaines étapes :")
    print("1. python scripts/test_prisma_simple.py")
    print("2. python examples/basic_rag_example.py")
    print("3. Consultez docs/PRISMA_SUPABASE_SETUP.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
