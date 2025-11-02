# CodeCoach - AI Interview Practice Platform

A RAG-enabled voice agent that helps you practice coding interviews in real-time. Built for the BlueJay take-home interview.

## What It Does

Talk to an AI interview coach while solving LeetCode problems. The agent:
- Guides you without giving away answers
- Analyzes your code when you ask
- Explains algorithms from textbook using RAG
- Knows when to let you struggle vs when to help

---

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- OpenAI API key ($5 credits)
- LiveKit account (free)

### 1. Backend Setup

```bash
cd backend

# Install dependencies
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp env.template .env
# Edit .env and add your API keys:
# - LIVEKIT_URL (from cloud.livekit.io)
# - LIVEKIT_API_KEY
# - LIVEKIT_API_SECRET
# - OPENAI_API_KEY

# Run API server (Terminal 1)
python -m api

# Run voice agent (Terminal 2)
python -m agent
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp env.template .env
# Default: VITE_API_URL=http://localhost:8000

# Run development server
npm run dev
```

Open http://localhost:5173

---

## Architecture

```
Frontend (React)
    ↓ (voice + code updates)
LiveKit Voice Agent
    ↓
┌─────────────────┐
│  analyze_code() │  → Checks your code
│  (Tool Call)    │
└─────────────────┘
    ↓
┌─────────────────┐
│ search_concepts()│  → Retrieves from textbook
│  (RAG Search)   │
└─────────────────┘
    ↓
Vector Database (CLRS Textbook)
```

---

## Tech Stack

**Backend:**
- LiveKit - Voice orchestration
- OpenAI gpt-4o - LLM
- OpenAI Whisper - Speech-to-text
- OpenAI TTS - Text-to-speech
- LangChain - RAG pipeline
- ChromaDB - Vector database
- FastAPI - Token API

**Frontend:**
- React + TypeScript
- Vite
- Tailwind CSS
- shadcn/ui
- Monaco Editor
- LiveKit React SDK

---

## Project Structure

```
BlueJay/
├── backend/
│   ├── agent/
│   │   ├── coach.py          # Main LiveKit agent
│   │   ├── prompts.py        # System prompt ⭐
│   │   ├── tools.py          # Tool functions
│   │   └── rag.py            # RAG system
│   ├── api/
│   │   └── server.py         # Token generation
│   ├── data/
│   │   └── textbook.pdf      # CLRS textbook
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── lib/             # API client & utils
│   │   └── App.tsx          # Main app
│   └── package.json
│
└── README.md
```

---

## How It Works

### 1. Code Analysis Tool

When you ask "Check my code":
- Frontend sends code to agent via LiveKit data channel
- Agent calls `analyze_code()` tool
- Tool sends code to gpt-4o for analysis
- Returns feedback on correctness, bugs, complexity
- Agent speaks the feedback

### 2. RAG Concept Retrieval

When you ask "How do hash tables work?":
- Agent calls `search_algorithm_concepts()` tool
- Searches vector database (CLRS textbook embeddings)
- Retrieves top 3 relevant chunks
- Passes to gpt-4o with context
- Agent explains with citations

### 3. System Prompt

The agent is Alex, a senior engineer at Google with 250+ interviews conducted. Key traits:
- Never gives away answers
- Guides with questions
- Natural speech (uses "hmm", "alright", not corporate jargon)
- Progressive hints (4 levels)
- Knows when to intervene vs stay quiet

---

## RAG Trade-offs

**Chunk Size: 1500 tokens** (vs typical 500-1000)
- Why: Algorithm explanations need full context
- Trade-off: Less precise retrieval, more complete answers

**Chunk Overlap: 300 tokens** (vs typical 100-200)
- Why: Preserve context across boundaries
- Trade-off: More storage, better continuity

**Retrieval: Top 3 chunks**
- Why: Good balance of context vs speed
- Trade-off: Might miss some info, but faster

**Textbook: CLRS** (Introduction to Algorithms)
- Why: Comprehensive, authoritative, 1300 pages
- Alternative: CTCI (more interview-focused, less depth)

---

## Demo Flow

1. Open platform → See Two Sum problem
2. Click "Start Call" → Connect to voice agent
3. Write code (intentionally suboptimal)
4. Say "Can you check my approach?" → Tool call
5. Agent: "I see nested loops, that's O(n²)..."
6. Say "How do hash tables work?" → RAG retrieval
7. Agent explains from textbook with citation
8. Fix code → Agent confirms it's correct

---

## Getting API Keys

### LiveKit (Free)
1. Go to https://cloud.livekit.io
2. Create account
3. Create project
4. Copy: URL, API Key, API Secret

### OpenAI
1. Go to https://platform.openai.com/api-keys
2. Create new secret key
3. Add $5+ credits to account

---

## Troubleshooting

**Backend won't start:**
- Check all env variables are set in `.env`
- Verify OpenAI API key has credits
- Ensure LiveKit credentials are correct

**Frontend can't connect:**
- Verify backend is running on port 8000
- Check `.env` has correct `VITE_API_URL`
- Test: curl http://localhost:8000

**Voice agent not responding:**
- Check both API and agent are running
- Verify microphone permissions in browser
- Check browser console for errors

**RAG not working:**
- Textbook PDF should be at `backend/data/textbook.pdf`
- First run takes 5-10 minutes to create embeddings
- Check agent logs for "RAG system ready"

---

## What Makes This Special

1. **Multi-modal**: Voice + Code analysis + RAG
2. **Natural coaching**: Progressive hints, knows when to help
3. **Real problem**: Interview prep is huge market
4. **Technical depth**: LiveKit, RAG, tool calling, voice pipeline
5. **Clean UX**: Microsoft-inspired design, professional layout

---

## File Checklist

**Backend:**
- [x] LiveKit agent with voice pipeline
- [x] System prompt with coaching personality
- [x] Code analysis tool
- [x] RAG concept search tool
- [x] Token generation API
- [x] CLRS textbook included

**Frontend:**
- [x] React + TypeScript + Vite
- [x] Monaco code editor
- [x] LiveKit voice integration
- [x] Problem display
- [x] Live transcript
- [x] Microsoft-inspired UI

---

Built by Kavish Soningra for BlueJay • Powered by LiveKit + OpenAI
