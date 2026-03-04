"""
Summarizer Module
Implements brief and detailed summarization using Groq LLM via LangChain.
"""

from typing import List
from pydantic import SecretStr
from langchain_core.documents import Document
from langchain_groq import ChatGroq


class Summarizer:
    """Handles news summarization via Groq LLM."""
    
    # Safety caps to prevent token overflow
    MAX_TOTAL_CHARS = 4000
    MAX_DOC_CHARS = 1200
    MAX_MAP_CHARS = 1200
    
    PROMPT_BRIEF = """You are a professional news summarizer.
Summarize the following news articles in 1-2 clear, concise sentences.

TEXT:
{text}

SUMMARY:"""
    
    PROMPT_DETAILED = """You are a professional news summarizer.
Write a detailed summary of the following articles in 6-10 bullet points.
Group related points by theme when possible.

TEXT:
{text}

DETAILED SUMMARY:"""
    
    def __init__(self, groq_api_key: str, model_name: str = "llama-3.1-8b-instant"):
        """
        Initialize Groq LLM for summarization.
        
        Args:
            groq_api_key: Groq API key
            model_name: Model to use (default: llama-3.1-8b-instant)
        """
        print(f"🚀 Initializing Groq LLM: {model_name}")
        
        self.llm = ChatGroq(
            api_key=SecretStr(groq_api_key),
            model=model_name,
            temperature=0
        )
        
        print("✅ Groq LLM initialized")
    
    def _docs_to_text_safe(self, docs: List[Document]) -> str:
        """
        Convert documents to text with character limits.
        
        Args:
            docs: List of documents
        
        Returns:
            Concatenated text respecting character limits
        """
        parts = []
        total = 0
        
        for doc in docs:
            text = (doc.page_content or "").strip()
            if not text:
                continue
            
            # Truncate individual document
            text = text[:self.MAX_DOC_CHARS]
            
            metadata = doc.metadata or {}
            header = (
                f"📰 TITLE: {metadata.get('title', 'N/A')}\n"
                f"📍 SOURCE: {metadata.get('source', 'N/A')}\n"
                f"📅 DATE: {metadata.get('publishedAt', 'N/A')}\n"
            )
            
            block = header + text + "\n\n" + "=" * 50 + "\n\n"
            
            # Check total character limit
            if total + len(block) > self.MAX_TOTAL_CHARS:
                break
            
            parts.append(block)
            total += len(block)
        
        return "".join(parts)
    
    def summarize_brief(self, docs: List[Document]) -> str:
        """
        Generate brief summary (1-2 sentences).
        
        Args:
            docs: List of documents to summarize
        
        Returns:
            Brief summary text
        """
        if not docs:
            return "❌ No documents to summarize."
        
        print(f"⏱️  Generating brief summary from {len(docs)} documents...")
        
        text = self._docs_to_text_safe(docs)
        prompt = self.PROMPT_BRIEF.format(text=text)
        
        response = self.llm.invoke(prompt)
        summary = response.content
        
        print("✅ Brief summary generated")
        return summary
    
    def summarize_detailed(self, docs: List[Document]) -> str:
        """
        Generate detailed summary using map-reduce approach.
        
        Args:
            docs: List of documents to summarize
        
        Returns:
            Detailed summary with bullet points
        """
        if not docs:
            return "❌ No documents to summarize."
        
        print(f"⏱️  Generating detailed summary from {len(docs)} documents...")
        
        # Map phase: summarize each document briefly
        mapped_summaries = []
        for i, doc in enumerate(docs, 1):
            text = (doc.page_content or "").strip()
            if not text:
                continue
            
            text = text[:self.MAX_MAP_CHARS]
            prompt = self.PROMPT_BRIEF.format(text=text)
            response = self.llm.invoke(prompt)
            mapped_summaries.append(response.content)
        
        # Reduce phase: combine summaries into detailed output
        combined = "\n".join(f"• {s}" for s in mapped_summaries)
        combined = combined[:self.MAX_TOTAL_CHARS]
        
        reduction_prompt = self.PROMPT_DETAILED.format(text=combined)
        response = self.llm.invoke(reduction_prompt)
        
        print("✅ Detailed summary generated")
        return response.content
