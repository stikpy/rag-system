"""
Module OCR
==========

Ce module contient les composants OCR pour traiter les documents scannés :
- OCRProcessor : Processeur OCR principal
- DocumentOCRProcessor : Processeur spécialisé pour le RAG
"""

from .ocr_processor import OCRProcessor, DocumentOCRProcessor

__all__ = ["OCRProcessor", "DocumentOCRProcessor"]
