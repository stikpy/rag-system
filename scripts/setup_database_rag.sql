-- Configuration de la base de données pour RAG
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
