#!/usr/bin/env python3
"""
Interface web Streamlit pour tester le système RAG.
"""

import streamlit as st
import sys
from pathlib import Path
import os

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

# Import des modules RAG
try:
    from rag.core.rag_system import RAGSystem
    from rag.ocr.document_processor import DocumentProcessor
    from rag.utils.config import config
except ImportError as e:
    st.error(f"Erreur d'import: {e}")
    st.stop()

def main():
    st.set_page_config(
        page_title="🚀 RAG System - Interface de Test",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🚀 Système RAG - Interface de Test")
    st.markdown("---")
    
    # Sidebar pour la configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Vérification des clés API
        st.subheader("🔑 Vérification des clés API")
        
        mistral_status = "✅" if config.mistral_api_key and config.mistral_api_key != "your_mistral_api_key_here" else "❌"
        openai_status = "✅" if config.openai_api_key and config.openai_api_key != "your_openai_api_key_here" else "❌"
        cohere_status = "✅" if config.cohere_api_key and config.cohere_api_key != "your_cohere_api_key_here" else "❌"
        supabase_status = "✅" if config.supabase_url and config.supabase_url != "your_supabase_url_here" else "❌"
        
        st.write(f"Mistral AI: {mistral_status}")
        st.write(f"OpenAI: {openai_status}")
        st.write(f"Cohere: {cohere_status}")
        st.write(f"Supabase: {supabase_status}")
        
        st.markdown("---")
        
        # Paramètres du système
        st.subheader("🎛️ Paramètres")
        
        chunk_size = st.slider("Taille des chunks", 512, 2048, 1024)
        max_tokens = st.slider("Tokens maximum", 512, 4096, 2048)
        temperature = st.slider("Température", 0.0, 1.0, 0.7)
        
        enable_reranking = st.checkbox("Activer le reranking Cohere", value=True)
        similarity_threshold = st.slider("Seuil de similarité", 0.0, 1.0, 0.7)
    
    # Interface principale
    tab1, tab2, tab3, tab4 = st.tabs(["🤖 Test RAG", "📄 Traitement OCR", "🔍 Recherche Vectorielle", "📊 Statistiques"])
    
    with tab1:
        st.header("🤖 Test du Système RAG")
        
        # Zone de texte pour la question
        question = st.text_area(
            "Posez votre question:",
            placeholder="Ex: Qu'est-ce que l'intelligence artificielle?",
            height=100
        )
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("🚀 Générer Réponse", type="primary"):
                if question:
                    try:
                        # Initialiser le système RAG
                        with st.spinner("Initialisation du système RAG..."):
                            rag = RAGSystem()
                        
                        # Générer la réponse
                        with st.spinner("Génération de la réponse..."):
                            response = rag.query(question)
                        
                        st.success("✅ Réponse générée avec succès!")
                        st.markdown("### 💬 Réponse:")
                        st.write(response)
                        
                    except Exception as e:
                        st.error(f"❌ Erreur lors de la génération: {e}")
                else:
                    st.warning("⚠️ Veuillez saisir une question.")
        
        with col2:
            if st.button("🧹 Effacer"):
                st.rerun()
    
    with tab2:
        st.header("📄 Traitement OCR")
        
        uploaded_file = st.file_uploader(
            "Téléchargez un document (PDF, image)",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Le fichier sera traité avec OCR pour extraire le texte"
        )
        
        if uploaded_file is not None:
            st.info(f"📁 Fichier reçu: {uploaded_file.name}")
            
            if st.button("🔍 Extraire le texte"):
                try:
                    with st.spinner("Traitement OCR en cours..."):
                        processor = DocumentProcessor()
                        
                        # Sauvegarder temporairement le fichier
                        temp_path = f"temp_{uploaded_file.name}"
                        with open(temp_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        
                        # Extraire le texte
                        if uploaded_file.name.lower().endswith('.pdf'):
                            text = processor.extract_text_from_pdf(temp_path)
                        else:
                            text = processor.extract_text_from_image(temp_path)
                        
                        # Nettoyer le fichier temporaire
                        os.remove(temp_path)
                    
                    st.success("✅ Texte extrait avec succès!")
                    st.markdown("### 📝 Texte extrait:")
                    st.text_area("", text, height=300)
                    
                    # Option pour ajouter au système RAG
                    if st.button("➕ Ajouter au système RAG"):
                        try:
                            rag = RAGSystem()
                            rag.add_documents([text])
                            st.success("✅ Document ajouté au système RAG!")
                        except Exception as e:
                            st.error(f"❌ Erreur: {e}")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement OCR: {e}")
    
    with tab3:
        st.header("🔍 Recherche Vectorielle")
        
        search_query = st.text_input("Recherche sémantique:")
        
        if st.button("🔍 Rechercher"):
            if search_query:
                try:
                    with st.spinner("Recherche en cours..."):
                        rag = RAGSystem()
                        results = rag.search_documents(search_query)
                    
                    st.success(f"✅ {len(results)} résultats trouvés!")
                    
                    for i, result in enumerate(results, 1):
                        with st.expander(f"Résultat {i} (Score: {result.get('score', 'N/A')})"):
                            st.write(result.get('content', ''))
                            if 'metadata' in result:
                                st.json(result['metadata'])
                except Exception as e:
                    st.error(f"❌ Erreur lors de la recherche: {e}")
            else:
                st.warning("⚠️ Veuillez saisir une requête de recherche.")
    
    with tab4:
        st.header("📊 Statistiques du Système")
        
        try:
            # Statistiques de base
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Modèles configurés", "4", "Mistral, OpenAI, Cohere, Supabase")
            
            with col2:
                st.metric("Fonctionnalités", "6", "RAG, OCR, Reranking, Embeddings, Vector Search, Langchain")
            
            with col3:
                st.metric("Langues supportées", "Multilingue", "Français, Anglais, etc.")
            
            with col4:
                st.metric("Status", "✅ Opérationnel", "Système prêt")
            
            # Informations détaillées
            st.subheader("🔧 Configuration actuelle")
            
            config_info = {
                "Chunk Size": chunk_size,
                "Max Tokens": max_tokens,
                "Temperature": temperature,
                "Reranking": "Activé" if enable_reranking else "Désactivé",
                "Similarity Threshold": similarity_threshold
            }
            
            for key, value in config_info.items():
                st.write(f"**{key}:** {value}")
        
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement des statistiques: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("🚀 **Système RAG** - Développé avec ❤️ pour l'innovation en IA")
    st.markdown("📚 [Documentation GitHub](https://github.com/stikpy/rag-system)")

if __name__ == "__main__":
    main()

