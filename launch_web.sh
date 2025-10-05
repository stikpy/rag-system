#!/bin/bash
# Script pour lancer l'interface web RAG

echo "🚀 Lancement de l'interface web RAG..."
echo "📱 L'interface sera disponible sur http://localhost:8501"
echo "🛑 Appuyez sur Ctrl+C pour arrêter"
echo ""

# Vérifier que les variables d'environnement sont chargées
if [ ! -f ".env.local" ]; then
    echo "⚠️  Fichier .env.local non trouvé. Copiez .env.example vers .env.local et configurez vos clés API."
    exit 1
fi

# Lancer Streamlit
python3 -m streamlit run app.py --server.port 8501 --server.address localhost

