# 🚀 Instructions de Configuration

## Configuration des Clés API

Après avoir cloné le repository, suivez ces étapes pour configurer votre environnement :

### 1. Copier le fichier d'environnement

```bash
cp .env.example .env.local
```

### 2. Configurer vos clés API

Éditez le fichier `.env.local` avec vos vraies clés API :

```bash
# Mistral AI Configuration
MISTRAL_API_KEY=votre_vraie_mistral_api_key

# OpenAI Configuration  
OPENAI_API_KEY=votre_vraie_openai_api_key

# Cohere Configuration
COHERE_API_KEY=votre_vraie_cohere_api_key

# Supabase Configuration
SUPABASE_URL=votre_supabase_url
SUPABASE_PUBLISHABLE_KEY=votre_supabase_publishable_key
SUPABASE_SECRET_KEY=votre_supabase_secret_key

# Database Configuration
DATABASE_URL="postgresql://user:password@host:port/database?pgbouncer=true"
DIRECT_URL="postgresql://user:password@host:port/database"
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
npm install -g prisma
```

### 4. Générer le client Prisma

```bash
prisma generate
```

### 5. Tester la connexion

```bash
python3 scripts/test_final_connection.py
```

### 6. Lancer Prisma Studio

```bash
prisma studio
```

## 🔒 Sécurité

- Le fichier `.env.local` est dans `.gitignore` et ne sera jamais committé
- Utilisez toujours `.env.example` comme template
- Ne partagez jamais vos vraies clés API

## 📚 Documentation

- [Guide de configuration Supabase](docs/SUPABASE_SETUP_GUIDE.md)
- [Configuration Prisma](docs/PRISMA_SUPABASE_SETUP.md)
- [Intégration Langchain](docs/LANGCHAIN_INTEGRATION.md)
- [Bonnes pratiques DGE](docs/DGE_BEST_PRACTICES.md)

## 🆘 Support

En cas de problème, consultez les logs ou ouvrez une issue sur GitHub.
