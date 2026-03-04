"""
Streamlit UI for News Summarizer
Beautiful deep-blue/purple theme with modern design.
"""

import os
import streamlit as st
from dotenv import load_dotenv

from news_retriever import NewsRetriever
from embedding_engine import EmbeddingEngine
from summarizer import Summarizer
from user_manager import UserManager


# Load environment variables
load_dotenv(override=True)

# Page config
st.set_page_config(
    page_title="🗞️ Deep Blue News Summarizer",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== CUSTOM CSS (Deep Blue + Purple) ====================
st.markdown("""
<style>
    :root {
        --primary-dark: #0B1020;
        --primary-blue: #0F1E2E;
        --accent-purple: #7C3AED;
        --accent-light: #A855F7;
        --card-bg: #1A2A42;
        --text-light: #E0E7FF;
        --text-muted: #A0AEC0;
    }
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0B1020 0%, #0F1E2E 50%, #1a1a3e 100%);
        color: #E0E7FF;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1E2E 0%, #1A2A42 100%);
        border-right: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #E0E7FF !important;
        font-weight: 700;
        letter-spacing: -0.5px;
    }
    
    /* Main title glow */
    h1 {
        background: linear-gradient(90deg, #A855F7, #7C3AED, #A855F7);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        padding: 20px 0;
        font-size: 3em !important;
    }
    
    /* Card containers */
    [data-testid="stVerticalBlock"] > [style*="flex-direction"] {
        background: rgba(26, 42, 66, 0.6);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 12px;
        padding: 20px;
        backdrop-filter: blur(10px);
    }
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        background-color: rgba(15, 30, 46, 0.8) !important;
        border: 1px solid rgba(124, 58, 237, 0.3) !important;
        color: #E0E7FF !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 16px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #7C3AED !important;
        box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #7C3AED, #A855F7) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.3) !important;
    }
    
    .stButton > button:hover {
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.5) !important;
        transform: translateY(-2px) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom: 1px solid rgba(124, 58, 237, 0.2);
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #A0AEC0 !important;
        border-radius: 8px 8px 0 0 !important;
        padding: 12px 20px !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: rgba(124, 58, 237, 0.2) !important;
        border-bottom: 2px solid #A855F7 !important;
        color: #A855F7 !important;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background-color: rgba(124, 58, 237, 0.1) !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
        border-radius: 8px !important;
        color: #A855F7 !important;
    }
    
    .streamlit-expanderContent {
        background-color: rgba(26, 42, 66, 0.4) !important;
    }
    
    /* Metric cards */
    [data-testid="metric-container"] {
        background-color: rgba(124, 58, 237, 0.1);
        border: 1px solid rgba(124, 58, 237, 0.2);
        border-radius: 8px;
        padding: 20px;
    }
    
    /* Code blocks */
    .stCodeBlock {
        background-color: rgba(15, 30, 46, 0.8) !important;
        border: 1px solid rgba(124, 58, 237, 0.2) !important;
    }
    
    /* Divider */
    hr {
        border-color: rgba(124, 58, 237, 0.2) !important;
    }
    
    /* Text */
    body {
        color: #E0E7FF;
    }
    
    /* Success/Info messages */
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.1) !important;
        color: #86EFAC !important;
        border-left: 4px solid #22C55E !important;
    }
    
    .stInfo {
        background-color: rgba(59, 130, 246, 0.1) !important;
        color: #93C5FD !important;
        border-left: 4px solid #3B82F6 !important;
    }
    
    .stWarning {
        background-color: rgba(217, 119, 6, 0.1) !important;
        color: #FCD34D !important;
        border-left: 4px solid #D97706 !important;
    }
    
    .stError {
        background-color: rgba(220, 38, 38, 0.1) !important;
        color: #FCA5A5 !important;
        border-left: 4px solid #DC2626 !important;
    }
</style>
""", unsafe_allow_html=True)

# ==================== SESSION STATE ====================
def initialize_components():
    """Initialize all components."""
    NEWS_API_KEY = os.getenv("NEWS_API_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    
    if not NEWS_API_KEY or not GROQ_API_KEY:
        st.error("❌ Missing API keys. Add NEWS_API_KEY and GROQ_API_KEY to .env file.")
        st.stop()
    
    try:
        st.session_state.retriever = NewsRetriever(api_key=NEWS_API_KEY)
        st.session_state.embedding_engine = EmbeddingEngine(
            persist_directory="./chroma_db",
            collection_name="news_articles"
        )
        st.session_state.summarizer = Summarizer(groq_api_key=GROQ_API_KEY)
        st.session_state.user_manager = UserManager(prefs_file="user_preferences.json")
        st.session_state.components_initialized = True
    except Exception as e:
        st.error(f"❌ Error initializing components: {e}")
        st.stop()


# Initialize session state variables
if "components_initialized" not in st.session_state:
    st.session_state.components_initialized = False

if "retriever" not in st.session_state:
    st.session_state.retriever = None

if "embedding_engine" not in st.session_state:
    st.session_state.embedding_engine = None

if "summarizer" not in st.session_state:
    st.session_state.summarizer = None

if "user_manager" not in st.session_state:
    st.session_state.user_manager = None

if "seen_urls" not in st.session_state:
    st.session_state.seen_urls = set()

# Initialize components on first load
if not st.session_state.components_initialized:
    initialize_components()

# Type assertions to satisfy linter
assert st.session_state.retriever is not None, "Retriever not initialized"
assert st.session_state.embedding_engine is not None, "Embedding engine not initialized"
assert st.session_state.summarizer is not None, "Summarizer not initialized"
assert st.session_state.user_manager is not None, "User manager not initialized"

# ==================== MAIN PAGE ====================
st.markdown("# 🗞️ Deep Blue News Summarizer")

# Create tabs
tab1, tab2, tab3 = st.tabs(
    ["🔍 Search & Summarize", "⭐ Saved Topics", "📜 History"]
)

# ==================== TAB 1: SEARCH & SUMMARIZE ====================
with tab1:
    col1, col2 = st.columns([3, 1])
    
    with col1:
        topic = st.text_input(
            "📝 Enter a news topic",
            placeholder="e.g., artificial intelligence, climate change, technology...",
            key="topic_input"
        )
    
    with col2:
        st.write("")  # Spacing
        save_topic_btn = st.button("⭐ Save Topic", use_container_width=True)
    
    if save_topic_btn and topic:
        try:
            result = st.session_state.user_manager.save_topic(topic)
            if result:
                st.success(f"✅ Topic saved: '{topic}'")
            else:
                st.warning(f"⚠️ Topic already saved: '{topic}'")
        except Exception as e:
            st.error(f"❌ Error saving topic: {e}")
            print(f"Error details: {e}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        brief_btn = st.button("📄 Brief Summary", use_container_width=True)
    
    with col2:
        detailed_btn = st.button("📊 Detailed Summary", use_container_width=True)
    
    with col3:
        clear_btn = st.button("🔄 Clear Results", use_container_width=True)
    
    # Display results
    if brief_btn or detailed_btn:
        if not topic.strip():
            st.error("❌ Please enter a topic")
        else:
            with st.spinner("⏳ Fetching articles..."):
                fresh_docs = st.session_state.retriever.fetch_articles(topic, page_size=10)
            
            if not fresh_docs:
                st.error("❌ No articles found. Try another topic.")
            else:
                # Add to vector store
                with st.spinner("🧠 Adding to knowledge base..."):
                    new_docs = []
                    for doc in fresh_docs:
                        url = (doc.metadata or {}).get("url")
                        if url and url not in st.session_state.seen_urls:
                            st.session_state.seen_urls.add(url)
                            new_docs.append(doc)
                    
                    if new_docs:
                        st.session_state.embedding_engine.add_documents(new_docs)
                
                # Record history
                st.session_state.user_manager.add_history_entry(topic, len(fresh_docs))
                
                # Use fresh, properly filtered documents directly
                # (Skip vector search to avoid semantically similar but irrelevant articles)
                docs = fresh_docs[:5]
                
                if not docs:
                    st.error("❌ No documents available for summarization.")
                else:
                    # Generate summary
                    with st.spinner("✍️ Generating summary..."):
                        if brief_btn:
                            summary = st.session_state.summarizer.summarize_brief(docs)
                        else:
                            summary = st.session_state.summarizer.summarize_detailed(docs)
                    
                    # Display summary
                    st.markdown("---")
                    st.markdown("### 📰 Summary")
                    
                    # Use a nice container
                    summary_container = st.container()
                    with summary_container:
                        st.markdown(f"""
                        <div style="
                            background: rgba(124, 58, 237, 0.1);
                            border-left: 4px solid #7C3AED;
                            padding: 20px;
                            border-radius: 8px;
                            margin: 10px 0;
                        ">
                        {summary}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Sources
                    st.markdown("---")
                    st.markdown("### 📚 Sources")
                    
                    for i, doc in enumerate(docs, 1):
                        metadata = doc.metadata or {}
                        title = metadata.get("title", "N/A")
                        url = metadata.get("url", "N/A")
                        source = metadata.get("source", "N/A")
                        date = metadata.get("publishedAt", "N/A")
                        
                        with st.expander(f"📰 Source {i}: {title[:60]}..."):
                            st.markdown(f"**Title:** {title}")
                            st.markdown(f"**Source:** {source}")
                            st.markdown(f"**Date:** {date}")
                            st.markdown(f"**Link:** [{url}]({url})")
    
    if clear_btn:
        st.rerun()

# ==================== TAB 2: SAVED TOPICS ====================
with tab2:
    st.markdown("### ⭐ Your Saved Topics")
    
    # Refresh button to reload topics
    col_refresh1, col_refresh2 = st.columns([3, 1])
    with col_refresh2:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()
    
    saved_topics = st.session_state.user_manager.get_saved_topics()
    
    # Debug info
    st.caption(f"📊 {len(saved_topics)} topic(s) saved")
    
    if not saved_topics:
        st.info("📌 No saved topics yet. Search and save topics from the main tab!")
    else:
        st.markdown("#### Search a Saved Topic")
        
        topic_to_search = st.selectbox(
            "Select a topic to search",
            saved_topics,
            key="saved_topic_select"
        )
        
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_btn = st.button("🔍 Search This Topic", use_container_width=True)
        
        # Perform search directly (don't modify other tab's widget state)
        if search_btn:
            with st.spinner("⏳ Fetching articles..."):
                fresh_docs = st.session_state.retriever.fetch_articles(topic_to_search, page_size=10)
            
            if not fresh_docs:
                st.error("❌ No articles found. Try another topic.")
            else:
                # Use fresh documents directly
                docs = fresh_docs[:5]
                
                if not docs:
                    st.error("❌ No documents available for summarization.")
                else:
                    # Generate brief summary
                    with st.spinner("✍️ Generating summary..."):
                        summary = st.session_state.summarizer.summarize_brief(docs)
                    
                    # Display summary
                    st.markdown("---")
                    st.markdown("### 📰 Summary")
                    
                    st.markdown(f"""
                    <div style="
                        background: rgba(124, 58, 237, 0.1);
                        border-left: 4px solid #7C3AED;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 10px 0;
                    ">
                    {summary}
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Sources
                    st.markdown("---")
                    st.markdown("### 📚 Sources")
                    
                    for i, doc in enumerate(docs, 1):
                        metadata = doc.metadata or {}
                        title = metadata.get("title", "N/A")
                        url = metadata.get("url", "N/A")
                        source = metadata.get("source", "N/A")
                        date = metadata.get("publishedAt", "N/A")
                        
                        with st.expander(f"📰 Source {i}: {title[:60]}..."):
                            st.markdown(f"**Title:** {title}")
                            st.markdown(f"**Source:** {source}")
                            st.markdown(f"**Date:** {date}")
                            st.markdown(f"**Link:** [{url}]({url})")
        
        st.markdown("---")
        st.markdown("#### Manage Topics")
        
        for topic in saved_topics:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"📌 {topic}")
            with col2:
                if st.button("🗑️", key=f"del_{topic}"):
                    st.session_state.user_manager.remove_topic(topic)
                    st.success(f"✅ Removed: {topic}")
                    st.rerun()

# ==================== TAB 3: HISTORY ====================
with tab3:
    st.markdown("### 📜 Search History")
    
    history = st.session_state.user_manager.get_history(limit=20)
    
    if not history:
        st.info("📋 No search history yet. Return to the main tab and start searching!")
    else:
        # Stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Searches", len(history))
        with col2:
            unique_topics = len(set(h["topic"] for h in history))
            st.metric("Unique Topics", unique_topics)
        with col3:
            total_results = sum(h.get("results", 0) for h in history)
            st.metric("Total Results", total_results)
        
        st.markdown("---")
        
        # History table
        st.markdown("#### Recent Searches")
        for i, entry in enumerate(history, 1):
            topic = entry.get("topic", "N/A")
            results = entry.get("results", 0)
            timestamp = entry.get("timestamp", "N/A")
            
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{i}. {topic}**")
            with col2:
                st.write(f"{results} results")
            with col3:
                st.caption(timestamp)
        
        if st.button("🗑️ Clear All History", use_container_width=True):
            st.session_state.user_manager.clear_history()
            st.success("✅ History cleared")
            st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #A0AEC0; padding: 20px;">
    <small>🚀 Built with LangChain | Powered by Groq | Data from NewsAPI</small><br>
    <small>© 2024 Deep Blue News Summarizer</small>
</div>
""", unsafe_allow_html=True)
