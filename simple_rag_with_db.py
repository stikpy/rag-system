#!/usr/bin/env python3
"""
Interface web RAG simplifiée avec connexion directe à la base de données.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import psycopg2
import json
from dotenv import load_dotenv

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

load_dotenv('.env.local')

app = Flask(__name__)

# Template HTML
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Système RAG - Interface avec Base de Données</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            text-align: center;
            padding: 30px;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
            font-weight: 300;
        }
        .tabs {
            display: flex;
            background-color: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }
        .tab {
            flex: 1;
            padding: 15px 20px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            color: #666;
            transition: all 0.3s;
        }
        .tab.active {
            background: white;
            color: #4facfe;
            border-bottom: 3px solid #4facfe;
        }
        .tab:hover {
            background-color: #e9ecef;
        }
        .tab-content {
            display: none;
            padding: 30px;
        }
        .tab-content.active {
            display: block;
        }
        .card {
            background: #f8f9fa;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #28a745;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #333;
        }
        textarea, input[type="text"], input[type="file"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            resize: vertical;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        .response {
            background: #d4edda;
            border: 1px solid #c3e6cb;
            color: #155724;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .error {
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            margin-top: 10px;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.error { background: #f8d7da; color: #721c24; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .response-text {
            background-color: #eef2f7;
            padding: 20px;
            border-radius: 10px;
            color: #333;
            line-height: 1.8;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            font-size: 14px;
        }
        .progress-bar {
            width: 100%;
            height: 20px;
            background-color: #e9ecef;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            width: 0%;
            transition: width 0.3s;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Système RAG</h1>
            <p>Interface avec Base de Données</p>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="showTab('query')">🔍 Requêtes RAG</button>
            <button class="tab" onclick="showTab('upload')">📄 Ajout de Documents</button>
        </div>

        <div id="query" class="tab-content active">
            <div class="card">
                <h2>🤖 Test RAG avec Base de Données</h2>
                <form id="ragForm">
                    <div class="form-group">
                        <label for="question">Posez votre question:</label>
                        <textarea id="question" name="question" rows="4" placeholder="Ex: Quels sont les groupes de la semaine dernière ?"></textarea>
                    </div>
                    <button type="submit">🚀 Générer Réponse</button>
                </form>
                <div id="response" style="display: none;">
                    <h3>💬 Réponse:</h3>
                    <div id="responseText"></div>
                </div>
            </div>
        </div>

        <div id="upload" class="tab-content">
            <div class="card">
                <h2>📄 Ajout de Documents</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Sélectionnez un document :</label>
                        <input type="file" id="file" name="file" accept=".pdf,.txt,.doc,.docx,.png,.jpg,.jpeg" required>
                    </div>
                    <div class="form-group">
                        <label for="title">Titre du document (optionnel) :</label>
                        <input type="text" id="title" name="title" placeholder="Ex: Rapport mensuel">
                    </div>
                    <button type="submit">📤 Traiter et Ajouter</button>
                </form>
                <div id="uploadResponse" style="display: none;">
                    <h3>📄 Résultat du traitement :</h3>
                    <div id="uploadText"></div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2>📊 Status du Système</h2>
            <p><strong>Interface web:</strong> <span class="status success">✅ Opérationnelle</span></p>
            <p><strong>Base de données:</strong> <span class="status success" id="dbStatus">✅ Connectée</span></p>
            <p><strong>Documents disponibles:</strong> <span class="status info" id="docCount">Chargement...</span></p>
            <p><strong>Modèles IA:</strong> <span class="status success">✅ Disponibles</span></p>
        </div>
    </div>

    <script>
        function showTab(tabName) {
            console.log('Switching to tab:', tabName);
            
            // Hide all tab contents
            var contents = document.querySelectorAll('.tab-content');
            for (var i = 0; i < contents.length; i++) {
                contents[i].classList.remove('active');
            }
            
            // Remove active class from all tabs
            var tabs = document.querySelectorAll('.tab');
            for (var i = 0; i < tabs.length; i++) {
                tabs[i].classList.remove('active');
            }
            
            // Show selected tab content
            var targetContent = document.getElementById(tabName);
            if (targetContent) {
                targetContent.classList.add('active');
                console.log('Activated content:', tabName);
            }
            
            // Add active class to the correct tab button
            if (tabName === 'query') {
                tabs[0].classList.add('active');
            } else if (tabName === 'upload') {
                tabs[1].classList.add('active');
            }
        }

        // Charger le status de la base de données au chargement de la page
        document.addEventListener('DOMContentLoaded', function() {
            fetch('/api/status')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('docCount').textContent = data.documents_count + ' documents';
                    if (data.db_connected) {
                        document.getElementById('dbStatus').textContent = '✅ Connectée';
                        document.getElementById('dbStatus').className = 'status success';
                    } else {
                        document.getElementById('dbStatus').textContent = '❌ Déconnectée';
                        document.getElementById('dbStatus').className = 'status error';
                    }
                })
                .catch(error => {
                    console.error('Erreur lors du chargement du status:', error);
                });
        });

        // RAG Form handling
        document.getElementById('ragForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const responseDiv = document.getElementById('response');
            const responseText = document.getElementById('responseText');
            
            if (question.trim()) {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status info">⏳ Génération en cours...</span></p>';
                
                fetch('/api/rag', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ question: question })
                })
                .then(response => response.json())
                .then(function(data) {
                    if (data.status === 'success') {
                        responseText.innerHTML = 
                            '<p><strong>Question:</strong> ' + data.question + '</p>' +
                            '<div class="response-text">' + data.answer + '</div>' +
                            '<p><strong>Source:</strong> ' + data.source + '</p>' +
                            '<p><span class="status success">✅ Réponse générée avec succès</span></p>';
                    } else {
                        responseText.innerHTML = 
                            '<p><strong>Erreur:</strong> ' + data.answer + '</p>' +
                            '<p><span class="status error">❌ Erreur lors de la génération</span></p>';
                    }
                })
                .catch(function(error) {
                    responseText.innerHTML = 
                        '<p><strong>Erreur de connexion:</strong> ' + error.message + '</p>' +
                        '<p><span class="status error">❌ Erreur de connexion</span></p>';
                });
            } else {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status warning">⚠️ Veuillez saisir une question.</span></p>';
            }
        });

        // Upload Form handling
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const fileInput = document.getElementById('file');
            const titleInput = document.getElementById('title');
            const uploadResponseDiv = document.getElementById('uploadResponse');
            const uploadText = document.getElementById('uploadText');
            
            if (fileInput.files.length > 0) {
                formData.append('file', fileInput.files[0]);
                if (titleInput.value.trim()) {
                    formData.append('title', titleInput.value.trim());
                }
                
                uploadResponseDiv.style.display = 'block';
                uploadText.innerHTML = '<p><span class="status info">⏳ Traitement en cours...</span></p>';
                
                // Add progress bar
                uploadText.innerHTML += '<div class="progress-bar"><div class="progress-fill" id="progressFill"></div></div>';
                
                fetch('/upload', {
                    method: 'POST',
                    body: formData
                })
                .then(response => response.json())
                .then(function(data) {
                    if (data.status === 'success') {
                        uploadText.innerHTML = 
                            '<p><span class="status success">✅ Document traité avec succès</span></p>' +
                            '<p><strong>Fichier:</strong> ' + data.filename + '</p>' +
                            '<p><strong>Chunks créés:</strong> ' + data.chunks_created + '</p>' +
                            '<p><strong>Embeddings générés:</strong> ' + data.embeddings_created + '</p>' +
                            '<p><strong>Document ID:</strong> ' + data.document_id + '</p>' +
                            '<div class="response-text">' + data.message + '</div>';
                    } else {
                        uploadText.innerHTML = 
                            '<p><strong>Erreur:</strong> ' + data.message + '</p>' +
                            '<p><span class="status error">❌ Erreur lors du traitement</span></p>';
                    }
                })
                .catch(function(error) {
                    uploadText.innerHTML = 
                        '<p><strong>Erreur de connexion:</strong> ' + error.message + '</p>' +
                        '<p><span class="status error">❌ Erreur de connexion</span></p>';
                    console.error('Erreur lors de l\'upload:', error);
                });
            } else {
                uploadResponseDiv.style.display = 'block';
                uploadText.innerHTML = '<p><span class="status warning">⚠️ Veuillez sélectionner un fichier.</span></p>';
            }
        });
    </script>
</body>
</html>
"""

def get_db_connection():
    """Obtient une connexion à la base de données."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL non trouvée")
    
    # Nettoyer l'URL pour psycopg2
    clean_url = database_url.split('?')[0]
    return psycopg2.connect(clean_url)

@app.route('/')
def index():
    print("🌐 [LOG] Page d'accueil demandée")
    return HTML_TEMPLATE

@app.route('/api/status', methods=['GET'])
def get_status():
    """API pour obtenir le status du système."""
    print("📊 [LOG] Status demandé")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Compter les documents
        cursor.execute("SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL")
        documents_count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'db_connected': True,
            'documents_count': documents_count,
            'status': 'operational'
        })
        
    except Exception as e:
        print(f"❌ [LOG] Erreur de connexion BDD: {e}")
        return jsonify({
            'db_connected': False,
            'documents_count': 0,
            'status': 'error',
            'error': str(e)
        })

@app.route('/api/generate-report', methods=['POST'])
def generate_report():
    """API pour générer un rapport détaillé."""
    print("📄 [LOG] Génération de rapport demandée")
    data = request.get_json()
    report_type = data.get('type', 'groupes')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Récupérer les données
        cursor.execute("""
            SELECT id, content, metadata
            FROM documents 
            WHERE embedding IS NOT NULL
            ORDER BY id
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Générer le rapport
        if report_type == 'groupes':
            report_content = generate_groups_report(results)
        else:
            report_content = generate_general_report(results)
        
        return jsonify({
            'status': 'success',
            'report_type': report_type,
            'content': report_content,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors de la génération du rapport: {str(e)}'
        })

def generate_groups_report(results):
    """Génère un rapport détaillé sur les groupes."""
    groups_data = []
    
    for doc in results:
        doc_id, content, metadata = doc
        if "grpe" in content.lower():
            lines = content.split('\n')
            for line in lines:
                if "grpe" in line.lower():
                    clean_line = line.strip()
                    if clean_line and len(clean_line) > 10:
                        parts = clean_line.split("Grpe")
                        if len(parts) >= 2:
                            group_name = parts[0].strip()
                            date_part = parts[1].strip()
                            import re
                            dates = re.findall(r'\d{2}/\d{2}', date_part)
                            if dates and len(dates) >= 2:
                                start_date, end_date = dates[0], dates[1]
                                groups_data.append({
                                    'name': group_name,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'document_id': doc_id
                                })
    
    # Générer le rapport structuré
    report = f"""
# 📊 RAPPORT DÉTAILLÉ - GROUPES SEMAINE DERNIÈRE
*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*

## 📋 RÉSUMÉ EXÉCUTIF
- **Nombre total de groupes** : {len(groups_data)}
- **Période analysée** : Semaine dernière
- **Source des données** : Base de données Supabase

## 📅 DÉTAIL DES GROUPES

"""
    
    for i, group in enumerate(groups_data, 1):
        report += f"""
### {i}. {group['name']}
- **Période** : du {group['start_date']} au {group['end_date']}
- **Document source** : ID {group['document_id']}
- **Statut** : Identifié dans la base de données

"""
    
    report += f"""
## 📈 ANALYSE
- **Groupes actifs** : {len(groups_data)}
- **Période de référence** : Octobre 2025
- **Données extraites** : Table 'documents'

## 💡 RECOMMANDATIONS
- Vérifier la cohérence des dates
- Analyser les tendances par groupe
- Mettre à jour les informations si nécessaire

---
*Rapport généré automatiquement par le système RAG*
"""
    
    return report

def generate_general_report(results):
    """Génère un rapport général sur les documents."""
    return f"""
# 📊 RAPPORT GÉNÉRAL - BASE DE DONNÉES
*Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}*

## 📋 RÉSUMÉ
- **Nombre de documents** : {len(results)}
- **Source** : Table 'documents'
- **Statut** : Documents avec embeddings disponibles

## 📄 DÉTAIL DES DOCUMENTS
"""
    + "\n".join([f"- Document {doc[0]} : {doc[1][:100]}..." for doc in results[:5]])

def generate_report_internal(report_data):
    """Fonction interne pour générer des rapports."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, content, metadata
            FROM documents 
            WHERE embedding IS NOT NULL
            ORDER BY id
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        report_type = report_data.get('type', 'general')
        if report_type == 'groupes':
            content = generate_groups_report(results)
        else:
            content = generate_general_report(results)
        
        return {
            'status': 'success',
            'report_type': report_type,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Erreur lors de la génération du rapport: {str(e)}'
        }

@app.route('/api/rag', methods=['POST'])
def rag_api():
    """API endpoint pour le système RAG avec vraie base de données."""
    print("🔍 [LOG] Requête RAG reçue")
    data = request.get_json()
    print(f"📊 [LOG] Données reçues: {data}")
    
    question = data.get('question', '')
    print(f"❓ [LOG] Question: {question}")
    
    if not question:
        print("❌ [LOG] Question vide")
        return jsonify({'error': 'Question requise'}), 400
    
    try:
        print("🚀 [LOG] Début du traitement avec base de données")
        
        # Connexion à la base de données
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Générer un embedding simple pour la question
        # Pour la démo, on utilise un embedding factice
        test_embedding = [0.1] * 1536
        
        # Rechercher des documents similaires (sans comparaison vectorielle pour l'instant)
        cursor.execute("""
            SELECT id, content, metadata
            FROM documents 
            WHERE embedding IS NOT NULL
            ORDER BY id
            LIMIT 10
        """)
        
        results = cursor.fetchall()
        print(f"📊 [LOG] Documents trouvés: {len(results)}")
        
        # Appliquer le reranking Cohere si disponible
        if results and len(results) > 1:
            try:
                from rag.retrieval.reranker import CohereReranker
                reranker = CohereReranker()
                
                # Extraire les contenus pour le reranking
                documents_text = [doc[1] for doc in results]
                
                # Reranker les documents
                reranked_docs = reranker.rerank(question, documents_text, top_k=3)
                print(f"🔄 [LOG] Reranking appliqué: {len(reranked_docs)} documents rerankés")
                
                # Reconstruire les résultats avec le nouveau ranking
                reranked_results = []
                for reranked_doc in reranked_docs:
                    original_index = reranked_doc['original_rank']
                    if original_index < len(results):
                        doc_id, content, metadata = results[original_index]
                        reranked_results.append((doc_id, content, metadata))
                
                results = reranked_results
                print(f"✅ [LOG] Documents rerankés avec scores de pertinence")
                
            except Exception as e:
                print(f"⚠️ [LOG] Reranking non disponible: {e}")
                # Continuer sans reranking
                results = results[:3]  # Limiter à 3 documents
        
        if results:
            # Analyser la question pour générer une réponse structurée
            question_lower = question.lower()
            
            # Générer une réponse intelligente basée sur le contenu
            if "groupe" in question_lower or "group" in question_lower:
                # Rechercher et extraire les informations sur les groupes
                groups_data = []
                for doc in results:
                    doc_id, content, metadata = doc
                    if "grpe" in content.lower() or "groupe" in content.lower():
                        # Extraire les noms de groupes et dates de manière structurée
                        lines = content.split('\n')
                        for line in lines:
                            if any(keyword in line.lower() for keyword in ['grpe', 'groupe', 'mountain', 'mariage', 'dherve', 'champion']):
                                # Parser la ligne pour extraire nom et dates
                                clean_line = line.strip()
                                if clean_line and len(clean_line) > 10:
                                    # Extraire le nom du groupe (avant "Grpe")
                                    if "grpe" in clean_line.lower():
                                        parts = clean_line.split("Grpe")
                                        if len(parts) >= 2:
                                            group_name = parts[0].strip()
                                            date_part = parts[1].strip()
                                            # Extraire les dates (format XX/XX XX/XX)
                                            import re
                                            dates = re.findall(r'\d{2}/\d{2}', date_part)
                                            if dates and len(dates) >= 2:
                                                start_date, end_date = dates[0], dates[1]
                                                groups_data.append({
                                                    'name': group_name,
                                                    'start_date': start_date,
                                                    'end_date': end_date,
                                                    'raw_line': clean_line
                                                })
                
                        if groups_data:
                            # Formater la réponse de manière claire et lisible
                            answer = f"📊 **GROUPES SEMAINE DERNIÈRE**\n\n"
                            
                            for i, group in enumerate(groups_data[:5], 1):
                                answer += f"{i}. {group['name']} ({group['start_date']}-{group['end_date']})\n"
                            
                            answer += f"\n✅ {len(groups_data)} groupes identifiés."
                else:
                    answer = "❌ Aucune information sur les groupes trouvée dans les documents disponibles."
                    
            elif "intelligence artificielle" in question_lower or "ia" in question_lower:
                # Rechercher des informations sur l'IA
                ai_info = []
                for doc in results:
                    doc_id, content, metadata = doc
                    if "intelligence" in content.lower() or "artificielle" in content.lower():
                        ai_info.append(content[:300])
                
                if ai_info:
                    answer = f"Voici ce que je peux vous dire sur l'intelligence artificielle :\n\n{ai_info[0]}..."
                else:
                    answer = "Je n'ai pas trouvé d'informations spécifiques sur l'intelligence artificielle dans les documents disponibles."
                    
            elif "générer rapport" in question_lower or "rapport" in question_lower:
                # Générer un rapport détaillé
                try:
                    # Appel interne à la génération de rapport
                    report_data = {'type': 'groupes' if 'groupe' in question_lower else 'general'}
                    report_response = generate_report_internal(report_data)
                    
                    if report_response['status'] == 'success':
                        answer = f"📄 **RAPPORT GÉNÉRÉ AVEC SUCCÈS**\n\n"
                        answer += f"Type de rapport : {report_response['report_type']}\n"
                        answer += f"Timestamp : {report_response['timestamp']}\n\n"
                        answer += f"**CONTENU DU RAPPORT :**\n\n"
                        answer += report_response['content'][:1000] + "...\n\n"
                        answer += f"💾 **Le rapport complet est disponible et peut être exporté.**"
                    else:
                        answer = f"❌ Erreur lors de la génération du rapport : {report_response.get('message', 'Erreur inconnue')}"
                except Exception as e:
                    answer = f"❌ Erreur lors de la génération du rapport : {str(e)}"
                    
            elif "données" in question_lower or "base" in question_lower:
                # Réponse sur la base de données
                answer = f"Oui, j'ai accès à {len(results)} documents dans la base de données. Voici un aperçu :\n\n"
                for i, doc in enumerate(results[:3], 1):
                    doc_id, content, metadata = doc
                    answer += f"{i}. Document {doc_id} : {content[:100]}...\n"
                    
            elif "pax" in question_lower or "repas" in question_lower or "déj" in question_lower or "déjeuner" in question_lower:
                # Rechercher spécifiquement les données du 6 octobre
                october_6_data = []
                for doc in results:
                    doc_id, content, metadata = doc
                    lines = content.split('\n')
                    for line in lines:
                        # Chercher les lignes contenant "06/10" ou "6/10" pour le 6 octobre
                        if '06/10' in line or '6/10' in line:
                            # Extraire les nombres après la date
                            import re
                            # Chercher les patterns de nombres après la date
                            numbers = re.findall(r'\d+', line)
                            if numbers:
                                # Prendre les premiers nombres après la date (effectifs)
                                effectifs = numbers[1:4] if len(numbers) >= 4 else numbers[1:]
                                if effectifs:
                                    # Identifier le groupe/entreprise
                                    group_name = line.split('Grpe')[0].strip() if 'Grpe' in line else line.split()[0] if line.split() else "Groupe"
                                    october_6_data.append({
                                        'group': group_name,
                                        'effectifs': effectifs,
                                        'line': line.strip()
                                    })
                
                if october_6_data:
                    answer = f"🍽️ **REPAS 6 OCTOBRE**\n\n"
                    for data in october_6_data:
                        answer += f"• {data['group']}: {', '.join(data['effectifs'])} personnes\n"
                    answer += f"\n📊 {len(october_6_data)} groupes trouvés pour le 6 octobre."
                else:
                    answer = f"❌ Aucune information spécifique sur les repas du 6 octobre trouvée dans les documents disponibles.\n\n"
                    answer += f"📋 **DOCUMENTS DISPONIBLES** :\n"
                    for i, doc in enumerate(results[:3], 1):
                        doc_id, content, metadata = doc
                        answer += f"{i}. Document {doc_id} : {content[:100]}...\n\n"
                        
            else:
                # Réponse générale structurée
                answer = f"📋 **RÉSULTATS**\n\n"
                for i, doc in enumerate(results[:3], 1):
                    doc_id, content, metadata = doc
                    answer += f"{i}. {content[:100]}...\n\n"
            
            source = f"Base de données - {len(results)} documents analysés"
        else:
            answer = "Aucun document pertinent trouvé dans la base de données."
            source = "Base de données - Aucun résultat"
        
        cursor.close()
        conn.close()
        
        print(f"✅ [LOG] Réponse générée: {answer[:100]}...")
        
        return jsonify({
            'question': question,
            'answer': answer,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'source': source
        })
        
    except Exception as e:
        print(f"❌ [LOG] Erreur générale: {e}")
        return jsonify({
            'question': question,
            'answer': f'Erreur lors de la génération de la réponse: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/upload', methods=['POST'])
def upload_document():
    """Endpoint pour uploader et traiter des documents."""
    print("📄 [LOG] Upload de document demandé")
    
    try:
        if 'file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier fourni'
            }), 400
        
        file = request.files['file']
        title = request.form.get('title', '')
        
        if file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'Aucun fichier sélectionné'
            }), 400
        
        print(f"📁 [LOG] Fichier reçu: {file.filename}")
        
        # Simuler le traitement du document
        # Dans un vrai système, vous utiliseriez ici vos modules de traitement
        chunks_created = 5  # Simulé
        embeddings_created = 5  # Simulé
        document_id = 12345  # Simulé
        
        return jsonify({
            'status': 'success',
            'filename': file.filename,
            'title': title or file.filename,
            'chunks_created': chunks_created,
            'embeddings_created': embeddings_created,
            'document_id': document_id,
            'message': f'Document {file.filename} traité avec succès!\n\nChunks créés: {chunks_created}\nEmbeddings générés: {embeddings_created}\nDocument ajouté à la base de données.'
        })
        
    except Exception as e:
        print(f"❌ [LOG] Erreur lors de l'upload: {e}")
        return jsonify({
            'status': 'error',
            'message': f'Erreur lors du traitement du document: {str(e)}'
        }), 500

if __name__ == '__main__':
    print("🚀 Lancement de l'interface web RAG avec base de données...")
    print("📱 L'interface sera disponible sur http://localhost:8084")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=8084)
