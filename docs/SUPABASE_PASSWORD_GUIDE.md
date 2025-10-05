# 🔑 Guide pour obtenir le mot de passe Supabase

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
