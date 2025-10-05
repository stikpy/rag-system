#!/usr/bin/env python3
"""
Interface web RAG avec vraie connexion à la base de données.
"""

import os
import sys
from pathlib import Path
from flask import Flask, render_template_string, request, jsonify
from datetime import datetime
import asyncio

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

app = Flask(__name__)

# Template HTML avec vraie intégration BDD
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
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .header h1 {
            color: #333;
            margin-bottom: 10px;
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
        textarea {
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Système RAG - Interface avec Base de Données</h1>
            <p>Testez votre système RAG avec une vraie connexion à la base de données</p>
        </div>

        <div class="card">
            <h2>🤖 Test RAG avec Base de Données</h2>
            <form id="ragForm">
                <div class="form-group">
                    <label for="question">Posez votre question:</label>
                    <textarea id="question" name="question" rows="4" placeholder="Ex: Qu'est-ce que l'intelligence artificielle?"></textarea>
                </div>
                <button type="submit">🚀 Générer Réponse</button>
            </form>
            <div id="response" style="display: none;">
                <h3>💬 Réponse:</h3>
                <div id="responseText"></div>
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
                .then(data => {
                    if (data.status === 'success') {
                        responseText.innerHTML = `
                            <p><strong>Question:</strong> ${data.question}</p>
                            <p><strong>Réponse:</strong> ${data.answer}</p>
                            <p><strong>Source:</strong> ${data.source}</p>
                            <p><span class="status success">✅ Réponse générée avec succès</span></p>
                        `;
                    } else {
                        responseText.innerHTML = `
                            <p><strong>Erreur:</strong> ${data.answer}</p>
                            <p><span class="status error">❌ Erreur lors de la génération</span></p>
                        `;
                    }
                })
                .catch(error => {
                    responseText.innerHTML = `
                        <p><strong>Erreur de connexion:</strong> ${error.message}</p>
                        <p><span class="status error">❌ Erreur de connexion</span></p>
                    `;
                });
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
    print("🌐 [LOG] Page d'accueil demandée")
    return HTML_TEMPLATE

@app.route('/api/status', methods=['GET'])
def get_status():
    """API pour obtenir le status du système."""
    print("📊 [LOG] Status demandé")
    
    try:
        # Tester la connexion à la base de données
        from prisma import Prisma
        
        async def check_db():
            prisma = Prisma()
            await prisma.connect()
            
            # Compter les documents
            doc_count = await prisma.query_raw("SELECT COUNT(*) as count FROM documents")
            await prisma.disconnect()
            
            return doc_count[0]['count']
        
        # Exécuter la vérification
        documents_count = asyncio.run(check_db())
        
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
        
        # Importer le système RAG réel
        from rag.core.rag_system import RAGSystem
        
        # Initialiser le système RAG
        rag = RAGSystem()
        print("✅ [LOG] Système RAG initialisé")
        
        # Générer la réponse basée sur la base de données
        response = rag.query(question)
        print(f"✅ [LOG] Réponse générée: {response}")
        
        return jsonify({
            'question': question,
            'answer': response,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'source': 'RAG System with Database'
        })
        
    except ImportError as e:
        print(f"❌ [LOG] Erreur d'import: {e}")
        return jsonify({
            'question': question,
            'answer': f'Erreur d\'import du système RAG: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        print(f"❌ [LOG] Erreur générale: {e}")
        return jsonify({
            'question': question,
            'answer': f'Erreur lors de la génération de la réponse: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        })

if __name__ == '__main__':
    print("🚀 Lancement de l'interface web RAG avec base de données...")
    print("📱 L'interface sera disponible sur http://localhost:8083")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=8083)
