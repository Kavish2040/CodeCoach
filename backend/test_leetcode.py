"""
Test script to verify LeetCode problem formatting.
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from agent.leetcode_service import LeetCodeService


async def test_problem_formatting():
    """Test fetching and formatting a LeetCode problem."""
    service = LeetCodeService()
    
    print("=" * 80)
    print("Testing LeetCode Problem Fetching and Formatting")
    print("=" * 80)
    
    # Test with "two-sum" problem
    problem_slug = "two-sum"
    print(f"\nFetching problem: {problem_slug}")
    print("-" * 80)
    
    # Get raw problem details
    raw_details = await service.get_problem_details(problem_slug)
    
    if not raw_details:
        print("❌ Failed to fetch problem details")
        return
    
    print(f"✅ Successfully fetched: {raw_details['title']}")
    print(f"   Difficulty: {raw_details['difficulty']}")
    print(f"   Topics: {', '.join([tag['name'] for tag in raw_details['topicTags']])}")
    
    # Show raw HTML content (for debugging)
    print("\n" + "=" * 80)
    print("RAW HTML CONTENT (last 1000 chars to see constraints)")
    print("=" * 80)
    print(raw_details['content'][-1000:])
    
    # Format for display
    formatted = service.format_problem_for_display(raw_details)
    
    print("\n" + "=" * 80)
    print("FORMATTED PROBLEM DESCRIPTION")
    print("=" * 80)
    print(formatted['description'])
    print("\n" + "=" * 80)
    print("CODE TEMPLATE")
    print("=" * 80)
    print(formatted['codeTemplate'])
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_problem_formatting())

