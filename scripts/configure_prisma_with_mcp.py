#!/usr/bin/env python3
"""
Configuration Prisma avec MCP Supabase
=====================================

Ce script utilise le MCP Supabase pour configurer Prisma automatiquement.
"""

import os
import sys
from pathlib import Path

def setup_prisma_schema():
    """Configure le schéma Prisma pour RAG"""
    print("🔧 Configuration du schéma Prisma...")
    
    # Créer le répertoire prisma
    prisma_dir = Path("prisma")
    prisma_dir.mkdir(exist_ok=True)
    
    # Schéma Prisma optimisé pour RAG
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
}'''
    
    # Écrire le schéma
    schema_path = prisma_dir / "schema.prisma"
    with open(schema_path, 'w', encoding='utf-8') as f:
        f.write(schema_content)
    
    print("✅ Schéma Prisma créé")
    return True

def create_database_setup_sql():
    """Crée le script SQL pour configurer la base de données"""
    print("📊 Création du script SQL de configuration...")
    
    setup_sql = '''-- Configuration de la base de données pour RAG
-- Ce script configure les tables et extensions nécessaires

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

-- Politiques RLS (Row Level Security)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE queries ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;

-- Politiques pour les documents (lecture publique, écriture authentifiée)
CREATE POLICY "Documents are viewable by everyone" ON documents FOR SELECT USING (true);
CREATE POLICY "Documents are insertable by authenticated users" ON documents FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Documents are updatable by authenticated users" ON documents FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Documents are deletable by authenticated users" ON documents FOR DELETE USING (auth.role() = 'authenticated');

-- Politiques pour les chunks
CREATE POLICY "Document chunks are viewable by everyone" ON document_chunks FOR SELECT USING (true);
CREATE POLICY "Document chunks are insertable by authenticated users" ON document_chunks FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Document chunks are updatable by authenticated users" ON document_chunks FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Document chunks are deletable by authenticated users" ON document_chunks FOR DELETE USING (auth.role() = 'authenticated');

-- Politiques pour les requêtes
CREATE POLICY "Queries are viewable by everyone" ON queries FOR SELECT USING (true);
CREATE POLICY "Queries are insertable by authenticated users" ON queries FOR INSERT WITH CHECK (auth.role() = 'authenticated');
CREATE POLICY "Queries are updatable by authenticated users" ON queries FOR UPDATE USING (auth.role() = 'authenticated');
CREATE POLICY "Queries are deletable by authenticated users" ON queries FOR DELETE USING (auth.role() = 'authenticated');

-- Politiques pour les utilisateurs
CREATE POLICY "Users can view their own data" ON users FOR SELECT USING (auth.uid()::text = id);
CREATE POLICY "Users can insert their own data" ON users FOR INSERT WITH CHECK (auth.uid()::text = id);
CREATE POLICY "Users can update their own data" ON users FOR UPDATE USING (auth.uid()::text = id);
CREATE POLICY "Users can delete their own data" ON users FOR DELETE USING (auth.uid()::text = id);

-- Politiques pour les sessions
CREATE POLICY "Sessions are viewable by their owner" ON sessions FOR SELECT USING (auth.uid()::text = user_id);
CREATE POLICY "Sessions are insertable by their owner" ON sessions FOR INSERT WITH CHECK (auth.uid()::text = user_id);
CREATE POLICY "Sessions are updatable by their owner" ON sessions FOR UPDATE USING (auth.uid()::text = user_id);
CREATE POLICY "Sessions are deletable by their owner" ON sessions FOR DELETE USING (auth.uid()::text = user_id);
'''
    
    # Créer le script SQL
    sql_file = Path("scripts/setup_database_rag.sql")
    with open(sql_file, 'w', encoding='utf-8') as f:
        f.write(setup_sql)
    
    print("✅ Script SQL créé: scripts/setup_database_rag.sql")
    return True

def create_prisma_client_wrapper():
    """Crée un wrapper Python pour Prisma"""
    print("🐍 Création du wrapper Python pour Prisma...")
    
    wrapper_content = '''"""
Wrapper Python pour Prisma avec Supabase
========================================

Ce module fournit une interface Python pour interagir avec Prisma.
"""

import asyncio
from typing import List, Dict, Any, Optional
from prisma import Prisma
from prisma.models import Document, DocumentChunk, Query, User, Session

class PrismaRAGClient:
    """Client Prisma pour le système RAG"""
    
    def __init__(self):
        self.prisma = Prisma()
    
    async def connect(self):
        """Connecte le client Prisma"""
        await self.prisma.connect()
    
    async def disconnect(self):
        """Déconnecte le client Prisma"""
        await self.prisma.disconnect()
    
    # Documents
    async def create_document(self, content: str, metadata: Dict[str, Any] = None) -> Document:
        """Crée un nouveau document"""
        return await self.prisma.document.create({
            "content": content,
            "metadata": metadata or {}
        })
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Récupère un document par ID"""
        return await self.prisma.document.find_unique(where={"id": document_id})
    
    async def search_documents(self, query: str, limit: int = 10) -> List[Document]:
        """Recherche des documents par contenu"""
        return await self.prisma.document.find_many(
            where={
                "content": {
                    "contains": query,
                    "mode": "insensitive"
                }
            },
            take=limit
        )
    
    # Document Chunks
    async def create_document_chunk(self, document_id: str, content: str, chunk_index: int, metadata: Dict[str, Any] = None) -> DocumentChunk:
        """Crée un nouveau chunk de document"""
        return await self.prisma.documentchunk.create({
            "documentId": document_id,
            "content": content,
            "chunkIndex": chunk_index,
            "metadata": metadata or {}
        })
    
    async def get_document_chunks(self, document_id: str) -> List[DocumentChunk]:
        """Récupère tous les chunks d'un document"""
        return await self.prisma.documentchunk.find_many(
            where={"documentId": document_id},
            order={"chunkIndex": "asc"}
        )
    
    # Queries
    async def create_query(self, query: str, response: str = None, document_id: str = None, chunk_id: str = None, metadata: Dict[str, Any] = None) -> Query:
        """Crée une nouvelle requête"""
        return await self.prisma.query.create({
            "query": query,
            "response": response,
            "documentId": document_id,
            "chunkId": chunk_id,
            "metadata": metadata or {}
        })
    
    async def get_queries(self, limit: int = 10) -> List[Query]:
        """Récupère les requêtes récentes"""
        return await self.prisma.query.find_many(
            order={"createdAt": "desc"},
            take=limit
        )
    
    # Users
    async def create_user(self, email: str, name: str = None, role: str = "user") -> User:
        """Crée un nouvel utilisateur"""
        return await self.prisma.user.create({
            "email": email,
            "name": name,
            "role": role
        })
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Récupère un utilisateur par ID"""
        return await self.prisma.user.find_unique(where={"id": user_id})
    
    # Sessions
    async def create_session(self, user_id: str, name: str = None, metadata: Dict[str, Any] = None) -> Session:
        """Crée une nouvelle session"""
        return await self.prisma.session.create({
            "userId": user_id,
            "name": name,
            "metadata": metadata or {}
        })
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Récupère les sessions d'un utilisateur"""
        return await self.prisma.session.find_many(
            where={"userId": user_id},
            order={"createdAt": "desc"}
        )

# Fonction utilitaire pour les tests
async def test_prisma_connection():
    """Teste la connexion Prisma"""
    client = PrismaRAGClient()
    
    try:
        await client.connect()
        print("✅ Connexion Prisma réussie")
        
        # Test simple
        documents = await client.prisma.document.find_many()
        print(f"📊 Documents trouvés: {len(documents)}")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_prisma_connection())
'''
    
    # Créer le wrapper
    wrapper_file = Path("src/rag/database/prisma_client.py")
    wrapper_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(wrapper_file, 'w', encoding='utf-8') as f:
        f.write(wrapper_content)
    
    print("✅ Wrapper Prisma créé: src/rag/database/prisma_client.py")
    return True

def create_test_script():
    """Crée un script de test pour Prisma"""
    print("🧪 Création du script de test...")
    
    test_script = '''#!/usr/bin/env python3
"""
Script de test pour Prisma avec Supabase
========================================

Ce script teste la configuration Prisma.
"""

import asyncio
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from rag.database.prisma_client import PrismaRAGClient, test_prisma_connection

async def test_full_functionality():
    """Test complet de la fonctionnalité Prisma"""
    print("🧪 Test complet de Prisma avec Supabase")
    print("=" * 50)
    
    client = PrismaRAGClient()
    
    try:
        await client.connect()
        print("✅ Connexion établie")
        
        # Test de création d'un document
        print("📄 Test de création d'un document...")
        document = await client.create_document(
            content="Ceci est un test de document pour le système RAG",
            metadata={"type": "test", "language": "fr"}
        )
        print(f"✅ Document créé: {document.id}")
        
        # Test de création d'un chunk
        print("📝 Test de création d'un chunk...")
        chunk = await client.create_document_chunk(
            document_id=document.id,
            content="Chunk de test",
            chunk_index=0,
            metadata={"chunk_type": "test"}
        )
        print(f"✅ Chunk créé: {chunk.id}")
        
        # Test de création d'une requête
        print("❓ Test de création d'une requête...")
        query = await client.create_query(
            query="Qu'est-ce que le RAG ?",
            response="Le RAG est un système de génération augmentée par récupération",
            document_id=document.id,
            chunk_id=chunk.id,
            metadata={"test": True}
        )
        print(f"✅ Requête créée: {query.id}")
        
        # Test de récupération
        print("🔍 Test de récupération...")
        documents = await client.prisma.document.find_many()
        chunks = await client.prisma.documentchunk.find_many()
        queries = await client.prisma.query.find_many()
        
        print(f"📊 Résultats:")
        print(f"  - Documents: {len(documents)}")
        print(f"  - Chunks: {len(chunks)}")
        print(f"  - Requêtes: {len(queries)}")
        
        await client.disconnect()
        print("✅ Test complet réussi !")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

async def main():
    """Fonction principale"""
    print("🗄️ Test de Prisma avec Supabase")
    print("=" * 40)
    
    # Test de connexion
    if not await test_prisma_connection():
        return False
    
    # Test complet
    if not await test_full_functionality():
        return False
    
    print("\\n🎉 Tous les tests sont passés avec succès !")
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
'''
    
    # Créer le script de test
    test_file = Path("scripts/test_prisma_supabase.py")
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    # Rendre le script exécutable
    test_file.chmod(0o755)
    
    print("✅ Script de test créé: scripts/test_prisma_supabase.py")
    return True

def main():
    """Fonction principale"""
    print("🗄️ Configuration Prisma avec MCP Supabase")
    print("=" * 50)
    
    # Configuration du schéma Prisma
    if not setup_prisma_schema():
        return False
    
    # Création du script SQL
    if not create_database_setup_sql():
        return False
    
    # Création du wrapper Python
    if not create_prisma_client_wrapper():
        return False
    
    # Création du script de test
    if not create_test_script():
        return False
    
    print("\n🎉 Configuration Prisma avec MCP Supabase terminée !")
    print("\n📋 Fichiers créés :")
    print("- prisma/schema.prisma")
    print("- scripts/setup_database_rag.sql")
    print("- src/rag/database/prisma_client.py")
    print("- scripts/test_prisma_supabase.py")
    
    print("\n🚀 Prochaines étapes :")
    print("1. Exécutez le script SQL dans Supabase :")
    print("   - Allez dans Supabase > SQL Editor")
    print("   - Copiez le contenu de scripts/setup_database_rag.sql")
    print("   - Exécutez le script")
    print("2. Installez Prisma : npm install -g prisma")
    print("3. Générez le client : npx prisma generate")
    print("4. Testez la configuration : python scripts/test_prisma_supabase.py")
    print("5. Utilisez le système RAG : python examples/basic_rag_example.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
