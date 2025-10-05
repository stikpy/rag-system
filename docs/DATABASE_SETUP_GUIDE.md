# 🗄️ Configuration de la Base de Données Supabase

## 📋 Vue d'ensemble

Ce guide vous explique comment configurer les URLs de base de données pour Prisma avec Supabase.

## 🔧 Configuration des URLs

### 1. **Obtenir le mot de passe de la base de données**

#### Accéder au Dashboard Supabase
1. Allez sur https://supabase.com/dashboard
2. Sélectionnez votre projet
3. Allez dans **Settings** > **Database**
4. Copiez le mot de passe de la base de données

### 2. **Configurer les variables d'environnement**

#### Fichier .env
```env
# Database Configuration
DATABASE_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:6543/postgres?pgbouncer=true"
DIRECT_URL="postgresql://postgres.nlunnxppbraflzyublfg:[YOUR-PASSWORD]@aws-1-eu-west-3.pooler.supabase.com:5432/postgres"
```

#### Remplacez [YOUR-PASSWORD]
- Remplacez `[YOUR-PASSWORD]` par le mot de passe de votre base de données
- Le mot de passe se trouve dans Supabase > Settings > Database

## 🚀 Test de la Configuration

### 1. **Test de connexion Prisma**
```bash
npx prisma db pull
```

### 2. **Test de Prisma Studio**
```bash
npx prisma studio
```

### 3. **Test du système RAG**
```bash
python examples/basic_rag_example.py
```

## 🔍 Vérification

### Variables d'environnement
```bash
# Vérifier les variables
echo $DATABASE_URL
echo $DIRECT_URL
```

### Test de connexion
```bash
# Test de connexion directe
npx prisma db pull

# Test de Prisma Studio
npx prisma studio
```

## 🚨 Dépannage

### Erreurs Courantes

#### 1. "Environment variable not found"
```bash
# Vérifier le fichier .env
cat .env | grep DATABASE_URL
cat .env | grep DIRECT_URL
```

#### 2. "Connection failed"
```bash
# Vérifier le mot de passe
# Vérifier l'URL du projet
# Vérifier la région (aws-1-eu-west-3)
```

#### 3. "Authentication failed"
```bash
# Vérifier le mot de passe dans Supabase
# Régénérer le mot de passe si nécessaire
```

## 📊 URLs de Base de Données

### **DATABASE_URL** (Connection Pooling)
- **Usage** : Connexions normales
- **Port** : 6543 (pooler)
- **Avantages** : Gestion automatique des connexions
- **Limitations** : Certaines opérations limitées

### **DIRECT_URL** (Direct Connection)
- **Usage** : Migrations, introspection
- **Port** : 5432 (direct)
- **Avantages** : Accès complet à la base
- **Limitations** : Plus de connexions simultanées

## 🔒 Sécurité

### Bonnes Pratiques
1. **Ne jamais commiter les mots de passe**
2. **Utiliser des variables d'environnement**
3. **Régénérer les mots de passe régulièrement**
4. **Limiter les accès par IP si possible**

### Variables Sensibles
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

**🎯 Configuration de la base de données Supabase terminée !**
