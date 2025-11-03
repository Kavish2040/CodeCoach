import os
import logging
from dotenv import load_dotenv
from livekit import agents, rtc
from livekit.agents import JobContext, WorkerOptions, cli, AgentSession, Agent, llm, function_tool, RunContext
from livekit.plugins import silero, openai as lk_openai, cartesia, deepgram

from .prompts import COACH_SYSTEM_PROMPT

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

_room = None
_shared_context = {"current_code": "", "current_problem": "", "cursor_line": None, "cursor_column": None} 


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
        """Get detailed information about a specific problem and load it for the user."""
        from .tools import select_leetcode_problem as select_problem_impl
        
        global _room
        
        result = await select_problem_impl(problem_id)
        
        import json
        try:
            result_data = json.loads(result)
            if result_data.get("success") and _room:
                problem = result_data["problem"]
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
        llm=lk_openai.LLM(model="gpt-4o-mini"),
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
