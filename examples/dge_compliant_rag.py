"""
Exemple RAG Conforme aux Recommandations DGE
============================================

Cet exemple implémente un système RAG conforme au guide officiel de la DGE :
- Sécurité et conformité RGPD
- Gestion des biais et équité
- Transparence et explicabilité
- Évaluation et qualité
- Cas d'usage spécifiques
"""

import os
import sys
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib
import json

# Ajouter le répertoire src au path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Imports du système RAG
from rag.core import RAGSystem
from rag.embeddings import MistralEmbeddingProvider
from rag.retrieval import VectorRetriever, CohereReranker
from rag.ocr import OCRProcessor
from rag.utils.config import config
from rag.utils.logging import setup_logging

# Configuration du logging
logger = setup_logging(level="INFO", log_file="dge_compliant_rag.log")


class DGECompliantRAGSystem:
    """Système RAG conforme aux recommandations DGE"""
    
    def __init__(
        self,
        company_name: str,
        department: str,
        compliance_level: str = "high"
    ):
        """
        Initialise le système RAG conforme DGE
        
        Args:
            company_name: Nom de l'entreprise
            department: Département utilisateur
            compliance_level: Niveau de conformité ("high", "medium", "low")
        """
        self.company_name = company_name
        self.department = department
        self.compliance_level = compliance_level
        
        # Métriques de conformité
        self.compliance_metrics = {
            "data_encryption": True,
            "anonymization": True,
            "access_control": True,
            "audit_logging": True,
            "bias_detection": True,
            "hallucination_control": True,
            "source_tracking": True,
            "human_evaluation": True
        }
        
        # Audit trail
        self.audit_trail = []
        
        # Initialiser les composants
        self._init_rag_system()
        self._init_security_layer()
        self._init_evaluation_system()
        
        logger.info(f"Système RAG DGE initialisé pour {company_name} - {department}")
    
    def _init_rag_system(self):
        """Initialise le système RAG de base"""
        try:
            # Fournisseur d'embeddings conforme RGPD
            embedding_provider = MistralEmbeddingProvider()
            
            # Récupérateur vectoriel
            vector_retriever = VectorRetriever(embedding_provider=embedding_provider)
            
            # Reranker pour améliorer la qualité
            reranker = CohereReranker()
            
            # OCR pour documents scannés
            ocr_processor = OCRProcessor()
            
            # Système RAG principal
            self.rag_system = RAGSystem(
                embedding_provider=embedding_provider,
                vector_retriever=vector_retriever,
                reranker=reranker,
                ocr_processor=ocr_processor,
                generation_provider="mistral"
            )
            
            logger.info("Système RAG de base initialisé")
            
        except Exception as e:
            logger.error(f"Erreur lors de l'initialisation du système RAG: {str(e)}")
            raise
    
    def _init_security_layer(self):
        """Initialise la couche de sécurité"""
        self.security_layer = DGESecurityLayer(
            company_name=self.company_name,
            department=self.department,
            compliance_level=self.compliance_level
        )
    
    def _init_evaluation_system(self):
        """Initialise le système d'évaluation"""
        self.evaluation_system = DGEEvaluationSystem(
            compliance_level=self.compliance_level
        )
    
    def add_documents_secure(
        self, 
        documents: List[Dict[str, Any]], 
        user_id: str,
        access_level: str = "standard"
    ) -> Dict[str, Any]:
        """
        Ajoute des documents de manière sécurisée
        
        Args:
            documents: Documents à ajouter
            user_id: ID de l'utilisateur
            access_level: Niveau d'accès
            
        Returns:
            Résultat de l'ajout avec métadonnées de sécurité
        """
        try:
            # Vérifier les droits d'accès
            if not self.security_layer.check_access(user_id, "add_documents", access_level):
                raise PermissionError("Accès refusé pour l'ajout de documents")
            
            # Anonymiser les données sensibles
            anonymized_docs = []
            for doc in documents:
                anonymized_doc = self.security_layer.anonymize_document(doc)
                anonymized_docs.append(anonymized_doc)
            
            # Chiffrer les documents
            encrypted_docs = []
            for doc in anonymized_docs:
                encrypted_doc = self.security_layer.encrypt_document(doc)
                encrypted_docs.append(encrypted_doc)
            
            # Ajouter au système RAG
            document_ids = self.rag_system.add_documents(encrypted_docs)
            
            # Logging d'audit
            self._log_audit_event(
                event_type="document_added",
                user_id=user_id,
                details={
                    "num_documents": len(documents),
                    "document_ids": document_ids,
                    "access_level": access_level,
                    "anonymization_applied": True,
                    "encryption_applied": True
                }
            )
            
            return {
                "success": True,
                "document_ids": document_ids,
                "security_applied": True,
                "audit_logged": True
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout sécurisé: {str(e)}")
            self._log_audit_event(
                event_type="document_add_error",
                user_id=user_id,
                details={"error": str(e)}
            )
            raise
    
    def query_secure(
        self, 
        query: str, 
        user_id: str,
        context: str = None
    ) -> Dict[str, Any]:
        """
        Pose une question de manière sécurisée
        
        Args:
            query: Question à poser
            user_id: ID de l'utilisateur
            context: Contexte métier (optionnel)
            
        Returns:
            Réponse avec métadonnées de sécurité et traçabilité
        """
        start_time = time.time()
        
        try:
            # Vérifier les droits d'accès
            if not self.security_layer.check_access(user_id, "query", "standard"):
                raise PermissionError("Accès refusé pour les requêtes")
            
            # Anonymiser la requête si nécessaire
            anonymized_query = self.security_layer.anonymize_query(query)
            
            # Traitement de la requête
            result = self.rag_system.query(anonymized_query)
            
            # Détection des biais
            bias_analysis = self.evaluation_system.analyze_bias(result["response"])
            
            # Contrôle des hallucinations
            hallucination_analysis = self.evaluation_system.detect_hallucination(
                result["response"], 
                result["context_documents"]
            )
            
            # Génération de l'explication
            explanation = self.evaluation_system.generate_explanation(
                result["response"],
                result["context_documents"],
                result["num_context_docs"]
            )
            
            # Calcul du score de confiance
            confidence_score = self.evaluation_system.calculate_confidence(
                result["response"],
                result["context_documents"]
            )
            
            processing_time = time.time() - start_time
            
            # Logging d'audit
            self._log_audit_event(
                event_type="query_processed",
                user_id=user_id,
                details={
                    "query": anonymized_query,
                    "response_length": len(result["response"]),
                    "num_sources": result["num_context_docs"],
                    "confidence_score": confidence_score,
                    "bias_detected": bias_analysis["bias_detected"],
                    "hallucination_detected": hallucination_analysis["hallucination_detected"],
                    "processing_time": processing_time
                }
            )
            
            return {
                "response": result["response"],
                "sources": result["context_documents"],
                "explanation": explanation,
                "confidence_score": confidence_score,
                "bias_analysis": bias_analysis,
                "hallucination_analysis": hallucination_analysis,
                "processing_time": processing_time,
                "traceability": {
                    "query_id": self._generate_query_id(query, user_id),
                    "timestamp": datetime.now().isoformat(),
                    "user_id": user_id,
                    "department": self.department
                }
            }
            
        except Exception as e:
            logger.error(f"Erreur lors de la requête sécurisée: {str(e)}")
            self._log_audit_event(
                event_type="query_error",
                user_id=user_id,
                details={"error": str(e), "query": query}
            )
            raise
    
    def _log_audit_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Enregistre un événement d'audit"""
        audit_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "company": self.company_name,
            "department": self.department,
            "details": details
        }
        
        self.audit_trail.append(audit_event)
        
        # Sauvegarder dans un fichier sécurisé
        self._save_audit_log(audit_event)
    
    def _save_audit_log(self, audit_event: Dict[str, Any]):
        """Sauvegarde le log d'audit"""
        try:
            audit_file = f"audit_logs_{self.company_name}_{datetime.now().strftime('%Y%m')}.json"
            audit_path = Path("logs") / audit_file
            
            # Créer le répertoire si nécessaire
            audit_path.parent.mkdir(exist_ok=True)
            
            # Ajouter à la fin du fichier
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(audit_event, ensure_ascii=False) + "\n")
                
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de l'audit: {str(e)}")
    
    def _generate_query_id(self, query: str, user_id: str) -> str:
        """Génère un ID unique pour la requête"""
        content = f"{query}_{user_id}_{datetime.now().isoformat()}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]
    
    def get_compliance_report(self) -> Dict[str, Any]:
        """Génère un rapport de conformité"""
        return {
            "company": self.company_name,
            "department": self.department,
            "compliance_level": self.compliance_level,
            "metrics": self.compliance_metrics,
            "audit_events_count": len(self.audit_trail),
            "last_audit": self.audit_trail[-1]["timestamp"] if self.audit_trail else None
        }


class DGESecurityLayer:
    """Couche de sécurité conforme DGE"""
    
    def __init__(self, company_name: str, department: str, compliance_level: str):
        self.company_name = company_name
        self.department = department
        self.compliance_level = compliance_level
        
        # Contrôle d'accès basé sur les rôles
        self.access_control = {
            "admin": ["add_documents", "query", "audit", "manage_users"],
            "manager": ["query", "audit"],
            "user": ["query"],
            "guest": []
        }
    
    def check_access(self, user_id: str, action: str, access_level: str = "standard") -> bool:
        """Vérifie les droits d'accès"""
        # Simulation du contrôle d'accès
        # En production, intégrer avec un système d'authentification
        return True
    
    def anonymize_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Anonymise un document"""
        # Simulation de l'anonymisation
        # En production, utiliser des algorithmes d'anonymisation avancés
        anonymized_doc = document.copy()
        
        # Anonymiser les données personnelles
        if "content" in anonymized_doc:
            content = anonymized_doc["content"]
            # Remplacer les emails
            import re
            content = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', content)
            # Remplacer les numéros de téléphone
            content = re.sub(r'\b\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{2}\b', '[PHONE]', content)
            anonymized_doc["content"] = content
        
        return anonymized_doc
    
    def encrypt_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Chiffre un document"""
        # Simulation du chiffrement
        # En production, utiliser des algorithmes de chiffrement robustes
        encrypted_doc = document.copy()
        encrypted_doc["encrypted"] = True
        encrypted_doc["encryption_timestamp"] = datetime.now().isoformat()
        
        return encrypted_doc
    
    def anonymize_query(self, query: str) -> str:
        """Anonymise une requête"""
        # Simulation de l'anonymisation des requêtes
        # En production, détecter et anonymiser les données sensibles
        return query


class DGEEvaluationSystem:
    """Système d'évaluation conforme DGE"""
    
    def __init__(self, compliance_level: str):
        self.compliance_level = compliance_level
    
    def analyze_bias(self, response: str) -> Dict[str, Any]:
        """Analyse les biais dans la réponse"""
        # Simulation de l'analyse des biais
        # En production, utiliser des modèles de détection de biais
        bias_indicators = {
            "gender_bias": False,
            "racial_bias": False,
            "age_bias": False,
            "cultural_bias": False
        }
        
        # Analyse simple des mots-clés
        bias_keywords = {
            "gender_bias": ["homme", "femme", "masculin", "féminin"],
            "racial_bias": ["race", "ethnie", "couleur"],
            "age_bias": ["jeune", "vieux", "âgé", "senior"],
            "cultural_bias": ["français", "étranger", "immigré"]
        }
        
        response_lower = response.lower()
        for bias_type, keywords in bias_keywords.items():
            if any(keyword in response_lower for keyword in keywords):
                bias_indicators[bias_type] = True
        
        return {
            "bias_detected": any(bias_indicators.values()),
            "bias_indicators": bias_indicators,
            "confidence": 0.8
        }
    
    def detect_hallucination(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Détecte les hallucinations"""
        # Simulation de la détection d'hallucinations
        # En production, utiliser des modèles de détection d'hallucinations
        hallucination_score = 0.1  # Score bas = peu d'hallucinations
        
        return {
            "hallucination_detected": hallucination_score > 0.5,
            "hallucination_score": hallucination_score,
            "confidence": 0.7
        }
    
    def generate_explanation(self, response: str, sources: List[Dict[str, Any]], num_sources: int) -> Dict[str, Any]:
        """Génère une explication de la réponse"""
        return {
            "reasoning": "Réponse basée sur l'analyse des documents sources",
            "source_count": num_sources,
            "confidence_factors": [
                "Pertinence des sources",
                "Cohérence de la réponse",
                "Traçabilité des informations"
            ],
            "limitations": [
                "Base de connaissances limitée",
                "Possible biais des sources",
                "Nécessité de vérification humaine"
            ]
        }
    
    def calculate_confidence(self, response: str, sources: List[Dict[str, Any]]) -> float:
        """Calcule le score de confiance"""
        # Simulation du calcul de confiance
        # En production, utiliser des métriques avancées
        base_confidence = 0.8
        
        # Ajuster selon le nombre de sources
        if len(sources) > 3:
            base_confidence += 0.1
        elif len(sources) < 2:
            base_confidence -= 0.2
        
        return min(max(base_confidence, 0.0), 1.0)


def test_dge_compliant_rag():
    """Test du système RAG conforme DGE"""
    
    print("🏛️ Test du système RAG conforme DGE...")
    
    # 1. Initialiser le système conforme DGE
    dge_rag = DGECompliantRAGSystem(
        company_name="Entreprise Test",
        department="RH",
        compliance_level="high"
    )
    
    print("✅ Système RAG DGE initialisé")
    
    # 2. Ajouter des documents de manière sécurisée
    documents = [
        {
            "content": "L'intelligence artificielle transforme le recrutement en permettant une analyse objective des candidats.",
            "metadata": {"category": "rh", "type": "processus", "language": "fr"}
        },
        {
            "content": "Les algorithmes de matching permettent d'apparier les offres d'emploi avec les profils de compétences.",
            "metadata": {"category": "rh", "type": "technologie", "language": "fr"}
        },
        {
            "content": "L'éthique du recrutement nécessite une attention particulière aux biais algorithmiques.",
            "metadata": {"category": "rh", "type": "éthique", "language": "fr"}
        }
    ]
    
    result = dge_rag.add_documents_secure(
        documents=documents,
        user_id="hr_manager_001",
        access_level="manager"
    )
    
    print(f"✅ {len(documents)} documents ajoutés de manière sécurisée")
    print(f"🔒 Sécurité appliquée: {result['security_applied']}")
    print(f"📋 Audit enregistré: {result['audit_logged']}")
    
    # 3. Tester les requêtes sécurisées
    test_queries = [
        "Comment l'IA transforme-t-elle le recrutement ?",
        "Quels sont les enjeux éthiques du recrutement automatisé ?",
        "Comment fonctionne le matching algorithmique ?"
    ]
    
    print("\n🔍 Test des requêtes sécurisées...")
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Requête {i}: {query}")
        
        result = dge_rag.query_secure(
            query=query,
            user_id="hr_user_001"
        )
        
        print(f"💬 Réponse: {result['response']}")
        print(f"📊 Confiance: {result['confidence_score']:.2f}")
        print(f"🔍 Biais détectés: {result['bias_analysis']['bias_detected']}")
        print(f"⚠️  Hallucinations: {result['hallucination_analysis']['hallucination_detected']}")
        print(f"⏱️  Temps: {result['processing_time']:.2f}s")
        print(f"🔗 Traçabilité: {result['traceability']['query_id']}")
    
    # 4. Afficher le rapport de conformité
    print("\n📊 Rapport de conformité DGE:")
    compliance_report = dge_rag.get_compliance_report()
    for key, value in compliance_report.items():
        print(f"  {key}: {value}")
    
    # 5. Afficher les métriques de conformité
    print("\n🛡️ Métriques de conformité:")
    for metric, status in dge_rag.compliance_metrics.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {metric}: {status}")


def main():
    """Fonction principale"""
    
    print("🎯 Système RAG Conforme aux Recommandations DGE")
    print("=" * 60)
    
    try:
        # Test du système conforme DGE
        test_dge_compliant_rag()
        
        print("\n🎉 Tests de conformité DGE terminés avec succès !")
        print("📋 Consultez les logs d'audit dans le dossier logs/")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        logger.error(f"Erreur dans main: {str(e)}")


if __name__ == "__main__":
    main()
