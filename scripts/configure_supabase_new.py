#!/usr/bin/env python3
"""
Script de configuration Supabase - Nouveau Format
===============================================

Ce script guide l'utilisateur dans la configuration du nouveau format des clés API Supabase.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Affiche la bannière du script"""
    print("🔑 Configuration Supabase - Nouveau Format")
    print("=" * 50)
    print("Ce script vous guide dans la configuration du nouveau format des clés API Supabase.")
    print()

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

def configure_supabase():
    """Configure Supabase avec le nouveau format"""
    print("\n🔑 Configuration Supabase (Nouveau Format)")
    print("-" * 50)
    print("1. Allez sur https://supabase.com/dashboard")
    print("2. Sélectionnez votre projet")
    print("3. Allez dans 'Settings' > 'API Keys'")
    print("4. Copiez les valeurs suivantes :")
    print()
    
    url = get_user_input("URL Supabase (https://xxx.supabase.co)", required=True)
    publishable_key = get_user_input("Publishable Key (sb_publishable_xxx)", required=True)
    secret_key = get_user_input("Secret Key (sb_secret_xxx)", required=True)
    
    return url, publishable_key, secret_key

def update_env_file(config):
    """Met à jour le fichier .env avec les nouvelles valeurs"""
    env_path = Path(".env")
    
    try:
        # Lire le fichier actuel
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remplacer les valeurs
        replacements = {
            "your_supabase_url_here": config["url"],
            "your_supabase_anon_key_here": config["publishable_key"],
            "your_supabase_service_role_key_here": config["secret_key"],
        }
        
        # Appliquer les remplacements
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Ajouter le nouveau format si pas présent
        if "SUPABASE_PUBLISHABLE_KEY" not in content:
            # Ajouter après SUPABASE_URL
            content = content.replace(
                f"SUPABASE_URL={config['url']}",
                f"SUPABASE_URL={config['url']}\nSUPABASE_PUBLISHABLE_KEY={config['publishable_key']}\nSUPABASE_SECRET_KEY={config['secret_key']}"
            )
        
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
        # Exécuter le script de test
        import subprocess
        result = subprocess.run([
            sys.executable, "scripts/test_supabase_new_format.py"
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
    
    # Configuration Supabase
    supabase_config = configure_supabase()
    config = {
        "url": supabase_config[0],
        "publishable_key": supabase_config[1],
        "secret_key": supabase_config[2]
    }
    
    # Mettre à jour le fichier .env
    print("\n📝 Mise à jour du fichier .env...")
    if not update_env_file(config):
        return False
    
    # Tester la configuration
    if test_configuration():
        print("\n🎉 Configuration Supabase terminée avec succès !")
        print("\n🚀 Prochaines étapes :")
        print("1. python examples/basic_rag_example.py")
        print("2. python examples/advanced_rag_example.py")
        print("3. Consultez docs/SUPABASE_NEW_API_FORMAT.md pour plus d'informations")
        return True
    else:
        print("\n❌ Configuration incomplète. Vérifiez les erreurs ci-dessus.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
