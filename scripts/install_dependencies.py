#!/usr/bin/env python3
"""
Script d'installation des dépendances
=====================================

Ce script installe toutes les dépendances nécessaires pour le système RAG.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Exécute une commande et affiche le résultat"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} terminé")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de {description}: {e}")
        print(f"Sortie: {e.stdout}")
        print(f"Erreur: {e.stderr}")
        return False

def check_python_version():
    """Vérifie la version de Python"""
    print("🐍 Vérification de la version Python...")
    
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Version 3.8+ requise")
        return False

def install_python_dependencies():
    """Installe les dépendances Python"""
    print("\n📦 Installation des dépendances Python...")
    
    # Vérifier que requirements.txt existe
    requirements_path = Path("requirements.txt")
    if not requirements_path.exists():
        print("❌ Fichier requirements.txt non trouvé")
        return False
    
    # Installer les dépendances
    return run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Installation des dépendances Python"
    )

def install_system_dependencies():
    """Installe les dépendances système"""
    print("\n🔧 Installation des dépendances système...")
    
    # Détecter le système d'exploitation
    import platform
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("🍎 Détection macOS")
        commands = [
            ("brew install tesseract", "Installation Tesseract OCR"),
            ("brew install poppler", "Installation Poppler"),
        ]
    elif system == "linux":
        print("🐧 Détection Linux")
        commands = [
            ("sudo apt-get update", "Mise à jour des paquets"),
            ("sudo apt-get install -y tesseract-ocr tesseract-ocr-fra poppler-utils", "Installation Tesseract et Poppler"),
        ]
    else:
        print(f"⚠️  Système {system} détecté - Installation manuelle requise")
        print("💡 Installez manuellement :")
        print("   - Tesseract OCR")
        print("   - Poppler")
        return True
    
    # Exécuter les commandes
    for command, description in commands:
        if not run_command(command, description):
            print(f"⚠️  {description} échoué - Continuez manuellement")
    
    return True

def create_directories():
    """Crée les répertoires nécessaires"""
    print("\n📁 Création des répertoires...")
    
    directories = [
        "logs",
        "data",
        "cache",
        "chroma_db"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Répertoire {directory} créé")
    
    return True

def setup_environment():
    """Configure l'environnement"""
    print("\n🔧 Configuration de l'environnement...")
    
    # Copier env.example vers .env si nécessaire
    env_path = Path(".env")
    if not env_path.exists():
        env_example_path = Path("env.example")
        if env_example_path.exists():
            import shutil
            shutil.copy(env_example_path, env_path)
            print("✅ Fichier .env créé à partir de env.example")
        else:
            print("❌ Fichier env.example non trouvé")
            return False
    else:
        print("✅ Fichier .env existe déjà")
    
    return True

def test_installation():
    """Teste l'installation"""
    print("\n🧪 Test de l'installation...")
    
    # Test des modules Python
    test_modules = [
        "mistralai",
        "openai", 
        "cohere",
        "supabase",
        "langchain",
        "pytesseract",
        "easyocr",
        "dotenv"
    ]
    
    failed_modules = []
    for module in test_modules:
        try:
            __import__(module)
            print(f"✅ {module} OK")
        except ImportError:
            print(f"❌ {module} manquant")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n⚠️  Modules manquants : {', '.join(failed_modules)}")
        print("💡 Réessayez : pip install -r requirements.txt")
        return False
    
    print("✅ Tous les modules Python sont installés")
    return True

def main():
    """Fonction principale"""
    print("🚀 Installation du Système RAG")
    print("=" * 40)
    
    # Vérifications préliminaires
    if not check_python_version():
        return False
    
    # Installation des dépendances Python
    if not install_python_dependencies():
        print("❌ Échec de l'installation des dépendances Python")
        return False
    
    # Installation des dépendances système
    if not install_system_dependencies():
        print("⚠️  Certaines dépendances système n'ont pas pu être installées")
        print("💡 Installez-les manuellement si nécessaire")
    
    # Création des répertoires
    if not create_directories():
        print("❌ Erreur lors de la création des répertoires")
        return False
    
    # Configuration de l'environnement
    if not setup_environment():
        print("❌ Erreur lors de la configuration de l'environnement")
        return False
    
    # Test de l'installation
    if not test_installation():
        print("❌ Installation incomplète")
        return False
    
    print("\n🎉 Installation terminée avec succès !")
    print("\n📋 Prochaines étapes :")
    print("1. Configurez vos clés API : python scripts/setup_quick.py")
    print("2. Vérifiez la configuration : python scripts/check_api_keys.py")
    print("3. Testez le système : python examples/basic_rag_example.py")
    print("\n📚 Consultez docs/ pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
