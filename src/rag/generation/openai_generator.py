"""
Générateur utilisant OpenAI pour la génération de texte.
"""

import logging
from typing import Dict, Any
from openai import OpenAI

from ..utils.config import config

logger = logging.getLogger(__name__)

class OpenAIGenerator:
    """
    Générateur de texte utilisant OpenAI.
    """
    
    def __init__(self):
        """Initialise le générateur OpenAI."""
        self.client = OpenAI(api_key=config.openai_api_key)
        self.model = config.openai_generation_model
        logger.info(f"OpenAIGenerator initialisé avec le modèle: {self.model}")
    
    def generate(self, question: str, context: str) -> str:
        """
        Génère une réponse basée sur la question et le contexte.
        
        Args:
            question: La question de l'utilisateur
            context: Le contexte récupéré
            
        Returns:
            La réponse générée
        """
        try:
            # Construire le prompt
            prompt = self._build_prompt(question, context)
            
            # Générer la réponse
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Vous êtes un assistant IA spécialisé dans l'analyse de documents. Répondez de manière précise et contextuelle en vous basant uniquement sur les informations fournies dans le contexte."
                    },
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ],
                max_tokens=config.max_tokens,
                temperature=config.temperature
            )
            
            answer = response.choices[0].message.content
            logger.info("Réponse générée avec succès par OpenAI")
            return answer
            
        except Exception as e:
            logger.error(f"Erreur lors de la génération OpenAI: {e}")
            raise
    
    def _build_prompt(self, question: str, context: str) -> str:
        """
        Construit le prompt pour la génération.
        
        Args:
            question: La question de l'utilisateur
            context: Le contexte récupéré
            
        Returns:
            Le prompt formaté
        """
        return f"""Contexte:
{context}

Question: {question}

Instructions:
- Répondez de manière précise et contextuelle
- Basez-vous uniquement sur les informations du contexte
- Si l'information n'est pas disponible dans le contexte, indiquez-le clairement
- Structurez votre réponse de manière claire et organisée

Réponse:"""
