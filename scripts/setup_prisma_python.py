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
