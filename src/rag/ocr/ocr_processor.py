"""
Module OCR pour le traitement des documents scannés
==================================================

Ce module implémente l'OCR pour extraire le texte de :
- PDF scannés
- Images (PNG, JPG, etc.)
- Documents non-texte
"""

import os
import tempfile
from typing import List, Dict, Any, Optional, Union
from pathlib import Path
import logging
import cv2
import numpy as np
from PIL import Image
import pytesseract
import easyocr
from pdf2image import convert_from_path
from ..utils.config import config

logger = logging.getLogger(__name__)


class OCRProcessor:
    """Processeur OCR principal avec support multiple moteurs"""
    
    def __init__(
        self, 
        ocr_engine: str = "tesseract",
        languages: List[str] = None,
        tesseract_path: str = None
    ):
        """
        Initialise le processeur OCR
        
        Args:
            ocr_engine: Moteur OCR ("tesseract", "easyocr", "hybrid")
            languages: Langues supportées
            tesseract_path: Chemin vers tesseract (optionnel)
        """
        self.ocr_engine = ocr_engine
        self.languages = languages or ["fra", "eng"]  # Français et anglais par défaut
        self.tesseract_path = tesseract_path
        
        # Initialiser les moteurs OCR
        self._init_ocr_engines()
    
    def _init_ocr_engines(self):
        """Initialise les moteurs OCR"""
        if self.ocr_engine in ["tesseract", "hybrid"]:
            try:
                if self.tesseract_path:
                    pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
                # Test de tesseract
                pytesseract.get_tesseract_version()
                logger.info("Tesseract initialisé avec succès")
            except Exception as e:
                logger.warning(f"Tesseract non disponible: {str(e)}")
                if self.ocr_engine == "tesseract":
                    raise
        
        if self.ocr_engine in ["easyocr", "hybrid"]:
            try:
                self.easyocr_reader = easyocr.Reader(self.languages)
                logger.info("EasyOCR initialisé avec succès")
            except Exception as e:
                logger.warning(f"EasyOCR non disponible: {str(e)}")
                if self.ocr_engine == "easyocr":
                    raise
    
    def extract_text_from_image(
        self, 
        image_path: Union[str, Path], 
        preprocess: bool = True
    ) -> Dict[str, Any]:
        """
        Extrait le texte d'une image
        
        Args:
            image_path: Chemin vers l'image
            preprocess: Appliquer le préprocessing (optionnel)
            
        Returns:
            Dictionnaire avec le texte extrait et métadonnées
        """
        try:
            # Charger l'image
            image = cv2.imread(str(image_path))
            if image is None:
                raise ValueError(f"Impossible de charger l'image: {image_path}")
            
            # Préprocessing si demandé
            if preprocess:
                image = self._preprocess_image(image)
            
            # Extraire le texte selon le moteur
            if self.ocr_engine == "tesseract":
                result = self._extract_with_tesseract(image)
            elif self.ocr_engine == "easyocr":
                result = self._extract_with_easyocr(image)
            elif self.ocr_engine == "hybrid":
                result = self._extract_with_hybrid(image)
            else:
                raise ValueError(f"Moteur OCR non supporté: {self.ocr_engine}")
            
            # Ajouter les métadonnées
            result.update({
                'source': str(image_path),
                'engine': self.ocr_engine,
                'languages': self.languages,
                'preprocessed': preprocess
            })
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction OCR: {str(e)}")
            raise
    
    def extract_text_from_pdf(
        self, 
        pdf_path: Union[str, Path], 
        pages: Optional[List[int]] = None,
        dpi: int = 300
    ) -> Dict[str, Any]:
        """
        Extrait le texte d'un PDF scanné
        
        Args:
            pdf_path: Chemin vers le PDF
            pages: Pages à traiter (optionnel, toutes si None)
            dpi: Résolution pour la conversion
            
        Returns:
            Dictionnaire avec le texte extrait et métadonnées
        """
        try:
            # Convertir le PDF en images
            images = convert_from_path(
                str(pdf_path), 
                dpi=dpi,
                first_page=pages[0] if pages else None,
                last_page=pages[-1] if pages else None
            )
            
            all_text = []
            page_results = []
            
            for i, image in enumerate(images):
                # Convertir PIL en OpenCV
                image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Extraire le texte de cette page
                page_result = self._extract_text_from_cv_image(image_cv)
                page_result['page_number'] = i + 1
                
                all_text.append(page_result['text'])
                page_results.append(page_result)
            
            # Combiner tous les textes
            full_text = '\n\n'.join(all_text)
            
            return {
                'text': full_text,
                'pages': page_results,
                'total_pages': len(images),
                'source': str(pdf_path),
                'engine': self.ocr_engine,
                'dpi': dpi
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'extraction PDF: {str(e)}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Préprocesse l'image pour améliorer l'OCR"""
        try:
            # Convertir en niveaux de gris
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Réduction du bruit
            denoised = cv2.medianBlur(gray, 3)
            
            # Amélioration du contraste
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Binarisation
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return binary
            
        except Exception as e:
            logger.warning(f"Erreur lors du préprocessing: {str(e)}")
            return image
    
    def _extract_with_tesseract(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrait le texte avec Tesseract"""
        try:
            # Configuration Tesseract
            config_tesseract = f"--oem 3 --psm 6 -l {'+'.join(self.languages)}"
            
            # Extraction du texte
            text = pytesseract.image_to_string(image, config=config_tesseract)
            
            # Extraction des données structurées
            data = pytesseract.image_to_data(image, config=config_tesseract, output_type=pytesseract.Output.DICT)
            
            # Calculer la confiance moyenne
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': text.strip(),
                'confidence': avg_confidence,
                'word_count': len(text.split()),
                'char_count': len(text)
            }
            
        except Exception as e:
            logger.error(f"Erreur Tesseract: {str(e)}")
            return {'text': '', 'confidence': 0, 'word_count': 0, 'char_count': 0}
    
    def _extract_with_easyocr(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrait le texte avec EasyOCR"""
        try:
            # Extraction avec EasyOCR
            results = self.easyocr_reader.readtext(image)
            
            # Combiner tous les textes
            text_parts = []
            confidences = []
            
            for (bbox, text, confidence) in results:
                if confidence > 0.5:  # Seuil de confiance
                    text_parts.append(text)
                    confidences.append(confidence)
            
            full_text = ' '.join(text_parts)
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            return {
                'text': full_text,
                'confidence': avg_confidence,
                'word_count': len(full_text.split()),
                'char_count': len(full_text),
                'detections': results
            }
            
        except Exception as e:
            logger.error(f"Erreur EasyOCR: {str(e)}")
            return {'text': '', 'confidence': 0, 'word_count': 0, 'char_count': 0}
    
    def _extract_with_hybrid(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrait le texte avec approche hybride"""
        try:
            # Essayer Tesseract d'abord
            tesseract_result = self._extract_with_tesseract(image)
            
            # Essayer EasyOCR
            easyocr_result = self._extract_with_easyocr(image)
            
            # Choisir le meilleur résultat
            if tesseract_result['confidence'] > easyocr_result['confidence']:
                result = tesseract_result
                result['method_used'] = 'tesseract'
            else:
                result = easyocr_result
                result['method_used'] = 'easyocr'
            
            # Combiner les textes si les confidences sont proches
            if abs(tesseract_result['confidence'] - easyocr_result['confidence']) < 10:
                combined_text = f"{tesseract_result['text']}\n{easyocr_result['text']}"
                result['text'] = combined_text
                result['method_used'] = 'hybrid'
            
            return result
            
        except Exception as e:
            logger.error(f"Erreur approche hybride: {str(e)}")
            return {'text': '', 'confidence': 0, 'word_count': 0, 'char_count': 0}
    
    def _extract_text_from_cv_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Extrait le texte d'une image OpenCV"""
        if self.ocr_engine == "tesseract":
            return self._extract_with_tesseract(image)
        elif self.ocr_engine == "easyocr":
            return self._extract_with_easyocr(image)
        elif self.ocr_engine == "hybrid":
            return self._extract_with_hybrid(image)
        else:
            raise ValueError(f"Moteur OCR non supporté: {self.ocr_engine}")
    
    def batch_process(
        self, 
        file_paths: List[Union[str, Path]], 
        output_dir: Optional[Union[str, Path]] = None
    ) -> List[Dict[str, Any]]:
        """
        Traite plusieurs fichiers en batch
        
        Args:
            file_paths: Liste des chemins de fichiers
            output_dir: Répertoire de sortie (optionnel)
            
        Returns:
            Liste des résultats pour chaque fichier
        """
        results = []
        
        for file_path in file_paths:
            try:
                file_path = Path(file_path)
                
                if file_path.suffix.lower() == '.pdf':
                    result = self.extract_text_from_pdf(file_path)
                elif file_path.suffix.lower() in ['.png', '.jpg', '.jpeg', '.tiff', '.bmp']:
                    result = self.extract_text_from_image(file_path)
                else:
                    logger.warning(f"Format de fichier non supporté: {file_path}")
                    continue
                
                # Sauvegarder si répertoire de sortie spécifié
                if output_dir:
                    output_path = Path(output_dir) / f"{file_path.stem}_ocr.txt"
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(result['text'])
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Erreur lors du traitement de {file_path}: {str(e)}")
                results.append({
                    'source': str(file_path),
                    'text': '',
                    'error': str(e)
                })
        
        return results


class DocumentOCRProcessor:
    """Processeur OCR spécialisé pour les documents du système RAG"""
    
    def __init__(self, ocr_processor: OCRProcessor = None):
        """
        Initialise le processeur OCR pour documents
        
        Args:
            ocr_processor: Processeur OCR (optionnel)
        """
        self.ocr_processor = ocr_processor or OCRProcessor()
    
    def process_document_for_rag(
        self, 
        file_path: Union[str, Path], 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Traite un document pour le système RAG
        
        Args:
            file_path: Chemin vers le document
            metadata: Métadonnées additionnelles
            
        Returns:
            Document formaté pour le RAG
        """
        try:
            file_path = Path(file_path)
            metadata = metadata or {}
            
            # Extraire le texte selon le type de fichier
            if file_path.suffix.lower() == '.pdf':
                ocr_result = self.ocr_processor.extract_text_from_pdf(file_path)
            else:
                ocr_result = self.ocr_processor.extract_text_from_image(file_path)
            
            # Formater pour le RAG
            document = {
                'content': ocr_result['text'],
                'source': str(file_path),
                'file_type': file_path.suffix.lower(),
                'metadata': {
                    **metadata,
                    'ocr_confidence': ocr_result.get('confidence', 0),
                    'ocr_engine': ocr_result.get('engine', 'unknown'),
                    'word_count': ocr_result.get('word_count', 0),
                    'char_count': ocr_result.get('char_count', 0)
                }
            }
            
            # Ajouter les informations de pages si PDF
            if 'pages' in ocr_result:
                document['metadata']['total_pages'] = ocr_result['total_pages']
                document['metadata']['page_results'] = ocr_result['pages']
            
            return document
            
        except Exception as e:
            logger.error(f"Erreur lors du traitement du document {file_path}: {str(e)}")
            raise
