"""
Test script to verify RAG (Retrieval Augmented Generation) is working.
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from agent.rag import initialize_rag
from agent.tools import search_algorithm_concepts


async def test_rag_system():
    """Test the RAG system with various queries."""
    print("=" * 80)
    print("Testing RAG System")
    print("=" * 80)
    
    # Initialize RAG
    print("\n1. Initializing RAG system...")
    print("-" * 80)
    rag = initialize_rag()
    
    if rag is None:
        print("❌ RAG initialization failed")
        return
    
    if rag.vectorstore is None:
        print("❌ Vectorstore not loaded")
        return
    
    print("✅ RAG system initialized successfully")
    print(f"   Vectorstore location: {rag.persist_directory}")
    
    # Test direct vectorstore search
    print("\n2. Testing direct vectorstore search...")
    print("-" * 80)
    test_query = "hash tables"
    print(f"Query: '{test_query}'")
    
    docs = rag.search(test_query, k=2)
    
    if docs:
        print(f"✅ Found {len(docs)} relevant documents")
        print(f"\nFirst result preview (first 300 chars):")
        print("-" * 80)
        print(docs[0].page_content[:300])
        print("...")
    else:
        print("❌ No documents found")
    
    # Test the search_algorithm_concepts tool
    print("\n3. Testing search_algorithm_concepts tool...")
    print("-" * 80)
    
    test_queries = [
        "How do hash tables work?",
        "What is dynamic programming?",
        "Explain binary search trees"
    ]
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        result = await search_algorithm_concepts(query, rag.vectorstore)
        
        if result and not result.startswith("Error"):
            print(f"✅ Got explanation ({len(result)} chars)")
            print(f"\nExplanation preview (first 400 chars):")
            print(result[:400])
            print("...\n")
        else:
            print(f"❌ Failed: {result}")
    
    print("\n" + "=" * 80)
    print("RAG Testing Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_rag_system())

