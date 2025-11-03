"""
Test script to verify solution fetching works with fallback.
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agent.leetcode_service import LeetCodeService


async def test_solution_fetch():
    """Test fetching solutions for various problems."""
    service = LeetCodeService()
    
    test_problems = [
        ("two-sum", "Two Sum"),
        ("reverse-linked-list", "Reverse Linked List"),
        ("valid-parentheses", "Valid Parentheses"),
        ("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock"),
        ("longest-substring-without-repeating-characters", "Longest Substring Without Repeating Characters (no fallback)"),
    ]
    
    print("=" * 80)
    print("Testing Solution Fetching with Fallback")
    print("=" * 80)
    
    for problem_slug, problem_name in test_problems:
        print(f"\n{'=' * 80}")
        print(f"Testing: {problem_name}")
        print(f"Slug: {problem_slug}")
        print("-" * 80)
        
        try:
            solution = await service.get_problem_solution(problem_slug)
            
            if solution:
                print("✓ Solution retrieved successfully!")
                print(f"  - ID: {solution.get('id')}")
                print(f"  - Content Type: {solution.get('contentTypeId')}")
                print(f"  - Can See Detail: {solution.get('canSeeDetail')}")
                
                content = solution.get('content', '')
                if content:
                    # Show first 200 characters of content
                    preview = content[:200].replace('\n', ' ')
                    print(f"  - Content Preview: {preview}...")
                else:
                    print("  - Content: (empty)")
                
                # Check if it's a fallback solution
                if solution.get('id', '').startswith('fallback-'):
                    print("  - Source: FALLBACK SOLUTION")
                else:
                    print("  - Source: OFFICIAL LEETCODE API")
            else:
                print("✗ No solution available (neither official nor fallback)")
                
        except Exception as e:
            print(f"✗ Error: {e}")
    
    print("\n" + "=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(test_solution_fetch())

