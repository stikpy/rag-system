#!/bin/bash
# Script pour lancer l'interface web RAG

echo "🚀 Lancement de l'interface web RAG..."
echo ""

# Vérifier que les variables d'environnement sont chargées
if [ ! -f ".env.local" ]; then
    echo "⚠️  Fichier .env.local non trouvé. Copiez .env.example vers .env.local et configurez vos clés API."
    echo "   cp .env.example .env.local"
    echo ""
fi

echo "🌐 Interface web disponible sur:"
echo "   📱 Flask: http://localhost:5000"
echo "   📊 Prisma Studio: http://localhost:5555"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter"
echo ""

# Lancer Flask
python3 web_app.py

