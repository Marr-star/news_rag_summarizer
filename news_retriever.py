"""
News Retriever Module
Handles NewsAPI calls, normalizes articles, deduplicates by URL.
Returns List[Document] for LangChain processing.
"""

import re
import requests
from typing import List
from urllib.parse import urlparse

from langchain_core.documents import Document


class BadURLFilter:
    """Filters out consent, support, and auth URLs."""
    
    BAD_URL_PATTERNS = [
        r"consent\.yahoo\.com",
        r"google\.com/consent",
        r"accounts\.google\.com",
        r"support\.google\.com",
        r"cookies|consent|privacy-policy",
    ]
    
    @staticmethod
    def is_good_url(url: str) -> bool:
        """Check if URL is valid and not a consent/support page."""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        if not url.lower().startswith(("http://", "https://")):
            return False
        
        try:
            parsed = urlparse(url)
            if not parsed.netloc:
                return False
        except Exception:
            return False
        
        for pattern in BadURLFilter.BAD_URL_PATTERNS:
            if re.search(pattern, url, flags=re.IGNORECASE):
                return False
        
        return True


class NewsRetriever:
    """Fetches news from NewsAPI and converts to LangChain Documents."""
    
    def __init__(self, api_key: str):
        """Initialize NewsAPI client."""
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2/everything"
    
    def fetch_articles(
        self,
        topic: str,
        page_size: int = 10,
        language: str = "en"
    ) -> List[Document]:
        """
        Fetch articles from NewsAPI and return as LangChain Documents.
        
        Args:
            topic: Search query
            page_size: Number of articles to fetch
            language: Language code (e.g., 'en')
        
        Returns:
            List of deduplicated LangChain Documents with metadata
        """
        print(f"\n📰 Fetching news for: '{topic}' (page_size={page_size})")
        
        try:
            # Wrap short terms in quotes for exact matching
            query = f'"{topic}"' if len(topic) <= 3 else topic
            
            params = {
                "q": query,
                "language": language,
                "sortBy": "relevancy",
                "pageSize": page_size * 2,  # Fetch more to filter
                "apiKey": self.api_key
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            print(f"❌ Error fetching articles: {e}")
            return []
        
        articles = data.get("articles", []) or []
        
        docs: List[Document] = []
        seen = set()
        
        for article in articles:
            url = article.get("url")
            
            # Skip duplicates
            if not url or url in seen:
                continue
            
            # Skip bad URLs
            if not BadURLFilter.is_good_url(url):
                continue
            
            # Check relevance - ensure title/description actually mentions the topic
            title = (article.get("title") or "").lower()
            description = (article.get("description") or "").lower()
            content = (article.get("content") or "").lower()
            topic_lower = topic.lower()
            
            # Use regex word boundaries for strict matching
            import re as regex_module
            pattern = r'\b' + regex_module.escape(topic_lower) + r'\b'
            
            # Check if topic appears as a whole word in title or description
            if not (regex_module.search(pattern, title) or regex_module.search(pattern, description)):
                continue
            
            seen.add(url)
            
            # Extract content
            title = article.get("title") or ""
            description = article.get("description") or ""
            content = article.get("content") or ""
            
            page_content = f"Title: {title}\nDescription: {description}\nContent: {content}"
            
            metadata = {
                "url": url,
                "source": (article.get("source") or {}).get("name", "Unknown"),
                "publishedAt": article.get("publishedAt", ""),
                "topic": topic,
                "title": title,
                "author": article.get("author", ""),
                "image": article.get("urlToImage", ""),
            }
            
            docs.append(Document(page_content=page_content, metadata=metadata))
            
            # Stop after getting enough results
            if len(docs) >= page_size:
                break
        
        print(f"✅ Returned {len(docs)} unique, relevant articles")
        return docs
    
    def dedupe_by_url(self, docs: List[Document]) -> List[Document]:
        """Remove duplicate documents by URL."""
        seen = set()
        result = []
        
        for doc in docs:
            url = (doc.metadata or {}).get("url")
            if url and url not in seen:
                seen.add(url)
                result.append(doc)
        
        return result
