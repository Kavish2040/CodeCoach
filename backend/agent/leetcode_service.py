import os
import json
import logging
from typing import Optional, List, Dict
import httpx
import asyncio

logger = logging.getLogger(__name__)


class LeetCodeService:
    """Service to interact with LeetCode's GraphQL API."""
    
    def __init__(self):
        self.base_url = "https://leetcode.com/graphql"
        self.session_cookie = os.getenv("LEETCODE_SESSION")
        self._last_request_time = 0
        self._min_request_interval = 1.0  # Minimum 1 second between requests 
        
    async def search_problems(
        self,
        tags: Optional[List[str]] = None,
        difficulty: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """Search LeetCode problems by tags and difficulty."""
        
        query = """
        query problemsetQuestionList($categorySlug: String, $limit: Int, $skip: Int, $filters: QuestionListFilterInput) {
          problemsetQuestionList: questionList(
            categorySlug: $categorySlug
            limit: $limit
            skip: $skip
            filters: $filters
          ) {
            total: totalNum
            questions: data {
              questionId
              questionFrontendId
              title
              titleSlug
              difficulty
              topicTags {
                name
                slug
              }
              isPaidOnly
            }
          }
        }
        """
        
        filters = {}
        if tags:
            filters["tags"] = tags
        if difficulty:
            filters["difficulty"] = difficulty
            
        variables = {
            "categorySlug": "",
            "skip": 0,
            "limit": limit,
            "filters": filters
        }
        
        try:
            # Rate limiting: wait if needed
            import time
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_request_interval:
                await asyncio.sleep(self._min_request_interval - time_since_last)
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
                if self.session_cookie:
                    headers["Cookie"] = f"LEETCODE_SESSION={self.session_cookie}"
                
                response = await client.post(
                    self.base_url,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=30.0  # Increased timeout
                )
                
                self._last_request_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        logger.error(f"LeetCode GraphQL errors: {data['errors']}")
                        return []
                    problems = data.get("data", {}).get("problemsetQuestionList", {}).get("questions", [])
                    return [p for p in problems if not p.get("isPaidOnly", False)]
                elif response.status_code == 429:
                    logger.error("LeetCode API rate limit exceeded. Waiting 60 seconds...")
                    await asyncio.sleep(60)
                    return []
                else:
                    logger.error(f"LeetCode API error: {response.status_code} - {response.text[:200]}")
                    return []
                    
        except httpx.TimeoutException:
            logger.error("LeetCode API timeout - request took too long")
            return []
        except Exception as e:
            logger.error(f"Error fetching LeetCode problems: {e}", exc_info=True)
            return []
    
    async def get_problem_details(self, title_slug: str) -> Optional[Dict]:
        """Get detailed information about a specific problem including description and code template."""
        
        query = """
        query questionData($titleSlug: String!) {
          question(titleSlug: $titleSlug) {
            questionId
            questionFrontendId
            title
            titleSlug
            content
            difficulty
            topicTags {
              name
              slug
            }
            codeSnippets {
              lang
              langSlug
              code
            }
            sampleTestCase
            exampleTestcases
          }
        }
        """
        
        variables = {"titleSlug": title_slug}
        
        try:
            # Rate limiting: wait if needed
            import time
            current_time = time.time()
            time_since_last = current_time - self._last_request_time
            if time_since_last < self._min_request_interval:
                await asyncio.sleep(self._min_request_interval - time_since_last)
            
            async with httpx.AsyncClient() as client:
                headers = {
                    "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                }
                if self.session_cookie:
                    headers["Cookie"] = f"LEETCODE_SESSION={self.session_cookie}"
                
                response = await client.post(
                    self.base_url,
                    json={"query": query, "variables": variables},
                    headers=headers,
                    timeout=30.0  # Increased timeout
                )
                
                self._last_request_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    if "errors" in data:
                        logger.error(f"LeetCode GraphQL errors: {data['errors']}")
                        return None
                    question = data.get("data", {}).get("question")
                    
                    if question:
                        return question
                    else:
                        logger.error(f"Problem not found: {title_slug}")
                        return None
                elif response.status_code == 429:
                    logger.error("LeetCode API rate limit exceeded. Waiting 60 seconds...")
                    await asyncio.sleep(60)
                    return None
                else:
                    logger.error(f"LeetCode API error: {response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error fetching problem details: {e}")
            return None
    
    def format_problem_for_display(self, problem_details: Dict) -> Dict:
        """Format problem details for frontend display."""
        python_code = next((s["code"] for s in problem_details.get("codeSnippets", []) 
                           if s["langSlug"] == "python3"), "")
        
        content = problem_details.get("content", "")
        
        if content:
            import re
            from html import unescape
            
            content = re.sub(r'<sup>(\d+)</sup>', r'^\1', content)
            content = re.sub(r'<sup>(.*?)</sup>', r'^(\1)', content)
            content = re.sub(r'<sub>(\d+)</sub>', r'_\1', content)
            content = re.sub(r'<sub>(.*?)</sub>', r'_(\1)', content)
            content = re.sub(r'<font[^>]*>', '', content)
            content = re.sub(r'</font>', '', content)
            content = unescape(content)
            content = re.sub(r'<pre[^>]*>(.*?)</pre>', r'\n```\n\1\n```\n', content, flags=re.DOTALL)
            content = re.sub(r'<code[^>]*>(.*?)</code>', r'`\1`', content, flags=re.DOTALL)
            content = re.sub(r'<strong[^>]*>(.*?)</strong>', r'\1', content, flags=re.DOTALL)
            content = re.sub(r'<b[^>]*>(.*?)</b>', r'\1', content, flags=re.DOTALL)
            content = re.sub(r'<em[^>]*>(.*?)</em>', r'\1', content, flags=re.DOTALL)
            content = re.sub(r'<i[^>]*>(.*?)</i>', r'\1', content, flags=re.DOTALL)
            content = re.sub(r'<p[^>]*>\s*', '\n\n', content)
            content = re.sub(r'\s*</p>', '', content)
            content = re.sub(r'<br\s*/?>', '\n', content)
            content = re.sub(r'<div[^>]*>\s*', '\n', content)
            content = re.sub(r'\s*</div>', '', content)
            content = re.sub(r'<ul[^>]*>', '\n', content)
            content = re.sub(r'</ul>', '\n', content)
            content = re.sub(r'<ol[^>]*>', '\n', content)
            content = re.sub(r'</ol>', '\n', content)
            content = re.sub(r'<li[^>]*>\s*', '\n- ', content)
            content = re.sub(r'\s*</li>', '', content)
            content = re.sub(r'<[^>]+>', '', content)
            content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
            content = re.sub(r'[ \t]+', ' ', content)
            content = re.sub(r' \n', '\n', content)
            content = re.sub(r'\n ', '\n', content)
            content = content.strip()
        
        example_testcases = problem_details.get("exampleTestcases", "")
        
        return {
            "id": problem_details.get("titleSlug"),
            "title": problem_details.get("title"),
            "difficulty": problem_details.get("difficulty"),
            "description": content,
            "codeTemplate": python_code,
            "topics": [tag["name"] for tag in problem_details.get("topicTags", [])],
            "testCases": example_testcases
        }


_leetcode_service = None

def get_leetcode_service() -> LeetCodeService:
    """Get or create the LeetCode service instance."""
    global _leetcode_service
    if _leetcode_service is None:
        _leetcode_service = LeetCodeService()
    return _leetcode_service

