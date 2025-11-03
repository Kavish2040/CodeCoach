import json
from pathlib import Path
from difflib import get_close_matches
from typing import Optional, Tuple
from .leetcode_service import get_leetcode_service

_leetcode_tags_cache = None

# Map common terms to official LeetCode tags
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
    """Load all LeetCode tags from JSON file (cached after first load)"""
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
    """Try to match user input to a LeetCode tag (handles typos and aliases)"""
    tags_data = _load_leetcode_tags()
    
    if not tags_data:
        return (user_input.lower().strip(), None)
    
    user_input_lower = user_input.lower().strip()
    slugs = tags_data["slugs"]
    names = tags_data["names"]
    name_to_slug = tags_data["mapping"]
    
    # Check if user said "dp" or "hashmap" etc
    if user_input_lower in COMMON_TAG_ALIASES:
        return (COMMON_TAG_ALIASES[user_input_lower], None)
    
    # Check exact match
    if user_input_lower in slugs:
        return (user_input_lower, None)
    
    # Check exact match in full names
    for name, slug in name_to_slug.items():
        if name.lower() == user_input_lower:
            return (slug, None)
    
    # Try fuzzy matching (handles typos)
    slug_matches = get_close_matches(user_input_lower, slugs, n=1, cutoff=0.6)
    if slug_matches:
        matched_slug = slug_matches[0]
        matched_name = next(
            (name for name, slug in name_to_slug.items() if slug == matched_slug),
            matched_slug
        )
        return (matched_slug, f"Using '{matched_name}' (closest match to '{user_input}')")
    
    name_matches = get_close_matches(user_input, names, n=1, cutoff=0.6)
    if name_matches:
        matched_name = name_matches[0]
        matched_slug = name_to_slug[matched_name]
        return (matched_slug, f"Using '{matched_name}' (closest match to '{user_input}')")
    
    # Couldn't find anything close
    sample_topics = ", ".join(slugs[:10]) + "..."
    error_message = f"Topic '{user_input}' not found. Available topics include: {sample_topics}"
    return (user_input_lower, error_message)


async def search_leetcode_problems(topic: str, difficulty: Optional[str] = None) -> str:
    """Search for LeetCode problems by topic (e.g., "arrays", "dp", "trees")"""
    leetcode = get_leetcode_service()
    leetcode_tag, suggestion_message = _find_best_matching_tag(topic)
    
    try:
        problems = await leetcode.search_problems(tags=[leetcode_tag], difficulty=difficulty, limit=5)
        
        if not problems:
            if suggestion_message and "not found" in suggestion_message:
                return json.dumps({"success": False, "message": suggestion_message})
            return json.dumps({"success": False, "message": f"No problems found for topic '{topic}'."})
        
        # Clean up the problem data
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
        
        if suggestion_message:
            response["note"] = suggestion_message
        
        return json.dumps(response)
        
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error searching problems: {str(e)}"})


async def select_leetcode_problem(problem_id: str) -> str:
    """Get full details for a specific problem (description, examples, test cases)"""
    leetcode = get_leetcode_service()
    
    try:
        problem_details = await leetcode.get_problem_details(problem_id)
        
        if not problem_details:
            return json.dumps({"success": False, "message": f"Problem '{problem_id}' not found."})
        
        formatted = leetcode.format_problem_for_display(problem_details)
        return json.dumps({"success": True, "problem": formatted})
        
    except Exception as e:
        return json.dumps({"success": False, "message": f"Error fetching problem: {str(e)}"})
