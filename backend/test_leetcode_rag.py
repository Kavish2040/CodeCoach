"""
Test script for the LeetCode Questions RAG system.
Tests various queries about company questions, difficulty levels, and frequency.
"""

import asyncio
from dotenv import load_dotenv
from agent.rag import initialize_rag
from agent.tools import search_algorithm_concepts

# Load environment variables
load_dotenv()


async def test_queries():
    """Test the RAG system with various queries."""
    
    print("🧪 Testing LeetCode Questions RAG System")
    print("=" * 80)
    print()
    
    # Initialize RAG
    print("Initializing RAG system...")
    rag = initialize_rag()
    
    if not rag or not rag.vectorstore:
        print("❌ Failed to initialize RAG")
        return
    
    print("✅ RAG system initialized successfully")
    print()
    print("=" * 80)
    print()
    
    # Test queries
    test_cases = [
        "What are the top easy questions for Meta?",
        "Show me Google's most frequent questions",
        "What hard problems does Amazon ask?",
        "List Bloomberg interview questions",
        "What are common medium difficulty questions across companies?",
        "Top questions for Stripe",
    ]
    
    for i, query in enumerate(test_cases, 1):
        print(f"Test {i}/{len(test_cases)}")
        print(f"Query: {query}")
        print("-" * 80)
        
        try:
            result = await search_algorithm_concepts(query, rag.vectorstore)
            print(result)
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()
        print("=" * 80)
        print()


if __name__ == "__main__":
    asyncio.run(test_queries())

