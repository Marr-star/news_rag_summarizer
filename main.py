"""
Main CLI Interface
Runs the News Summarizer in CLI mode.
"""

import os
from dotenv import load_dotenv

from news_retriever import NewsRetriever
from embedding_engine import EmbeddingEngine
from summarizer import Summarizer
from user_manager import UserManager


def main():
    """Run the News Summarizer CLI."""
    
    # Load environment variables
    load_dotenv(override=True)
    
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not NEWS_API_KEY:
        print("❌ NEWS_API_KEY is missing. Add it to .env file: NEWS_API_KEY=<your_key>")
        return
    
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY is missing. Add it to .env file: GROQ_API_KEY=<your_key>")
        return
    
    # Initialize components
    print("\n" + "="*60)
    print("🗞️  NEWS SUMMARIZER CLI".center(60))
    print("="*60)
    
    retriever = NewsRetriever(api_key=NEWS_API_KEY)
    embedding_engine = EmbeddingEngine(
        persist_directory="./chroma_db",
        collection_name="news_articles"
    )
    summarizer = Summarizer(groq_api_key=GROQ_API_KEY)
    user_manager = UserManager(prefs_file="user_preferences.json")
    
    seen_urls = set()
    
    while True:
        print("\n" + "-"*60)
        print("Choose an action:")
        print("  1) 🔍 Search + Brief Summary")
        print("  2) 📊 Search + Detailed Summary")
        print("  3) ⭐ Save a Topic")
        print("  4) 📑 View Saved Topics")
        print("  5) 📜 View Search History")
        print("  6) 🗑️  Clear History")
        print("  0) 🚪 Exit")
        print("-"*60)
        
        choice = input("Choose (0-6): ").strip()
        
        if choice == "0":
            print("\n👋 Goodbye!\n")
            break
        
        elif choice in ("1", "2"):
            topic = input("\n📝 Enter topic: ").strip()
            if not topic:
                print("❌ Topic cannot be empty")
                continue
            
            summary_type = "Brief" if choice == "1" else "Detailed"
            
            # Fetch fresh articles
            fresh_docs = retriever.fetch_articles(topic, page_size=10)
            
            if not fresh_docs:
                print("❌ No articles found. Try another topic.")
                continue
            
            # Add new docs to vector store
            new_docs = []
            for doc in fresh_docs:
                url = (doc.metadata or {}).get("url")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    new_docs.append(doc)
            
            if new_docs:
                embedding_engine.add_documents(new_docs)
            
            # Record in history
            user_manager.add_history_entry(topic, len(fresh_docs))
            
            # Personalized query with saved topics
            saved_topics = user_manager.get_saved_topics()
            if saved_topics:
                query = f"{topic}. Related interests: {', '.join(saved_topics[:3])}"
            else:
                query = topic
            
            # Retrieve and deduplicate
            docs = embedding_engine.search(query, k=12)
            docs = retriever.dedupe_by_url(docs)
            
            # Keep top 5
            docs = docs[:5]
            
            if not docs:
                print("❌ No documents available for summarization.")
                continue
            
            # Summarize
            print(f"\n{'='*60}")
            print(f"📰 {summary_type.upper()} SUMMARY".center(60))
            print(f"{'='*60}\n")
            
            if choice == "1":
                summary = summarizer.summarize_brief(docs)
            else:
                summary = summarizer.summarize_detailed(docs)
            
            print(summary)
            
            # Sources
            print(f"\n{'='*60}")
            print("📚 SOURCES:".ljust(60))
            print(f"{'='*60}")
            for i, doc in enumerate(docs, 1):
                metadata = doc.metadata or {}
                title = metadata.get("title", "N/A")
                url = metadata.get("url", "N/A")
                print(f"{i}. {title}")
                print(f"   🔗 {url}\n")
        
        elif choice == "3":
            topic = input("\n📝 Topic to save: ").strip()
            if topic:
                user_manager.save_topic(topic)
            else:
                print("❌ Topic cannot be empty")
        
        elif choice == "4":
            topics = user_manager.get_saved_topics()
            if topics:
                print("\n⭐ Saved Topics:")
                for i, t in enumerate(topics, 1):
                    print(f"  {i}. {t}")
            else:
                print("\n⚠️  No saved topics yet")
        
        elif choice == "5":
            history = user_manager.get_history(limit=10)
            if history:
                print("\n📜 Recent Searches:")
                for i, entry in enumerate(history, 1):
                    timestamp = entry.get("timestamp", "N/A")
                    topic = entry.get("topic", "N/A")
                    results = entry.get("results", 0)
                    print(f"  {i}. '{topic}' ({results} results) - {timestamp}")
            else:
                print("\n⚠️  No search history yet")
        
        elif choice == "6":
            confirm = input("\n⚠️  Clear all search history? (yes/no): ").strip().lower()
            if confirm == "yes":
                user_manager.clear_history()
            else:
                print("Cancelled")
        
        else:
            print("❌ Invalid choice. Please select 0-6.")


if __name__ == "__main__":
    main()
