#!/usr/bin/env python3
"""
Script pour créer la fonction match_documents via Python et psycopg2.
"""

import os
import psycopg2
from dotenv import load_dotenv

load_dotenv('.env.local')

def create_match_function():
    """Crée la fonction match_documents via psycopg2."""
    print("🔧 Création de la fonction match_documents via Python...")
    print("=" * 60)
    
    # Récupérer les variables d'environnement
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL non trouvée dans .env.local")
        return
    
    # Convertir l'URL pour psycopg2
    # Format: postgresql://user:password@host:port/database?pgbouncer=true
    # -> postgresql://user:password@host:port/database
    clean_url = database_url.split('?')[0]
    
    try:
        # Connexion à la base de données
        print("🔌 Connexion à la base de données...")
        conn = psycopg2.connect(clean_url)
        cursor = conn.cursor()
        print("✅ Connexion réussie")
        
        # SQL pour créer la fonction
        sql_function = """
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
        """
        
        print("🚀 Création de la fonction match_documents...")
        cursor.execute(sql_function)
        conn.commit()
        print("✅ Fonction match_documents créée avec succès!")
        
        # Tester la fonction
        print("🧪 Test de la fonction...")
        test_sql = """
        SELECT COUNT(*) as total_docs FROM documents WHERE embedding IS NOT NULL;
        """
        cursor.execute(test_sql)
        result = cursor.fetchone()
        print(f"📊 Documents avec embeddings: {result[0]}")
        
        # Fermer la connexion
        cursor.close()
        conn.close()
        print("✅ Connexion fermée")
        
        print("\n🎉 Fonction match_documents créée et testée!")
        print("🚀 Votre système RAG devrait maintenant fonctionner!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la création: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    create_match_function()
