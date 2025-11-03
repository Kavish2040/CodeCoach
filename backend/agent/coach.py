import os
import logging
import openai
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, Agent, llm, function_tool, RunContext
from livekit.plugins import silero, openai as lk_openai, cartesia, deepgram

from .prompts import COACH_SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_room = None
_shared_context = {"current_code": "", "current_problem": "", "code_template": "", "cursor_line": None, "cursor_column": None} 


class InterviewCoach(Agent):
    """Interview coach agent that helps users practice coding problems."""
    def __init__(self):
        super().__init__(instructions=COACH_SYSTEM_PROMPT)
    
    async def on_enter(self) -> None:
        """Called when the agent becomes active."""
        await self.session.say(
            "Hey! I'm Maya. What do you want to work on today?",
            allow_interruptions=True
        )
    
    @function_tool()
    async def get_current_code_and_problem(self, context: RunContext) -> str:
        """Gets the user's current code, problem description, and cursor position. CALL THIS ON EVERY TURN."""
        global _shared_context
        
        code = _shared_context.get("current_code", "")
        problem = _shared_context.get("current_problem", "")
        cursor_line = _shared_context.get("cursor_line")
        cursor_column = _shared_context.get("cursor_column")
        
        if not problem and not code:
            return "No problem selected and no code written yet."
        
        result_parts = []
        
        if problem:
            result_parts.append(f"[Current Problem]\n{problem}")
        else:
            result_parts.append("[Current Problem]\nNo problem selected yet.")
        
        if code and code.strip():
            # Add line numbers to the code for reference
            code_lines = code.split('\n')
            numbered_code = '\n'.join([f"{i+1:3d} | {line}" for i, line in enumerate(code_lines)])
            result_parts.append(f"[User's Current Code]\n```python\n{numbered_code}\n```")
            
            # Add cursor position information
            if cursor_line is not None:
                cursor_info = f"[Cursor Position]\nLine {cursor_line + 1}"
                if cursor_column is not None:
                    cursor_info += f", Column {cursor_column + 1}"
                
                # Show the specific line where cursor is
                if 0 <= cursor_line < len(code_lines):
                    current_line_content = code_lines[cursor_line]
                    cursor_info += f"\nCurrent line content: `{current_line_content}`"
                    cursor_info += f"\n\n💡 The user is actively working on line {cursor_line + 1}. Focus your feedback on this area if relevant."
                
                result_parts.append(cursor_info)
        else:
            result_parts.append("[User's Current Code]\nNo code written yet.")
        
        return "\n\n".join(result_parts)
    
    
    @function_tool()
    async def search_leetcode_problems(self, context: RunContext, topic: str, difficulty: str = None) -> str:
        """Search for LeetCode problems by topic."""
        from .tools import search_leetcode_problems as search_problems_impl
        
        result = await search_problems_impl(topic, difficulty)
        return result
    
    @function_tool()
    async def select_leetcode_problem(self, context: RunContext, problem_id: str) -> str:
        """
        Get detailed information about a specific problem and load it for the user.
        
        Args:
            problem_id: The problem slug (e.g., "two-sum", "lru-cache") or problem name (e.g., "Two Sum", "LRU Cache").
                       If a name is provided, it will be automatically converted to slug format.
        """
        from .tools import select_leetcode_problem as select_problem_impl
        
        global _room, _shared_context
        
        # Convert problem name to slug if needed (if it contains spaces or capital letters)
        if " " in problem_id or any(c.isupper() for c in problem_id):
            # Convert to slug format: lowercase, spaces to hyphens, remove special chars
            problem_slug = problem_id.lower().strip()
            problem_slug = problem_slug.replace(" ", "-")
            # Remove any characters that aren't alphanumeric or hyphens
            problem_slug = "".join(c for c in problem_slug if c.isalnum() or c == "-")
            # Remove consecutive hyphens
            while "--" in problem_slug:
                problem_slug = problem_slug.replace("--", "-")
            problem_slug = problem_slug.strip("-")
            logger.info(f"Converted problem name '{problem_id}' to slug '{problem_slug}'")
            problem_id = problem_slug
        
        result = await select_problem_impl(problem_id)
        
        import json
        try:
            result_data = json.loads(result)
            if result_data.get("success") and _room:
                problem = result_data["problem"]
                # Store the code template in shared context for solution generation
                _shared_context["code_template"] = problem.get("codeTemplate", "")
                await _room.local_participant.publish_data(
                    json.dumps({"type": "problem_selected", "problem": problem}).encode('utf-8'),
                    reliable=True
                )
        except Exception as e:
            logger.error(f"Error broadcasting problem: {e}")
        
        return result
    
    @function_tool()
    async def query_company_leetcode_questions(self, context: RunContext, company_name: str, difficulty: str = None) -> str:
        """
        Query company-specific LeetCode interview questions from the knowledge base.
        Use this when users ask about what questions specific companies ask in interviews.
        
        Args:
            company_name: Name of the company (e.g., "Google", "Amazon", "Meta", "Microsoft")
            difficulty: Optional difficulty filter ("easy", "medium", "hard")
        
        Returns:
            str: Information about LeetCode questions asked by that company
        """
        from .rag import query_leetcode_rag
        
        # Let the user know we're checking the database
        await self.session.say(
            "Let me check the database for you, give me a moment.",
            allow_interruptions=True
        )
        
        # Build the query
        query_parts = [f"{company_name} LeetCode interview questions"]
        if difficulty:
            query_parts.append(f"{difficulty} difficulty")
        
        query = " ".join(query_parts)
        
        logger.info(f"Querying RAG for: {query}")
        result = await query_leetcode_rag(query)
        
        return result
    
    @function_tool()
    async def generate_solution(self, context: RunContext) -> str:
        """
        Generate an optimal but easy-to-understand solution for the current problem.
        Use this ONLY when the user explicitly asks for the solution or says they give up.
        This should be a last resort after coaching attempts.
        
        Returns:
            str: Status message indicating solution was generated and sent to the editor
        """
        global _shared_context, _room
        
        problem = _shared_context.get("current_problem", "")
        code_template = _shared_context.get("code_template", "")
        
        if not problem:
            return "No problem is currently loaded. Please select a problem first."
        
        # Let the user know we're generating the solution
        await self.session.say(
            "Alright, let me generate a clean solution for you. Give me a moment.",
            allow_interruptions=True
        )
        
        try:
            # Use OpenAI to generate an optimal solution
            import openai
            
            # Build the prompt with function definition if available
            function_context = ""
            if code_template:
                function_context = f"""
Function Definition (YOU MUST USE THIS EXACT SIGNATURE):
```python
{code_template}
```
"""
            
            solution_prompt = f"""You are an expert coding instructor. Generate a clean, optimal, and well-commented Python solution for this LeetCode problem.

Problem:
{problem}
{function_context}
Requirements:
1. Write clean, readable Python code
2. Use an optimal approach (best time/space complexity)
3. Add helpful comments explaining the logic
4. Keep it simple and easy to understand
5. MUST use the exact function signature provided above (if given)
6. Add a brief explanation at the top as a comment
7. Include time and space complexity in comments

Return ONLY the Python code, no markdown formatting or explanations outside the code."""

            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an expert coding instructor who writes clean, optimal solutions. Always follow the exact function signature provided."},
                    {"role": "user", "content": solution_prompt}
                ],
                temperature=0.3,
                max_tokens=1500
            )
            
            solution_code = response.choices[0].message.content.strip()
            
            # Remove markdown code blocks if present
            if solution_code.startswith("```python"):
                solution_code = solution_code.replace("```python", "").replace("```", "").strip()
            elif solution_code.startswith("```"):
                solution_code = solution_code.replace("```", "").strip()
            
            # Send the solution to the frontend
            if _room:
                import json
                await _room.local_participant.publish_data(
                    json.dumps({
                        "type": "solution_generated",
                        "solution": solution_code
                    }).encode('utf-8'),
                    reliable=True
                )
                logger.info("Solution generated and sent to frontend")
            
            return "Solution generated successfully and displayed in the code editor. Take your time to understand the approach and logic."
            
        except Exception as e:
            logger.error(f"Error generating solution: {e}")
            return f"Sorry, I encountered an error generating the solution: {str(e)}"


async def entrypoint(ctx: JobContext):
    """Main entrypoint for the LiveKit agent."""
    global _room, _shared_context
    
    logger.info(f"Starting interview coach agent for room: {ctx.room.name}")
    
    _room = ctx.room
    
    await ctx.connect()
    
    @ctx.room.on("data_received")
    def on_data_received(data_packet: rtc.DataPacket):
        global _shared_context
        try:
            import json
            message = json.loads(data_packet.data.decode('utf-8'))
            if message.get("type") == "code_update":
                _shared_context["current_code"] = message.get("code", "")
                _shared_context["current_problem"] = message.get("problem", "")
                _shared_context["cursor_line"] = message.get("cursor_line")
                _shared_context["cursor_column"] = message.get("cursor_column")
                logger.info(f"Code updated. Cursor at line {_shared_context['cursor_line']}, col {_shared_context['cursor_column']}")
        except Exception as e:
            logger.error(f"Error processing data: {e}")

    session = AgentSession(
        vad=silero.VAD.load(),
        stt=deepgram.STT(model="nova-3"), 
        llm=lk_openai.LLM(model="gpt-4o"),
        tts=cartesia.TTS(
            model="sonic-3", 
            voice="79a125e8-cd45-4c13-8a67-188112f4dd22", 
        ),
    )
    
    await session.start(room=ctx.room, agent=InterviewCoach())
    logger.info("Interview coach ready")


def main():
    """Runs the agent worker."""
    required_vars = ["LIVEKIT_URL", "LIVEKIT_API_KEY", "LIVEKIT_API_SECRET", "OPENAI_API_KEY"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        logger.error(f"Missing required environment variables: {', '.join(missing)}")
        logger.error("Please set these in your .env file")
        return
    
    cli.run_app(WorkerOptions(
        entrypoint_fnc=entrypoint
    ))


if __name__ == "__main__":
    main()
