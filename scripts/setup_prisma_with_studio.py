#!/usr/bin/env python3
"""
Configuration Prisma avec Studio
===============================

Ce script configure Prisma avec Studio pour la visualisation des données.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_prisma_installed():
    """Vérifie si Prisma est installé"""
    try:
        result = subprocess.run(["npx", "prisma", "--version"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Prisma installé")
            return True
    except:
        pass
    
    print("❌ Prisma non installé")
    return False

def install_prisma():
    """Installe Prisma"""
    print("📦 Installation de Prisma...")
    try:
        subprocess.run(["npm", "install", "-g", "prisma"], check=True)
        print("✅ Prisma installé avec succès")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'installation: {e}")
        return False

def setup_env_variables():
    """Configure les variables d'environnement"""
    print("🔧 Configuration des variables d'environnement...")
    
    # Vérifier si le fichier .env existe
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        print("💡 Créez le fichier .env avec vos variables Supabase")
        return False
    
    # Lire le fichier .env
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Vérifier les variables requises
    required_vars = ["DATABASE_URL", "DIRECT_URL"]
    missing_vars = []
    
    for var in required_vars:
        if f"{var}=" not in content or f"{var}=your_" in content:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables manquantes: {', '.join(missing_vars)}")
        print("💡 Configurez ces variables dans votre fichier .env")
        return False
    
    print("✅ Variables d'environnement configurées")
    return True

def generate_client():
    """Génère le client Prisma"""
    print("🔧 Génération du client Prisma...")
    try:
        result = subprocess.run(["npx", "prisma", "generate"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Client Prisma généré")
            return True
        else:
            print(f"❌ Erreur lors de la génération: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de la génération: {e}")
        return False

def push_schema():
    """Applique le schéma à la base de données"""
    print("📊 Application du schéma à la base de données...")
    try:
        result = subprocess.run(["npx", "prisma", "db", "push"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Schéma appliqué à la base de données")
            return True
        else:
            print(f"❌ Erreur lors de l'application: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Erreur lors de l'application: {e}")
        return False

def start_prisma_studio():
    """Démarre Prisma Studio"""
    print("🎨 Démarrage de Prisma Studio...")
    print("💡 Prisma Studio va s'ouvrir dans votre navigateur")
    print("🌐 URL: http://localhost:5555")
    print("⏹️  Pour arrêter: Ctrl+C")
    
    try:
        # Démarrer Prisma Studio en arrière-plan
        process = subprocess.Popen(["npx", "prisma", "studio"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        print("✅ Prisma Studio démarré")
        print("📋 Fonctionnalités disponibles:")
        print("   - Visualisation des tables")
        print("   - Édition des données")
        print("   - Filtrage et recherche")
        print("   - Relations entre tables")
        
        return process
        
    except Exception as e:
        print(f"❌ Erreur lors du démarrage de Prisma Studio: {e}")
        return None

def create_studio_guide():
    """Crée un guide pour Prisma Studio"""
    print("📚 Création du guide Prisma Studio...")
    
    guide_content = '''# 🎨 Guide Prisma Studio

## 📋 Vue d'ensemble

Prisma Studio est une interface graphique pour visualiser et gérer vos données Supabase.

## 🚀 Démarrage

### 1. **Démarrer Prisma Studio**
```bash
npx prisma studio
```

### 2. **Accéder à l'interface**
- URL: http://localhost:5555
- Interface web moderne et intuitive

## 🔧 Fonctionnalités

### **Visualisation des Données**
- **Tables** : Vue d'ensemble de toutes les tables
- **Relations** : Navigation entre les relations
- **Filtres** : Recherche et filtrage avancé
- **Pagination** : Navigation dans les grandes datasets

### **Gestion des Données**
- **Création** : Ajouter de nouveaux enregistrements
- **Édition** : Modifier les données existantes
- **Suppression** : Supprimer des enregistrements
- **Import/Export** : Gestion des données en masse

### **Tables Disponibles**

#### **Documents**
- `id` : Identifiant unique
- `content` : Contenu du document
- `metadata` : Métadonnées JSON
- `createdAt` : Date de création
- `updatedAt` : Date de modification

#### **Document Chunks**
- `id` : Identifiant unique
- `documentId` : ID du document parent
- `content` : Contenu du chunk
- `metadata` : Métadonnées JSON
- `chunkIndex` : Index du chunk
- `createdAt` : Date de création
- `updatedAt` : Date de modification

#### **Queries**
- `id` : Identifiant unique
- `query` : Requête utilisateur
- `response` : Réponse générée
- `metadata` : Métadonnées JSON
- `createdAt` : Date de création
- `updatedAt` : Date de modification

## 🎯 Cas d'Usage

### **Développement**
- Vérifier les données de test
- Déboguer les requêtes
- Valider les relations

### **Production**
- Monitoring des données
- Gestion des utilisateurs
- Analyse des performances

### **Maintenance**
- Nettoyage des données
- Migration des données
- Sauvegarde et restauration

## 🔍 Recherche et Filtrage

### **Recherche Textuelle**
- Recherche dans le contenu
- Filtrage par métadonnées
- Recherche par date

### **Filtres Avancés**
- Filtres par relation
- Filtres par plage de dates
- Filtres par statut

## 📊 Statistiques

### **Métriques Disponibles**
- Nombre total d'enregistrements
- Taille des données
- Relations les plus utilisées
- Activité récente

## 🚨 Dépannage

### **Problèmes Courants**

#### 1. "Studio not starting"
```bash
# Vérifier la connexion
npx prisma db pull

# Redémarrer Studio
npx prisma studio
```

#### 2. "Connection failed"
```bash
# Vérifier les variables d'environnement
echo $DATABASE_URL
echo $DIRECT_URL
```

#### 3. "Tables not visible"
```bash
# Synchroniser le schéma
npx prisma db push
```

## 📞 Support

### **Ressources Officielles**
- **Prisma Studio Docs** : https://www.prisma.io/docs/studio
- **Prisma Docs** : https://www.prisma.io/docs
- **Supabase Docs** : https://supabase.com/docs

### **Support Communauté**
- **GitHub Issues** : Ouvrir une issue
- **Discord** : Rejoindre le serveur
- **Stack Overflow** : Tag `prisma`

---

**🎨 Prisma Studio - Interface de gestion des données Supabase**
'''
    
    guide_file = Path("docs/PRISMA_STUDIO_GUIDE.md")
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guide Prisma Studio créé: docs/PRISMA_STUDIO_GUIDE.md")
    return True

def create_studio_script():
    """Crée un script pour démarrer Prisma Studio"""
    print("📝 Création du script de démarrage...")
    
    script_content = '''#!/usr/bin/env python3
"""
Script de démarrage Prisma Studio
================================

Ce script démarre Prisma Studio avec les bonnes configurations.
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def start_prisma_studio():
    """Démarre Prisma Studio"""
    print("🎨 Démarrage de Prisma Studio...")
    print("=" * 40)
    
    try:
        # Vérifier que Prisma est installé
        result = subprocess.run(["npx", "prisma", "--version"], 
                              capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Prisma non installé")
            print("💡 Installez Prisma : npm install -g prisma")
            return False
        
        print("✅ Prisma installé")
        
        # Générer le client si nécessaire
        print("🔧 Génération du client Prisma...")
        result = subprocess.run(["npx", "prisma", "generate"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Client Prisma généré")
        else:
            print("⚠️  Erreur lors de la génération du client")
        
        # Démarrer Prisma Studio
        print("🚀 Démarrage de Prisma Studio...")
        print("🌐 URL: http://localhost:5555")
        print("⏹️  Pour arrêter: Ctrl+C")
        print()
        
        # Ouvrir le navigateur après un délai
        def open_browser():
            time.sleep(3)
            webbrowser.open("http://localhost:5555")
        
        import threading
        browser_thread = threading.Thread(target=open_browser)
        browser_thread.daemon = True
        browser_thread.start()
        
        # Démarrer Prisma Studio
        subprocess.run(["npx", "prisma", "studio"])
        
        return True
        
    except KeyboardInterrupt:
        print("\\n⏹️  Prisma Studio arrêté")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du démarrage: {e}")
        return False

if __name__ == "__main__":
    success = start_prisma_studio()
    sys.exit(0 if success else 1)
'''
    
    script_file = Path("scripts/start_prisma_studio.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendre le script exécutable
    script_file.chmod(0o755)
    
    print("✅ Script de démarrage créé: scripts/start_prisma_studio.py")
    return True

def main():
    """Fonction principale"""
    print("🎨 Configuration Prisma avec Studio")
    print("=" * 50)
    
    # Vérifier Prisma
    if not check_prisma_installed():
        if not install_prisma():
            return False
    
    # Configurer les variables d'environnement
    if not setup_env_variables():
        return False
    
    # Générer le client
    if not generate_client():
        return False
    
    # Appliquer le schéma
    if not push_schema():
        return False
    
    # Créer le guide
    if not create_studio_guide():
        return False
    
    # Créer le script de démarrage
    if not create_studio_script():
        return False
    
    print("\n🎉 Configuration Prisma avec Studio terminée !")
    print("\n📋 Prochaines étapes :")
    print("1. Démarrer Prisma Studio : python scripts/start_prisma_studio.py")
    print("2. Ou directement : npx prisma studio")
    print("3. Accéder à l'interface : http://localhost:5555")
    print("4. Consultez docs/PRISMA_STUDIO_GUIDE.md pour plus d'informations")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
