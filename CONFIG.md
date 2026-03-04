# Configuration & Settings Reference

## Environment Variables

### Required

| Variable | Description | Example | How to Get |
|----------|-------------|---------|-----------|
| `NEWS_API_KEY` | API key for NewsAPI | `abc123xyz...` | https://newsapi.org/ → Get API Key |
| `GROQ_API_KEY` | API key for Groq LLM | `gsk_abc123...` | https://console.groq.com/ → API Keys |

### Optional (Defaults Used If Not Set)

| Variable | Default | Purpose |
|----------|---------|---------|
| `VECTORDB_PATH` | `./chroma_db` | Location for vector database |
| `PREFS_FILE` | `user_preferences.json` | User preferences file location |

### Example `.env` File

```env
# Required API Keys
NEWS_API_KEY=your_newsapi_key_here
GROQ_API_KEY=your_groq_api_key_here

# Optional (uncomment to customize)
# VECTORDB_PATH=./my_chroma_db
# PREFS_FILE=./my_preferences.json
```

---

## Application Configuration

### Vector Database Settings

**File**: Hardcoded in `embedding_engine.py`

```python
# Current defaults
model_name = "all-MiniLM-L6-v2"      # SentenceTransformer model
persist_directory = "./chroma_db"    # Local storage path
collection_name = "news_articles"    # Chroma collection name
```

**To customize:**
1. Edit `embedding_engine.py` constructor
2. Restart application
3. Chroma will create new collection if needed

### LLM Settings

**File**: Hardcoded in `summarizer.py`

```python
# Current defaults
model_name = "llama-3.1-8b-instant"  # Groq model
temperature = 0                       # 0 = deterministic, 1 = creative
```

**Options**:
- `llama-3.1-8b-instant` (current, fast)
- `llama-3.1-70b-versatile` (slower, more capable)
- `mixtral-8x7b-32768` (large model)

**To customize:**
1. Edit `summarizer.py` constructor
2. Restart application

### Character Limits

**File**: Hardcoded in `summarizer.py`

```python
MAX_TOTAL_CHARS = 4000      # Total chars sent to LLM
MAX_DOC_CHARS = 1200        # Per-document limit
MAX_MAP_CHARS = 1200        # Per-document in map phase
```

**Why these limits?**
- Prevent token overflow
- Keep costs reasonable
- Maintain response speed
- Token ≈ 4 characters

**To increase:**
```python
# Edit summarizer.py
MAX_TOTAL_CHARS = 8000      # Increases cost and latency
```

### NewsAPI Settings

**File**: Hardcoded in `news_retriever.py` and user settings

```python
# Default fetch size
page_size = 10              # Articles per search

# API parameters
sort_by = "relevancy"       # or "publishedAt", "popularity"
language = "en"             # Language of articles
```

**To customize per search** (Streamlit):
1. Go to Settings tab
2. Adjust "Number of Articles per Search"
3. Changes saved to `user_preferences.json`

---

## User Preferences File

### Location

```
./user_preferences.json
```

### Structure

```json
{
  "saved_topics": [
    "Artificial Intelligence",
    "Climate Change",
    "Technology"
  ],
  "history": [
    {
      "topic": "AI",
      "results": 10,
      "timestamp": "2024-03-03T14:30:00.123456"
    },
    {
      "topic": "Climate",
      "results": 8,
      "timestamp": "2024-03-03T14:45:00.654321"
    }
  ],
  "settings": {
    "language": "en",
    "page_size": 10
  }
}
```

### Field Descriptions

**saved_topics** (List[str])
- User's favorite topics
- Personalize search results
- Max recommended: 10-15 topics

**history** (List[Dict])
- Each search operation
- Keeps last 50 entries (auto-trimmed)
- Timestamp: ISO 8601 format

**settings** (Dict)
- `language`: Language preference for articles
- `page_size`: Articles to fetch per search

### Editing Manually

You can edit `user_preferences.json` directly:

```bash
# Open in vs code
code user_preferences.json

# Or notepad
notepad user_preferences.json

# Or any text editor
```

**Be careful:** Keep proper JSON formatting!

---

## File Structure Reference

### Application Files

```
news_summarizer/
├── news_retriever.py          (Data acquisition)
├── embedding_engine.py        (Vector DB layer)
├── summarizer.py              (LLM integration)
├── user_manager.py            (Persistence)
├── main.py                    (CLI interface)
├── streamlit_app.py           (Web UI)
├── requirements.txt           (Dependencies)
├── .env                       (Your API keys)
└── .env.example               (Template)
```

### Auto-Generated Files

```
news_summarizer/
├── chroma_db/                 (Vector database)
│   ├── data/
│   ├── index/
│   └── chroma.sqlite3
└── user_preferences.json      (User data)
```

### Documentation Files

```
├── README.md                  (Full documentation)
├── QUICKSTART.md              (5-minute setup)
├── ARCHITECTURE.md            (Technical deep-dive)
└── CONFIG.md                  (This file)
```

---

## Performance Tuning

### Reduce Response Time

| Change | Impact | Trade-off |
|--------|--------|-----------|
| Reduce `page_size` from 10 → 5 | 20% faster fetch | Less relevant results |
| Reduce `k` in search from 5 → 3 | 30% faster search | Fewer sources |
| Use `temperature=0` (default) | Faster, consistent | Less creative |
| Use "Brief" mode | 3-5x faster | Less detail |

### Reduce Cost

| Change | Savings | Trade-off |
|--------|---------|-----------|
| Reduce `MAX_TOTAL_CHARS` | Token usage ↓ | Context loss |
| Use brief summaries only | 3-5x cheaper | Less detail |
| Re-use vector DB results | No re-embedding | Stale data |

### Improve Relevance

| Change | Benefit | Trade-off |
|--------|---------|-----------|
| Save more topics | Better personalization | More noise |
| Increase `k` from 5 → 10 | More context | Slower |
| Use detailed summaries | Better understanding | 3x slower |

---

## API Rate Limits

### NewsAPI (Free Tier)

| Limit | Value | Reset |
|-------|-------|-------|
| Requests/month | 5,000 | 1st of month |
| Requests/second | 1 | Immediate |
| Articles/request | 100 max | Per request |

**Current usage:**
- Per search: 1 request (~10 articles)
- 500 searches/month possible
- Plenty for personal use!

### Groq API (Free Tier)

| Limit | Value | Reset |
|-------|-------|-------|
| Tokens/minute | 5,000 | Rolling minute |
| Requests/minute | Unlimited | N/A |
| Cost | Free (for now) | Monitoring |

**Current usage:**
- Brief summary: ~150 tokens
- Detailed summary: ~500 tokens
- ~10 brief or ~3 detailed per minute

---

## Streamlit Configuration

### Port & Network

```bash
# Default
streamlit run streamlit_app.py
# Runs on: http://localhost:8501

# Custom port
streamlit run streamlit_app.py --server.port 8080

# Access externally (NOT recommended for production)
streamlit run streamlit_app.py --server.address 0.0.0.0
```

### Performance Settings (Streamlit config)

Create `.streamlit/config.toml`:

```toml
[client]
showErrorDetails = true
maxMessageSize = 200

[server]
maxUploadSize = 200
headless = true

[logger]
level = "info"
```

---

## Logging Configuration

### Current Logging

All logging is done via `print()` statements.

**To customize**, you can modify any module:

```python
import logging

# Add logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("Message")
```

### Log File Integration

Create `setup_logging.py`:

```python
import logging
import logging.handlers

def setup_logging():
    handler = logging.handlers.RotatingFileHandler(
        'app.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    
    logging.root.addHandler(handler)
    logging.root.setLevel(logging.INFO)
```

---

## Database Maintenance

### Clear Vector Database

```bash
# Delete vectordb folder
rm -r chroma_db          # Mac/Linux
rmdir /s chroma_db       # Windows

# Restart application - will auto-create fresh DB
python main.py
```

### Clear User Data

```bash
# Delete preferences file
rm user_preferences.json              # Mac/Linux
del user_preferences.json             # Windows

# Restart application - will use defaults
python main.py
```

### Backup Data

```bash
# Backup user preferences before major changes
cp user_preferences.json user_preferences.json.backup

# Backup vector database
cp -r chroma_db chroma_db.backup
```

---

## Troubleshooting Configuration

### Issue: "Very slow searches"

**Check:**
1. `page_size` is not too high (>20)
2. `MAX_TOTAL_CHARS` is not too large
3. NewsAPI is responding normally

**Solution:**
```python
# In main.py or streamlit_app.py
page_size = 5  # Reduce from 10
```

### Issue: "LLM taking forever"

**Check:**
1. Groq API not rate-limited
2. Model not overloaded

**Solution:**
```python
# Switch to smaller model in summarizer.py
model_name = "llama-3.1-8b-instant"  # Already fast, no change needed
```

### Issue: "Embeddings very slow"

**Check:**
1. Chroma database path accessible
2. Sentence transformer model fully downloaded

**Solution:**
```bash
# Force re-download model
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Delete and recreate DB
rm -r chroma_db
python main.py
```

---

## Deployment Configuration

### For Production

Save credentials as secrets (not `.env`):

```python
# main.py
import os
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    project_id = "your-project"
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

NEWS_API_KEY = get_secret("NEWS_API_KEY")
GROQ_API_KEY = get_secret("GROQ_API_KEY")
```

### Docker Deployment

See `Dockerfile` (to be created):

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Set API keys as env vars at runtime
ENV NEWS_API_KEY=${NEWS_API_KEY}
ENV GROQ_API_KEY=${GROQ_API_KEY}

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py"]
```

---

## Reference Versions

As of March 2024:

| Component | Version | Status |
|-----------|---------|--------|
| Python | 3.9+ | Required |
| LangChain | 0.3.5 | Latest |
| Streamlit | 1.35.0 | Latest |
| Chroma | 0.5.2 | Latest |
| SentenceTransformers | 3.0.0 | Latest |

---

**Configuration Reference (v1.0)**  
Last Updated: March 2024
