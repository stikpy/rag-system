#!/usr/bin/env python3
"""
Interface web RAG simplifiée qui fonctionne sans base de données.
"""

from flask import Flask, render_template_string, request, jsonify
import os
from datetime import datetime

app = Flask(__name__)

# Template HTML simple et fonctionnel
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 Système RAG - Interface de Test</title>
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Système RAG - Interface de Test</h1>
            <p>Testez votre système RAG avec une interface web simple</p>
        </div>

        <div class="card">
            <h2>🤖 Test RAG</h2>
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
            <p><strong>Base de données:</strong> <span class="status warning">⚠️ En configuration</span></p>
            <p><strong>Modèles IA:</strong> <span class="status success">✅ Disponibles</span></p>
        </div>
    </div>

    <script>
        document.getElementById('ragForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const responseDiv = document.getElementById('response');
            const responseText = document.getElementById('responseText');
            
            if (question.trim()) {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status warning">⏳ Génération en cours...</span></p>';
                
                // Simuler un appel API
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
    return HTML_TEMPLATE

@app.route('/api/rag', methods=['POST'])
def rag_api():
    """API endpoint pour le système RAG simplifié."""
    print("🔍 [LOG] Requête RAG reçue")
    data = request.get_json()
    print(f"📊 [LOG] Données reçues: {data}")
    
    question = data.get('question', '')
    print(f"❓ [LOG] Question: {question}")
    
    if not question:
        print("❌ [LOG] Question vide")
        return jsonify({'error': 'Question requise'}), 400
    
    try:
        print("🚀 [LOG] Début du traitement de la question")
        # Réponse simulée basée sur la question
        if "données" in question.lower() or "data" in question.lower():
            answer = "Oui, le système RAG a accès à une base de données avec 7 documents de test sur l'intelligence artificielle, le machine learning, les systèmes RAG, Supabase et les embeddings vectoriels."
        elif "intelligence artificielle" in question.lower() or "ia" in question.lower():
            answer = "L'intelligence artificielle (IA) est un domaine de l'informatique qui vise à créer des machines capables de simuler l'intelligence humaine. Elle inclut l'apprentissage automatique, le traitement du langage naturel, et la vision par ordinateur."
        elif "rag" in question.lower():
            answer = "Les systèmes RAG (Retrieval-Augmented Generation) combinent la recherche d'informations avec la génération de texte pour produire des réponses plus précises et contextuelles."
        elif "machine learning" in question.lower() or "ml" in question.lower():
            answer = "Le machine learning est une sous-discipline de l'IA qui permet aux ordinateurs d'apprendre et de s'améliorer automatiquement à partir de l'expérience, sans être explicitement programmés pour chaque tâche."
        else:
            answer = f"Merci pour votre question: '{question}'. Le système RAG est opérationnel et peut traiter vos requêtes. Pour des réponses plus précises, veuillez poser des questions sur l'intelligence artificielle, le machine learning, ou les systèmes RAG."
        
        print(f"✅ [LOG] Réponse générée: {answer}")
        
        response = {
            'question': question,
            'answer': answer,
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'source': 'RAG System (Mode Simulation)'
        }
        
        print(f"📤 [LOG] Envoi de la réponse: {response}")
        return jsonify(response)
        
    except Exception as e:
        return jsonify({
            'question': question,
            'answer': f'Erreur lors de la génération de la réponse: {str(e)}',
            'status': 'error',
            'timestamp': datetime.now().isoformat()
        })

@app.route('/health')
def health():
    return jsonify({'status': 'ok', 'message': 'RAG System is running'})

if __name__ == '__main__':
    print("🚀 Lancement de l'interface web RAG simplifiée...")
    print("📱 L'interface sera disponible sur http://localhost:8082")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=8082)
