# 🗄️ Configuration Prisma avec Supabase

## 📋 Vue d'ensemble

Ce guide vous explique comment configurer Prisma avec Supabase pour votre système RAG, en utilisant les meilleures pratiques et la configuration optimale.

## 🔧 Configuration Prisma

### 1. **Schéma Prisma pour RAG**

#### Créer le fichier `prisma/schema.prisma`
```prisma
// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

// Modèle pour les documents
model Document {
  id        String   @id @default(cuid())
  content   String
  metadata  Json?
  embedding Vector? // Extension pgvector
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  chunks    DocumentChunk[]
  queries   Query[]

  @@map("documents")
}

// Modèle pour les chunks de documents
model DocumentChunk {
  id         String   @id @default(cuid())
  documentId String
  content    String
  metadata   Json?
  embedding  Vector? // Extension pgvector
  chunkIndex Int
  createdAt  DateTime @default(now())
  updatedAt  DateTime @updatedAt

  // Relations
  document   Document @relation(fields: [documentId], references: [id], onDelete: Cascade)
  queries    Query[]

  @@map("document_chunks")
}

// Modèle pour les requêtes
model Query {
  id        String   @id @default(cuid())
  query     String
  response  String?
  metadata  Json?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  documentId String?
  chunkId    String?
  document   Document?     @relation(fields: [documentId], references: [id])
  chunk      DocumentChunk? @relation(fields: [chunkId], references: [id])

  @@map("queries")
}

// Modèle pour les utilisateurs
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  role      String   @default("user")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  queries   Query[]

  @@map("users")
}

// Modèle pour les sessions
model Session {
  id        String   @id @default(cuid())
  userId    String
  name      String?
  metadata  Json?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  queries   Query[]

  @@map("sessions")
}
```

### 2. **Configuration de l'environnement**

#### Fichier `.env`
```env
# Supabase Configuration
SUPABASE_URL=https://nlunnxppbraflzyublfg.supabase.co
SUPABASE_PUBLISHABLE_KEY=sb_publishable_FiZwYQ6125mNYSWBbCIuGQ_5czStcTx
SUPABASE_SECRET_KEY=sb_secret_FRMIT••••••••••••

# Database Configuration (Prisma)
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"

# Prisma Configuration
PRISMA_GENERATE_DATAPROXY="true"
```

### 3. **Scripts de configuration**

#### Script de configuration Prisma
```bash
# scripts/setup_prisma.sh
#!/bin/bash

echo "🗄️ Configuration Prisma avec Supabase"
echo "====================================="

# Vérifier que Prisma est installé
if ! command -v prisma &> /dev/null; then
    echo "📦 Installation de Prisma..."
    npm install -g prisma
fi

# Générer le client Prisma
echo "🔧 Génération du client Prisma..."
npx prisma generate

# Appliquer les migrations
echo "📊 Application des migrations..."
npx prisma db push

# Vérifier la connexion
echo "🧪 Test de la connexion..."
npx prisma db pull

echo "✅ Configuration Prisma terminée !"
```

## 🚀 Configuration Automatique

### 1. **Script de configuration Python**

#### `scripts/setup_prisma_python.py`
```python
#!/usr/bin/env python3
"""
Script de configuration Prisma avec Supabase
===========================================

Ce script configure Prisma avec Supabase de manière automatique.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prisma_installed():
    """Vérifie si Prisma est installé"""
    try:
        result = subprocess.run(["npx", "prisma", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Prisma installé")
            return True
    except:
        pass
    
    print("❌ Prisma non installé")
    return False

def install_prisma():
    """Installe Prisma"""
    print("📦 Installation de Prisma...")
    try:
        subprocess.run(["npm", "install", "-g", "prisma"], check=True)
        print("✅ Prisma installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def generate_prisma_schema():
    """Génère le schéma Prisma"""
    print("🔧 Génération du schéma Prisma...")
    
    schema_content = '''// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
  directUrl = env("DIRECT_URL")
}

// Modèle pour les documents
model Document {
  id        String   @id @default(cuid())
  content   String
  metadata  Json?
  embedding Vector? // Extension pgvector
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  chunks    DocumentChunk[]
  queries   Query[]

  @@map("documents")
}

// Modèle pour les chunks de documents
model DocumentChunk {
  id         String   @id @default(cuid())
  documentId String
  content    String
  metadata   Json?
  embedding  Vector? // Extension pgvector
  chunkIndex Int
  createdAt  DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  document   Document @relation(fields: [documentId], references: [id], onDelete: Cascade)
  queries    Query[]

  @@map("document_chunks")
}

// Modèle pour les requêtes
model Query {
  id        String   @id @default(cuid())
  query     String
  response  String?
  metadata  Json?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  documentId String?
  chunkId    String?
  document   Document?     @relation(fields: [documentId], references: [id])
  chunk      DocumentChunk? @relation(fields: [chunkId], references: [id])

  @@map("queries")
}

// Modèle pour les utilisateurs
model User {
  id        String   @id @default(cuid())
  email     String   @unique
  name      String?
  role      String   @default("user")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  queries   Query[]

  @@map("users")
}

// Modèle pour les sessions
model Session {
  id        String   @id @default(cuid())
  userId    String
  name      String?
  metadata  Json?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  user      User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  queries   Query[]

  @@map("sessions")
}'''
    
    # Créer le répertoire prisma
    prisma_dir = Path("prisma")
    prisma_dir.mkdir(exist_ok=True)
    
    # Écrire le schéma
    schema_path = prisma_dir / "schema.prisma"
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    print("✅ Schéma Prisma créé")
    return True

def generate_client():
    """Génère le client Prisma"""
    print("🔧 Génération du client Prisma...")
    try:
        subprocess.run(["npx", "prisma", "generate"], check=True)
        print("✅ Client Prisma généré")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

def push_schema():
    """Applique le schéma à la base de données"""
    print("📊 Application du schéma à la base de données...")
    try:
        subprocess.run(["npx", "prisma", "db", "push"], check=True)
        print("✅ Schéma appliqué à la base de données")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False

def test_connection():
    """Teste la connexion à la base de données"""
    print("🧪 Test de la connexion...")
    try:
        subprocess.run(["npx", "prisma", "db", "pull"], check=True)
        print("✅ Connexion testée avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🗄️ Configuration Prisma avec Supabase")
    print("=" * 50)
    
    # Vérifier Prisma
    if not check_prisma_installed():
        if not install_prisma():
            return False
    
    # Générer le schéma
    if not generate_prisma_schema():
        return False
    
    # Générer le client
    if not generate_client():
        return False
    
    # Appliquer le schéma
    if not push_schema():
        return False
    
    # Tester la connexion
    if not test_connection():
        return False
    
    print("\n🎉 Configuration Prisma terminée avec succès !")
    print("\n🚀 Prochaines étapes :")
    print("1. python3 examples/basic_rag_example.py")
    print("2. python3 examples/advanced_rag_example.py")
    print("3. Consultez docs/PRISMA_SUPABASE_SETUP.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
```

## 🧪 Tests de Configuration

### 1. **Test de connexion Prisma**
```bash
# Test de la connexion
npx prisma db pull

# Test du client
npx prisma studio
```

### 2. **Test avec Python**
```python
# Test de la connexion Prisma
from prisma import Prisma

async def test_prisma():
    prisma = Prisma()
    await prisma.connect()
    
    # Test simple
    documents = await prisma.document.find_many()
    print(f"Documents trouvés: {len(documents)}")
    
    await prisma.disconnect()

# Exécuter le test
import asyncio
asyncio.run(test_prisma())
```

## 📊 Configuration Optimale

### 1. **Configuration de production**
```env
# Production
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
PRISMA_GENERATE_DATAPROXY="true"
```

### 2. **Configuration de développement**
```env
# Développement
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

## 🚨 Dépannage

### **Erreurs Courantes**

#### 1. "Prisma not found"
```bash
# Installer Prisma
npm install -g prisma
```

#### 2. "Database connection failed"
```bash
# Vérifier les variables d'environnement
echo $DATABASE_URL
echo $DIRECT_URL
```

#### 3. "Schema not found"
```bash
# Générer le schéma
npx prisma generate
```

#### 4. "Migration failed"
```bash
# Réinitialiser la base
npx prisma db push --force-reset
```

## 📞 Support

### **Ressources Officielles**
- **Prisma Docs** : https://www.prisma.io/docs
- **Supabase Docs** : https://supabase.com/docs
- **Prisma + Supabase** : https://supabase.com/docs/guides/integrations/prisma

### **Support Communauté**
- **GitHub Issues** : Ouvrir une issue sur le repository
- **Discord** : Rejoindre le serveur Discord
- **Email** : support@example.com

---

**🎯 Configuration Prisma avec Supabase terminée ! Votre système RAG est prêt.**
