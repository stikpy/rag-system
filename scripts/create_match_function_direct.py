#!/usr/bin/env python3
"""
Script pour créer la fonction match_documents directement via psql.
"""

import os
import subprocess
from dotenv import load_dotenv

load_dotenv('.env.local')

def create_match_function():
    """Crée la fonction match_documents via psql."""
    print("🔧 Création de la fonction match_documents...")
    print("=" * 60)
    
    # Récupérer les variables d'environnement
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL non trouvée dans .env.local")
        return
    
    # Extraire les informations de connexion
    # Format: postgresql://user:password@host:port/database
    import re
    match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', database_url)
    if not match:
        print("❌ Format de DATABASE_URL invalide")
        return
    
    user, password, host, port, database = match.groups()
    
    # SQL pour créer la fonction
    sql_content = """
-- Fonction pour la recherche vectorielle
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
    
    try:
        # Exécuter via psql
        cmd = [
            'psql',
            f'postgresql://{user}:{password}@{host}:{port}/{database}',
            '-c', sql_content
        ]
        
        print(f"🚀 Exécution de la commande psql...")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Fonction match_documents créée avec succès!")
            print("📊 Fonction disponible pour la recherche vectorielle")
        else:
            print(f"❌ Erreur lors de la création: {result.stderr}")
            
    except FileNotFoundError:
        print("❌ psql non trouvé. Installation de PostgreSQL requise.")
        print("💡 Alternative: Créez la fonction manuellement dans l'interface Supabase")
        
        # Afficher le SQL à exécuter manuellement
        print("\n📋 SQL à exécuter dans l'interface Supabase:")
        print("-" * 50)
        print(sql_content)
        print("-" * 50)

if __name__ == "__main__":
    create_match_function()
