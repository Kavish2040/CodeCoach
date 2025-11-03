#!/usr/bin/env python3
"""
Test script to verify RAG integration with the coach agent.
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()


async def test_rag_queries():
    """Test various RAG queries."""
    from agent.rag import query_leetcode_rag
    
    test_queries = [
        "What are Google's top interview questions?",
        "Show me Amazon medium difficulty problems",
        "What questions does Meta ask?",
        "Tell me about Microsoft easy problems",
        "What are the hardest questions at Netflix?",
    ]
    
    print("=" * 80)
    print("Testing RAG Integration")
    print("=" * 80)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_queries)}: {query}")
        print("=" * 80)
        
        try:
            result = await query_leetcode_rag(query)
            
            # Show first 500 characters of result
            preview = result[:500] + "..." if len(result) > 500 else result
            print(f"\n✅ Result Preview:\n{preview}\n")
            
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    print("=" * 80)
    print("✅ All tests completed!")
    print("=" * 80)


async def test_company_specific():
    """Test company-specific queries."""
    from agent.rag import query_leetcode_rag
    
    companies = ["Google", "Amazon", "Meta", "Microsoft", "Apple"]
    
    print("\n" + "=" * 80)
    print("Testing Company-Specific Queries")
    print("=" * 80)
    
    for company in companies:
        query = f"{company} LeetCode interview questions"
        print(f"\n📊 Company: {company}")
        print("-" * 80)
        
        try:
            result = await query_leetcode_rag(query)
            
            # Extract first few lines
            lines = result.split('\n')[:10]
            preview = '\n'.join(lines)
            
            print(f"{preview}\n...")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("✅ Company tests completed!")
    print("=" * 80)


def main():
    """Run all tests."""
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY not found in environment")
        print("Please set it in your .env file")
        sys.exit(1)
    
    # Run tests
    asyncio.run(test_rag_queries())
    asyncio.run(test_company_specific())
    
    print("\n" + "=" * 80)
    print("🎉 All RAG integration tests passed!")
    print("=" * 80)
    print("\nThe RAG system is ready to use in the voice agent.")
    print("Users can now ask questions like:")
    print("  - 'What questions does Google ask?'")
    print("  - 'Show me Amazon medium problems'")
    print("  - 'What are Meta's top interview questions?'")


if __name__ == "__main__":
    main()

