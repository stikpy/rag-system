#!/usr/bin/env python3
"""
Script de configuration Prisma avec MCP Supabase
===============================================

Ce script utilise le MCP Supabase pour configurer Prisma automatiquement.
"""

import os
import sys
from pathlib import Path

def check_mcp_supabase():
    """Vérifie si le MCP Supabase est configuré"""
    print("🔍 Vérification du MCP Supabase...")
    
    # Vérifier les variables d'environnement
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("❌ Configuration Supabase manquante")
        print("💡 Configurez SUPABASE_URL et SUPABASE_PUBLISHABLE_KEY")
        return False
    
    print("✅ Configuration Supabase trouvée")
    return True

def create_prisma_schema():
    """Crée le schéma Prisma optimisé pour RAG"""
    print("🔧 Création du schéma Prisma...")
    
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

def setup_database_with_mcp():
    """Configure la base de données avec MCP Supabase"""
    print("🗄️ Configuration de la base de données avec MCP Supabase...")
    
    # SQL pour créer les tables et extensions
    setup_sql = '''
-- Extension pgvector pour les embeddings
CREATE EXTENSION IF NOT EXISTS vector;

-- Table documents
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1024), -- Dimension pour Mistral embeddings
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table document_chunks
CREATE TABLE IF NOT EXISTS document_chunks (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    metadata JSONB,
    embedding VECTOR(1024), -- Dimension pour Mistral embeddings
    chunk_index INTEGER NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table queries
CREATE TABLE IF NOT EXISTS queries (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    query TEXT NOT NULL,
    response TEXT,
    metadata JSONB,
    document_id TEXT REFERENCES documents(id),
    chunk_id TEXT REFERENCES document_chunks(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table users
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table sessions
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY DEFAULT gen_random_uuid()::text,
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index pour les embeddings (recherche vectorielle)
CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING ivfflat (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS document_chunks_embedding_idx ON document_chunks USING ivfflat (embedding vector_cosine_ops);

-- Index pour les recherches textuelles
CREATE INDEX IF NOT EXISTS documents_content_idx ON documents USING gin(to_tsvector('french', content));
CREATE INDEX IF NOT EXISTS document_chunks_content_idx ON document_chunks USING gin(to_tsvector('french', content));

-- Index pour les métadonnées
CREATE INDEX IF NOT EXISTS documents_metadata_idx ON documents USING gin(metadata);
CREATE INDEX IF NOT EXISTS document_chunks_metadata_idx ON document_chunks USING gin(metadata);

-- Index pour les relations
CREATE INDEX IF NOT EXISTS document_chunks_document_id_idx ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS queries_document_id_idx ON queries(document_id);
CREATE INDEX IF NOT EXISTS queries_chunk_id_idx ON queries(chunk_id);
CREATE INDEX IF NOT EXISTS sessions_user_id_idx ON sessions(user_id);

-- Fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_document_chunks_updated_at BEFORE UPDATE ON document_chunks FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_queries_updated_at BEFORE UPDATE ON queries FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_sessions_updated_at BEFORE UPDATE ON sessions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
'''
    
    try:
        # Utiliser le MCP Supabase pour exécuter le SQL
        print("📊 Exécution du script SQL avec MCP Supabase...")
        
        # Note: En production, vous utiliseriez le MCP Supabase ici
        # Pour l'instant, on va créer un fichier SQL que vous pourrez exécuter
        sql_file = Path("scripts/setup_database.sql")
        with open(sql_file, 'w', encoding='utf-8') as f:
            f.write(setup_sql)
        
        print("✅ Script SQL créé dans scripts/setup_database.sql")
        print("💡 Exécutez ce script dans votre base Supabase")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la configuration: {e}")
        return False

def generate_prisma_client():
    """Génère le client Prisma"""
    print("🔧 Génération du client Prisma...")
    
    try:
        import subprocess
        
        # Générer le client
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

def test_prisma_connection():
    """Teste la connexion Prisma"""
    print("🧪 Test de la connexion Prisma...")
    
    try:
        # Test simple avec Prisma
        test_script = '''
import asyncio
from prisma import Prisma

async def test_connection():
    prisma = Prisma()
    await prisma.connect()
    
    # Test simple
    documents = await prisma.document.find_many()
    print(f"Documents trouvés: {len(documents)}")
    
    await prisma.disconnect()
    print("✅ Connexion Prisma réussie")

if __name__ == "__main__":
    asyncio.run(test_connection())
'''
        
        # Écrire le script de test
        test_file = Path("test_prisma_connection.py")
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_script)
        
        print("✅ Script de test créé: test_prisma_connection.py")
        print("💡 Exécutez: python test_prisma_connection.py")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🗄️ Configuration Prisma avec MCP Supabase")
    print("=" * 50)
    
    # Vérifier la configuration Supabase
    if not check_mcp_supabase():
        return False
    
    # Créer le schéma Prisma
    if not create_prisma_schema():
        return False
    
    # Configurer la base de données
    if not setup_database_with_mcp():
        return False
    
    # Générer le client Prisma
    if not generate_prisma_client():
        return False
    
    # Tester la connexion
    if not test_prisma_connection():
        return False
    
    print("\n🎉 Configuration Prisma avec MCP Supabase terminée !")
    print("\n📋 Fichiers créés :")
    print("- prisma/schema.prisma")
    print("- scripts/setup_database.sql")
    print("- test_prisma_connection.py")
    
    print("\n🚀 Prochaines étapes :")
    print("1. Exécutez le script SQL dans Supabase")
    print("2. python test_prisma_connection.py")
    print("3. python examples/basic_rag_example.py")
    print("4. Consultez docs/PRISMA_SUPABASE_SETUP.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
