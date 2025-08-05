# 🧠 Assistant IA interne pour GPSEA – LangChain + RAG + Streamlit

## 🎯 Objectif

Concevoir un assistant conversationnel interne pour **GPSEA** (Grand Paris Sud Est Avenir), permettant aux agents de rechercher rapidement des informations à partir de documents internes (rapports, pages web, PDF). Le système repose sur l’architecture **Retrieval-Augmented Generation (RAG)** et une interface Streamlit.

---

## 🏢 Contexte métier

GPSEA est une structure territoriale regroupant 16 communes du Val-de-Marne. L’entité gère de nombreux domaines : urbanisme, déchets, culture, voirie…  
La **direction des relations usagers** reçoit des centaines de questions internes sur des sujets opérationnels :  
- Horaires d’une médiathèque  
- Nombre d’agents d’un service  
- Taux de collecte des déchets  

Or, les réponses sont **éparpillées** dans des documents internes (PDF, pages web, comptes rendus), peu accessibles rapidement.  
👉 **Le besoin : un outil intelligent pour rechercher dans la base documentaire interne.**

---

## 🧠 Architecture de la solution

### 🔍 Récupération des documents
- 🌐 **Scraping** du site GPSEA (plus de 2700 pages HTML)
- 📄 Intégration de PDF internes
- 📦 Stockage des textes nettoyés et convertis en Markdown

### 🧹 Nettoyage & Prétraitement
- Suppression de bruit HTML (balises, liens, scripts)
- Structuration Markdown
- **Chunking récursif** (segmentation logique avec continuité sémantique)
- Normalisation des dates, doublons, etc.

### 📐 Vectorisation
- Modèle : `all-MiniLM-L6-v2` (HuggingFace)
- Création d’embeddings par chunk
- Stockage dans **ChromaDB** (vector database)
- Indexation avec HNSW (Approximate Nearest Neighbor Search)

### 🧠 LLM & Génération
- Modèle : **LLaMA 3.3** via **Groq API** (ultra basse latence)
- Architecture **RAG-Sequence**
- Prompt engineering : injection de contexte + instructions
- Génération en **streaming** (réponse incrémentale)

### 💬 Interface utilisateur
- **Streamlit** en web app
- Interface conversationnelle avec historique local
- Système de session utilisateur
- Mode streaming des réponses

---

## ⚙️ Stack technique

```yaml
Langages :
  - Python

NLP & Vectorisation :
  - HuggingFace Transformers
  - LangChain
  - SentenceTransformers (MiniLM-L6-v2)

Bases de données :
  - ChromaDB (HNSW indexing)

LLM & API :
  - LLaMA 3.3 (via Groq API)
  - LangChain integrations

Interface :
  - Streamlit (Web UI)

Outils :
  - VS Code, GitHub, Markdown, YAML
```

---

## 📐 Schéma d’architecture

```
[ Pages web / PDFs ]
          ↓
[ Scraping & Nettoyage ]
          ↓
[ Chunking logique ]
          ↓
[ Embedding (MiniLM) ]
          ↓
[ Stockage dans ChromaDB ]
          ↓
[ Requête utilisateur → Embedding ]
          ↓
[ Récupération de k chunks les plus proches ]
          ↓
[ Prompt enrichi ]
          ↓
[ LLaMA 3.3 via LangChain → Réponse ]
          ↓
[ Affichage Streamlit + Historique ]
```

---

## ✅ Résultats

- 🎯 Réponses précises à des requêtes internes complexes
- ⚡ Temps de réponse quasi instantané grâce à Groq
- 🔁 Mises à jour automatiques hebdomadaires du corpus
- 🧩 Architecture modulaire et réutilisable

---

## 🚧 Limites & améliorations

- Le système est uniquement textuel (voix = piste future)
- Limité au français
- Évaluation utilisateur en conditions réelles à mettre en place
- À terme : dashboard admin + journalisation des requêtes + feedback loop

---

## 👩‍💻 Auteur

Projet réalisé dans le cadre du Master 2 MASERATI – UPEC  
👤 **Carlie Valdayard PETIT**  et **Jassen EUGENE**
📍 En partenariat avec **GPSEA**  
📅 Année universitaire : 2024 – 2025

📧 carlievaldayardpetit@gmail.com  
🔗 [LinkedIn](https://linkedin.com/in/carlie-valdayard-petit)

---

> *“RAG is the bridge between frozen models and living knowledge.”*
