-- Fonction pour la recherche vectorielle dans Supabase
-- Cette fonction permet de rechercher des documents similaires

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1024),
    match_count int DEFAULT 5,
    match_threshold float DEFAULT 0.7
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        1 - (d.embedding <=> query_embedding) as similarity
    FROM documents d
    WHERE 1 - (d.embedding <=> query_embedding) > match_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Fonction alternative pour nods_page_section
CREATE OR REPLACE FUNCTION match_page_sections(
    query_embedding vector(1024),
    match_count int DEFAULT 5,
    match_threshold float DEFAULT 0.7
)
RETURNS TABLE (
    id bigint,
    content text,
    metadata jsonb,
    similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        nps.id,
        nps.content,
        nps.metadata,
        1 - (nps.embedding <=> query_embedding) as similarity
    FROM nods_page_section nps
    WHERE 1 - (nps.embedding <=> query_embedding) > match_threshold
    ORDER BY nps.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;
