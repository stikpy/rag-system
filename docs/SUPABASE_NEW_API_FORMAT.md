# 🔑 Configuration Supabase - Nouveau Format API

## 📋 Vue d'ensemble

Supabase a mis à jour son système de clés API. Ce guide vous explique comment configurer le nouveau format.

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

## 🔧 Configuration du Fichier .env

### 1. **Copier le fichier de configuration**
```bash
cp env.example .env
```

### 2. **Configurer avec le nouveau format**
```env
# Supabase Configuration (Nouveau Format)
SUPABASE_URL=https://nlunnxppbraflzyublfg.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SECRET_KEY=sb_secret_FRMIT••••••••••••

# Ancien format (pour compatibilité)
SUPABASE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SERVICE_ROLE_KEY=sb_secret_FRMIT••••••••••••
```

## 🛠️ Mise à Jour du Code

### 1. **Mettre à jour la configuration**
```python
# src/rag/utils/config.py
class RAGConfig(BaseSettings):
    # Supabase Configuration (Nouveau Format)
    supabase_url: str = Field(..., env="SUPABASE_URL")
    supabase_publishable_key: str = Field(..., env="SUPABASE_PUBLISHABLE_KEY")
    supabase_secret_key: str = Field(..., env="SUPABASE_SECRET_KEY")
    
    # Ancien format (pour compatibilité)
    supabase_key: Optional[str] = Field(None, env="SUPABASE_KEY")
    supabase_service_role_key: Optional[str] = Field(None, env="SUPABASE_SERVICE_ROLE_KEY")
```

### 2. **Mettre à jour le client Supabase**
```python
# src/rag/retrieval/vector_retriever.py
from supabase import create_client

class VectorRetriever:
    def __init__(self, embedding_provider=None):
        self.config = config
        
        # Nouveau format
        if config.supabase_publishable_key and config.supabase_secret_key:
            self.supabase = create_client(
                config.supabase_url,
                config.supabase_publishable_key,
                config.supabase_secret_key
            )
        # Ancien format (compatibilité)
        elif config.supabase_key and config.supabase_service_role_key:
            self.supabase = create_client(
                config.supabase_url,
                config.supabase_key,
                config.supabase_service_role_key
            )
        else:
            raise ValueError("Configuration Supabase manquante")
```

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

## 🧪 Test de Configuration

### Script de Test
```python
# scripts/test_supabase_new_format.py
import os
from dotenv import load_dotenv
from supabase import create_client

def test_new_format():
    load_dotenv()
    
    url = os.getenv("SUPABASE_URL")
    publishable_key = os.getenv("SUPABASE_PUBLISHABLE_KEY")
    secret_key = os.getenv("SUPABASE_SECRET_KEY")
    
    if not all([url, publishable_key, secret_key]):
        print("❌ Configuration incomplète")
        return False
    
    try:
        # Test avec le nouveau format
        supabase = create_client(url, publishable_key, secret_key)
        
        # Test de connexion
        response = supabase.table("documents").select("id").limit(1).execute()
        
        print("✅ Connexion Supabase réussie (nouveau format)")
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion : {e}")
        return False

if __name__ == "__main__":
    test_new_format()
```

## 🔄 Migration

### Étapes de Migration
1. **Sauvegarder** l'ancienne configuration
2. **Obtenir** les nouvelles clés API
3. **Mettre à jour** le fichier .env
4. **Tester** la nouvelle configuration
5. **Déployer** en production

### Script de Migration
```bash
# Migration automatique
python scripts/migrate_supabase_keys.py
```

## 📞 Support

### Ressources Officielles
- **Documentation Supabase** : https://supabase.com/docs
- **Migration Guide** : https://supabase.com/docs/guides/api-keys
- **Support** : https://supabase.com/support

### Dépannage
- **Clés invalides** : Vérifiez le format dans le dashboard
- **Erreur de connexion** : Vérifiez l'URL du projet
- **Permissions** : Vérifiez les politiques RLS

---

**🎯 Configuration Supabase mise à jour pour le nouveau format !**
