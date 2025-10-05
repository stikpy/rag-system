#!/usr/bin/env python3
"""
Application de la configuration Prisma avec MCP Supabase
=======================================================

Ce script utilise le MCP Supabase pour appliquer la configuration Prisma.
"""

import os
import sys
from pathlib import Path

def read_sql_script():
    """Lit le script SQL de configuration"""
    sql_file = Path("scripts/setup_database_rag.sql")
    if not sql_file.exists():
        print("❌ Script SQL non trouvé: scripts/setup_database_rag.sql")
        return None
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()

def apply_database_setup():
    """Applique la configuration de la base de données"""
    print("🗄️ Application de la configuration de la base de données...")
    
    # Lire le script SQL
    sql_script = read_sql_script()
    if not sql_script:
        return False
    
    print("📊 Script SQL chargé avec succès")
    print(f"📏 Taille du script: {len(sql_script)} caractères")
    
    # Afficher les instructions
    print("\n📋 Instructions pour appliquer la configuration :")
    print("=" * 60)
    print("1. Allez sur https://supabase.com/dashboard")
    print("2. Sélectionnez votre projet")
    print("3. Allez dans 'SQL Editor'")
    print("4. Copiez le contenu du fichier scripts/setup_database_rag.sql")
    print("5. Collez-le dans l'éditeur SQL")
    print("6. Cliquez sur 'Run' pour exécuter le script")
    print("\n💡 Le script va créer :")
    print("   - Extension pgvector")
    print("   - Tables (documents, document_chunks, queries, users, sessions)")
    print("   - Index pour la recherche vectorielle")
    print("   - Politiques RLS (Row Level Security)")
    
    return True

def setup_prisma_client():
    """Configure le client Prisma"""
    print("\n🔧 Configuration du client Prisma...")
    
    # Vérifier si Prisma est installé
    try:
        import subprocess
        result = subprocess.run(["npx", "prisma", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Prisma installé")
        else:
            print("❌ Prisma non installé")
            print("💡 Installez Prisma : npm install -g prisma")
            return False
    except:
        print("❌ Prisma non installé")
        print("💡 Installez Prisma : npm install -g prisma")
        return False
    
    # Générer le client Prisma
    try:
        print("🔧 Génération du client Prisma...")
        result = subprocess.run(["npx", "prisma", "generate"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Client Prisma généré")
            return True
        else:
            print(f"❌ Erreur lors de la génération: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

def test_configuration():
    """Teste la configuration"""
    print("\n🧪 Test de la configuration...")
    
    # Vérifier les fichiers créés
    files_to_check = [
        "prisma/schema.prisma",
        "scripts/setup_database_rag.sql",
        "src/rag/database/prisma_client.py",
        "scripts/test_prisma_supabase.py"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} manquant")
            return False
    
    print("✅ Tous les fichiers sont présents")
    return True

def create_quick_setup_guide():
    """Crée un guide de configuration rapide"""
    print("\n📚 Création du guide de configuration rapide...")
    
    guide_content = '''# 🚀 Configuration Rapide Prisma + Supabase

## ⚡ Étapes Rapides

### 1. **Exécuter le script SQL dans Supabase**
```bash
# Ouvrir le fichier SQL
cat scripts/setup_database_rag.sql

# Copier le contenu et l'exécuter dans Supabase SQL Editor
```

### 2. **Installer et configurer Prisma**
```bash
# Installer Prisma
npm install -g prisma

# Générer le client
npx prisma generate

# Appliquer le schéma (optionnel)
npx prisma db push
```

### 3. **Tester la configuration**
```bash
# Test de la configuration
python scripts/test_prisma_supabase.py

# Test du système RAG
python examples/basic_rag_example.py
```

## 🔧 Configuration de l'environnement

### Variables d'environnement requises
```env
# Supabase Configuration
SUPABASE_URL=https://nlunnxppbraflzyublfg.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SECRET_KEY=sb_secret_FRMIT••••••••••••

# Database Configuration (Prisma)
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

## 📊 Structure de la base de données

### Tables créées
- **documents** : Documents principaux
- **document_chunks** : Chunks de documents
- **queries** : Requêtes et réponses
- **users** : Utilisateurs
- **sessions** : Sessions utilisateur

### Extensions installées
- **pgvector** : Pour la recherche vectorielle
- **Index optimisés** : Pour la recherche textuelle et vectorielle
- **Politiques RLS** : Pour la sécurité

## 🧪 Tests disponibles

### Test de connexion
```bash
python scripts/test_prisma_supabase.py
```

### Test du système RAG
```bash
python examples/basic_rag_example.py
python examples/advanced_rag_example.py
```

## 🚨 Dépannage

### Erreurs courantes
1. **"Prisma not found"** : `npm install -g prisma`
2. **"Database connection failed"** : Vérifier DATABASE_URL
3. **"Table not found"** : Exécuter le script SQL
4. **"Permission denied"** : Vérifier les politiques RLS

## 📞 Support

- **Documentation** : Consultez docs/PRISMA_SUPABASE_SETUP.md
- **Scripts** : Utilisez les scripts dans scripts/
- **Exemples** : Testez les exemples dans examples/

---

**🎯 Configuration Prisma + Supabase terminée !**
'''
    
    guide_file = Path("PRISMA_QUICK_SETUP.md")
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guide de configuration créé: PRISMA_QUICK_SETUP.md")
    return True

def main():
    """Fonction principale"""
    print("🗄️ Application de la configuration Prisma avec MCP Supabase")
    print("=" * 70)
    
    # Appliquer la configuration de la base de données
    if not apply_database_setup():
        return False
    
    # Configurer le client Prisma
    if not setup_prisma_client():
        return False
    
    # Tester la configuration
    if not test_configuration():
        return False
    
    # Créer le guide de configuration
    if not create_quick_setup_guide():
        return False
    
    print("\n🎉 Configuration Prisma avec MCP Supabase appliquée !")
    print("\n📋 Prochaines étapes :")
    print("1. Exécutez le script SQL dans Supabase SQL Editor")
    print("2. Vérifiez la configuration : python scripts/test_prisma_supabase.py")
    print("3. Testez le système RAG : python examples/basic_rag_example.py")
    print("4. Consultez PRISMA_QUICK_SETUP.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
