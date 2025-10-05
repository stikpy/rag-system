#!/bin/bash
# Script pour lancer l'interface web RAG

echo "🚀 Lancement de l'interface web RAG..."
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
pkill -f "python3.*web_app.py" 2>/dev/null || true
pkill -f "python3.*simple_web.py" 2>/dev/null || true
sleep 2

echo "🌐 Lancement de l'interface web..."
echo "📱 L'interface sera disponible sur http://localhost:8080"
echo "🔧 Prisma Studio disponible sur http://localhost:5555"
echo ""

# Lancer l'interface
python3 simple_web.py
