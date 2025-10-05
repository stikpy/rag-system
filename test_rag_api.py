#!/usr/bin/env python3
"""
Script de test pour l'API RAG.
"""

import requests
import json

def test_rag_api():
    """Test de l'API RAG."""
    print("🧪 Test de l'API RAG...")
    print("=" * 50)
    
    # URL de l'API
    url = "http://localhost:8082/api/rag"
    
    # Question de test
    question = "as tu des données ?"
    
    print(f"❓ Question: {question}")
    print(f"🌐 URL: {url}")
    
    try:
        # Préparer les données
        data = {
            "question": question
        }
        
        print(f"📤 Envoi des données: {data}")
        
        # Faire la requête
        response = requests.post(
            url,
            json=data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"📊 Status code: {response.status_code}")
        print(f"📊 Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Réponse reçue: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result.get('status') == 'success':
                print("🎉 Test réussi !")
                return True
            else:
                print("❌ Erreur dans la réponse")
                return False
        else:
            print(f"❌ Erreur HTTP: {response.status_code}")
            print(f"📄 Contenu: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erreur de connexion - L'interface web n'est pas accessible")
        return False
    except requests.exceptions.Timeout:
        print("❌ Timeout - La requête a pris trop de temps")
        return False
    except Exception as e:
        print(f"❌ Erreur générale: {e}")
        return False

if __name__ == "__main__":
    success = test_rag_api()
    if not success:
        print("\n🔧 Vérifiez que l'interface web est lancée sur http://localhost:8082")
        exit(1)
    else:
        print("\n✅ Test de l'API RAG réussi !")
