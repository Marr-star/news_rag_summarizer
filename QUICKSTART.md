# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Get Your API Keys (2 minutes)

#### NewsAPI Key
1. Go to https://newsapi.org/
2. Click "Get API Key" (free tier available)
3. Sign up with email
4. Copy your API key

#### Groq API Key
1. Go to https://console.groq.com/
2. Sign up with GitHub or email (free tier: 5,000 tokens/min)
3. Go to "API Keys" section
4. Create new key
5. Copy it

### Step 2: Setup Project (1 minute)

```bash
# 1. Navigate to project
cd news-summarizer

# 2. Create environment file
cp .env.example .env

# 3. Edit .env and add your keys
# On Windows (Notepad):
notepad .env

# Paste this and replace with your keys:
# NEWS_API_KEY=your_newsapi_key_here
# GROQ_API_KEY=your_groq_api_key_here
```

### Step 3: Install Dependencies (1 minute)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

### Step 4: Run! (1 minute)

#### Option A: CLI (Terminal)

```bash
python main.py
```

Menu appears:
```
- Choose 1 or 2
- Type your topic (e.g., "AI", "climate change")
- Wait for summary + sources
- Done!
```

#### Option B: Beautiful Web UI (Recommended)

```bash
streamlit run streamlit_app.py
```

Browser opens → Beautiful interface → Done!

---

## 📖 Your First Search

### In CLI:

```
--- News Summarizer CLI ---
1) 🔍 Search topic + summarize (brief)
2) 📊 Search topic + summarize (detailed)
3) ⭐ Save a topic
4) 📑 View saved topics
5) 📜 View history
6) 🗑️ Clear History
0) 🚪 Exit

Choose (0-6): 1
📝 Enter topic: artificial intelligence
⏳ Fetching news for: 'artificial intelligence' (page_size=10)
✅ Returned 10 unique docs.
🧠 Adding to knowledge base...
✅ Added 10 documents
🔍 Found 5 similar documents
✍️ Generating summary...

============================================================
📰 BRIEF SUMMARY
============================================================

[Your summary appears here - 1-2 sentences]

============================================================
📚 SOURCES:
============================================================
1. Article Title One
   🔗 https://example.com/article1

2. Article Title Two
   🔗 https://example.com/article2
```

### In Streamlit UI:

1. Type topic in input field
2. Click "📄 Brief Summary" or "📊 Detailed Summary"
3. Wait 10-15 seconds
4. Beautiful summary + sources appear
5. Click source titles to expand links

---

## 🎯 Common Tasks

### Search for News

```bash
# CLI: Choose option 1 or 2
# UI: Type topic, click button
```

### Save Your Favorite Topics

```bash
# CLI: Choose option 3
# UI: Type topic, click "⭐ Save Topic"
```

### View What You've Searched

```bash
# CLI: Choose option 5
# UI: Click "📜 History" tab
```

### Use Detailed Summaries

**Better for:** Research, deep dives, understanding multiple perspectives

**Output:** 6-10 bullet points grouped by theme

```bash
# CLI: Choose option 2
# UI: Search topic, click "📊 Detailed Summary"
```

---

## ⚡ Performance Notes

| Action | Time | Notes |
|--------|------|-------|
| Fetch articles | 2-3s | First request always slower |
| Generate brief | 2-3s | LLM is fast |
| Generate detailed | 5-10s | Map-reduce approach |
| **Total** | ~10-18s | Mostly waiting for LLM |

*Times can vary based on:*
- Internet speed
- NewsAPI response time
- Groq API load

---

## 🛠️ Troubleshooting

### "API key missing" error

```bash
# Check .env file exists and has correct format
# Should look like:
# NEWS_API_KEY=abc123...
# GROQ_API_KEY=xyz789...

# Make sure no spaces after =
```

### "No articles found"

```bash
# Try a more general topic:
# ❌ "machine learning classification algorithms"
# ✅ "machine learning"
# ✅ "technology news"
```

### "Vector database error"

```bash
# Delete DB and restart:
rm -r chroma_db
# Windows: delete chroma_db folder manually
# Then re-run:
python main.py
```

### "Streamlit won't start"

```bash
# Kill previous process
# Windows: Task Manager → End streamlit
# Then restart:
streamlit run streamlit_app.py
```

---

## 📚 What's Happening Behind the Scenes

When you search for "AI":

1. **NewsAPI** fetches 10 latest articles about AI
2. **AI Language Model** converts articles to numeric embeddings
3. **Vector Database** stores them for fast searching
4. **Semantic Search** finds 5 most relevant articles
5. **Groq LLM** reads articles and writes smart summary
6. **Your PC** displays summary + original sources

All in ~15 seconds! 🚀

---

## 🎓 Next Steps

Once you're comfortable:

1. **Save Topics**: Build a list of interests you follow
2. **Track History**: See what you've researched over time
3. **Try Detailed Mode**: Better for serious research
4. **Explore Settings**: Adjust language and article count
5. **Read ARCHITECTURE.md**: Understand how it works

---

## 💡 Pro Tips

✅ **Personalized Summaries**: Save topics that interest you → system personalizes results

✅ **Quick Checks**: Use Brief mode for daily news scan (2-3s)

✅ **Deep Dives**: Use Detailed mode for research projects (6-10s)

✅ **Clear Topics List**: Remove old topics to keep focus

✅ **Check History**: See trending topics you've researched

---

## 📞 Need Help?

1. Check **README.md** for full documentation
2. Read **ARCHITECTURE.md** to understand components
3. Review **Troubleshooting** section above
4. Check `.env` has correct API keys

---

## 🎉 You're All Set!

Start by running:

```bash
# For CLI:
python main.py

# For Beautiful Web UI:
streamlit run streamlit_app.py
```

**Happy news summarizing!** 🗞️📰

---

Last Updated: March 2024
