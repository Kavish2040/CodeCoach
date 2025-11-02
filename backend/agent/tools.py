import os
import json
from openai import AsyncOpenAI
from .leetcode_service import get_leetcode_service


_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def search_algorithm_concepts(query: str, vectorstore=None) -> str:
    """Searches the LeetCode company questions database for specific company questions, difficulty levels, and patterns."""
    if vectorstore is None:
        return await _fallback_question_response(query)
    
    try:
        query_lower = query.lower()
        
        companies = ['google', 'meta', 'amazon', 'microsoft', 'apple', 'netflix', 'uber', 
                    'airbnb', 'linkedin', 'bloomberg', 'adobe', 'salesforce', 'oracle',
                    'stripe', 'coinbase', 'doordash', 'goldman', 'jpmorgan', 'citadel',
                    'bytedance', 'snapchat', 'databricks', 'snowflake', 'atlassian',
                    'twilio', 'paypal', 'walmart', 'tesla', 'nvidia']
        
        detected_company = next((c for c in companies if c in query_lower), None)
        
        detected_difficulty = None
        if 'easy' in query_lower:
            detected_difficulty = 'easy'
        elif 'medium' in query_lower:
            detected_difficulty = 'medium'
        elif 'hard' in query_lower:
            detected_difficulty = 'hard'
        
        if detected_company and detected_difficulty:
            filter_dict = {
                "$and": [
                    {"company": {"$eq": detected_company}},
                    {"difficulty": {"$eq": detected_difficulty}}
                ]
            }
            docs = vectorstore.similarity_search(query, k=5, filter=filter_dict)
        elif detected_company:
            docs = vectorstore.similarity_search(query, k=5, filter={"company": {"$eq": detected_company}})
        elif detected_difficulty:
            docs = vectorstore.similarity_search(query, k=5, filter={"difficulty": {"$eq": detected_difficulty}})
        else:
            docs = vectorstore.similarity_search(query, k=5)
        
        context = "\n\n".join([doc.page_content for doc in docs])
        
        if not context.strip():
            return await _fallback_question_response(query)
        
        explanation_prompt = f"""You are helping someone prepare for coding interviews. You have access to a comprehensive database of LeetCode questions organized by company, difficulty, and frequency.

            User's question: {query}

            Relevant information from the LeetCode company questions database:
            {context}

            Based on the information above, provide a helpful, organized response that:
            1. Lists specific questions if the user is asking about a company or difficulty level
            2. Includes difficulty levels (Easy/Medium/Hard) and frequency ratings when available
            3. Groups questions logically (by difficulty or company)
            4. Mentions which companies frequently ask these questions
            5. Keeps the response concise but informative

            Format your response conversationally. For example:
            - "For Meta, the top Easy questions include..."
            - "Google frequently asks these Medium difficulty questions..."
            - "The most common Hard questions across companies are..."

            Be specific and cite the actual question names from the database.
            """
        
        response = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert interview coach with access to a comprehensive LeetCode questions database."},
                {"role": "user", "content": explanation_prompt}
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error searching questions database: {str(e)}"


async def _fallback_question_response(query: str) -> str:
    """Fallback if RAG isn't set up - provides general guidance."""
    fallback_prompt = f"""The user is asking about LeetCode interview questions: {query}

        Provide general guidance about common interview questions for the company/difficulty/topic they're asking about.
        Be helpful but note that you don't have access to the specific questions database right now.
        """
    
    try:
        response = await _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an interview coach helping with LeetCode preparation."},
                {"role": "user", "content": fallback_prompt}
            ],
            temperature=0.7,
            max_tokens=600,
        )
        return response.choices[0].message.content
    except Exception as e:
        return "I'm having trouble accessing the questions database right now. Try asking about a specific topic or company!"


async def search_leetcode_problems(topic: str, difficulty: str = None) -> str:
    """Search LeetCode problems by topic/tag."""
    leetcode = get_leetcode_service()
    
    topic_mapping = {
        "hashmap": "hash-table",
        "hash map": "hash-table",
        "hash": "hash-table",
        "arrays": "array",
        "linked lists": "linked-list",
        "linked list": "linked-list",
        "trees": "tree",
        "graphs": "graph",
        "dp": "dynamic-programming",
        "dynamic programming": "dynamic-programming",
        "two pointers": "two-pointers",
        "binary search": "binary-search",
        "sliding window": "sliding-window",
        "backtracking": "backtracking",
        "greedy": "greedy",
        "stack": "stack",
        "queue": "queue",
        "heap": "heap",
        "sorting": "sorting",
        "string": "string",
        "math": "math",
        "bit manipulation": "bit-manipulation",
    }
    
    topic_lower = topic.lower().strip()
    leetcode_tag = topic_mapping.get(topic_lower, topic_lower)
    
    try:
        problems = await leetcode.search_problems(
            tags=[leetcode_tag],
            difficulty=difficulty,
            limit=5
        )
        
        if not problems:
            return json.dumps({
                "success": False,
                "message": f"No problems found for topic '{topic}'. Try a different topic."
            })
        
        formatted_problems = [{
            "id": p["titleSlug"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "topics": [tag["name"] for tag in p.get("topicTags", [])]
        } for p in problems]
        
        return json.dumps({
            "success": True,
            "topic": topic,
            "problems": formatted_problems,
            "count": len(formatted_problems)
        })
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"Error searching problems: {str(e)}"
        })


async def select_leetcode_problem(problem_id: str) -> str:
    """Get detailed information about a specific LeetCode problem."""
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
