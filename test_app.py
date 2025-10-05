#!/usr/bin/env python3
"""
Application Streamlit simplifiée pour tester le système RAG.
"""

import streamlit as st
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

def main():
    st.set_page_config(
        page_title="🚀 RAG System - Test",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🚀 Système RAG - Interface de Test")
    st.markdown("---")
    
    # Test simple
    st.header("🤖 Test du Système RAG")
    
    question = st.text_area(
        "Posez votre question:",
        placeholder="Ex: Qu'est-ce que l'intelligence artificielle?",
        height=100
    )
    
    if st.button("🚀 Générer Réponse", type="primary"):
        if question:
            st.success("✅ Question reçue!")
            st.write(f"**Question:** {question}")
            st.write("**Réponse:** Cette fonctionnalité sera implémentée avec le système RAG complet.")
        else:
            st.warning("⚠️ Veuillez saisir une question.")
    
    # Informations sur le système
    st.markdown("---")
    st.header("📊 Informations du Système")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Status", "✅ Opérationnel", "Interface web active")
    
    with col2:
        st.metric("Port", "8501", "Streamlit")
    
    with col3:
        st.metric("Version", "1.50.0", "Streamlit")
    
    # Configuration
    st.markdown("---")
    st.header("⚙️ Configuration")
    
    st.write("**Modules disponibles:**")
    st.write("- 🤖 RAG System")
    st.write("- 📄 OCR Processing")
    st.write("- 🔍 Vector Search")
    st.write("- 📊 Analytics")
    
    # Footer
    st.markdown("---")
    st.markdown("🚀 **Système RAG** - Interface de test fonctionnelle")
    st.markdown("📚 [Documentation GitHub](https://github.com/stikpy/rag-system)")

if __name__ == "__main__":
    main()

