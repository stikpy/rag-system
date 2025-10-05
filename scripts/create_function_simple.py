#!/usr/bin/env python3
"""
Script pour créer la fonction match_documents avec URL directe.
"""

import os
from dotenv import load_dotenv

load_dotenv('.env.local')

def show_sql_function():
    """Affiche le SQL à exécuter manuellement."""
    print("🔧 Création de la fonction match_documents...")
    print("=" * 60)
    
    # SQL pour créer la fonction
    sql_content = """
-- Fonction pour la recherche vectorielle dans Supabase
-- À exécuter dans l'interface Supabase > SQL Editor

CREATE OR REPLACE FUNCTION match_documents(
    query_embedding vector(1536),
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

-- Test de la fonction (optionnel)
-- SELECT * FROM match_documents('[0.1, 0.2, ...]'::vector, 3, 0.5);
"""
    
    print("📋 SQL à exécuter dans l'interface Supabase:")
    print("=" * 60)
    print(sql_content)
    print("=" * 60)
    
    print("\n🚀 Instructions:")
    print("1. Allez sur https://supabase.com/dashboard")
    print("2. Sélectionnez votre projet")
    print("3. Allez dans 'SQL Editor'")
    print("4. Collez le SQL ci-dessus")
    print("5. Cliquez sur 'Run'")
    print("\n✅ Une fois la fonction créée, le système RAG fonctionnera !")

if __name__ == "__main__":
    show_sql_function()
