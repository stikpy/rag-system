-- Script de configuration Supabase pour le système RAG
-- =====================================================

-- 1. Activer l'extension pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Créer la table documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content TEXT NOT NULL,
    embedding VECTOR(1024), -- Dimension pour Mistral embeddings
    metadata JSONB DEFAULT '{}',
    source TEXT,
    chunk_id INTEGER DEFAULT 0,
    document_id TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Créer les index pour la recherche vectorielle
-- Index principal pour la similarité cosinus
CREATE INDEX IF NOT EXISTS documents_embedding_idx 
ON documents USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index pour la recherche par métadonnées
CREATE INDEX IF NOT EXISTS documents_metadata_idx 
ON documents USING GIN (metadata);

-- Index pour la recherche par source
CREATE INDEX IF NOT EXISTS documents_source_idx 
ON documents (source);

-- Index pour la recherche par document_id
CREATE INDEX IF NOT EXISTS documents_document_id_idx 
ON documents (document_id);

-- Index pour les timestamps
CREATE INDEX IF NOT EXISTS documents_created_at_idx 
ON documents (created_at);

-- 4. Créer une fonction pour mettre à jour updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 5. Créer le trigger pour updated_at
DROP TRIGGER IF EXISTS update_documents_updated_at ON documents;
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- 6. Activer Row Level Security (RLS)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- 7. Créer les politiques RLS
-- Politique pour les lectures publiques (ajustez selon vos besoins)
DROP POLICY IF EXISTS "Allow public read access" ON documents;
CREATE POLICY "Allow public read access" ON documents
    FOR SELECT USING (true);

-- Politique pour les insertions (ajustez selon vos besoins)
DROP POLICY IF EXISTS "Allow public insert" ON documents;
CREATE POLICY "Allow public insert" ON documents
    FOR INSERT WITH CHECK (true);

-- Politique pour les mises à jour (ajustez selon vos besoins)
DROP POLICY IF EXISTS "Allow public update" ON documents;
CREATE POLICY "Allow public update" ON documents
    FOR UPDATE USING (true);

-- Politique pour les suppressions (ajustez selon vos besoins)
DROP POLICY IF EXISTS "Allow public delete" ON documents;
CREATE POLICY "Allow public delete" ON documents
    FOR DELETE USING (true);

-- 8. Créer une fonction de recherche vectorielle personnalisée
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding VECTOR(1024),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    source TEXT,
    similarity FLOAT
)
LANGUAGE SQL
AS $$
    SELECT
        documents.id,
        documents.content,
        documents.metadata,
        documents.source,
        1 - (documents.embedding <=> query_embedding) AS similarity
    FROM documents
    WHERE 1 - (documents.embedding <=> query_embedding) > match_threshold
    ORDER BY documents.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- 9. Créer une fonction pour obtenir les statistiques
CREATE OR REPLACE FUNCTION get_document_stats()
RETURNS TABLE (
    total_documents BIGINT,
    total_sources BIGINT,
    avg_embedding_norm FLOAT,
    oldest_document TIMESTAMP WITH TIME ZONE,
    newest_document TIMESTAMP WITH TIME ZONE
)
LANGUAGE SQL
AS $$
    SELECT
        COUNT(*) as total_documents,
        COUNT(DISTINCT source) as total_sources,
        AVG(embedding <#> embedding) as avg_embedding_norm,
        MIN(created_at) as oldest_document,
        MAX(created_at) as newest_document
    FROM documents;
$$;

-- 10. Créer une vue pour les documents avec métadonnées enrichies
CREATE OR REPLACE VIEW documents_enriched AS
SELECT
    d.id,
    d.content,
    d.source,
    d.chunk_id,
    d.document_id,
    d.created_at,
    d.updated_at,
    d.metadata,
    d.metadata->>'title' as title,
    d.metadata->>'category' as category,
    d.metadata->>'language' as language,
    LENGTH(d.content) as content_length,
    ARRAY_LENGTH(STRING_TO_ARRAY(d.content, ' '), 1) as word_count
FROM documents d;

-- 11. Créer des fonctions utilitaires
-- Fonction pour nettoyer les anciens documents
CREATE OR REPLACE FUNCTION cleanup_old_documents(
    days_old INTEGER DEFAULT 30
)
RETURNS INTEGER
LANGUAGE SQL
AS $$
    DELETE FROM documents 
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old;
    SELECT ROW_COUNT();
$$;

-- Fonction pour obtenir les sources uniques
CREATE OR REPLACE FUNCTION get_unique_sources()
RETURNS TABLE (source TEXT, document_count BIGINT)
LANGUAGE SQL
AS $$
    SELECT 
        source,
        COUNT(*) as document_count
    FROM documents 
    WHERE source IS NOT NULL
    GROUP BY source
    ORDER BY document_count DESC;
$$;

-- 12. Créer des index supplémentaires pour les performances
-- Index composite pour les requêtes fréquentes
CREATE INDEX IF NOT EXISTS documents_source_created_at_idx 
ON documents (source, created_at);

-- Index pour les métadonnées spécifiques
CREATE INDEX IF NOT EXISTS documents_metadata_category_idx 
ON documents USING GIN ((metadata->>'category'));

CREATE INDEX IF NOT EXISTS documents_metadata_language_idx 
ON documents USING GIN ((metadata->>'language'));

-- 13. Insérer des données de test (optionnel)
-- Décommentez si vous voulez des données de test
/*
INSERT INTO documents (content, source, metadata) VALUES
(
    'L''intelligence artificielle est une technologie qui permet aux machines d''apprendre et de prendre des décisions.',
    'test_document',
    '{"title": "Introduction IA", "category": "technology", "language": "fr"}'::jsonb
),
(
    'Le machine learning utilise des algorithmes pour apprendre à partir de données.',
    'test_document',
    '{"title": "Machine Learning", "category": "technology", "language": "fr"}'::jsonb
);
*/

-- 14. Afficher les informations de configuration
SELECT 
    'Configuration Supabase terminée' as status,
    COUNT(*) as tables_created,
    (SELECT COUNT(*) FROM pg_extension WHERE extname = 'vector') as vector_extension_installed
FROM information_schema.tables 
WHERE table_name = 'documents';
