"""
RAG (Retrieval-Augmented Generation) module for LeetCode company-specific questions.

This module uses LlamaIndex to:
- Index the leetcode.pdf document containing company-specific LeetCode questions
- Retrieve relevant context when users ask about company interview questions
- Provide accurate answers about which companies ask which problems
"""

import logging
from pathlib import Path
from typing import Optional

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

logger = logging.getLogger(__name__)

# Paths
THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data"
PERSIST_DIR = THIS_DIR / "rag_storage"


class LeetCodeRAG:
    """RAG system for company-specific LeetCode questions."""
    
    def __init__(self):
        """Initialize the RAG system."""
        self.index: Optional[VectorStoreIndex] = None
        self._initialize_settings()
        self._load_or_create_index()
    
    def _initialize_settings(self):
        """Configure LlamaIndex settings."""
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
        Settings.chunk_size = 2048  
        Settings.chunk_overlap = 200 
        
        logger.info("LlamaIndex settings configured")
    
    def _load_or_create_index(self):
        """Load existing index or create a new one from the PDF."""
        try:
            if PERSIST_DIR.exists():
                logger.info(f"Loading existing index from {PERSIST_DIR}")
                storage_context = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))
                self.index = load_index_from_storage(storage_context)
                logger.info("Index loaded successfully")
            else:
                logger.info("Creating new index from documents")
                self._create_index()
        except Exception as e:
            logger.error(f"Error loading index: {e}")
            logger.info("Attempting to create new index")
            self._create_index()
    
    def _create_index(self):
        """Create a new index from the PDF documents."""
        try:
            # Check if data directory exists
            if not DATA_DIR.exists():
                raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")
            
            # Load documents
            logger.info(f"Loading documents from {DATA_DIR}")
            documents = SimpleDirectoryReader(
                input_dir=str(DATA_DIR),
                required_exts=[".pdf"]
            ).load_data()
            
            if not documents:
                raise ValueError(f"No PDF documents found in {DATA_DIR}")
            
            logger.info(f"Loaded {len(documents)} documents")
            
            # Create index
            logger.info("Creating vector index...")
            self.index = VectorStoreIndex.from_documents(
                documents,
                show_progress=True
            )
            
            # Persist index
            PERSIST_DIR.mkdir(parents=True, exist_ok=True)
            self.index.storage_context.persist(persist_dir=str(PERSIST_DIR))
            logger.info(f"Index created and persisted to {PERSIST_DIR}")
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    async def query_company_questions(self, query: str, top_k: int = 5) -> str:
        """
        Query the RAG system for company-specific LeetCode questions.
        
        Args:
            query: User's question about company interview questions
            top_k: Number of relevant chunks to retrieve
        
        Returns:
            str: Answer based on retrieved context
        """
        if not self.index:
            return "RAG system not initialized. Please check the logs."
        
        try:
            # Enhance query to better match company sections
            # Add context keywords to improve retrieval
            enhanced_query = f"COMPANY: {query} interview questions LeetCode problems difficulty topics"
            
            # Create retriever with more results to ensure we get the full company section
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            
            # Retrieve relevant nodes
            nodes = await retriever.aretrieve(enhanced_query)
            
            if not nodes:
                return "I couldn't find relevant information about that company or topic in the LeetCode questions database."
            
            # Format the retrieved context
            context_parts = []
            for i, node in enumerate(nodes, 1):
                content = node.get_content()
                # Clean up the content
                content = content.strip()
                if content:
                    # Add score for debugging (helps understand retrieval quality)
                    score = node.score if hasattr(node, 'score') else 'N/A'
                    logger.info(f"Retrieved chunk {i} with score {score}")
                    context_parts.append(f"[Context {i}]\n{content}")
            
            context = "\n\n".join(context_parts)
            
            return context
            
        except Exception as e:
            logger.error(f"Error querying RAG: {e}")
            return f"Error retrieving information: {str(e)}"
    
    def rebuild_index(self):
        """Force rebuild the index from scratch."""
        logger.info("Rebuilding index from scratch")
        
        # Remove existing index
        if PERSIST_DIR.exists():
            import shutil
            shutil.rmtree(PERSIST_DIR)
            logger.info("Removed existing index")
        
        # Create new index
        self._create_index()
        logger.info("Index rebuilt successfully")


# Global instance
_rag_instance: Optional[LeetCodeRAG] = None


def get_rag_instance() -> LeetCodeRAG:
    """Get or create the global RAG instance."""
    global _rag_instance
    
    if _rag_instance is None:
        logger.info("Initializing RAG system")
        _rag_instance = LeetCodeRAG()
    
    return _rag_instance


async def query_leetcode_rag(query: str) -> str:
    """
    Convenience function to query the RAG system.
    
    Args:
        query: User's question about company interview questions
    
    Returns:
        str: Retrieved context from the LeetCode PDF
    """
    rag = get_rag_instance()
    return await rag.query_company_questions(query)

