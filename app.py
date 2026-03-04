# ============================================================
# News Summarizer CLI (app.py) — Windows/VS Code safe version
# - Uses .env for NEWS_API_KEY and GROQ_API_KEY
# - NewsAPI -> LangChain Documents -> Chroma -> Groq summaries
# ============================================================

import os
import re
import json
import requests
from datetime import datetime
from typing import List
from urllib.parse import urlparse

from pydantic import SecretStr
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_groq import ChatGroq


# -------------------------
# Load environment variables
# -------------------------
load_dotenv(override=True)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not NEWS_API_KEY:
    raise ValueError("NEWS_API_KEY is missing. Add it to .env file.")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing. Add it to .env file.")


# -------------------------
# Initialize Groq LLM
# -------------------------
llm_groq = ChatGroq(
    api_key=SecretStr(GROQ_API_KEY),
    model="llama-3.1-8b-instant",
    temperature=0
)

prompt_brief = """You are a helpful news summarizer.
Summarize the following in 1-2 short sentences.
TEXT:
{text}
"""

prompt_detailed = """You are a helpful news summarizer.
Write a detailed summary in 6-10 bullet points grouped by themes.
TEXT:
{text}
"""


# -------------------------
# NewsAPI client
# -------------------------
NEWS_API_BASE_URL = "https://newsapi.org/v2/everything"


def get_news_articles(topic: str, page_size: int = 10, language: str = "en") -> List[Document]:
    try:
        params = {
            "q": topic,
            "language": language,
            "sortBy": "relevancy",
            "pageSize": page_size,
            "apiKey": NEWS_API_KEY
        }
        response = requests.get(NEWS_API_BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

    articles = data.get("articles", []) or []

    docs: List[Document] = []
    seen = set()

    for a in articles:
        url = a.get("url")
        if not url or url in seen:
            continue
        seen.add(url)

        title = a.get("title") or ""
        description = a.get("description") or ""
        content = a.get("content") or ""

        page_content = f"Title: {title}\nDescription: {description}\nContent: {content}"

        metadata = {
            "url": url,
            "source": (a.get("source") or {}).get("name"),
            "publishedAt": a.get("publishedAt"),
            "topic": topic,
            "title": title,
        }

        docs.append(Document(page_content=page_content, metadata=metadata))

    return docs


# -------------------------
# Vector Store (Chroma)
# -------------------------
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(
    collection_name="news_articles",
    embedding_function=embeddings,
    persist_directory="./chroma_db"
)


# -------------------------
# Preferences (JSON file)
# -------------------------
PREFS_FILE = "user_preferences.json"


def load_prefs():
    if not os.path.exists(PREFS_FILE):
        return {"saved_topics": [], "history": []}

    try:
        with open(PREFS_FILE, "r", encoding="utf-8") as f:
            prefs = json.load(f)
    except Exception:
        return {"saved_topics": [], "history": []}

    prefs.setdefault("saved_topics", [])
    prefs.setdefault("history", [])
    return prefs


def save_prefs(prefs):
    with open(PREFS_FILE, "w", encoding="utf-8") as f:
        json.dump(prefs, f, indent=4)


def save_topic(topic: str):
    prefs = load_prefs()
    if topic not in prefs["saved_topics"]:
        prefs["saved_topics"].append(topic)
        save_prefs(prefs)


def add_history(topic: str, n_results: int):
    prefs = load_prefs()
    prefs["history"].append({
        "topic": topic,
        "results": n_results,
        "timestamp": datetime.now().isoformat()
    })
    save_prefs(prefs)


# -------------------------
# URL filtering
# -------------------------
BAD_URL_PATTERNS = [
    r"consent\.yahoo\.com",
    r"accounts\.google\.com",
    r"support\.google\.com",
]


def is_good_url(url: str) -> bool:
    if not url or not url.startswith(("http://", "https://")):
        return False
    for pat in BAD_URL_PATTERNS:
        if re.search(pat, url, re.IGNORECASE):
            return False
    return True


def dedupe_docs_by_url(docs: List[Document]) -> List[Document]:
    seen = set()
    unique = []
    for d in docs:
        url = (d.metadata or {}).get("url")
        if url and url not in seen:
            seen.add(url)
            unique.append(d)
    return unique


# -------------------------
# Safe summarization limits
# -------------------------
MAX_TOTAL_CHARS = 4000
MAX_DOC_CHARS = 1200


def _docs_to_text_safe(docs: List[Document]) -> str:
    parts = []
    total = 0

    for d in docs:
        txt = (d.page_content or "")[:MAX_DOC_CHARS]
        if total + len(txt) > MAX_TOTAL_CHARS:
            break
        parts.append(txt)
        total += len(txt)

    return "\n\n".join(parts)


def summarize_brief(docs: List[Document]) -> str:
    text = _docs_to_text_safe(docs)
    response = llm_groq.invoke(prompt_brief.format(text=text))
    if hasattr(response, 'content'):
        content = response.content
        return content if isinstance(content, str) else str(content)
    return str(response)


def summarize_detailed(docs: List[Document]) -> str:
    text = _docs_to_text_safe(docs)
    response = llm_groq.invoke(prompt_detailed.format(text=text))
    if hasattr(response, 'content'):
        content = response.content
        return content if isinstance(content, str) else str(content)
    return str(response)


# -------------------------
# CLI
# -------------------------
def run_cli():
    seen_urls = set()

    while True:
        print("\n--- News Summarizer CLI ---")
        print("1) Brief summary")
        print("2) Detailed summary")
        print("3) Save topic")
        print("4) View saved topics")
        print("5) View history")
        print("0) Exit")

        choice = input("Choose: ").strip()

        if choice == "0":
            break

        elif choice in ("1", "2"):
            topic = input("Topic: ").strip()
            docs = get_news_articles(topic, 10)

            new_docs = []
            for d in docs:
                url = (d.metadata or {}).get("url")
                if url and url not in seen_urls and is_good_url(url):
                    seen_urls.add(url)
                    new_docs.append(d)

            if new_docs:
                vectorstore.add_documents(new_docs)

            add_history(topic, len(docs))

            docs = vectorstore.similarity_search(topic, k=5)
            docs = dedupe_docs_by_url(docs)

            if not docs:
                print("No documents found.")
                continue

            if choice == "1":
                summary = summarize_brief(docs)
            else:
                summary = summarize_detailed(docs)

            print("\nSUMMARY:\n", summary)
            print("\nSOURCES:")
            for d in docs:
                print("-", d.metadata.get("title"), "|", d.metadata.get("url"))

        elif choice == "3":
            t = input("Topic to save: ")
            save_topic(t)

        elif choice == "4":
            print(load_prefs()["saved_topics"])

        elif choice == "5":
            print(load_prefs()["history"])

        else:
            print("Invalid choice.")


if __name__ == "__main__":
    run_cli()