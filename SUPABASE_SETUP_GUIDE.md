# 🔑 Guide de Configuration Supabase - Nouveau Format

## 📋 Vue d'ensemble

Ce guide vous explique comment configurer Supabase avec le nouveau format des clés API pour votre système RAG.

## 🆕 Nouveau Format des Clés API

### Ancien Format (Legacy)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Nouveau Format (Recommandé)
```
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_xxx
SUPABASE_SECRET_KEY=sb_secret_xxx
```

## 🔧 Configuration Étape par Étape

### 1. **Obtenir les Clés API**

#### Accéder au Dashboard Supabase
1. Allez sur https://supabase.com/dashboard
2. Connectez-vous à votre compte
3. Sélectionnez votre projet

#### Copier les Clés API
1. Allez dans **Settings** > **API Keys**
2. Copiez les valeurs suivantes :
   - **URL** : `https://nlunnxppbraflzyublfg.supabase.co`
   - **Publishable key** : `sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx`
   - **Secret key** : `sb_secret_FRMIT••••••••••••`

### 2. **Configurer le Fichier .env**

#### Créer le fichier .env
```bash
cp env.example .env
```

#### Éditer le fichier .env
```bash
nano .env  # ou votre éditeur préféré
```

#### Ajouter les valeurs Supabase
```env
# Supabase Configuration (Nouveau Format)
SUPABASE_URL=https://nlunnxppbraflzyublfg.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SECRET_KEY=sb_secret_FRMIT••••••••••••

# Ancien format (pour compatibilité)
SUPABASE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SERVICE_ROLE_KEY=sb_secret_FRMIT••••••••••••
```

### 3. **Tester la Configuration**

#### Test automatique
```bash
python3 scripts/test_supabase_new_format.py
```

#### Test manuel
```python
from supabase import create_client

# Test de connexion
supabase = create_client(
    "https://nlunnxppbraflzyublfg.supabase.co",
    "sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx",
    "sb_secret_FRMIT••••••••••••"
)

# Test simple
response = supabase.table("documents").select("id").limit(1).execute()
print(response)
```

## 🛠️ Configuration Automatique

### Script de Configuration
```bash
python3 scripts/configure_supabase_new.py
```

Ce script vous guide dans la configuration interactive.

## 📊 Comparaison des Formats

| Aspect | Ancien Format | Nouveau Format |
|--------|---------------|----------------|
| **Publishable Key** | `anon public` | `sb_publishable_xxx` |
| **Secret Key** | `service_role` | `sb_secret_xxx` |
| **Sécurité** | Basique | Améliorée |
| **Gestion** | Manuelle | Automatique |
| **Compatibilité** | Legacy | Moderne |

## 🔒 Sécurité

### Nouveau Format - Avantages
- **Clés plus sécurisées** : Format cryptographique amélioré
- **Gestion centralisée** : Dashboard unifié
- **Rotation automatique** : Renouvellement simplifié
- **Audit trail** : Suivi des accès

### Bonnes Pratiques
1. **Utiliser le nouveau format** pour les nouveaux projets
2. **Migrer progressivement** les projets existants
3. **Maintenir la compatibilité** avec l'ancien format
4. **Surveiller l'usage** des clés

## 🧪 Tests de Validation

### Test de Connexion
```bash
# Test du nouveau format
python3 scripts/test_supabase_new_format.py
```

### Test du Système RAG
```bash
# Test complet du système
python3 examples/basic_rag_example.py
```

## 🚨 Dépannage

### Erreurs Courantes

#### 1. "Invalid URL"
```bash
# Vérifier l'URL Supabase
echo $SUPABASE_URL
# Doit être : https://xxx.supabase.co
```

#### 2. "Invalid API key"
```bash
# Vérifier les clés API
echo $SUPABASE_PUBLISHABLE_KEY
echo $SUPABASE_SECRET_KEY
```

#### 3. "Table not found"
```bash
# Exécuter le script SQL
psql -f scripts/setup_supabase.sql
```

#### 4. "Permission denied"
```bash
# Vérifier les politiques RLS
# Aller dans Supabase > Authentication > Policies
```

## 📞 Support

### Ressources Officielles
- **Documentation Supabase** : https://supabase.com/docs
- **Migration Guide** : https://supabase.com/docs/guides/api-keys
- **Support** : https://supabase.com/support

### Support Communauté
- **GitHub Issues** : Ouvrir une issue sur le repository
- **Discord** : Rejoindre le serveur Discord
- **Email** : support@example.com

## 🎯 Prochaines Étapes

Une fois Supabase configuré :

1. **Tester la connexion** : `python3 scripts/test_supabase_new_format.py`
2. **Configurer la base de données** : `psql -f scripts/setup_supabase.sql`
3. **Tester le système RAG** : `python3 examples/basic_rag_example.py`
4. **Déployer en production** : Suivre le guide de déploiement

---

**🎉 Configuration Supabase terminée ! Votre système RAG est prêt à fonctionner.**
