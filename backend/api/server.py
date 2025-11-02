import os
import uuid
import json
import traceback
from io import StringIO
import sys as python_sys
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
from livekit import api
from dotenv import load_dotenv
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from agent.leetcode_service import get_leetcode_service


load_dotenv()

app = FastAPI(title="Interview Coach API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TokenRequest(BaseModel):
    """Request body for token generation"""
    room_name: str = None
    participant_name: str = "user"


class TokenResponse(BaseModel):
    """Response with token and room info"""
    token: str
    room_name: str
    url: str


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "Interview Coach API",
        "version": "1.0.0"
    }


@app.post("/token", response_model=TokenResponse)
async def get_token(request: TokenRequest):
    """Generates a LiveKit access token for the frontend."""
    livekit_url = os.getenv("LIVEKIT_URL")
    api_key = os.getenv("LIVEKIT_API_KEY")
    api_secret = os.getenv("LIVEKIT_API_SECRET")
    
    if not all([livekit_url, api_key, api_secret]):
        raise HTTPException(
            status_code=500,
            detail="LiveKit credentials not configured. Check your .env file."
        )
    
    room_name = request.room_name or f"interview-{uuid.uuid4().hex[:8]}"
    
    token = api.AccessToken(api_key, api_secret)
    token.with_identity(request.participant_name)
    token.with_name(request.participant_name)
    token.with_grants(
        api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
            can_publish_data=True,
        )
    )
    
    jwt_token = token.to_jwt()
    
    return TokenResponse(
        token=jwt_token,
        room_name=room_name,
        url=livekit_url
    )


class SearchProblemsRequest(BaseModel):
    """Request body for searching LeetCode problems"""
    tags: Optional[List[str]] = None
    difficulty: Optional[str] = None
    limit: int = 10


@app.post("/leetcode/search")
async def search_leetcode_problems(request: SearchProblemsRequest):
    """Search LeetCode problems by tags and difficulty."""
    leetcode = get_leetcode_service()
    
    try:
        problems = await leetcode.search_problems(
            tags=request.tags,
            difficulty=request.difficulty,
            limit=request.limit
        )
        
        if not problems:
            return {"problems": [], "message": "No problems found matching criteria"}
        
        simplified = [{
            "id": p["titleSlug"],
            "title": p["title"],
            "difficulty": p["difficulty"],
            "topics": [tag["name"] for tag in p.get("topicTags", [])]
        } for p in problems]
        
        return {"problems": simplified}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching problems: {str(e)}")


@app.get("/leetcode/problem/{title_slug}")
async def get_leetcode_problem(title_slug: str):
    """Get detailed problem information including description and code template."""
    leetcode = get_leetcode_service()
    
    try:
        problem_details = await leetcode.get_problem_details(title_slug)
        
        if not problem_details:
            raise HTTPException(status_code=404, detail="Problem not found")
        
        formatted = leetcode.format_problem_for_display(problem_details)
        
        return formatted
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching problem: {str(e)}")


class RunCodeRequest(BaseModel):
    """Request body for running code"""
    code: str
    problem_id: str
    test_cases: str


@app.post("/run-code")
async def run_code(request: RunCodeRequest):
    """Execute user's code against test cases."""
    try:
        test_lines = [line.strip() for line in request.test_cases.strip().split('\n') if line.strip()]
        
        exec_globals = {
            '__builtins__': __builtins__,
            'List': list,
            'Optional': type(None),
            'Dict': dict,
            'Set': set,
        }
        
        exec(request.code, exec_globals)
        
        if 'Solution' not in exec_globals:
            return {
                "success": False,
                "error": "No Solution class found in code"
            }
        
        solution = exec_globals['Solution']()
        
        method_name = next((name for name in dir(solution) 
                           if not name.startswith('_') and callable(getattr(solution, name))), None)
        
        if not method_name:
            return {"success": False, "error": "No solution method found"}
        
        method = getattr(solution, method_name)
        import inspect
        sig = inspect.signature(method)
        param_count = len(sig.parameters)
        
        if len(test_lines) % param_count != 0:
            return {
                "success": False,
                "error": f"Test case count mismatch. Method expects {param_count} parameters, but got {len(test_lines)} values."
            }
        
        test_cases = [test_lines[i:i+param_count] for i in range(0, len(test_lines), param_count)]
        
        results = []
        all_passed = True
        
        for test_num, test_inputs_str in enumerate(test_cases, 1):
            try:
                inputs = [json.loads(input_str) for input_str in test_inputs_str]
                result = method(*inputs)
                input_display = ", ".join(test_inputs_str)
                
                results.append({
                    "test_case": test_num,
                    "input": input_display,
                    "output": str(result),
                    "passed": True,
                    "error": None
                })
                
            except Exception as e:
                all_passed = False
                input_display = ", ".join(test_inputs_str) if test_inputs_str else "N/A"
                results.append({
                    "test_case": test_num,
                    "input": input_display,
                    "output": None,
                    "passed": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "all_passed": all_passed,
            "results": results
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Execution error: {str(e)}",
            "traceback": traceback.format_exc()
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", "8000"))
    print(f"Interview Coach API Server running on http://localhost:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )

