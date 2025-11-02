# CodeCoach

AI-powered voice agent for coding interview practice. Talk through LeetCode problems with real-time feedback and company-specific question recommendations.

## Features

- **Voice Coaching**: Natural conversation with AI interviewer
- **Live Code Analysis**: Get feedback on your approach and complexity
- **Smart Problem Selection**: RAG-powered recommendations from LeetCode company questions database
- **Real-time Editor**: Write and test code with instant feedback

## Quick Start

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Setup .env with API keys
cp env.template .env
# Add: LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET, OPENAI_API_KEY

# Run (2 terminals)
python -m api      # Terminal 1
python -m agent    # Terminal 2
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## Architecture

```
Frontend (React + TypeScript)
    ↓
LiveKit Voice Agent (OpenAI GPT-4o)
    ↓
┌─────────────────────────────┐
│ get_current_code()          │ → Analyzes your code
│ search_algorithm_concepts() │ → RAG search (LeetCode questions DB)
│ search_leetcode_problems()  │ → Find problems by topic
│ select_leetcode_problem()   │ → Load problem details
└─────────────────────────────┘
    ↓
ChromaDB (Company Questions) + LeetCode GraphQL API
```

## Tech Stack

**Backend:**
- LiveKit Agents SDK (voice orchestration)
- OpenAI GPT-4o (LLM), Whisper (STT), TTS
- LangChain + ChromaDB (RAG pipeline)
- FastAPI (API server)

**Frontend:**
- React + TypeScript + Vite
- Monaco Editor (code editing)
- Tailwind CSS + shadcn/ui
- LiveKit React SDK

## RAG System

The agent uses a vector database of LeetCode company questions:

**Database**: 30+ companies (Google, Meta, Amazon, Microsoft, etc.)
**Chunk Strategy**: 3000 tokens with 500 overlap (preserves full question lists)
**Metadata**: Company name, difficulty level, section type
**Retrieval**: Top 5 chunks with metadata filtering

When you ask "What are top Meta questions?":
1. Extracts company/difficulty from query
2. Searches with metadata filters
3. Returns relevant question lists
4. Agent formats and speaks recommendations

## Project Structure

```
├── backend/
│   ├── agent/
│   │   ├── coach.py           # LiveKit agent
│   │   ├── prompts.py         # System prompt
│   │   ├── tools.py           # Tool functions
│   │   ├── rag.py             # RAG system
│   │   └── leetcode_service.py # LeetCode API client
│   ├── api/
│   │   └── server.py          # FastAPI server
│   └── data/
│       └── Leetcode.pdf       # Company questions database
│
└── frontend/
    └── src/
        ├── components/        # React components
        └── lib/              # API client
```

## API Keys

**LiveKit** (free): https://cloud.livekit.io
**OpenAI**: https://platform.openai.com/api-keys

## License

MIT
