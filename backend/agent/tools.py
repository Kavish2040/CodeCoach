"""
Tools for LeetCode problem search.

This module provides functions to:
- Search LeetCode problems by topic with fuzzy matching
- Get detailed problem information
"""

import json
from pathlib import Path
from difflib import get_close_matches
from typing import Optional, Tuple
from .leetcode_service import get_leetcode_service


_leetcode_tags_cache = None

# Common abbreviations and aliases that users might use
COMMON_TAG_ALIASES = {
    "hashmap": "hash-table",
    "hash map": "hash-table",
    "hash": "hash-table",
    "hashtable": "hash-table",
    "arrays": "array",
    "dp": "dynamic-programming",
    "dfs": "depth-first-search",
    "bfs": "breadth-first-search",
    "linked lists": "linked-list",
    "trees": "tree",
    "graphs": "graph",
    "heap": "heap-priority-queue",
    "priority queue": "heap-priority-queue",
    "pq": "heap-priority-queue",
    "bst": "binary-search-tree",
    "bt": "binary-tree",
    "uf": "union-find",
    "disjoint set": "union-find",
}


def _load_leetcode_tags() -> Optional[dict]:
    """
    Load LeetCode tags from the JSON file.
    
    Returns:
        dict: Tags data with 'slugs', 'names', and 'mapping' keys, or None if loading fails.
    """
    global _leetcode_tags_cache
    
    if _leetcode_tags_cache is not None:
        return _leetcode_tags_cache
    
    try:
        tags_file = Path(__file__).parent / "leetcode_tags.json"
        with open(tags_file, "r") as f:
            _leetcode_tags_cache = json.load(f)
        return _leetcode_tags_cache
    except Exception as e:
        print(f"Warning: Could not load leetcode_tags.json: {e}")
        return None


def _find_best_matching_tag(user_input: str) -> Tuple[str, Optional[str]]:
    """
    Find the best matching LeetCode tag using fuzzy matching.
    
    Matching strategy:
    1. Check common aliases (e.g., 'dp' -> 'dynamic-programming')
    2. Check exact match in tag slugs
    3. Check exact match in tag names (case-insensitive)
    4. Try fuzzy matching on slugs
    5. Try fuzzy matching on names
    6. Return error message with suggestions if no match found
    
    Args:
        user_input: The topic/tag string provided by the user.
    
    Returns:
        tuple: (matched_tag_slug, suggestion_message)
            - If exact match found: (tag_slug, None)
            - If fuzzy match found: (tag_slug, "Using '{matched_name}' (closest match...)")
            - If no match: (user_input, "Topic not found. Available topics include: ...")
    """
    tags_data = _load_leetcode_tags()
    
    if not tags_data:
        return (user_input.lower().strip(), None)
    
    user_input_lower = user_input.lower().strip()
    slugs = tags_data["slugs"]
    names = tags_data["names"]
    name_to_slug = tags_data["mapping"]
    
    # 1. Check common aliases first
    if user_input_lower in COMMON_TAG_ALIASES:
        return (COMMON_TAG_ALIASES[user_input_lower], None)
    
    # 2. Check for exact match in slugs
    if user_input_lower in slugs:
        return (user_input_lower, None)
    
    # 3. Check for exact match in names (case-insensitive)
    for name, slug in name_to_slug.items():
        if name.lower() == user_input_lower:
            return (slug, None)
    
    # 4. Try fuzzy matching on slugs
    slug_matches = get_close_matches(user_input_lower, slugs, n=1, cutoff=0.6)
    if slug_matches:
        matched_slug = slug_matches[0]
        matched_name = next(
            (name for name, slug in name_to_slug.items() if slug == matched_slug),
            matched_slug
        )
        return (matched_slug, f"Using '{matched_name}' (closest match to '{user_input}')")
    
    # 5. Try fuzzy matching on names
    name_matches = get_close_matches(user_input, names, n=1, cutoff=0.6)
    if name_matches:
        matched_name = name_matches[0]
        matched_slug = name_to_slug[matched_name]
        return (matched_slug, f"Using '{matched_name}' (closest match to '{user_input}')")
    
    # 6. No match found - provide suggestions
    sample_topics = ", ".join(slugs[:10]) + "..."
    error_message = f"Topic '{user_input}' not found. Available topics include: {sample_topics}"
    return (user_input_lower, error_message)


async def search_leetcode_problems(topic: str, difficulty: Optional[str] = None) -> str:
    """
    Search LeetCode problems by topic/tag using fuzzy matching.
    
    Args:
        topic: The topic/tag to search for (e.g., "arrays", "dp", "hash-table").
        difficulty: Optional difficulty filter ("easy", "medium", or "hard").
    
    Returns:
        str: JSON string containing search results with problems or error message.
    """
    leetcode = get_leetcode_service()
    
    # Use fuzzy matching to find the best matching tag
    leetcode_tag, suggestion_message = _find_best_matching_tag(topic)
    
    try:
        problems = await leetcode.search_problems(
            tags=[leetcode_tag],
            difficulty=difficulty,
            limit=5
        )
        
        if not problems:
            if suggestion_message and "not found" in suggestion_message:
                return json.dumps({
                    "success": False,
                    "message": suggestion_message
                })
            
            return json.dumps({
                "success": False,
                "message": f"No problems found for topic '{topic}'. Try a different topic or difficulty level."
            })
        
        # Format problems for response
        formatted_problems = [
            {
                "id": p["titleSlug"],
                "title": p["title"],
                "difficulty": p["difficulty"],
                "topics": [tag["name"] for tag in p.get("topicTags", [])]
            }
            for p in problems
        ]
        
        response = {
            "success": True,
            "topic": topic,
            "matched_tag": leetcode_tag,
            "problems": formatted_problems,
            "count": len(formatted_problems)
        }
        
        # Add note if fuzzy matching was used
        if suggestion_message:
            response["note"] = suggestion_message
        
        return json.dumps(response)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error searching problems: {str(e)}"
        })


async def select_leetcode_problem(problem_id: str) -> str:
    """
    Get detailed information about a specific LeetCode problem.
    
    Args:
        problem_id: The problem's title slug (e.g., "two-sum", "reverse-linked-list").
    
    Returns:
        str: JSON string containing problem details or error message.
    """
    leetcode = get_leetcode_service()
    
    try:
        problem_details = await leetcode.get_problem_details(problem_id)
        
        if not problem_details:
            return json.dumps({
                "success": False,
                "message": f"Problem '{problem_id}' not found."
            })
        
        formatted = leetcode.format_problem_for_display(problem_details)
        
        return json.dumps({
            "success": True,
            "problem": formatted
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error fetching problem: {str(e)}"
        })
