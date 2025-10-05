"""
Traitement de texte pour le système RAG
=======================================

Ce module contient les utilitaires de traitement de texte :
- Découpage de documents
- Nettoyage de texte
- Tokenisation
"""

import re
import tiktoken
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class DocumentSplitter(ABC):
    """Classe abstraite pour le découpage de documents"""
    
    @abstractmethod
    def split(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Découpe le texte en chunks"""
        pass


class CharacterSplitter(DocumentSplitter):
    """Découpage par caractères avec overlap"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Découpe le texte par caractères"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            chunk_text = text[start:end]
            
            if chunk_text.strip():
                chunks.append({
                    'content': chunk_text,
                    'start': start,
                    'end': end,
                    'length': len(chunk_text)
                })
            
            start = end - self.chunk_overlap
            
        return chunks


class TokenSplitter(DocumentSplitter):
    """Découpage par tokens (pour respecter les limites d'API)"""
    
    def __init__(self, model: str = "gpt-3.5-turbo", chunk_size: int = 1000, chunk_overlap: int = 100):
        self.model = model
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.encoding = tiktoken.encoding_for_model(model)
    
    def split(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Découpe le texte par tokens"""
        tokens = self.encoding.encode(text)
        chunks = []
        start = 0
        
        while start < len(tokens):
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            chunk_text = self.encoding.decode(chunk_tokens)
            
            if chunk_text.strip():
                chunks.append({
                    'content': chunk_text,
                    'start': start,
                    'end': end,
                    'token_count': len(chunk_tokens),
                    'tokens': chunk_tokens
                })
            
            start = end - self.chunk_overlap
            
        return chunks


class SentenceSplitter(DocumentSplitter):
    """Découpage par phrases pour maintenir la cohérence"""
    
    def __init__(self, chunk_size: int = 1024, chunk_overlap: int = 200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Découpe le texte par phrases"""
        # Découper en phrases
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = ""
        start_char = 0
        
        for sentence in sentences:
            # Vérifier si ajouter cette phrase dépasse la taille limite
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Finaliser le chunk actuel
                chunks.append({
                    'content': current_chunk.strip(),
                    'start': start_char,
                    'end': start_char + len(current_chunk),
                    'length': len(current_chunk)
                })
                
                # Commencer un nouveau chunk avec overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                start_char += len(current_chunk) - len(overlap_text) - len(sentence) - 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Ajouter le dernier chunk
        if current_chunk.strip():
            chunks.append({
                'content': current_chunk.strip(),
                'start': start_char,
                'end': start_char + len(current_chunk),
                'length': len(current_chunk)
            })
        
        return chunks


class TextProcessor:
    """Processeur de texte principal"""
    
    def __init__(self, splitter: DocumentSplitter = None):
        self.splitter = splitter or CharacterSplitter()
    
    def clean_text(self, text: str) -> str:
        """Nettoie le texte"""
        # Supprimer les caractères de contrôle
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
        
        # Normaliser les espaces
        text = re.sub(r'\s+', ' ', text)
        
        # Supprimer les espaces en début/fin
        text = text.strip()
        
        return text
    
    def split_document(self, text: str, **kwargs) -> List[Dict[str, Any]]:
        """Découpe un document en chunks"""
        # Nettoyer le texte
        clean_text = self.clean_text(text)
        
        # Découper
        chunks = self.splitter.split(clean_text, **kwargs)
        
        # Ajouter des métadonnées
        for i, chunk in enumerate(chunks):
            chunk['chunk_id'] = i
            chunk['content'] = self.clean_text(chunk['content'])
        
        return chunks
    
    def split_documents(self, documents: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Découpe plusieurs documents"""
        all_chunks = []
        
        for doc_idx, document in enumerate(documents):
            content = document.get('content', document.get('text', ''))
            chunks = self.split_document(content, **kwargs)
            
            # Ajouter les métadonnées du document original
            for chunk in chunks:
                chunk.update({
                    'document_id': document.get('id', doc_idx),
                    'document_metadata': document.get('metadata', {}),
                    'source': document.get('source', 'unknown')
                })
            
            all_chunks.extend(chunks)
        
        return all_chunks


def create_splitter(splitter_type: str = "character", **kwargs) -> DocumentSplitter:
    """Factory pour créer des splitters"""
    if splitter_type == "character":
        return CharacterSplitter(**kwargs)
    elif splitter_type == "token":
        return TokenSplitter(**kwargs)
    elif splitter_type == "sentence":
        return SentenceSplitter(**kwargs)
    else:
        raise ValueError(f"Type de splitter non supporté: {splitter_type}")
