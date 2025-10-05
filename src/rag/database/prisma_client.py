"""
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
