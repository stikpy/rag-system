"""
Module de base de données
=========================

Ce module contient les composants de base de données :
- PrismaRAGClient : Client Prisma pour Supabase
- PrismaRAGRepository : Repository pattern
"""

from .prisma_client import PrismaRAGClient, PrismaRAGRepository

__all__ = ["PrismaRAGClient", "PrismaRAGRepository"]
