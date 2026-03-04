# 🗞️ Deep Blue News Summarizer

A modern, intelligent news summarization application that uses **LangChain**, **NewsAPI**, **Chroma Vector Database**, and **Groq LLM** to fetch, embed, and summarize news articles.

Features a beautiful **deep-blue/purple themed UI** built with Streamlit.

---

## 📋 Table of Contents

- [Features](#features)
- [Architecture & Pipeline](#architecture--pipeline)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
  - [CLI Mode](#cli-mode)
  - [Streamlit UI](#streamlit-ui)
- [Module Documentation](#module-documentation)
- [API Keys & Requirements](#api-keys--requirements)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

✅ **Dual Interface**: CLI and modern Streamlit UI  
✅ **Two Summarization Modes**: Brief (1-2 sentences) and Detailed (bullet points)  
✅ **Persistent Vector Database**: LangChain + Chroma for efficient semantic search  
✅ **User Preferences**: Save favorite topics and track search history  
✅ **Smart URL Filtering**: Avoids consent/support pages automatically  
✅ **Deep Blue/Purple Theme**: Beautiful, modern interface with gradient accents  
✅ **Async-Ready Architecture**: Modular components for easy extension  

---

## 🏗️ Architecture & Pipeline

```
┌─────────────┐
│   User      │
│   Query     │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│   NewsAPI Client     │  ← Fetch latest articles
│   get_everything()   │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────┐
│  Normalize & Filter  │  ← Remove duplicates, bad URLs
│  LangChain Docs      │
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────┐
│  SentenceTransformers    │  ← Generate embeddings
│  (all-MiniLM-L6-v2)      │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   Chroma Vector Store    │  ← Persist embeddings locally
│   (./chroma_db)          │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   Semantic Retrieval     │  ← Similarity search with personalization
│   (similarity_search)    │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   Groq LLM (LangChain)   │  ← llama-3.1-8b-instant
│   Brief / Detailed       │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│   Summarized Results     │  ← + Sources + Metadata
│   + User Preferences     │
└──────────────────────────┘
```

---

## 📁 Project Structure

```
news-summarizer/
├── news_retriever.py        # NewsAPI + deduplication logic
├── embedding_engine.py      # Chroma vector store setup
├── summarizer.py            # Brief/Detailed LLM summarization
├── user_manager.py          # Preferences & history persistence
├── main.py                  # CLI interface
├── streamlit_app.py         # Beautiful Streamlit UI (deep-blue/purple theme)
├── user_preferences.json    # User data (auto-generated)
├── chroma_db/               # Vector store data (auto-generated)
├── .env                     # Environment variables (create this)
├── requirements.txt         # Python dependencies
└── README.md                # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.9+**
- **API Keys**:
  - NewsAPI key: https://newsapi.org/
  - Groq API key: https://console.groq.com/

### Step 1: Clone & Setup

```bash
# Navigate to project directory
cd news-summarizer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Create `.env` File

Create a file named `.env` in the project root:

```env
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_api_key_here
```

Replace with your actual API keys.

---

## ⚙️ Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `NEWS_API_KEY` | Yes | API key from newsapi.org |
| `GROQ_API_KEY` | Yes | API key from console.groq.com |

### Vector Store

- **Location**: `./chroma_db/` (created automatically)
- **Model**: `all-MiniLM-L6-v2` (SentenceTransformers)
- **Collection**: `news_articles`

### Preferences File

- **File**: `user_preferences.json` (auto-created)
- **Contains**: Saved topics, search history, user settings

---

## 📖 Usage

### CLI Mode

Run the command-line interface:

```bash
python main.py
```

**Menu Options:**
1. 🔍 Search + Brief Summary
2. 📊 Search + Detailed Summary
3. ⭐ Save a Topic
4. 📑 View Saved Topics
5. 📜 View Search History
6. 🗑️ Clear History
0. 🚪 Exit

**Example Workflow:**

```
Choose (0-6): 1
Enter topic: artificial intelligence
📰 BRIEF SUMMARY

[Summary text...]

📚 SOURCES:
1. Title of article
   🔗 https://example.com/article
```

### Streamlit UI

Run the beautiful web interface:

```bash
streamlit run streamlit_app.py
```

This opens a browser at `http://localhost:8501/`

**Features in UI:**

- **🔍 Search & Summarize Tab**: Main search interface with brief/detailed summaries
- **⭐ Saved Topics Tab**: Manage favorite topics
- **📜 History Tab**: View search history and statistics
- **⚙️ Settings Tab**: Configure language, article count, check API status

---

## 📚 Module Documentation

### `news_retriever.py`

**Class: `NewsRetriever`**

Handles fetching articles from NewsAPI.

```python
from news_retriever import NewsRetriever

retriever = NewsRetriever(api_key="your_key")
docs = retriever.fetch_articles(topic="AI", page_size=10, language="en")
```

**Methods:**
- `fetch_articles(topic, page_size, language)` → `List[Document]`
  - Fetches articles, removes duplicates and bad URLs
- `dedupe_by_url(docs)` → `List[Document]`
  - Deduplicates documents by URL

---

### `embedding_engine.py`

**Class: `EmbeddingEngine`**

Manages embeddings and Chroma vector store.

```python
from embedding_engine import EmbeddingEngine

engine = EmbeddingEngine(persist_directory="./chroma_db")
engine.add_documents(docs)
results = engine.search(query="AI breakthroughs", k=5)
```

**Methods:**
- `add_documents(docs)` → `None`
  - Add LangChain Documents to vector store
- `search(query, k)` → `List[Document]`
  - Semantic similarity search
- `get_retriever()` → LangChain Retriever
  - Get retriever instance for chains

---

### `summarizer.py`

**Class: `Summarizer`**

Implements LLM-based summarization using Groq.

```python
from summarizer import Summarizer

summarizer = Summarizer(groq_api_key="your_key")
brief = summarizer.summarize_brief(docs)
detailed = summarizer.summarize_detailed(docs)
```

**Methods:**
- `summarize_brief(docs)` → `str`
  - 1-2 sentence summary
- `summarize_detailed(docs)` → `str`
  - 6-10 bullet point summary (map-reduce)

**Character Limits:**
- Total: 4000 chars
- Per document: 1200 chars
- Prevents token overflow

---

### `user_manager.py`

**Class: `UserManager`**

Manages user preferences and search history.

```python
from user_manager import UserManager

manager = UserManager(prefs_file="user_preferences.json")
manager.save_topic("AI")
topics = manager.get_saved_topics()
history = manager.get_history(limit=10)
```

**Methods:**
- `load_prefs()` → `Dict`
- `save_prefs(prefs)` → `None`
- `save_topic(topic)` → `bool`
- `remove_topic(topic)` → `bool`
- `get_saved_topics()` → `List[str]`
- `add_history_entry(topic, n_results)` → `None`
- `get_history(limit)` → `List[Dict]`
- `clear_history()` → `None`

---

## 🔑 API Keys & Requirements

### NewsAPI

1. Visit: https://newsapi.org/
2. Sign up (free tier available)
3. Get your API key
4. Add to `.env`: `NEWS_API_KEY=xxx`

### Groq

1. Visit: https://console.groq.com/
2. Sign up with GitHub or email
3. Get your API key
4. Add to `.env`: `GROQ_API_KEY=xxx`

### Python Dependencies

See `requirements.txt`:

```
python-dotenv
newsapi-client
langchain
langchain-core
langchain-community
langchain-groq
sentence-transformers
chromadb
streamlit
```

---

## 🐛 Troubleshooting

### "NEWS_API_KEY is missing"

**Solution:** Create `.env` file with your NewsAPI key:
```env
NEWS_API_KEY=your_actual_key
GROQ_API_KEY=your_actual_key
```

### "No documents to summarize"

**Causes:**
- Bad internet connection
- Topic has no articles
- All URLs filtered out as "bad"

**Solution:** Try a more general topic like "technology" or "news"

### Chroma database errors

**Solution:** Delete `chroma_db/` folder and restart:
```bash
rm -r chroma_db
python main.py  # or streamlit run streamlit_app.py
```

### Slow summarization

**Causes:**
- Groq API rate limiting
- Large number of documents

**Solution:**
- Reduce `page_size` in settings
- Wait a moment, then retry
- Check Groq console for rate limits

### Streamlit connection refused

**Solution:**
```bash
# Kill existing Streamlit processes
pkill streamlit  # or use Process Manager on Windows

# Restart
streamlit run streamlit_app.py
```

---

## 📊 Example Workflows

### Workflow 1: CLI - Quick Summary

```bash
python main.py
# Choose: 1
# Topic: "quantum computing"
# View 1-2 sentence summary + sources
```

### Workflow 2: Streamlit - Detailed Research

1. Open `http://localhost:8501/`
2. Search for "renewable energy"
3. Click "Detailed Summary"
4. Read multi-point analysis
5. Save topic to favorites
6. Check history tab for statistics

### Workflow 3: Personalized Summaries

1. Save multiple topics: "AI", "Climate", "Tech Policy"
2. Search for "neural networks"
3. System personalized query: "neural networks + user interests: AI, Tech Policy"
4. Retrieval returns more relevant articles
5. Summary focused on your interests

---

## 🎨 UI Theme

The Streamlit app uses a custom **deep-blue/purple theme**:

- **Primary**: Dark navy (#0B1020)
- **Accent**: Purple gradient (#7C3AED → #A855F7)
- **Cards**: Semi-transparent blue backgrounds
- **Buttons**: Purple gradients with glow effects
- **Text**: Light indigo (#E0E7FF)

To customize, edit the CSS in `streamlit_app.py` under the `<style>` section.

---

## 📝 License

This project is open source and available for academic and commercial use.

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more summarization models
- [ ] Multi-language support improvements
- [ ] Database export features
- [ ] Real-time article updates
- [ ] Advanced filtering options
- [ ] User authentication

---

## 📧 Support

For issues, questions, or feature requests, please refer to the troubleshooting section or review the module documentation above.

---

**Happy summarizing! 🚀📰**
