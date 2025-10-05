#!/usr/bin/env python3
"""
Script pour lancer l'interface web Streamlit du système RAG.
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Lance l'interface web Streamlit."""
    print("🚀 Lancement de l'interface web RAG...")
    
    # Vérifier que Streamlit est installé
    try:
        import streamlit
        print(f"✅ Streamlit {streamlit.__version__} détecté")
    except ImportError:
        print("❌ Streamlit n'est pas installé. Installation en cours...")
        subprocess.run([sys.executable, "-m", "pip", "install", "streamlit"])
        print("✅ Streamlit installé")
    
    # Changer vers le répertoire du projet
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Lancer Streamlit
    print("🌐 Lancement de l'interface web...")
    print("📱 L'interface sera disponible sur http://localhost:8501")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "localhost"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Interface arrêtée par l'utilisateur")
    except Exception as e:
        print(f"❌ Erreur lors du lancement: {e}")

if __name__ == "__main__":
    main()

