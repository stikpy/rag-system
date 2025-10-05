# 🔑 Configuration des Clés API

## 📋 Vue d'ensemble

Ce guide vous explique comment obtenir et configurer toutes les clés API nécessaires pour le système RAG.

## 🚀 Configuration Rapide

### 1. Copier le fichier de configuration
```bash
cp env.example .env
```

### 2. Éditer le fichier .env
```bash
nano .env  # ou votre éditeur préféré
```

## 🔑 Obtenir les Clés API

### 1. **Mistral AI** (Recommandé - Conforme RGPD)
- **Site** : https://console.mistral.ai/
- **Prix** : Gratuit jusqu'à 50k tokens/mois
- **Avantages** : Conforme RGPD, performant, français
- **Étapes** :
  1. Créer un compte sur console.mistral.ai
  2. Aller dans "API Keys"
  3. Créer une nouvelle clé
  4. Copier la clé dans `MISTRAL_API_KEY`

### 2. **OpenAI** (Optionnel)
- **Site** : https://platform.openai.com/
- **Prix** : Payant (crédits requis)
- **Avantages** : Très performant, large écosystème
- **Étapes** :
  1. Créer un compte sur platform.openai.com
  2. Aller dans "API Keys"
  3. Créer une nouvelle clé
  4. Ajouter des crédits (minimum $5)
  5. Copier la clé dans `OPENAI_API_KEY`

### 3. **Cohere** (Pour le reranking)
- **Site** : https://dashboard.cohere.ai/
- **Prix** : Gratuit jusqu'à 1000 requêtes/mois
- **Avantages** : Excellent reranking, multilingue
- **Étapes** :
  1. Créer un compte sur dashboard.cohere.ai
  2. Aller dans "API Keys"
  3. Créer une nouvelle clé
  4. Copier la clé dans `COHERE_API_KEY`

### 4. **Supabase** (Base de données)
- **Site** : https://supabase.com/
- **Prix** : Gratuit jusqu'à 500MB
- **Avantages** : PostgreSQL + pgvector, interface web
- **Étapes** :
  1. Créer un compte sur supabase.com
  2. Créer un nouveau projet
  3. Aller dans "Settings" > "API"
  4. Copier :
     - `URL` → `SUPABASE_URL`
     - `anon public` → `SUPABASE_KEY`
     - `service_role` → `SUPABASE_SERVICE_ROLE_KEY`

## 🛠️ Configuration Détaillée

### Fichier .env complet
```env
# ===========================================
# CONFIGURATION OBLIGATOIRE
# ===========================================

# Mistral AI (Recommandé - Conforme RGPD)
MISTRAL_API_KEY=mistral-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Cohere (Pour le reranking)
COHERE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Supabase (Base de données)
SUPABASE_URL=https://xxxxxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# ===========================================
# CONFIGURATION OPTIONNELLE
# ===========================================

# OpenAI (Optionnel - si vous voulez utiliser GPT-4)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Base de données (Optionnel - si vous voulez utiliser Prisma)
DATABASE_URL=postgresql://user:password@host:port/database

# ===========================================
# CONFIGURATION AVANCÉE
# ===========================================

# Taille des chunks de texte
CHUNK_SIZE=1024
CHUNK_OVERLAP=200

# Configuration des modèles
MAX_TOKENS=4096
TEMPERATURE=0.7
```

## 🧪 Test de Configuration

### 1. Vérifier les clés API
```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

print('🔑 Vérification des clés API:')
print(f'Mistral: {\"✅\" if os.getenv(\"MISTRAL_API_KEY\") else \"❌\"}')
print(f'Cohere: {\"✅\" if os.getenv(\"COHERE_API_KEY\") else \"❌\"}')
print(f'Supabase: {\"✅\" if os.getenv(\"SUPABASE_URL\") else \"❌\"}')
print(f'OpenAI: {\"✅\" if os.getenv(\"OPENAI_API_KEY\") else \"❌\"}')
"
```

### 2. Test complet du système
```bash
# Test basique
python examples/basic_rag_example.py

# Test avec toutes les fonctionnalités
python examples/advanced_rag_example.py
```

## 💰 Coûts Estimés

### Configuration Minimale (Gratuite)
- **Mistral** : Gratuit (50k tokens/mois)
- **Cohere** : Gratuit (1000 requêtes/mois)
- **Supabase** : Gratuit (500MB)
- **Total** : 0€/mois

### Configuration Complète
- **Mistral** : Gratuit (50k tokens/mois)
- **OpenAI** : ~10-50€/mois (selon usage)
- **Cohere** : Gratuit (1000 requêtes/mois)
- **Supabase** : Gratuit (500MB)
- **Total** : 10-50€/mois

## 🔒 Sécurité

### Bonnes Pratiques
1. **Ne jamais commiter le fichier .env**
2. **Utiliser des clés API avec permissions limitées**
3. **Régénérer les clés régulièrement**
4. **Surveiller l'usage des clés**

### Fichier .gitignore
```gitignore
# Fichiers de configuration sensibles
.env
.env.local
.env.production

# Logs
*.log
logs/

# Base de données locale
*.db
*.sqlite
```

## 🚨 Dépannage

### Erreurs Courantes

#### 1. "API key not found"
```bash
# Vérifier que le fichier .env existe
ls -la .env

# Vérifier le contenu
cat .env
```

#### 2. "Invalid API key"
```bash
# Vérifier la clé sur le dashboard
# Régénérer si nécessaire
```

#### 3. "Rate limit exceeded"
```bash
# Attendre ou augmenter les limites
# Vérifier les quotas sur les dashboards
```

#### 4. "Database connection failed"
```bash
# Vérifier l'URL Supabase
# Vérifier que le projet est actif
```

## 📞 Support

### Ressources Officielles
- **Mistral** : https://docs.mistral.ai/
- **OpenAI** : https://platform.openai.com/docs
- **Cohere** : https://docs.cohere.ai/
- **Supabase** : https://supabase.com/docs

### Support Communauté
- **GitHub Issues** : Ouvrir une issue sur le repository
- **Discord** : Rejoindre le serveur Discord
- **Email** : support@example.com

---

**🎯 Configuration terminée ! Vous pouvez maintenant utiliser le système RAG complet.**
