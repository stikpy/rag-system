#!/usr/bin/env python3
"""
Test de connexion à la base de données Supabase
==============================================

Ce script teste la connexion à la base de données Supabase.
"""

import os
import sys
import psycopg2
from pathlib import Path

def load_env_variables():
    """Charge les variables d'environnement depuis .env"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    # Nettoyer les guillemets
                    value = value.strip('"').strip("'")
                    os.environ[key] = value
    
    print("✅ Variables d'environnement chargées")
    return True

def test_database_connection():
    """Teste la connexion à la base de données"""
    print("🔍 Test de connexion à la base de données...")
    
    # Récupérer les variables
    database_url = os.getenv('DATABASE_URL')
    direct_url = os.getenv('DIRECT_URL')
    
    if not database_url:
        print("❌ DATABASE_URL non définie")
        return False
    
    if not direct_url:
        print("❌ DIRECT_URL non définie")
        return False
    
    print(f"📊 DATABASE_URL: {database_url[:50]}...")
    print(f"📊 DIRECT_URL: {direct_url[:50]}...")
    
    # Test avec DATABASE_URL (connection pooling)
    print("\n🔗 Test avec DATABASE_URL (connection pooling)...")
    try:
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion DATABASE_URL réussie")
        print(f"📊 Version PostgreSQL: {version[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur DATABASE_URL: {e}")
        return False
    
    # Test avec DIRECT_URL (connexion directe)
    print("\n🔗 Test avec DIRECT_URL (connexion directe)...")
    try:
        conn = psycopg2.connect(direct_url)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connexion DIRECT_URL réussie")
        print(f"📊 Version PostgreSQL: {version[0][:50]}...")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erreur DIRECT_URL: {e}")
        return False
    
    return True

def test_supabase_connection():
    """Teste la connexion Supabase via l'API"""
    print("\n🌐 Test de connexion Supabase API...")
    
    try:
        from supabase import create_client, Client
        
        url = os.getenv('SUPABASE_URL')
        key = os.getenv('SUPABASE_SECRET_KEY')
        
        if not url or not key:
            print("❌ Variables Supabase manquantes")
            return False
        
        supabase: Client = create_client(url, key)
        
        # Test simple
        result = supabase.table('documents').select('*').limit(1).execute()
        print(f"✅ Connexion Supabase API réussie")
        print(f"📊 Documents trouvés: {len(result.data)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur Supabase API: {e}")
        return False

def create_connection_guide():
    """Crée un guide de dépannage"""
    print("\n📚 Création du guide de dépannage...")
    
    guide_content = '''# 🔧 Guide de Dépannage - Connexion Base de Données

## 🚨 Problèmes Courants

### 1. **Erreur d'authentification**
```
Error: P1000: Authentication failed
```

#### Solutions :
- Vérifier le mot de passe dans Supabase Dashboard
- Régénérer le mot de passe si nécessaire
- Vérifier l'URL du projet

### 2. **Erreur de connexion**
```
Error: Connection refused
```

#### Solutions :
- Vérifier l'URL du projet
- Vérifier la région (aws-1-eu-west-3)
- Vérifier le port (5432 pour direct, 6543 pour pooling)

### 3. **Variables d'environnement**
```
Error: Environment variable not found
```

#### Solutions :
- Vérifier le fichier .env
- Vérifier les noms des variables
- Redémarrer le terminal

## 🔍 Diagnostic

### 1. **Vérifier les variables**
```bash
echo $DATABASE_URL
echo $DIRECT_URL
```

### 2. **Test de connexion**
```bash
# Test Prisma
npx prisma db pull

# Test direct
psql $DATABASE_URL
```

### 3. **Vérifier Supabase Dashboard**
- Allez dans Settings > Database
- Vérifier l'URL de connexion
- Vérifier le mot de passe

## 🛠️ Solutions

### 1. **Régénérer le mot de passe**
1. Allez dans Supabase Dashboard
2. Settings > Database
3. Reset database password
4. Copier le nouveau mot de passe

### 2. **Vérifier l'URL du projet**
1. Allez dans Supabase Dashboard
2. Settings > General
3. Vérifier l'URL du projet

### 3. **Tester avec psql**
```bash
# Test direct
psql "postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
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

**🔧 Guide de dépannage - Connexion base de données**
'''
    
    guide_file = Path("docs/TROUBLESHOOTING_DATABASE.md")
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guide de dépannage créé: docs/TROUBLESHOOTING_DATABASE.md")
    return True

def main():
    """Fonction principale"""
    print("🔍 Test de connexion à la base de données Supabase")
    print("=" * 60)
    
    # Charger les variables d'environnement
    if not load_env_variables():
        return False
    
    # Tester la connexion à la base de données
    if not test_database_connection():
        print("\n❌ Test de connexion échoué")
        print("💡 Consultez docs/TROUBLESHOOTING_DATABASE.md pour plus d'informations")
        return False
    
    # Tester la connexion Supabase
    if not test_supabase_connection():
        print("\n⚠️  Connexion Supabase API échouée")
        print("💡 Vérifiez vos clés API Supabase")
    
    # Créer le guide de dépannage
    if not create_connection_guide():
        return False
    
    print("\n🎉 Tests de connexion terminés !")
    print("\n📋 Prochaines étapes :")
    print("1. npx prisma db push")
    print("2. npx prisma studio")
    print("3. python examples/basic_rag_example.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
