#!/usr/bin/env python3
"""
Configuration des URLs de base de données
=======================================

Ce script configure automatiquement DATABASE_URL et DIRECT_URL pour Supabase.
"""

import os
import sys
from pathlib import Path

def get_supabase_url():
    """Récupère l'URL Supabase depuis le fichier .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return None
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Chercher SUPABASE_URL
    for line in content.split('\n'):
        if line.startswith('SUPABASE_URL='):
            return line.split('=', 1)[1].strip()
    
    return None

def generate_database_urls(supabase_url):
    """Génère les URLs de base de données"""
    if not supabase_url:
        return None, None
    
    # Extraire l'ID du projet depuis l'URL
    # Format: https://nlunnxppbraflzyublfg.supabase.co
    project_id = supabase_url.replace('https://', '').replace('.supabase.co', '')
    
    # Générer les URLs
    database_url = f"postgresql://postgres.{project_id}:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
    direct_url = f"postgresql://postgres.{project_id}:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
    
    return database_url, direct_url

def update_env_file(database_url, direct_url):
    """Met à jour le fichier .env avec les URLs de base de données"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    # Lire le fichier actuel
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer ou ajouter les variables
    lines = content.split('\n')
    updated_lines = []
    database_url_found = False
    direct_url_found = False
    
    for line in lines:
        if line.startswith('DATABASE_URL='):
            updated_lines.append(f'DATABASE_URL="{database_url}"')
            database_url_found = True
        elif line.startswith('DIRECT_URL='):
            updated_lines.append(f'DIRECT_URL="{direct_url}"')
            direct_url_found = True
        else:
            updated_lines.append(line)
    
    # Ajouter les variables si elles n'existent pas
    if not database_url_found:
        updated_lines.append(f'DATABASE_URL="{database_url}"')
    
    if not direct_url_found:
        updated_lines.append(f'DIRECT_URL="{direct_url}"')
    
    # Écrire le fichier mis à jour
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(updated_lines))
    
    print("✅ Fichier .env mis à jour")
    return True

def create_database_setup_guide():
    """Crée un guide pour configurer la base de données"""
    print("📚 Création du guide de configuration de la base de données...")
    
    guide_content = '''# 🗄️ Configuration de la Base de Données Supabase

## 📋 Vue d'ensemble

Ce guide vous explique comment configurer les URLs de base de données pour Prisma avec Supabase.

## 🔧 Configuration des URLs

### 1. **Obtenir le mot de passe de la base de données**

#### Accéder au Dashboard Supabase
1. Allez sur https://supabase.com/dashboard
2. Sélectionnez votre projet
3. Allez dans **Settings** > **Database**
4. Copiez le mot de passe de la base de données

### 2. **Configurer les variables d'environnement**

#### Fichier .env
```env
# Database Configuration
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

#### Remplacez [YOUR-PASSWORD]
- Remplacez `[YOUR-PASSWORD]` par le mot de passe de votre base de données
- Le mot de passe se trouve dans Supabase > Settings > Database

## 🚀 Test de la Configuration

### 1. **Test de connexion Prisma**
```bash
npx prisma db pull
```

### 2. **Test de Prisma Studio**
```bash
npx prisma studio
```

### 3. **Test du système RAG**
```bash
python examples/basic_rag_example.py
```

## 🔍 Vérification

### Variables d'environnement
```bash
# Vérifier les variables
echo $DATABASE_URL
echo $DIRECT_URL
```

### Test de connexion
```bash
# Test de connexion directe
npx prisma db pull

# Test de Prisma Studio
npx prisma studio
```

## 🚨 Dépannage

### Erreurs Courantes

#### 1. "Environment variable not found"
```bash
# Vérifier le fichier .env
cat .env | grep DATABASE_URL
cat .env | grep DIRECT_URL
```

#### 2. "Connection failed"
```bash
# Vérifier le mot de passe
# Vérifier l'URL du projet
# Vérifier la région (aws-1-eu-west-3)
```

#### 3. "Authentication failed"
```bash
# Vérifier le mot de passe dans Supabase
# Régénérer le mot de passe si nécessaire
```

## 📊 URLs de Base de Données

### **DATABASE_URL** (Connection Pooling)
- **Usage** : Connexions normales
- **Port** : 6543 (pooler)
- **Avantages** : Gestion automatique des connexions
- **Limitations** : Certaines opérations limitées

### **DIRECT_URL** (Direct Connection)
- **Usage** : Migrations, introspection
- **Port** : 5432 (direct)
- **Avantages** : Accès complet à la base
- **Limitations** : Plus de connexions simultanées

## 🔒 Sécurité

### Bonnes Pratiques
1. **Ne jamais commiter les mots de passe**
2. **Utiliser des variables d'environnement**
3. **Régénérer les mots de passe régulièrement**
4. **Limiter les accès par IP si possible**

### Variables Sensibles
```bash
# Ajouter au .gitignore
.env
.env.local
.env.production
```

## 📞 Support

### Ressources Officielles
- **Supabase Docs** : https://supabase.com/docs
- **Prisma Docs** : https://www.prisma.io/docs
- **PostgreSQL Docs** : https://www.postgresql.org/docs

### Support Communauté
- **GitHub Issues** : Ouvrir une issue
- **Discord** : Rejoindre le serveur
- **Stack Overflow** : Tag `supabase` + `prisma`

---

**🎯 Configuration de la base de données Supabase terminée !**
'''
    
    guide_file = Path("docs/DATABASE_SETUP_GUIDE.md")
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guide de configuration créé: docs/DATABASE_SETUP_GUIDE.md")
    return True

def main():
    """Fonction principale"""
    print("🗄️ Configuration des URLs de base de données")
    print("=" * 50)
    
    # Récupérer l'URL Supabase
    supabase_url = get_supabase_url()
    if not supabase_url:
        print("❌ SUPABASE_URL non trouvée dans le fichier .env")
        return False
    
    print(f"✅ URL Supabase trouvée: {supabase_url}")
    
    # Générer les URLs de base de données
    database_url, direct_url = generate_database_urls(supabase_url)
    if not database_url or not direct_url:
        print("❌ Erreur lors de la génération des URLs")
        return False
    
    print("✅ URLs de base de données générées")
    
    # Mettre à jour le fichier .env
    if not update_env_file(database_url, direct_url):
        return False
    
    # Créer le guide
    if not create_database_setup_guide():
        return False
    
    print("\n🎉 Configuration des URLs de base de données terminée !")
    print("\n📋 Prochaines étapes :")
    print("1. Remplacez [YOUR-PASSWORD] par le mot de passe de votre base de données")
    print("2. Le mot de passe se trouve dans Supabase > Settings > Database")
    print("3. Testez la configuration : npx prisma db pull")
    print("4. Démarrez Prisma Studio : npx prisma studio")
    print("5. Consultez docs/DATABASE_SETUP_GUIDE.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
