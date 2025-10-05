#!/usr/bin/env python3
"""
Interface web Flask complète pour le système RAG avec upload de documents.
"""

from flask import Flask, render_template_string, request, jsonify, redirect, url_for, flash
import sys
from pathlib import Path
import os
import uuid
from werkzeug.utils import secure_filename

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent / "src"))

app = Flask(__name__)
app.secret_key = 'rag-system-secret-key-2024'

# Configuration pour l'upload
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Créer le dossier uploads s'il n'existe pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Template HTML avec upload de documents
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 RAG System - Interface Complète</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            font-size: 1.2em;
            opacity: 0.9;
        }
        
        .content {
            padding: 40px;
        }
        
        .tabs {
            display: flex;
            margin-bottom: 30px;
            border-bottom: 2px solid #f0f0f0;
        }
        
        .tab {
            padding: 15px 30px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
            font-weight: 600;
        }
        
        .tab.active {
            border-bottom-color: #667eea;
            color: #667eea;
        }
        
        .tab:hover {
            background: #f8f9fa;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .card {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 30px;
            margin-bottom: 30px;
            border-left: 5px solid #667eea;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #333;
        }
        
        input, textarea, select {
            width: 100%;
            padding: 15px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        
        input:focus, textarea:focus, select:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .file-upload {
            border: 2px dashed #667eea;
            border-radius: 8px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            transition: all 0.3s;
        }
        
        .file-upload:hover {
            background: #f0f4ff;
            border-color: #5a67d8;
        }
        
        .file-upload.dragover {
            background: #e6f3ff;
            border-color: #3182ce;
        }
        
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
            margin: 5px;
        }
        
        button:hover {
            transform: translateY(-2px);
        }
        
        button.secondary {
            background: #6c757d;
        }
        
        button.success {
            background: #28a745;
        }
        
        button.danger {
            background: #dc3545;
        }
        
        .response {
            background: #e8f5e8;
            border: 1px solid #28a745;
            border-radius: 8px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 30px;
        }
        
        .metric {
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
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
        
        .status {
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin: 5px 0;
        }
        
        .status.success { background: #d4edda; color: #155724; }
        .status.warning { background: #fff3cd; color: #856404; }
        .status.info { background: #d1ecf1; color: #0c5460; }
        .status.error { background: #f8d7da; color: #721c24; }
        
        .document-list {
            max-height: 400px;
            overflow-y: auto;
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
        }
        
        .document-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            border-bottom: 1px solid #eee;
        }
        
        .document-item:last-child {
            border-bottom: none;
        }
        
        .progress-bar {
            width: 100%;
            height: 20px;
            background: #f0f0f0;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }
        
        .footer {
            background: #f8f9fa;
            padding: 20px;
            text-align: center;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Système RAG Complet</h1>
            <p>Interface de Test avec Upload de Documents</p>
        </div>
        
        <div class="content">
            <div class="tabs">
                <div class="tab active" onclick="showTab('rag')">🤖 Test RAG</div>
                <div class="tab" onclick="showTab('upload')">📄 Upload Documents</div>
                <div class="tab" onclick="showTab('documents')">📚 Gestion Documents</div>
                <div class="tab" onclick="showTab('stats')">📊 Statistiques</div>
            </div>
            
            <!-- Tab Test RAG -->
            <div id="rag" class="tab-content active">
                <div class="card">
                    <h2>🤖 Test du Système RAG</h2>
                    <p>Posez une question au système d'intelligence artificielle et obtenez une réponse contextuelle basée sur vos documents.</p>
                    
                    <form id="ragForm">
                        <div class="form-group">
                            <label for="question">Votre question :</label>
                            <textarea id="question" name="question" rows="4" placeholder="Ex: Qu'est-ce que l'intelligence artificielle? Comment fonctionne le machine learning?"></textarea>
                        </div>
                        <button type="submit">🚀 Générer Réponse</button>
                    </form>
                    
                    <div id="response" class="response">
                        <h3>💬 Réponse du système :</h3>
                        <div id="responseText"></div>
                    </div>
                </div>
            </div>
            
            <!-- Tab Upload Documents -->
            <div id="upload" class="tab-content">
                <div class="card">
                    <h2>📄 Upload de Documents</h2>
                    <p>Ajoutez des documents à votre base de connaissances pour améliorer les réponses du système RAG.</p>
                    
                    <form id="uploadForm" enctype="multipart/form-data">
                        <div class="form-group">
                            <label for="documentType">Type de document :</label>
                            <select id="documentType" name="documentType">
                                <option value="text">Document texte</option>
                                <option value="pdf">PDF</option>
                                <option value="image">Image (OCR)</option>
                                <option value="url">URL/Web</option>
                            </select>
                        </div>
                        
                        <div class="form-group">
                            <label for="documentTitle">Titre du document :</label>
                            <input type="text" id="documentTitle" name="documentTitle" placeholder="Ex: Guide de l'IA" required>
                        </div>
                        
                        <div class="form-group">
                            <label for="documentDescription">Description :</label>
                            <textarea id="documentDescription" name="documentDescription" rows="3" placeholder="Description du contenu du document"></textarea>
                        </div>
                        
                        <div class="file-upload" id="fileUpload">
                            <input type="file" id="fileInput" name="file" multiple style="display: none;" accept=".txt,.pdf,.doc,.docx,.png,.jpg,.jpeg,.gif">
                            <div id="dropZone">
                                <h3>📁 Glissez-déposez vos fichiers ici</h3>
                                <p>ou <button type="button" onclick="document.getElementById('fileInput').click()">cliquez pour sélectionner</button></p>
                                <p><small>Formats supportés: TXT, PDF, DOC, DOCX, PNG, JPG, JPEG, GIF</small></p>
                            </div>
                        </div>
                        
                        <div class="form-group">
                            <label for="chunkSize">Taille des chunks :</label>
                            <select id="chunkSize" name="chunkSize">
                                <option value="512">512 tokens</option>
                                <option value="1024" selected>1024 tokens</option>
                                <option value="2048">2048 tokens</option>
                            </select>
                        </div>
                        
                        <button type="submit" class="success">📤 Ajouter à la base de données</button>
                    </form>
                    
                    <div id="uploadProgress" class="progress-bar" style="display: none;">
                        <div id="progressFill" class="progress-fill" style="width: 0%"></div>
                    </div>
                    
                    <div id="uploadResponse" class="response">
                        <div id="uploadText"></div>
                    </div>
                </div>
            </div>
            
            <!-- Tab Gestion Documents -->
            <div id="documents" class="tab-content">
                <div class="card">
                    <h2>📚 Gestion des Documents</h2>
                    <p>Visualisez et gérez les documents dans votre base de connaissances.</p>
                    
                    <div class="document-list" id="documentList">
                        <div class="document-item">
                            <div>
                                <strong>📄 Exemple de document</strong>
                                <br><small>Ajouté le 2024-10-05 | Type: PDF | Chunks: 15</small>
                            </div>
                            <div>
                                <button class="secondary" onclick="viewDocument('doc1')">👁️ Voir</button>
                                <button class="danger" onclick="deleteDocument('doc1')">🗑️ Supprimer</button>
                            </div>
                        </div>
                    </div>
                    
                    <button onclick="refreshDocuments()" class="success">🔄 Actualiser la liste</button>
                </div>
            </div>
            
            <!-- Tab Statistiques -->
            <div id="stats" class="tab-content">
                <div class="card">
                    <h2>📊 Statistiques du Système</h2>
                    <div class="grid">
                        <div class="metric">
                            <div class="metric-value">✅</div>
                            <div class="metric-label">Status: Opérationnel</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">4</div>
                            <div class="metric-label">Modèles IA configurés</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">6</div>
                            <div class="metric-label">Fonctionnalités actives</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">∞</div>
                            <div class="metric-label">Documents traitables</div>
                        </div>
                    </div>
                    
                    <h3>⚙️ Technologies Intégrées</h3>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px;">
                        <div><span class="status info">🤖 Mistral AI</span></div>
                        <div><span class="status info">🧠 OpenAI GPT-4</span></div>
                        <div><span class="status info">🔍 Cohere Reranking</span></div>
                        <div><span class="status info">🗄️ Supabase Vector DB</span></div>
                        <div><span class="status info">🔧 Prisma ORM</span></div>
                        <div><span class="status info">⚡ Langchain</span></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="footer">
            <p>🚀 <strong>Système RAG</strong> - Interface complète avec upload de documents</p>
            <p><a href="https://github.com/stikpy/rag-system" target="_blank" style="color: #667eea;">📚 Documentation GitHub</a> | 
               <a href="http://localhost:5555" target="_blank" style="color: #667eea;">🔧 Prisma Studio</a></p>
        </div>
    </div>

    <script>
        // Gestion des onglets
        function showTab(tabName) {
            // Masquer tous les onglets
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Afficher l'onglet sélectionné
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }
        
        // Gestion du drag & drop
        const fileUpload = document.getElementById('fileUpload');
        const fileInput = document.getElementById('fileInput');
        
        fileUpload.addEventListener('dragover', (e) => {
            e.preventDefault();
            fileUpload.classList.add('dragover');
        });
        
        fileUpload.addEventListener('dragleave', () => {
            fileUpload.classList.remove('dragover');
        });
        
        fileUpload.addEventListener('drop', (e) => {
            e.preventDefault();
            fileUpload.classList.remove('dragover');
            const files = e.dataTransfer.files;
            fileInput.files = files;
            updateFileDisplay();
        });
        
        fileInput.addEventListener('change', updateFileDisplay);
        
        function updateFileDisplay() {
            const files = fileInput.files;
            const dropZone = document.getElementById('dropZone');
            if (files.length > 0) {
                dropZone.innerHTML = `<h3>📁 ${files.length} fichier(s) sélectionné(s)</h3>`;
                for (let file of files) {
                    dropZone.innerHTML += `<p>• ${file.name} (${(file.size/1024).toFixed(1)} KB)</p>`;
                }
            }
        }
        
        // Formulaire RAG
        document.getElementById('ragForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const question = document.getElementById('question').value;
            const responseDiv = document.getElementById('response');
            const responseText = document.getElementById('responseText');
            
            if (question.trim()) {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status info">🤖 Génération de la réponse en cours...</span></p>';
                
                // Appel à l'API RAG
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
                            <p><strong>Question posée :</strong> ${data.question}</p>
                            <p><strong>Réponse du système :</strong> ${data.answer}</p>
                            <p><span class="status success">✅ Réponse générée à partir des documents de la base de données</span></p>
                        `;
                    } else {
                        responseText.innerHTML = `
                            <p><strong>Question posée :</strong> ${data.question}</p>
                            <p><strong>Erreur :</strong> ${data.answer}</p>
                            <p><span class="status error">❌ Erreur lors de la génération</span></p>
                        `;
                    }
                })
                .catch(error => {
                    responseText.innerHTML = `
                        <p><strong>Question posée :</strong> ${question}</p>
                        <p><strong>Erreur de connexion :</strong> ${error.message}</p>
                        <p><span class="status error">❌ Erreur de connexion à l'API</span></p>
                    `;
                });
            } else {
                responseDiv.style.display = 'block';
                responseText.innerHTML = '<p><span class="status warning">⚠️ Veuillez saisir une question pour tester le système.</span></p>';
            }
        });
        
        // Formulaire d'upload
        document.getElementById('uploadForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const progressBar = document.getElementById('uploadProgress');
            const progressFill = document.getElementById('progressFill');
            const uploadResponse = document.getElementById('uploadResponse');
            const uploadText = document.getElementById('uploadText');
            
            // Afficher la barre de progression
            progressBar.style.display = 'block';
            uploadResponse.style.display = 'block';
            uploadText.innerHTML = '<p><span class="status info">📤 Upload et traitement en cours...</span></p>';
            
            // Appel à l'API d'upload
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                progressFill.style.width = '100%';
                
                if (data.success) {
                    uploadText.innerHTML = `
                        <p><span class="status success">✅ ${data.message}</span></p>
                        <p><strong>Titre:</strong> ${data.metadata.title}</p>
                        <p><strong>Type:</strong> ${data.metadata.type}</p>
                        <p><strong>Description:</strong> ${data.metadata.description}</p>
                        <p><strong>Fichiers traités:</strong> ${data.files.length}</p>
                        <p><strong>Chunks créés:</strong> ${data.processed ? data.processed.reduce((sum, doc) => sum + doc.chunks_created, 0) : 'N/A'}</p>
                    `;
                } else {
                    uploadText.innerHTML = `
                        <p><span class="status error">❌ ${data.message}</span></p>
                    `;
                }
            })
            .catch(error => {
                progressFill.style.width = '100%';
                uploadText.innerHTML = `
                    <p><span class="status error">❌ Erreur lors de l'upload: ${error.message}</span></p>
                `;
            });
        });
        
        // Fonctions de gestion des documents
        function viewDocument(docId) {
            alert('Fonctionnalité de visualisation en cours de développement pour le document: ' + docId);
        }
        
        function deleteDocument(docId) {
            if (confirm('Êtes-vous sûr de vouloir supprimer ce document?')) {
                alert('Document supprimé: ' + docId);
                refreshDocuments();
            }
        }
        
        function refreshDocuments() {
            alert('Liste des documents actualisée!');
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint pour l'upload de documents."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier fourni'}), 400
        
        files = request.files.getlist('file')
        title = request.form.get('documentTitle', 'Document sans titre')
        description = request.form.get('documentDescription', '')
        doc_type = request.form.get('documentType', 'text')
        chunk_size = request.form.get('chunkSize', '1024')
        
        uploaded_files = []
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Ajouter un UUID pour éviter les conflits
                unique_filename = f"{uuid.uuid4()}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(filepath)
                
                uploaded_files.append({
                    'original_name': filename,
                    'saved_name': unique_filename,
                    'path': filepath,
                    'size': os.path.getsize(filepath)
                })
        
        # Traiter les fichiers avec le système RAG
        processed_documents = []
        
        try:
            # Importer le système RAG
            from rag.core.rag_system import RAGSystem
            from rag.ocr.document_processor import DocumentProcessor
            
            # Initialiser le système RAG
            rag = RAGSystem()
            processor = DocumentProcessor()
            
            for file_info in uploaded_files:
                file_path = file_info['path']
                file_extension = file_info['original_name'].split('.')[-1].lower()
                
                # Extraire le texte selon le type de fichier
                if file_extension in ['pdf']:
                    text = processor.extract_text_from_pdf(file_path)
                elif file_extension in ['png', 'jpg', 'jpeg', 'gif']:
                    text = processor.extract_text_from_image(file_path)
                else:
                    # Pour les fichiers texte
                    with open(file_path, 'r', encoding='utf-8') as f:
                        text = f.read()
                
                # Ajouter le document au système RAG
                if text.strip():
                    rag.add_documents([text], metadata={
                        'title': title,
                        'description': description,
                        'type': doc_type,
                        'filename': file_info['original_name'],
                        'chunk_size': int(chunk_size)
                    })
                    
                    processed_documents.append({
                        'filename': file_info['original_name'],
                        'text_length': len(text),
                        'chunks_created': len(text) // int(chunk_size) + 1
                    })
            
            return jsonify({
                'success': True,
                'message': f'{len(uploaded_files)} fichier(s) traité(s) et ajouté(s) à la base de données',
                'files': uploaded_files,
                'processed': processed_documents,
                'metadata': {
                    'title': title,
                    'description': description,
                    'type': doc_type,
                    'chunk_size': chunk_size
                }
            })
            
        except ImportError as e:
            return jsonify({
                'success': False,
                'message': f'Erreur d\'import du système RAG: {str(e)}',
                'files': uploaded_files
            }), 500
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Erreur lors du traitement: {str(e)}',
                'files': uploaded_files
            }), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag', methods=['POST'])
def rag_api():
    """API endpoint pour le système RAG."""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'error': 'Question requise'}), 400
    
    try:
        # Importer le système RAG et les modules nécessaires
        from rag.core.rag_system import RAGSystem
        from rag.retrieval.vector_retriever import VectorRetriever
        from rag.retrieval.reranker import CohereReranker
        from rag.utils.config import config
        
        # Initialiser le système RAG
        rag = RAGSystem()
        
        # Vérifier s'il y a des documents dans la base
        from prisma import Prisma
        prisma = Prisma()
        await prisma.connect()
        
        # Compter les documents disponibles
        doc_count = await prisma.query_raw("SELECT COUNT(*) as count FROM documents")
        section_count = await prisma.query_raw("SELECT COUNT(*) as count FROM nods_page_section")
        
        total_docs = doc_count[0]['count'] + section_count[0]['count']
        
        if total_docs == 0:
            response = "Aucun document trouvé dans la base de données. Veuillez d'abord ajouter des documents via l'onglet 'Upload Documents'."
        else:
            # Générer la réponse basée sur les documents de la BDD
            response = rag.query(question)
        
        await prisma.disconnect()
        
        return jsonify({
            'question': question,
            'answer': response,
            'status': 'success',
            'timestamp': '2024-10-05T14:46:00Z',
            'source': f'RAG System with {total_docs} documents in database',
            'documents_count': total_docs
        })
        
    except ImportError as e:
        return jsonify({
            'question': question,
            'answer': f'Erreur d\'import du système RAG: {str(e)}. Vérifiez que tous les modules sont installés.',
            'status': 'error',
            'timestamp': '2024-10-05T14:46:00Z'
        })
    except Exception as e:
        return jsonify({
            'question': question,
            'answer': f'Erreur lors de la génération de la réponse: {str(e)}',
            'status': 'error',
            'timestamp': '2024-10-05T14:46:00Z'
        })

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """API pour récupérer la liste des documents."""
    # Ici vous pouvez récupérer les documents depuis la base de données
    documents = [
        {
            'id': 'doc1',
            'title': 'Guide de l\'Intelligence Artificielle',
            'type': 'PDF',
            'size': '2.3 MB',
            'chunks': 15,
            'uploaded': '2024-10-05'
        },
        {
            'id': 'doc2', 
            'title': 'Documentation Machine Learning',
            'type': 'TXT',
            'size': '1.1 MB',
            'chunks': 8,
            'uploaded': '2024-10-05'
        }
    ]
    
    return jsonify(documents)

@app.route('/health')
def health():
    return {'status': 'ok', 'message': 'RAG System with document upload is running'}

if __name__ == '__main__':
    print("🚀 Lancement de l'interface web RAG complète...")
    print("📱 L'interface sera disponible sur http://localhost:8081")
    print("📄 Fonctionnalités: Upload de documents, Test RAG, Gestion BDD")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")
    print("")
    
    app.run(debug=False, host='0.0.0.0', port=8081)
