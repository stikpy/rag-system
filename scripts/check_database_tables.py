#!/usr/bin/env python3
"""
Script pour vérifier les tables de la base de données Supabase.
"""

import asyncio
import os
import sys
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from dotenv import load_dotenv
load_dotenv('.env.local')

from prisma import Prisma

async def check_database_tables():
    """Vérifie les tables de la base de données."""
    try:
        print("🔍 Vérification des tables de la base de données...")
        print("=" * 60)
        
        # Initialiser Prisma
        prisma = Prisma()
        await prisma.connect()
        
        print("✅ Connexion à la base de données réussie!")
        
        # Vérifier les tables existantes
        print("\n📊 Tables existantes:")
        print("-" * 40)
        
        # Requête pour lister toutes les tables
        tables_query = """
        SELECT table_name, table_type 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
        """
        
        tables = await prisma.query_raw(tables_query)
        
        if tables:
            for table in tables:
                print(f"📋 {table['table_name']} ({table['table_type']})")
        else:
            print("❌ Aucune table trouvée dans le schéma public")
        
        # Vérifier les colonnes de chaque table
        print("\n🔍 Détails des tables:")
        print("-" * 40)
        
        for table in tables:
            table_name = table['table_name']
            print(f"\n📋 Table: {table_name}")
            
            # Requête pour lister les colonnes
            columns_query = f"""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            AND table_schema = 'public'
            ORDER BY ordinal_position;
            """
            
            columns = await prisma.query_raw(columns_query)
            
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
                print(f"  • {col['column_name']}: {col['data_type']} {nullable}{default}")
        
        # Vérifier les extensions PostgreSQL
        print("\n🔧 Extensions PostgreSQL:")
        print("-" * 40)
        
        extensions_query = """
        SELECT extname, extversion 
        FROM pg_extension 
        ORDER BY extname;
        """
        
        extensions = await prisma.query_raw(extensions_query)
        
        for ext in extensions:
            print(f"🔌 {ext['extname']} (version {ext['extversion']})")
        
        # Vérifier les index
        print("\n📈 Index existants:")
        print("-" * 40)
        
        indexes_query = """
        SELECT schemaname, tablename, indexname, indexdef
        FROM pg_indexes 
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        
        indexes = await prisma.query_raw(indexes_query)
        
        for idx in indexes:
            print(f"📊 {idx['tablename']}.{idx['indexname']}")
        
        # Statistiques de la base de données
        print("\n📊 Statistiques de la base de données:")
        print("-" * 40)
        
        stats_query = """
        SELECT 
            schemaname,
            tablename,
            n_tup_ins as inserts,
            n_tup_upd as updates,
            n_tup_del as deletes,
            n_live_tup as live_tuples,
            n_dead_tup as dead_tuples
        FROM pg_stat_user_tables 
        WHERE schemaname = 'public'
        ORDER BY n_live_tup DESC;
        """
        
        stats = await prisma.query_raw(stats_query)
        
        for stat in stats:
            print(f"📋 {stat['tablename']}: {stat['live_tuples']} tuples vivants")
        
        await prisma.disconnect()
        print("\n✅ Vérification terminée avec succès!")
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification: {e}")
        return False
    
    return True

async def main():
    """Fonction principale."""
    success = await check_database_tables()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
