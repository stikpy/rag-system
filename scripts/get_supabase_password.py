#!/usr/bin/env python3
"""
Guide pour obtenir le mot de passe Supabase
==========================================

Ce script vous guide pour obtenir le bon mot de passe depuis Supabase.
"""

import os
import sys
from pathlib import Path

def create_password_guide():
    """Crée un guide pour obtenir le mot de passe"""
    print("📚 Création du guide pour obtenir le mot de passe Supabase...")
    
    guide_content = '''# 🔑 Guide pour obtenir le mot de passe Supabase

## 🚨 Problème d'authentification

L'erreur `password authentication failed` indique que le mot de passe utilisé n'est pas correct.

## 🔍 Étapes pour obtenir le bon mot de passe

### 1. **Accéder au Dashboard Supabase**
1. Allez sur https://supabase.com/dashboard
2. Connectez-vous à votre compte
3. Sélectionnez votre projet

### 2. **Accéder aux paramètres de la base de données**
1. Dans le menu de gauche, cliquez sur **Settings**
2. Cliquez sur **Database**
3. Faites défiler jusqu'à la section **Connection string**

### 3. **Obtenir le mot de passe**
1. Dans la section **Connection string**, vous verrez :
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.nlunnxppbraflzyublfg.supabase.co:5432/postgres
   ```
2. Copiez le mot de passe entre les crochets `[YOUR-PASSWORD]`

### 4. **Alternative : Régénérer le mot de passe**
1. Dans **Settings** > **Database**
2. Cliquez sur **Reset database password**
3. Copiez le nouveau mot de passe généré

## 🔧 Configuration des variables

### 1. **Mettre à jour le fichier .env**
```env
# Database Configuration
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[NOUVEAU-MOT-DE-PASSE]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"

# Direct connection to the database. Used for migrations
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[NOUVEAU-MOT-DE-PASSE]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

### 2. **Remplacez [NOUVEAU-MOT-DE-PASSE]**
- Remplacez `[NOUVEAU-MOT-DE-PASSE]` par le mot de passe obtenu
- Gardez les crochets `[]` dans l'URL

## 🧪 Test de la configuration

### 1. **Test avec psql (optionnel)**
```bash
psql "postgresql://postgres.nlunnxppbraflzyublfg:[MOT-DE-PASSE]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

### 2. **Test avec Prisma**
```bash
npx prisma db pull
```

### 3. **Test avec Prisma Studio**
```bash
npx prisma studio
```

## 🚨 Dépannage

### Erreurs courantes

#### 1. **"password authentication failed"**
- Vérifiez que le mot de passe est correct
- Vérifiez qu'il n'y a pas d'espaces dans le mot de passe
- Régénérez le mot de passe si nécessaire

#### 2. **"connection refused"**
- Vérifiez l'URL du projet
- Vérifiez la région (aws-1-eu-west-3)
- Vérifiez le port (5432 pour direct, 6543 pour pooling)

#### 3. **"database does not exist"**
- Vérifiez que le projet Supabase est actif
- Vérifiez que la base de données est accessible

## 📊 URLs de connexion

### **Format des URLs**
```
# Connection pooling (pour les applications)
DATABASE_URL="postgresql://postgres.[PROJECT-ID]:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"

# Direct connection (pour les migrations)
DIRECT_URL="postgresql://postgres.[PROJECT-ID]:[PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

### **Votre configuration actuelle**
- **Project ID** : `nlunnxppbraflzyublfg`
- **Région** : `aws-1-eu-west-3`
- **Port pooling** : `6543`
- **Port direct** : `5432`

## 🔒 Sécurité

### Bonnes pratiques
1. **Ne jamais commiter les mots de passe**
2. **Utiliser des variables d'environnement**
3. **Régénérer les mots de passe régulièrement**
4. **Limiter les accès par IP si possible**

### Variables sensibles
```bash
# Ajouter au .gitignore
.env
.env.local
.env.production
```

## 📞 Support

### Ressources Officielles
- **Supabase Docs** : https://supabase.com/docs
- **Prisma Docs** : https://www.prisma.io/docs
- **PostgreSQL Docs** : https://www.postgresql.org/docs

### Support Communauté
- **GitHub Issues** : Ouvrir une issue
- **Discord** : Rejoindre le serveur
- **Stack Overflow** : Tag `supabase` + `prisma`

---

**🔑 Guide pour obtenir le mot de passe Supabase**
'''
    
    guide_file = Path("docs/SUPABASE_PASSWORD_GUIDE.md")
    guide_file.parent.mkdir(exist_ok=True)
    
    with open(guide_file, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    
    print("✅ Guide créé: docs/SUPABASE_PASSWORD_GUIDE.md")
    return True

def create_password_script():
    """Crée un script pour mettre à jour le mot de passe"""
    print("📝 Création du script de mise à jour du mot de passe...")
    
    script_content = '''#!/usr/bin/env python3
"""
Script de mise à jour du mot de passe Supabase
============================================

Ce script vous aide à mettre à jour le mot de passe dans le fichier .env.
"""

import os
import sys
from pathlib import Path

def update_password():
    """Met à jour le mot de passe dans le fichier .env"""
    print("🔑 Mise à jour du mot de passe Supabase")
    print("=" * 50)
    
    # Demander le nouveau mot de passe
    new_password = input("Entrez le nouveau mot de passe Supabase: ").strip()
    
    if not new_password:
        print("❌ Mot de passe vide")
        return False
    
    # Lire le fichier .env
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ Fichier .env non trouvé")
        return False
    
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remplacer le mot de passe dans les URLs
    content_updated = content.replace('[1Arene2Folie]', new_password)
    
    # Écrire le fichier mis à jour
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(content_updated)
    
    print("✅ Mot de passe mis à jour dans le fichier .env")
    return True

def test_connection():
    """Teste la connexion avec le nouveau mot de passe"""
    print("\\n🧪 Test de la connexion...")
    
    try:
        import subprocess
        
        # Test avec npx prisma db pull
        result = subprocess.run(["npx", "prisma", "db", "pull"], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Connexion réussie !")
            return True
        else:
            print(f"❌ Erreur de connexion: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur lors du test: {e}")
        return False

def main():
    """Fonction principale"""
    print("🔑 Script de mise à jour du mot de passe Supabase")
    print("=" * 60)
    
    # Mettre à jour le mot de passe
    if not update_password():
        return False
    
    # Tester la connexion
    if not test_connection():
        print("\\n❌ Test de connexion échoué")
        print("💡 Vérifiez que le mot de passe est correct")
        return False
    
    print("\\n🎉 Configuration terminée avec succès !")
    print("\\n📋 Prochaines étapes :")
    print("1. npx prisma db push")
    print("2. npx prisma studio")
    print("3. python examples/basic_rag_example.py")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
'''
    
    script_file = Path("scripts/update_supabase_password.py")
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # Rendre le script exécutable
    script_file.chmod(0o755)
    
    print("✅ Script créé: scripts/update_supabase_password.py")
    return True

def main():
    """Fonction principale"""
    print("🔑 Guide pour obtenir le mot de passe Supabase")
    print("=" * 60)
    
    # Créer le guide
    if not create_password_guide():
        return False
    
    # Créer le script de mise à jour
    if not create_password_script():
        return False
    
    print("\n🎉 Guide et script créés !")
    print("\n📋 Prochaines étapes :")
    print("1. Consultez docs/SUPABASE_PASSWORD_GUIDE.md")
    print("2. Obtenez le bon mot de passe depuis Supabase Dashboard")
    print("3. Exécutez: python scripts/update_supabase_password.py")
    print("4. Testez la connexion: npx prisma db pull")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
