# 🚀 Système RAG (Retrieval-Augmented Generation) Complet

Un système RAG avancé intégrant Mistral AI, OpenAI, Supabase, Cohere, Langchain et Prisma pour la génération de réponses contextuelles.

## ✨ Fonctionnalités

### 🤖 Modèles d'IA Intégrés
- **Mistral AI** : Embeddings et génération de texte
- **OpenAI** : GPT-4 pour la génération avancée
- **Cohere** : Reranking pour améliorer la pertinence des résultats

### 🗄️ Base de Données
- **Supabase** : Base de données vectorielle PostgreSQL
- **Prisma** : ORM moderne et type-safe
- **Prisma Studio** : Interface graphique pour la gestion des données

### 🔧 Traitement de Documents
- **OCR** : Extraction de texte depuis PDF scannés et images
- **Langchain** : Chaînes de traitement avancées
- **Chunking** : Découpage intelligent des documents

### 🎯 Fonctionnalités Avancées
- **Reranking** : Amélioration de la qualité de récupération
- **Embeddings** : Représentations vectorielles du texte
- **Recherche sémantique** : Recherche basée sur le sens
- **Génération contextuelle** : Réponses basées sur le contexte récupéré

## 🏗️ Architecture

```
src/
├── rag/
│   ├── core/           # Module principal RAG
│   ├── embeddings/     # Génération d'embeddings
│   ├── retrieval/      # Système de récupération
│   ├── generation/     # Génération de réponses
│   ├── ocr/           # Traitement OCR
│   ├── utils/         # Utilitaires
│   └── langchain/     # Intégration Langchain
├── examples/          # Exemples d'utilisation
├── scripts/           # Scripts utilitaires
└── tests/            # Tests unitaires
```

## 🚀 Installation

### Prérequis
- Python 3.11+
- Node.js (pour Prisma)
- Comptes API : Mistral AI, OpenAI, Cohere, Supabase

### Installation des dépendances

```bash
# Cloner le repository
git clone https://github.com/votre-username/rag-system.git
cd rag-system

# Installer les dépendances Python
pip install -r requirements.txt

# Installer Prisma CLI
npm install -g prisma

# Générer le client Prisma
prisma generate
```

### Configuration

1. **Copier le fichier d'environnement** :
```bash
cp env.local .env.local
```

2. **Configurer les variables d'environnement** dans `.env.local` :
```bash
# Mistral AI
MISTRAL_API_KEY=votre_mistral_api_key

# OpenAI
OPENAI_API_KEY=votre_openai_api_key

# Cohere
COHERE_API_KEY=votre_cohere_api_key

# Supabase
SUPABASE_URL=votre_supabase_url
SUPABASE_PUBLISHABLE_KEY=votre_publishable_key
SUPABASE_SECRET_KEY=votre_secret_key

# Base de données
DATABASE_URL=postgresql://user:password@host:port/database?pgbouncer=true
DIRECT_URL=postgresql://user:password@host:port/database
```

3. **Tester la connexion** :
```bash
python3 scripts/test_final_connection.py
```

## 📖 Utilisation

### Exemple basique

```python
from src.rag.core.rag_system import RAGSystem

# Initialiser le système RAG
rag = RAGSystem()

# Ajouter des documents
rag.add_documents(["document1.pdf", "document2.txt"])

# Poser une question
response = rag.query("Quelle est la réponse à ma question?")
print(response)
```

### Exemple avec OCR

```python
from src.rag.ocr.document_processor import DocumentProcessor

# Traiter un PDF scanné
processor = DocumentProcessor()
text = processor.extract_text_from_pdf("scanned_document.pdf")
print(text)
```

### Exemple avec Langchain

```python
from src.rag.langchain.chains import create_rag_chain

# Créer une chaîne RAG avec Langchain
chain = create_rag_chain()
result = chain.invoke({"question": "Votre question ici"})
```

## 🛠️ Développement

### Lancer Prisma Studio
```bash
prisma studio
```
Accédez à http://localhost:5555 pour visualiser vos données.

### Tests
```bash
# Lancer tous les tests
python -m pytest tests/

# Tests avec couverture
python -m pytest --cov=src tests/
```

### Linting
```bash
# Vérifier le code
flake8 src/
black src/
```

## 📊 Monitoring et Logs

Le système inclut un logging complet :
- Logs structurés avec niveaux configurables
- Monitoring des performances
- Traçabilité des requêtes

## 🔒 Sécurité

- Variables d'environnement pour les clés API
- Validation des entrées utilisateur
- Gestion sécurisée des connexions base de données

## 📈 Performance

- **Embeddings** : Cache intelligent des embeddings
- **Recherche** : Indexation vectorielle optimisée
- **Reranking** : Amélioration de la pertinence
- **Parallélisation** : Traitement multi-thread

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📝 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🙏 Remerciements

- [Mistral AI](https://mistral.ai/) pour les modèles d'embeddings
- [OpenAI](https://openai.com/) pour GPT-4
- [Cohere](https://cohere.ai/) pour le reranking
- [Supabase](https://supabase.com/) pour la base de données
- [Langchain](https://langchain.com/) pour les chaînes de traitement
- [Prisma](https://prisma.io/) pour l'ORM

## 📞 Support

Pour toute question ou problème :
- Ouvrir une issue sur GitHub
- Consulter la documentation
- Contacter l'équipe de développement

---

**Développé avec ❤️ pour l'innovation en IA**