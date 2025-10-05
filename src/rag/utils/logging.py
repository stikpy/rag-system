"""
Configuration du logging pour le système RAG
============================================

Ce module configure le système de logging pour le RAG.
"""

import logging
import sys
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """
    Configure le système de logging
    
    Args:
        level: Niveau de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Fichier de log (optionnel)
        format_string: Format personnalisé (optionnel)
        
    Returns:
        Logger configuré
    """
    # Format par défaut
    if format_string is None:
        format_string = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s"
        )
    
    # Configuration du logger principal
    logger = logging.getLogger("rag_system")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Supprimer les handlers existants
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    console_formatter = logging.Formatter(format_string)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Handler pour le fichier (si spécifié)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_formatter = logging.Formatter(format_string)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    # Éviter la duplication des logs
    logger.propagate = False
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Obtient un logger pour un module spécifique
    
    Args:
        name: Nom du module
        
    Returns:
        Logger pour le module
    """
    return logging.getLogger(f"rag_system.{name}")
