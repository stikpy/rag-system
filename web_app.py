#!/usr/bin/env python3
"""
Interface web Flask pour tester le système RAG.
"""

from flask import Flask, render_template_string, request, jsonify
import sys
from pathlib import Path
import os

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

app = Flask(__name__)

# Template HTML simple
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 RAG System - Interface de Test</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }
        .card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
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
        input, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
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
            background: #f8f9fa;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin-top: 20px;
            border-radius: 5px;
        }
        .status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        .status.success { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.error { background: #f8d7da; color: #721c24; }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }
        .metric {
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }
        .metric-label {
            color: #666;
            margin-top: 5px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚀 Système RAG - Interface de Test</h1>
        <p>Testez votre système RAG avec une interface web simple</p>
    </div>

    <div class="grid">
        <div class="card">
            <h2>🤖 Test RAG</h2>
            <form id="ragForm">
                <div class="form-group">
                    <label for="question">Posez votre question:</label>
                    <textarea id="question" name="question" rows="4" placeholder="Ex: Qu'est-ce que l'intelligence artificielle?"></textarea>
                </div>
                <button type="submit">🚀 Générer Réponse</button>
            </form>
            <div id="response" class="response" style="display: none;">
                <h3>💬 Réponse:</h3>
                <div id="responseText"></div>
            </div>
        </div>

        <div class="card">
            <h2>📊 Statistiques</h2>
            <div class="metric">
                <div class="metric-value">✅</div>
                <div class="metric-label">Status: Opérationnel</div>
            </div>
            <div class="metric">
                <div class="metric-value">4</div>
                <div class="metric-label">Modèles configurés</div>
            </div>
            <div class="metric">
                <div class="metric-value">6</div>
                <div class="metric-label">Fonctionnalités</div>
            </div>
        </div>
    </div>

    <div class="card">
        <h2>⚙️ Configuration</h2>
        <p><strong>Modules disponibles:</strong></p>
        <ul>
            <li>🤖 RAG System - Génération de réponses contextuelles</li>
            <li>📄 OCR Processing - Extraction de texte depuis images/PDF</li>
            <li>🔍 Vector Search - Recherche sémantique</li>
            <li>📊 Analytics - Statistiques et monitoring</li>
        </ul>
        
        <p><strong>Technologies intégrées:</strong></p>
        <ul>
            <li>Mistral AI - Embeddings et génération</li>
            <li>OpenAI - GPT-4 pour la génération avancée</li>
            <li>Cohere - Reranking pour améliorer la pertinence</li>
            <li>Supabase - Base de données vectorielle</li>
            <li>Prisma - ORM moderne</li>
            <li>Langchain - Chaînes de traitement</li>
        </ul>
    </div>

    <div class="card">
        <h2>🔗 Liens utiles</h2>
        <p>
            <a href="https://github.com/stikpy/rag-system" target="_blank">📚 Documentation GitHub</a> |
            <a href="http://localhost:5555" target="_blank">🔧 Prisma Studio</a> |
            <a href="http://localhost:8501" target="_blank">📱 Streamlit (si disponible)</a>
        </p>
    </div>

    <script>
        document.getElementById('ragForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const responseDiv = document.getElementById('response');
            const responseText = document.getElementById('responseText');
            
            if (question.trim()) {
                responseDiv.style.display = 'block';
                responseText.innerHTML = `
                    <p><strong>Question:</strong> ${question}</p>
                    <p><strong>Réponse:</strong> Cette fonctionnalité sera implémentée avec le système RAG complet. 
                    Le système est configuré et prêt à traiter vos questions avec les modèles Mistral AI, OpenAI, et Cohere.</p>
                    <p><span class="status success">✅ Interface fonctionnelle</span></p>
                `;
            } else {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status warning">⚠️ Veuillez saisir une question.</span></p>';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/rag', methods=['POST'])
def rag_api():
    """API endpoint pour le système RAG."""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Question requise'}), 400
    
    # Ici vous pouvez intégrer le vrai système RAG
    response = {
        'question': question,
        'answer': 'Cette fonctionnalité sera implémentée avec le système RAG complet.',
        'status': 'success',
        'timestamp': '2024-10-05T14:46:00Z'
    }
    
    return jsonify(response)

@app.route('/api/status')
def status():
    """Endpoint de statut du système."""
    return jsonify({
        'status': 'operational',
        'modules': ['RAG', 'OCR', 'Vector Search', 'Analytics'],
        'models': ['Mistral AI', 'OpenAI', 'Cohere', 'Supabase'],
        'version': '1.0.0'
    })

if __name__ == '__main__':
    print("🚀 Lancement de l'interface web RAG...")
    print("📱 L'interface sera disponible sur http://localhost:5000")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    
    app.run(debug=True, host='localhost', port=5000)

