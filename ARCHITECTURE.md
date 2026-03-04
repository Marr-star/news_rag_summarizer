# Architecture Documentation

## System Overview

The Deep Blue News Summarizer follows a **microservices-inspired modular architecture** where each component has a single responsibility.

---

## Component Responsibilities

### 1. **news_retriever.py** - Data Acquisition Layer

**Responsibility**: Fetch and normalize news articles from external sources.

**Key Classes**:
- `BadURLFilter`: Static utility class for URL validation
  - Filters out consent pages, support portals, auth pages
  - Uses regex patterns for quick identification
  
- `NewsRetriever`: Main article fetching and normalization
  - Calls NewsAPI `get_everything()` endpoint
  - Converts articles to LangChain `Document` objects
  - Removes duplicates by URL
  - Adds rich metadata (title, source, rating, date, etc.)

**Interface**:
```python
retriever = NewsRetriever(api_key: str)
docs: List[Document] = retriever.fetch_articles(
    topic: str,
    page_size: int = 10,
    language: str = "en"
) → List[Document]
```

**Output Format** (LangChain Document):
```python
Document(
    page_content="Title: ...\nDescription: ...\nContent: ...",
    metadata={
        "url": "...",
        "source": "CNN",
        "publishedAt": "2024-03-03T...",
        "topic": "artificial intelligence",
        "title": "New AI Model...",
        "author": "...",
        "image": "..."
    }
)
```

---

### 2. **embedding_engine.py** - Vector Database Layer

**Responsibility**: Generate embeddings and manage persistent vector store.

**Key Classes**:
- `EmbeddingEngine`: Handles all vector DB operations
  - Uses `SentenceTransformerEmbeddings` (all-MiniLM-L6-v2)
  - Local persistence in `./chroma_db/` directory
  - HNSW indexing for fast similarity search

**Embedding Model**:
- Model: `all-MiniLM-L6-v2`
- Dimensions: 384
- Speed: ~1000 embeddings/second
- Size: ~90MB

**Interface**:
```python
engine = EmbeddingEngine(
    model_name: str = "all-MiniLM-L6-v2",
    persist_directory: str = "./chroma_db",
    collection_name: str = "news_articles"
)

engine.add_documents(docs: List[Document]) → None

results: List[Document] = engine.search(
    query: str,
    k: int = 5
) → List[Document]

retriever = engine.get_retriever() → LangChain Retriever
```

**Retrieval Strategy**:
- Semantic similarity search using vector dot product
- Top-K results (default K=5)
- Can be combined with metadata filters

---

### 3. **summarizer.py** - LLM Integration Layer

**Responsibility**: Transform retrieved documents into human-readable summaries.

**Key Classes**:
- `Summarizer`: LLM-powered summarization engine
  - Uses Groq API (via LangChain)
  - Two summarization strategies:

**Strategy 1: Brief Summary**
- Approach: Direct prompt to LLM
- Output: 1-2 sentences
- Speed: ~1-2 seconds
- Tokens: ~100-200

**Strategy 2: Detailed Summary (Map-Reduce)**
- Approach: 
  1. **Map**: Summarize each document briefly (1-2 sentences)
  2. **Reduce**: Combine all brief summaries into structured output
- Output: 6-10 bullet points grouped by theme
- Speed: ~5-10 seconds
- Tokens: ~500-800

**Safety Limits**:
```python
MAX_TOTAL_CHARS = 4000      # Total input to LLM
MAX_DOC_CHARS = 1200        # Per-document limit
MAX_MAP_CHARS = 1200        # Per-document in map phase
```

**Interface**:
```python
summarizer = Summarizer(
    groq_api_key: str,
    model_name: str = "llama-3.1-8b-instant"
)

brief = summarizer.summarize_brief(docs: List[Document]) → str

detailed = summarizer.summarize_detailed(docs: List[Document]) → str
```

---

### 4. **user_manager.py** - Persistence & Preferences Layer

**Responsibility**: Maintain user state across sessions.

**Persistence Strategy**:
- Single JSON file: `user_preferences.json`
- Schema versioning not required (flexible JSON)
- Auto-creation of defaults on first run

**Data Structures**:

```json
{
  "saved_topics": ["AI", "Climate Change"],
  "history": [
    {
      "topic": "AI",
      "results": 10,
      "timestamp": "2024-03-03T14:30:00"
    }
  ],
  "settings": {
    "language": "en",
    "page_size": 10
  }
}
```

**Key Methods**:
```python
manager = UserManager(prefs_file: str = "user_preferences.json")

# Topic management
manager.save_topic(topic: str) → bool
manager.remove_topic(topic: str) → bool
topics: List[str] = manager.get_saved_topics()

# History management
manager.add_history_entry(topic: str, n_results: int) → None
history: List[Dict] = manager.get_history(limit: int = 10)
manager.clear_history() → None

# Settings
value = manager.get_setting(key: str, default=None)
manager.set_setting(key: str, value: Any)
```

---

### 5. **main.py** - CLI Interface

**Responsibility**: Command-line user interaction.

**Features**:
- Interactive menu system
- Input validation
- Rich console output with emojis
- History and preferences integration

**Menu Options**:
1. Search + Brief Summary
2. Search + Detailed Summary
3. Save Topic
4. View Saved Topics
5. View History
6. Clear History
0. Exit

**Workflow** (for search):
```
User Query → Fetch Articles → Add to Vector DB
→ Personalized Retrieval → Summarize → Display Results
```

---

### 6. **streamlit_app.py** - Web UI Layer

**Responsibility**: Beautiful, interactive web interface.

**Technology**:
- Framework: Streamlit v1.35+
- Styling: Custom CSS with deep-blue/purple theme
- Components: Tabs, columns, expanders, buttons

**Tabs**:
1. **🔍 Search & Summarize**: Main interface
   - Topic input
   - Brief/Detailed buttons
   - Live summary display with sources
   
2. **⭐ Saved Topics**: Favorites management
   - Select and search
   - Add/remove topics
   
3. **📜 History**: Search analytics
   - Statistics (total searches, unique topics, total results)
   - Recent search table
   - Clear history button
   
4. **⚙️ Settings**: Configuration
   - Language selection
   - Article count slider
   - API status check
   - About section

**UI Theme**:
- Primary color: #0B1020 (deep navy)
- Accent: #7C3AED / #A855F7 (purple gradient)
- Backdrop blur effects
- Soft glow shadows
- Rounded corners (8px standard)

---

## Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
├──────────────────────────────────────────────────────────────┤
│  [Streamlit App] ◄──────────────► [CLI Interface]           │
└┬────────────────────────────────────────────────────────────┘
 │
 │ topic: str
 ▼
┌──────────────────────────────────────────────────────────────┐
│                   DATA ACQUISITION LAYER                     │
├──────────────────────────────────────────────────────────────┤
│  news_retriever.py                                           │
│  ├─ NewsAPI Client (get_everything)                          │
│  ├─ BadURLFilter                                             │
│  └─ Document Normalization → List[Document]                 │
└┬────────────────────────────────────────────────────────────┘
 │ docs: List[Document]
 ▼
┌──────────────────────────────────────────────────────────────┐
│                  VECTOR DATABASE LAYER                       │
├──────────────────────────────────────────────────────────────┤
│  embedding_engine.py                                         │
│  ├─ SentenceTransformers (all-MiniLM-L6-v2)                 │
│  ├─ Chroma Vector Store (./chroma_db/)                      │
│  │  ├─ Add Documents (with embeddings)                       │
│  │  └─ Semantic Search (HNSW indexing)                       │
│  └─ Retrieved Docs → Personalized Query                      │
└┬────────────────────────────────────────────────────────────┘
 │ relevant_docs: List[Document]
 ▼
┌──────────────────────────────────────────────────────────────┐
│                   LLM SUMMARIZATION LAYER                    │
├──────────────────────────────────────────────────────────────┤
│  summarizer.py                                               │
│  ├─ Groq LLM (llama-3.1-8b-instant via LangChain)            │
│  ├─ Brief Path: Single LLM call → 1-2 sentences             │
│  └─ Detailed Path: Map-Reduce → Structured bullets          │
└┬────────────────────────────────────────────────────────────┘
 │ summary: str
 ▼
┌──────────────────────────────────────────────────────────────┐
│                 PERSISTENCE & PREFERENCES LAYER              │
├──────────────────────────────────────────────────────────────┤
│  user_manager.py                                             │
│  ├─ Saved Topics (user_preferences.json)                     │
│  ├─ Search History (timestamped entries)                     │
│  └─ User Settings                                            │
└┬────────────────────────────────────────────────────────────┘
 │
 ▼
┌──────────────────────────────────────────────────────────────┐
│                    OUTPUT & DISPLAY LAYER                    │
├──────────────────────────────────────────────────────────────┤
│  ├─ Summary text + metadata                                  │
│  ├─ Source links                                             │
│  └─ Formatting (emoji icons, colors, etc.)                   │
└──────────────────────────────────────────────────────────────┘
```

---

## Scalability Considerations

### For Production:

1. **Database**: Switch from local Chroma to cloud vector DB
   - Pinecone, Weaviate, or Milvus

2. **Caching**: Add Redis for recent documents
   - Avoid re-fetching same topics

3. **Rate Limiting**: Implement user throttling
   - NewsAPI has ~5000 requests/month (free tier)

4. **Monitor LLM**: Track token usage
   - Groq has rate limits

5. **Async Operations**: Use FastAPI + Celery for long-running tasks
   - Non-blocking UI updates

---

## Testing Strategy

### Unit Tests (by module):

```python
# test_news_retriever.py
def test_fetch_articles()
def test_bad_url_filter()
def test_deduplication()

# test_embedding_engine.py
def test_add_documents()
def test_semantic_search()

# test_summarizer.py
def test_brief_summarization()
def test_detailed_summarization()
def test_char_limits()

# test_user_manager.py
def test_save_load_prefs()
def test_topic_management()
def test_history_tracking()
```

### Integration Tests:

```python
# Full pipeline test
def test_end_to_end_workflow()
    topic → fetch → embed → search → summarize → save
```

---

## Error Handling

### By Layer:

| Layer | Error Type | Handling |
|-------|-----------|----------|
| NewsAPI | Network / API Key | Log + user message |
| Embeddings | Model loading | Fallback, clear cache |
| Chroma | DB corrupted | Re-initialize DB |
| Groq LLM | Rate limit / API | Retry with backoff |
| File I/O | Permission denied | Log + skip |

---

## Performance Metrics

### Typical Response Times:

| Operation | Time | Notes |
|-----------|------|-------|
| Fetch 10 articles | 2-3s | Network dependent |
| Generate embeddings | 1-2s | 384-dim, 10 docs |
| Vector search | 0.1-0.2s | HNSW index |
| Brief summary | 2-3s | LLM generation |
| Detailed summary | 5-10s | Map-reduce |
| **Total** | **10-18s** | Full pipeline |

---

## Future Enhancements

- [ ] Multi-source news aggregation (Guardian, BBC, etc.)
- [ ] Entity extraction (people, places, organizations)
- [ ] Fact-checking integration
- [ ] Multi-language summarization
- [ ] Real-time streaming updates
- [ ] User collaboration features
- [ ] Advanced filtering (date range, source credibility)
- [ ] Export to PDF/Email

---

**End of Architecture Documentation**
