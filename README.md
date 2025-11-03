# CodeCoach

AI-powered voice agent for coding interview practice. Talk through LeetCode problems with real-time feedback.

## Features

- **Voice Coaching**: Natural conversation with AI interviewer
- **Live Code Analysis**: Get feedback on your approach and complexity
- **Smart Problem Selection**: Search and select LeetCode problems by topic
- **Company-Specific Questions**: RAG-powered search for company interview questions
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

# Build RAG index (first time only)
python build_rag_index.py

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
┌──────────────────────────────────────┐
│ get_current_code()                   │ → Analyzes your code
│ search_leetcode_problems()           │ → Find problems by topic
│ query_company_leetcode_questions()   │ → RAG search for company questions
│ select_leetcode_problem()            │ → Load problem details
└──────────────────────────────────────┘
    ↓                        ↓
LeetCode GraphQL API    LlamaIndex RAG
                        (leetcode.pdf)
```

## Tech Stack

**Backend:**
- LiveKit Agents SDK (voice orchestration)
- OpenAI GPT-4o (LLM), Whisper (STT), TTS
- LlamaIndex (RAG for company questions)
- FastAPI (API server)
- LeetCode GraphQL API integration

**Frontend:**
- React + TypeScript + Vite
- Monaco Editor (code editing)
- Tailwind CSS + shadcn/ui
- LiveKit React SDK

## Project Structure

```
├── backend/
│   ├── agent/
│   │   ├── coach.py           # LiveKit agent
│   │   ├── prompts.py         # System prompt
│   │   ├── tools.py           # Tool functions
│   │   ├── rag.py             # RAG system
│   │   ├── leetcode_service.py # LeetCode API client
│   │   └── rag_storage/       # Vector index (auto-generated)
│   ├── api/
│   │   └── server.py          # FastAPI server
│   ├── data/
│   │   └── leetcode.pdf       # Company questions database
│   ├── build_rag_index.py     # Build RAG index
│   └── RAG_SETUP.md           # RAG documentation
│
└── frontend/
    └── src/
        ├── components/        # React components
        └── lib/              # API client
```

## Company-Specific Questions (RAG)

The agent uses **LlamaIndex RAG** to answer company-specific interview questions from a curated database.

### Supported Companies
Google, Amazon, Meta, Microsoft, Apple, Netflix, Uber, Airbnb, Adobe, Bloomberg, Citadel, Coinbase, DoorDash, Goldman Sachs, LinkedIn, NVIDIA, Oracle, Salesforce, Stripe, Tesla, and more.

### Example Queries
- "What questions does Google ask?"
- "Show me Amazon medium problems"
- "What are Meta's top interview questions?"
- "Tell me about Microsoft easy problems"

### RAG Setup
```bash
# First time setup
python build_rag_index.py

# Rebuild index (if PDF updated)
python build_rag_index.py --rebuild

# Test the system
python build_rag_index.py --test
```

See `backend/RAG_SETUP.md` for detailed documentation.

## API Keys

**LiveKit** (free): https://cloud.livekit.io
**OpenAI**: https://platform.openai.com/api-keys

## License

MIT
