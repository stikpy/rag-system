# 🚀 Démarrage Rapide

## ⚡ Installation en 3 étapes

### 1. **Installation des dépendances**
```bash
python3 scripts/install_dependencies.py
```

### 2. **Configuration des clés API**
```bash
python3 scripts/setup_quick.py
```

### 3. **Test du système**
```bash
python3 examples/basic_rag_example.py
```

## 🔑 Configuration des Clés API

### **Obligatoires** (Gratuites)
- **Mistral AI** : https://console.mistral.ai/ (50k tokens/mois gratuits)
- **Cohere** : https://dashboard.cohere.ai/ (1000 requêtes/mois gratuites)
- **Supabase** : https://supabase.com/ (500MB gratuits)

### **Optionnelles**
- **OpenAI** : https://platform.openai.com/ (payant, pour GPT-4)

## 📋 Checklist de Configuration

### ✅ Prérequis
- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`python3 scripts/install_dependencies.py`)
- [ ] Fichier `.env` créé (`cp env.example .env`)

### ✅ Clés API
- [ ] `MISTRAL_API_KEY` configurée
- [ ] `COHERE_API_KEY` configurée  
- [ ] `SUPABASE_URL` configurée
- [ ] `SUPABASE_KEY` configurée
- [ ] `SUPABASE_SERVICE_ROLE_KEY` configurée

### ✅ Test
- [ ] `python3 scripts/check_api_keys.py` → ✅
- [ ] `python3 examples/basic_rag_example.py` → ✅

## 🎯 Exemples d'Utilisation

### **Basique**
```bash
python3 examples/basic_rag_example.py
```

### **Avancé**
```bash
python3 examples/advanced_rag_example.py
```

### **Langchain**
```bash
python3 examples/langchain_rag_example.py
```

### **Production**
```bash
python3 examples/production_rag_example.py
```

### **Conformité DGE**
```bash
python3 examples/dge_compliant_rag.py
```

## 🛠️ Dépannage

### **Erreur "Module not found"**
```bash
pip install -r requirements.txt
```

### **Erreur "API key not found"**
```bash
# Vérifier le fichier .env
cat .env

# Vérifier la configuration
python3 scripts/check_api_keys.py
```

### **Erreur Supabase**
```bash
# Vérifier l'URL et les clés
# Exécuter le script SQL
psql -f scripts/setup_supabase.sql
```

## 📚 Documentation Complète

- **Guide principal** : `README.md`
- **Configuration API** : `docs/API_KEYS_SETUP.md`
- **Intégration Langchain** : `docs/LANGCHAIN_INTEGRATION.md`
- **Bonnes pratiques DGE** : `docs/DGE_BEST_PRACTICES.md`

## 🆘 Support

- **GitHub Issues** : Ouvrir une issue
- **Documentation** : Consultez `docs/`
- **Exemples** : Testez les exemples dans `examples/`

---

**🎉 Vous êtes prêt à utiliser le système RAG !**
