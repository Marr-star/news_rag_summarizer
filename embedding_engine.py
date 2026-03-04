"""
Embedding Engine Module
Handles embeddings and Chroma vector store initialization/loading.
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from typing import List


class EmbeddingEngine:
    """Manages embeddings and Chroma vector store."""
    
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        persist_directory: str = "./chroma_db",
        collection_name: str = "news_articles"
    ):
        """
        Initialize embedding engine and vector store.
        
        Args:
            model_name: SentenceTransformer model name
            persist_directory: Local directory for Chroma persistence
            collection_name: Chroma collection name
        """
        print(f"🔧 Initializing embeddings with model: {model_name}")
        
        self.model_name = model_name
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        
        # Initialize or load Chroma vector store
        self.vectorstore = Chroma(
            collection_name=collection_name,
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
        
        print(f"✅ Vector store initialized at: {persist_directory}")
    
    def add_documents(self, docs: List[Document]) -> None:
        """
        Add documents to vector store.
        
        Args:
            docs: List of LangChain Documents to add
        """
        if not docs:
            print("⚠️  No documents to add")
            return
        
        self.vectorstore.add_documents(docs)
        print(f"✅ Added {len(docs)} documents to vector store")
    
    def search(self, query: str, k: int = 5) -> List[Document]:
        """
        Semantic similarity search.
        
        Args:
            query: Search query
            k: Number of results to return
        
        Returns:
            List of most similar documents
        """
        results = self.vectorstore.similarity_search(query, k=k)
        print(f"🔍 Found {len(results)} similar documents for query: '{query}'")
        return results
    
    def get_retriever(self):
        """Return a LangChain retriever for the vector store."""
        return self.vectorstore.as_retriever(search_kwargs={"k": 5})
