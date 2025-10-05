#!/bin/bash
# Script pour lancer l'interface web RAG complète avec upload de documents

echo "🚀 Lancement de l'interface web RAG complète..."
echo ""

# Vérifier que les variables d'environnement sont chargées
if [ ! -f ".env.local" ]; then
    echo "⚠️  Fichier .env.local non trouvé."
    echo "   Copiez .env.example vers .env.local et configurez vos clés API:"
    echo "   cp .env.example .env.local"
    echo ""
fi

# Arrêter toute application existante
echo "🛑 Arrêt des applications existantes..."
pkill -f "python3.*simple_web.py" 2>/dev/null || true
pkill -f "python3.*rag_web_app.py" 2>/dev/null || true
sleep 2

# Créer le dossier uploads s'il n'existe pas
mkdir -p uploads

echo "🌐 Lancement de l'interface web complète..."
echo "📱 Interface principale: http://localhost:8080"
echo "📄 Fonctionnalités: Upload de documents, Test RAG, Gestion BDD"
echo "🔧 Prisma Studio: http://localhost:5555"
echo ""

# Lancer l'interface
python3 rag_web_app.py
