#!/usr/bin/env python3
"""Test script to verify LeetCode API is working with rate limiting."""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.leetcode_service import LeetCodeService


async def test_leetcode_api():
    """Test LeetCode API with various queries."""
    
    service = LeetCodeService()
    
    print("=" * 60)
    print("Testing LeetCode API")
    print("=" * 60)
    
    # Test 1: Search problems by difficulty
    print("\n1. Searching for easy problems...")
    try:
        problems = await service.search_problems(difficulty="EASY", limit=5)
        if problems:
            print(f"✅ Found {len(problems)} easy problems")
            for p in problems[:3]:
                print(f"   - {p['title']} ({p['difficulty']})")
        else:
            print("❌ No problems found or API error")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Search problems by tags
    print("\n2. Searching for array problems...")
    try:
        problems = await service.search_problems(tags=["array"], limit=5)
        if problems:
            print(f"✅ Found {len(problems)} array problems")
            for p in problems[:3]:
                print(f"   - {p['title']} ({p['difficulty']})")
        else:
            print("❌ No problems found or API error")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Get problem details
    print("\n3. Getting details for 'two-sum'...")
    try:
        details = await service.get_problem_details("two-sum")
        if details:
            print(f"✅ Got problem details")
            print(f"   - Title: {details['title']}")
            print(f"   - Difficulty: {details['difficulty']}")
            print(f"   - Has code snippets: {len(details.get('codeSnippets', [])) > 0}")
        else:
            print("❌ Problem not found or API error")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: Multiple rapid requests (test rate limiting)
    print("\n4. Testing rate limiting (3 rapid requests)...")
    try:
        import time
        start = time.time()
        for i in range(3):
            problems = await service.search_problems(difficulty="MEDIUM", limit=3)
            print(f"   Request {i+1}: {'✅' if problems else '❌'} ({len(problems)} problems)")
        elapsed = time.time() - start
        print(f"   Total time: {elapsed:.2f}s (should be ~2-3s with rate limiting)")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_leetcode_api())

