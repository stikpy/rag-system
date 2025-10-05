#!/usr/bin/env python3
"""
Script de configuration rapide
==============================

Ce script guide l'utilisateur dans la configuration des clés API
de manière interactive.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Affiche la bannière du script"""
    print("🚀 Configuration Rapide du Système RAG")
    print("=" * 50)
    print("Ce script vous guide dans la configuration des clés API.")
    print()

def check_env_file():
    """Vérifie et crée le fichier .env si nécessaire"""
    env_path = Path(".env")
    
    if env_path.exists():
        print("✅ Fichier .env trouvé")
        return True
    
    print("📝 Création du fichier .env...")
    
    # Copier env.example vers .env
    try:
        import shutil
        shutil.copy("env.example", ".env")
        print("✅ Fichier .env créé à partir de env.example")
        return True
    except Exception as e:
        print(f"❌ Erreur lors de la création du fichier .env : {e}")
        return False

def get_user_input(prompt, default=None, required=True):
    """Demande une entrée utilisateur avec validation"""
    while True:
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()
        
        if not user_input and required:
            print("❌ Cette valeur est obligatoire")
            continue
        
        return user_input

def configure_mistral():
    """Configure la clé API Mistral"""
    print("\n🔑 Configuration Mistral AI (OBLIGATOIRE)")
    print("-" * 40)
    print("1. Allez sur https://console.mistral.ai/")
    print("2. Créez un compte ou connectez-vous")
    print("3. Allez dans 'API Keys'")
    print("4. Créez une nouvelle clé")
    print("5. Copiez la clé ici")
    print()
    
    api_key = get_user_input("Clé API Mistral", required=True)
    return api_key

def configure_cohere():
    """Configure la clé API Cohere"""
    print("\n🔑 Configuration Cohere (OBLIGATOIRE)")
    print("-" * 40)
    print("1. Allez sur https://dashboard.cohere.ai/")
    print("2. Créez un compte ou connectez-vous")
    print("3. Allez dans 'API Keys'")
    print("4. Créez une nouvelle clé")
    print("5. Copiez la clé ici")
    print()
    
    api_key = get_user_input("Clé API Cohere", required=True)
    return api_key

def configure_supabase():
    """Configure Supabase"""
    print("\n🔑 Configuration Supabase (OBLIGATOIRE)")
    print("-" * 40)
    print("1. Allez sur https://supabase.com/")
    print("2. Créez un compte ou connectez-vous")
    print("3. Créez un nouveau projet")
    print("4. Allez dans 'Settings' > 'API'")
    print("5. Copiez les valeurs suivantes :")
    print()
    
    url = get_user_input("URL Supabase (https://xxx.supabase.co)", required=True)
    anon_key = get_user_input("Clé anon public", required=True)
    service_key = get_user_input("Clé service_role", required=True)
    
    return url, anon_key, service_key

def configure_openai():
    """Configure OpenAI (optionnel)"""
    print("\n🔑 Configuration OpenAI (OPTIONNEL)")
    print("-" * 40)
    print("OpenAI est optionnel. Vous pouvez utiliser seulement Mistral.")
    print("Si vous voulez utiliser GPT-4, configurez OpenAI :")
    print("1. Allez sur https://platform.openai.com/")
    print("2. Créez un compte ou connectez-vous")
    print("3. Allez dans 'API Keys'")
    print("4. Créez une nouvelle clé")
    print("5. Ajoutez des crédits (minimum $5)")
    print()
    
    use_openai = get_user_input("Voulez-vous configurer OpenAI ? (y/n)", default="n", required=False)
    
    if use_openai.lower() in ['y', 'yes', 'oui']:
        api_key = get_user_input("Clé API OpenAI", required=True)
        return api_key
    
    return None

def update_env_file(config):
    """Met à jour le fichier .env avec les nouvelles valeurs"""
    env_path = Path(".env")
    
    try:
        # Lire le fichier actuel
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les valeurs
        replacements = {
            "your_mistral_api_key_here": config.get("mistral_key", "your_mistral_api_key_here"),
            "your_cohere_api_key_here": config.get("cohere_key", "your_cohere_api_key_here"),
            "your_supabase_url_here": config.get("supabase_url", "your_supabase_url_here"),
            "your_supabase_anon_key_here": config.get("supabase_anon_key", "your_supabase_anon_key_here"),
            "your_supabase_service_role_key_here": config.get("supabase_service_key", "your_supabase_service_role_key_here"),
        }
        
        if config.get("openai_key"):
            replacements["your_openai_api_key_here"] = config["openai_key"]
        
        # Appliquer les remplacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Écrire le fichier mis à jour
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fichier .env mis à jour")
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la mise à jour du fichier .env : {e}")
        return False

def test_configuration():
    """Teste la configuration"""
    print("\n🧪 Test de la configuration...")
    
    try:
        # Exécuter le script de vérification
        import subprocess
        result = subprocess.run([
            sys.executable, "scripts/check_api_keys.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Configuration testée avec succès !")
            return True
        else:
            print("❌ Erreurs détectées dans la configuration")
            print(result.stdout)
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test : {e}")
        return False

def main():
    """Fonction principale"""
    print_banner()
    
    # Vérifier le fichier .env
    if not check_env_file():
        return False
    
    # Configuration des services
    config = {}
    
    # Mistral (obligatoire)
    config["mistral_key"] = configure_mistral()
    
    # Cohere (obligatoire)
    config["cohere_key"] = configure_cohere()
    
    # Supabase (obligatoire)
    supabase_config = configure_supabase()
    config["supabase_url"] = supabase_config[0]
    config["supabase_anon_key"] = supabase_config[1]
    config["supabase_service_key"] = supabase_config[2]
    
    # OpenAI (optionnel)
    openai_key = configure_openai()
    if openai_key:
        config["openai_key"] = openai_key
    
    # Mettre à jour le fichier .env
    print("\n📝 Mise à jour du fichier .env...")
    if not update_env_file(config):
        return False
    
    # Tester la configuration
    if test_configuration():
        print("\n🎉 Configuration terminée avec succès !")
        print("\n🚀 Prochaines étapes :")
        print("1. python examples/basic_rag_example.py")
        print("2. python examples/advanced_rag_example.py")
        print("3. Consultez docs/ pour plus d'informations")
        return True
    else:
        print("\n❌ Configuration incomplète. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
