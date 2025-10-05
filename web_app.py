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
<html lang=\"fr\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>🚀 RAG System - Interface de Test</title>
    <style>
        :root {
            --bg-color: #0f172a;
            --bg-gradient: radial-gradient(circle at 20% 20%, rgba(59,130,246,0.35), transparent 55%),
                              radial-gradient(circle at 80% 0%, rgba(236,72,153,0.35), transparent 55%),
                              #0f172a;
            --card-bg: rgba(15, 23, 42, 0.72);
            --card-border: rgba(148, 163, 184, 0.15);
            --text-primary: #f8fafc;
            --text-secondary: #cbd5f5;
            --accent: linear-gradient(135deg, #6366f1 0%, #ec4899 100%);
            --accent-strong: #6366f1;
            --success: #22c55e;
            --warning: #f59e0b;
            --error: #ef4444;
            color-scheme: dark;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-gradient);
            color: var(--text-primary);
            display: flex;
            justify-content: center;
            padding: 32px 16px 48px;
        }

        main {
            width: min(1180px, 100%);
            display: flex;
            flex-direction: column;
            gap: 28px;
        }

        header {
            padding: 28px 32px;
            border-radius: 26px;
            background: rgba(15, 23, 42, 0.78);
            border: 1px solid var(--card-border);
            box-shadow: 0 18px 60px rgba(15, 23, 42, 0.45);
            position: relative;
            overflow: hidden;
        }

        header::after {
            content: '';
            position: absolute;
            inset: 0;
            background: radial-gradient(circle at top right, rgba(99,102,241,0.35), transparent 45%);
            pointer-events: none;
        }

        header h1 {
            margin: 0 0 12px;
            font-size: clamp(1.8rem, 2.5vw + 1rem, 2.6rem);
            font-weight: 700;
            letter-spacing: -0.02em;
        }

        header p {
            margin: 0;
            color: var(--text-secondary);
            font-size: 1.05rem;
        }

        .header-actions {
            margin-top: 22px;
            display: flex;
            flex-wrap: wrap;
            gap: 12px;
        }

        .chip {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 16px;
            border-radius: 999px;
            border: 1px solid rgba(148, 163, 184, 0.3);
            background: rgba(30, 41, 59, 0.68);
            font-size: 0.95rem;
            font-weight: 500;
            color: var(--text-secondary);
            backdrop-filter: blur(16px);
        }

        .chip[data-status=\"operational\"] {
            border-color: rgba(34, 197, 94, 0.35);
            color: #bbf7d0;
        }

        .chip[data-status=\"degraded\"] {
            border-color: rgba(245, 158, 11, 0.35);
            color: #fde68a;
        }

        .chip[data-status=\"offline\"] {
            border-color: rgba(239, 68, 68, 0.35);
            color: #fecaca;
        }

        .dashboard-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 24px;
        }

        .card {
            position: relative;
            padding: 26px;
            border-radius: 24px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            box-shadow: 0 16px 40px rgba(15, 23, 42, 0.35);
            display: flex;
            flex-direction: column;
            gap: 20px;
            backdrop-filter: blur(18px);
        }

        .card h2 {
            margin: 0;
            font-size: 1.3rem;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .card h2 span {
            display: inline-flex;
            width: 38px;
            height: 38px;
            align-items: center;
            justify-content: center;
            border-radius: 14px;
            background: rgba(99, 102, 241, 0.18);
            font-size: 1.1rem;
        }

        .card p,
        .card li,
        label {
            color: var(--text-secondary);
            line-height: 1.6;
        }

        .card ul {
            margin: 0;
            padding-left: 20px;
            display: grid;
            gap: 8px;
        }

        textarea {
            width: 100%;
            min-height: 150px;
            padding: 16px;
            border-radius: 18px;
            border: 1px solid rgba(99, 102, 241, 0.25);
            background: rgba(15, 23, 42, 0.85);
            color: var(--text-primary);
            font-size: 1rem;
            resize: vertical;
            transition: border-color 0.2s ease, box-shadow 0.2s ease;
        }

        textarea:focus {
            outline: none;
            border-color: rgba(236, 72, 153, 0.45);
            box-shadow: 0 0 0 4px rgba(99, 102, 241, 0.18);
        }

        .primary-button {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 14px 22px;
            font-size: 1rem;
            font-weight: 600;
            border-radius: 16px;
            background-image: var(--accent);
            color: white;
            border: none;
            cursor: pointer;
            transition: transform 0.18s ease, box-shadow 0.18s ease;
        }

        .primary-button:hover:not([disabled]) {
            transform: translateY(-2px);
            box-shadow: 0 12px 30px rgba(99, 102, 241, 0.35);
        }

        .primary-button[disabled] {
            opacity: 0.65;
            cursor: progress;
        }

        .response-panel {
            display: none;
            flex-direction: column;
            gap: 14px;
            padding: 20px;
            border-radius: 18px;
            background: rgba(30, 41, 59, 0.75);
            border: 1px solid rgba(99, 102, 241, 0.18);
        }

        .response-panel.active {
            display: flex;
            animation: fadeIn 0.32s ease;
        }

        .response-meta {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            font-size: 0.95rem;
            color: var(--text-secondary);
        }

        .badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            padding: 6px 12px;
            border-radius: 999px;
            font-size: 0.85rem;
            background: rgba(99, 102, 241, 0.12);
            color: var(--text-primary);
        }

        .badge.success { background: rgba(34, 197, 94, 0.15); color: #bbf7d0; }
        .badge.warning { background: rgba(245, 158, 11, 0.18); color: #fde68a; }
        .badge.error { background: rgba(239, 68, 68, 0.18); color: #fecaca; }

        .history-list {
            display: grid;
            gap: 12px;
            margin: 0;
            padding: 0;
            list-style: none;
        }

        .history-item {
            padding: 16px;
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background: rgba(15, 23, 42, 0.72);
            display: grid;
            gap: 8px;
        }

        .history-item span {
            font-size: 0.85rem;
            color: rgba(148, 163, 184, 0.85);
        }

        .links-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 12px;
        }

        .link-tile {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 14px 18px;
            border-radius: 16px;
            border: 1px solid rgba(148, 163, 184, 0.2);
            background: rgba(30, 41, 59, 0.75);
            color: var(--text-secondary);
            text-decoration: none;
            transition: transform 0.18s ease, border-color 0.18s ease;
        }

        .link-tile:hover {
            transform: translateY(-2px);
            border-color: rgba(236, 72, 153, 0.38);
            color: white;
        }

        .loader {
            display: none;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            border: 3px solid rgba(255, 255, 255, 0.25);
            border-top-color: white;
            animation: spin 0.8s linear infinite;
        }

        .loader.active {
            display: inline-flex;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(6px); }
            to { opacity: 1; transform: translateY(0); }
        }

        @media (max-width: 720px) {
            body {
                padding: 24px 12px 36px;
            }

            header, .card {
                padding: 22px;
            }

            .header-actions {
                gap: 10px;
            }
        }
    </style>
</head>
<body>
    <main>
        <header>
            <h1>🚀 Interface de test du système RAG</h1>
            <p>Formulez une question, visualisez la réponse générée et surveillez l'état du pipeline en temps réel.</p>
            <div class=\"header-actions\">
                <span id=\"statusChip\" class=\"chip\" data-status=\"loading\">⏳ Vérification du statut…</span>
                <span class=\"chip\">⚡️ Embeddings multi-fournisseurs</span>
                <span class=\"chip\">🛡️ Observabilité intégrée</span>
            </div>
        </header>

        <div class=\"dashboard-grid\">
            <section class=\"card\">
                <h2><span>🤖</span>Tester le RAG</h2>
                <form id=\"ragForm\" autocomplete=\"off\">
                    <label for=\"question\">Votre question</label>
                    <textarea id=\"question\" name=\"question\" placeholder=\"Ex. Comment le pipeline gère-t-il l'OCR sur les PDF ?\" required></textarea>
                    <div style=\"display:flex;align-items:center;gap:12px;flex-wrap:wrap;\">
                        <button id=\"submitBtn\" class=\"primary-button\" type=\"submit\">
                            <span id=\"submitIcon\">🚀</span>
                            <span>Générer la réponse</span>
                        </button>
                        <div id=\"loadingIndicator\" class=\"loader\"></div>
                        <span id=\"formHelper\" style=\"color:var(--text-secondary);font-size:0.9rem;\">Aucune donnée n'est stockée — vos requêtes restent locales.</span>
                    </div>
                </form>

                <div id=\"responsePanel\" class=\"response-panel\">
                    <div class=\"response-meta\">
                        <span class=\"badge\" id=\"timestampBadge\">🕒 En attente</span>
                        <span class=\"badge success\" id=\"statusBadge\">Prêt</span>
                    </div>
                    <div id=\"responseText\" style=\"white-space:pre-line;font-size:1rem;line-height:1.7;\"></div>
                </div>
            </section>

            <section class=\"card\">
                <h2><span>📊</span>État du pipeline</h2>
                <div class=\"history-list\">
                    <div class=\"history-item\">
                        <strong>Modules actifs</strong>
                        <span id=\"modulesList\">Chargement…</span>
                    </div>
                    <div class=\"history-item\">
                        <strong>Modèles disponibles</strong>
                        <span id=\"modelsList\">Chargement…</span>
                    </div>
                    <div class=\"history-item\">
                        <strong>Version</strong>
                        <span id=\"versionInfo\">—</span>
                    </div>
                </div>
            </section>

            <section class=\"card\">
                <h2><span>🕑</span>Historique des requêtes</h2>
                <ul id=\"historyList\" class=\"history-list\">
                    <li class=\"history-item\" data-placeholder>
                        <strong>Aucun échange pour le moment.</strong>
                        <span>Les questions récentes apparaîtront ici pour faciliter vos itérations.</span>
                    </li>
                </ul>
            </section>
        </div>

        <section class=\"card\">
            <h2><span>🧩</span>Architecture & Intégrations</h2>
            <p>Le système RAG s'appuie sur un pipeline modulaire capable de gérer l'ingestion de documents, la vectorisation multi-fournisseurs et la génération assistée par contexte.</p>
            <ul>
                <li>📄 OCR & pré-traitement pour les PDF, images et textes bruts.</li>
                <li>🔍 Stockage vectoriel Supabase & recherches par similarité cosinus.</li>
                <li>🧠 Générateurs compatibles (OpenAI, Mistral, Cohere) orchestrés via le cœur RAG.</li>
                <li>📈 Observabilité : métriques de latence, suivi des versions et monitoring des modules.</li>
            </ul>
        </section>

        <section class=\"card\">
            <h2><span>🔗</span>Ressources utiles</h2>
            <div class=\"links-grid\">
                <a class=\"link-tile\" href=\"https://github.com/stikpy/rag-system\" target=\"_blank\">📚 Documentation GitHub</a>
                <a class=\"link-tile\" href=\"http://localhost:5555\" target=\"_blank\">🔧 Prisma Studio</a>
                <a class=\"link-tile\" href=\"http://localhost:8501\" target=\"_blank\">📱 Interface Streamlit</a>
            </div>
        </section>
    </main>

    <script>
        (function () {
            var form = document.getElementById('ragForm');
            var questionInput = document.getElementById('question');
            var submitBtn = document.getElementById('submitBtn');
            var submitIcon = document.getElementById('submitIcon');
            var loader = document.getElementById('loadingIndicator');
            var responsePanel = document.getElementById('responsePanel');
            var responseText = document.getElementById('responseText');
            var timestampBadge = document.getElementById('timestampBadge');
            var statusBadge = document.getElementById('statusBadge');
            var historyList = document.getElementById('historyList');
            var statusChip = document.getElementById('statusChip');
            var modulesList = document.getElementById('modulesList');
            var modelsList = document.getElementById('modelsList');
            var versionInfo = document.getElementById('versionInfo');
            var formHelper = document.getElementById('formHelper');

            var statusLabels = {
                operational: '✅ Système opérationnel',
                degraded: '⚠️ Système dégradé',
                offline: '❌ Système hors-ligne',
                loading: '⏳ Vérification du statut…'
            };

            var history = [];

            function updateStatusChip(status) {
                statusChip.setAttribute('data-status', status);
                statusChip.textContent = statusLabels[status] || statusLabels.loading;
            }

            function setLoadingState(isLoading) {
                submitBtn.disabled = isLoading;
                if (isLoading) {
                    loader.classList.add('active');
                    statusBadge.className = 'badge warning';
                    statusBadge.textContent = '⏳ Génération en cours…';
                    timestampBadge.textContent = '🕒 —';
                } else {
                    loader.classList.remove('active');
                }
                submitIcon.textContent = isLoading ? '⏳' : '🚀';
                formHelper.textContent = isLoading
                    ? 'Génération en cours…'
                    : "Aucune donnée n'est stockée — vos requêtes restent locales.";
            }

            function renderResponse(question, answer, formattedTimestamp) {
                responsePanel.classList.add('active');
                statusBadge.className = 'badge success';
                statusBadge.textContent = '✅ Réponse générée';

                timestampBadge.textContent = '🕒 ' + formattedTimestamp;

                responseText.innerHTML = '';

                var questionBlock = document.createElement('div');
                var questionLabel = document.createElement('strong');
                questionLabel.textContent = 'Question';
                questionBlock.appendChild(questionLabel);
                questionBlock.appendChild(document.createElement('br'));
                questionBlock.appendChild(document.createTextNode(question));

                var answerBlock = document.createElement('div');
                answerBlock.style.marginTop = '14px';
                var answerLabel = document.createElement('strong');
                answerLabel.textContent = 'Réponse';
                answerBlock.appendChild(answerLabel);
                answerBlock.appendChild(document.createElement('br'));
                answerBlock.appendChild(document.createTextNode(answer));

                responseText.appendChild(questionBlock);
                responseText.appendChild(answerBlock);
            }

            function renderHistory() {
                historyList.innerHTML = '';

                if (history.length === 0) {
                    var placeholder = document.createElement('li');
                    placeholder.className = 'history-item';
                    placeholder.setAttribute('data-placeholder', '');

                    var title = document.createElement('strong');
                    title.textContent = 'Aucun échange pour le moment.';
                    var subtitle = document.createElement('span');
                    subtitle.textContent = 'Les questions récentes apparaîtront ici pour faciliter vos itérations.';

                    placeholder.appendChild(title);
                    placeholder.appendChild(subtitle);
                    historyList.appendChild(placeholder);
                    return;
                }

                history.forEach(function (entry) {
                    var item = document.createElement('li');
                    item.className = 'history-item';

                    var questionEl = document.createElement('strong');
                    questionEl.textContent = entry.question;

                    var answerEl = document.createElement('span');
                    answerEl.textContent = entry.answer;

                    var timeEl = document.createElement('span');
                    timeEl.textContent = '🕒 ' + entry.timestamp;

                    item.appendChild(questionEl);
                    item.appendChild(answerEl);
                    item.appendChild(timeEl);
                    historyList.appendChild(item);
                });
            }

            function recordHistory(entry) {
                history.unshift(entry);
                if (history.length > 5) {
                    history.length = 5;
                }
                renderHistory();
            }

            function refreshStatus() {
                fetch('/api/status')
                    .then(function (res) {
                        if (!res.ok) {
                            throw new Error('Réponse invalide');
                        }
                        return res.json();
                    })
                    .then(function (data) {
                        updateStatusChip(data.status || 'operational');
                        modulesList.textContent = (data.modules || []).join(' • ') || '—';
                        modelsList.textContent = (data.models || []).join(' • ') || '—';
                        versionInfo.textContent = data.version || '—';
                    })
                    .catch(function () {
                        updateStatusChip('offline');
                        modulesList.textContent = 'Statut indisponible';
                        modelsList.textContent = 'Statut indisponible';
                        versionInfo.textContent = '—';
                    });
            }

            form.addEventListener('submit', function (event) {
                event.preventDefault();
                var question = questionInput.value.trim();

                if (!question) {
                    responsePanel.classList.add('active');
                    statusBadge.className = 'badge warning';
                    statusBadge.textContent = '⚠️ Veuillez saisir une question.';
                    timestampBadge.textContent = '🕒 —';
                    responseText.textContent = '';
                    return;
                }

                setLoadingState(true);

                fetch('/api/rag', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                })
                    .then(function (res) {
                        if (!res.ok) {
                            throw new Error('Erreur serveur');
                        }
                        return res.json();
                    })
                    .then(function (data) {
                        var timestampSource = data.timestamp ? new Date(data.timestamp) : new Date();
                        var timestampValue = isNaN(timestampSource.getTime()) ? new Date() : timestampSource;
                        var formattedTimestamp = timestampValue.toLocaleString('fr-FR', { hour12: false });
                        var answer = data.answer ? String(data.answer) : '';

                        renderResponse(question, answer, formattedTimestamp);
                        recordHistory({ question: question, answer: answer, timestamp: formattedTimestamp });
                        questionInput.value = '';
                        setLoadingState(false);
                    })
                    .catch(function () {
                        responsePanel.classList.add('active');
                        statusBadge.className = 'badge error';
                        statusBadge.textContent = '❌ Une erreur est survenue';
                        timestampBadge.textContent = '🕒 —';
                        responseText.textContent = "Impossible de générer une réponse. Vérifiez que l'API est disponible.";
                        setLoadingState(false);
                    });
            });

            refreshStatus();
            renderHistory();
            setInterval(refreshStatus, 30000);
        })();
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
    print("📱 L'interface sera disponible sur http://0.0.0.0:5000")
    print("🛑 Appuyez sur Ctrl+C pour arrêter")

    app.run(debug=True, host='0.0.0.0', port=5000)

