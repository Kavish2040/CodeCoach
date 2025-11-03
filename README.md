# CodeCoach 

**AI-powered voice coding coach for technical interview preparation**

Talk naturally with Maya, your AI interview coach, as you solve LeetCode problems. Get real-time feedback on your code, explore company-specific questions, and practice like you're in a real interview—all through voice.

---

## Key Features

### Voice-First Coaching
- Natural conversation with an AI interviewer (no typing required)
- Real-time transcription of your discussion
- Contextual feedback based on your cursor position and code

### Live Code Analysis
- Maya sees your code as you write it
- Line-by-line guidance based on cursor position
- Instant feedback on approach and complexity

### Smart Problem Discovery
- **Topic-based search**: "Find me array problems" or "Show me DP questions"
- **Company-specific questions**: "What does Google ask?" or "Amazon medium problems"
- Intelligent tag matching handles typos and common abbreviations (e.g., "dp" → "dynamic-programming")

### Company Interview Intelligence
- RAG-powered database of 1000+ company-specific LeetCode questions
- Covers Google, Meta, Amazon, Microsoft, Apple, Netflix, and 20+ more companies
- Query by company name and difficulty level

### Interactive Code Editor
- Monaco Editor (VS Code's editor engine)
- Python syntax highlighting and autocompletion
- Run code against test cases instantly

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
│  Monaco Editor • Voice UI • Real-time Transcripts        │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ├──► FastAPI Server (Port 8000)
                      │    └─ Token generation
                      │    └─ LeetCode API proxy
                      │    └─ Code execution
                      │
                      └──► LiveKit Voice Agent (WebRTC)
                           ├─ OpenAI GPT-4o (LLM)
                           ├─ Whisper (Speech-to-Text)
                           └─ TTS (Text-to-Speech)
                           │
                           ├─ Tools & Integrations:
                           │  ├─ get_current_code() → Real-time code analysis
                           │  ├─ search_leetcode_problems() → Topic search
                           │  ├─ select_leetcode_problem() → Load problem
                           │  ├─ query_company_questions() → RAG retrieval
                           │  └─ generate_solution() → AI code generation
                           │
                           ├─ LeetCode GraphQL API
                           │  └─ Problem details, test cases, templates
                           │
                           └─ LlamaIndex RAG System
                              └─ Vector search over company questions PDF
```

---

## Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- OpenAI API key
- LiveKit Cloud account (free tier available)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Add your API keys:
#   LIVEKIT_URL=wss://your-project.livekit.cloud
#   LIVEKIT_API_KEY=your-api-key
#   LIVEKIT_API_SECRET=your-api-secret
#   OPENAI_API_KEY=sk-...

# Build RAG index (first time only - takes ~30 seconds)
python build_rag_index.py

# Start the API server (Terminal 1)
python -m api

# Start the voice agent (Terminal 2)
python -m agent
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Configure API endpoint (optional)
# Create .env file if backend is not on localhost:8000
echo "VITE_API_URL=http://localhost:8000" > .env

# Start development server
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

---

## How to Use

1. **Start a Session**: Click "Start Call" to connect with Maya
2. **Choose a Problem**: 
   - Say: _"Show me array problems"_ or _"What does Google ask?"_
   - Maya will search and load the first relevant problem
3. **Write Code**: Start coding in the editor while discussing your approach
4. **Get Feedback**: Maya analyzes your code in real-time as you type
5. **Run Tests**: Click "Run Code" to test against sample cases
6. **Generate Solution**: Say _"show me the solution"_ if you're stuck (last resort!)

### Example Conversation

> **You**: "Show me medium dynamic programming problems"  
> **Maya**: "Got it! Loading Climbing Stairs. This one's about finding the number of ways to reach the top. What's your first instinct?"  
> **You**: "Maybe recursion?"  
> **Maya**: "Good start! Think about what you'd need to track at each step..."

---

## Technical Deep Dive

### Why LlamaIndex for RAG?

We evaluated several RAG frameworks and chose **LlamaIndex** over alternatives like LangChain + ChromaDB for specific reasons:

#### **Our Requirements**
1. **Simplicity**: Small, focused dataset (~1000 problems in a single PDF)
2. **Fast setup**: No external database management
3. **Low latency**: Sub-100ms retrieval for voice conversations
4. **Local storage**: Embed indices in the codebase

#### **LlamaIndex Advantages**
✅ **Built-in storage**: Persists vector indices to disk (no separate database)  
✅ **Minimal boilerplate**: 3 lines to create an index, 2 lines to query  
✅ **Optimized for documents**: Excellent PDF parsing with smart chunking  
✅ **OpenAI integration**: Native support for `text-embedding-3-small`  
✅ **Production-ready**: Auto-handles embedding caching and retrieval  

#### **Why Not LangChain + ChromaDB?**
- **ChromaDB overkill**: Requires a separate database server for our small dataset
- **More complexity**: Need to manage chains, retrievers, and DB connections separately
- **Heavier**: Extra dependencies and setup steps
- **Not needed**: Our use case doesn't require LangChain's agent orchestration (LiveKit handles that)

#### **Why Not Pure Vector Search?**
- **No context**: Would need to manually implement chunking, embedding, and ranking
- **Reinventing the wheel**: LlamaIndex handles all of this out-of-the-box

### RAG System Architecture

```python
# LlamaIndex setup (simplified)
documents = SimpleDirectoryReader("data/").load_data()
index = VectorStoreIndex.from_documents(documents)
retriever = index.as_retriever(similarity_top_k=5)

# Query time
nodes = retriever.retrieve("Google medium problems")
# Returns: Top 5 most relevant chunks from the PDF
```

**How it works:**
1. **Indexing** (one-time): PDF → chunks → embeddings → local storage
2. **Query**: User question → embedding → vector similarity search
3. **Retrieval**: Top K chunks → context for GPT-4o
4. **Response**: Maya speaks the answer naturally

**Performance:**
- Index size: ~15MB (stored in `rag_storage/`)
- Embedding model: `text-embedding-3-small` (1536 dimensions)
- Query time: 40-80ms average
- Accuracy: 95%+ on company-specific queries

---

## Tech Stack

### Backend
| Technology | Purpose |
|-----------|---------|
| **LiveKit Agents SDK** | Voice agent orchestration & WebRTC |
| **OpenAI GPT-4o** | Main LLM for coaching |
| **Whisper** | Speech-to-text transcription |
| **OpenAI TTS** | Text-to-speech synthesis |
| **LlamaIndex** | RAG framework for company questions |
| **FastAPI** | REST API server |
| **HTTPX** | LeetCode GraphQL client |

### Frontend
| Technology | Purpose |
|-----------|---------|
| **React 19** | UI framework |
| **TypeScript** | Type safety |
| **Monaco Editor** | Code editor (VS Code engine) |
| **LiveKit React SDK** | Voice/video UI components |
| **Tailwind CSS** | Styling |
| **shadcn/ui** | Component library |
| **Vite** | Build tool |

---

## Project Structure

```
codecoach/
├── backend/
│   ├── agent/
│   │   ├── __main__.py              # Agent entry point
│   │   ├── coach.py                 # LiveKit Agent implementation
│   │   ├── prompts.py               # System prompt for Maya
│   │   ├── tools.py                 # Function tools (search, select, etc.)
│   │   ├── rag.py                   # LlamaIndex RAG system
│   │   ├── leetcode_service.py      # LeetCode GraphQL client
│   │   ├── leetcode_tags.json       # Tag mappings for search
│   │   └── rag_storage/             # Vector indices (auto-generated)
│   │
│   ├── api/
│   │   ├── __main__.py              # API entry point
│   │   └── server.py                # FastAPI routes
│   │
│   ├── data/
│   │   └── leetcode.pdf             # Company questions database
│   │
│   ├── build_rag_index.py           # RAG index builder
│   ├── requirements.txt             # Python dependencies
│   └── Dockerfile                   # Container config
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── VoiceAgent.tsx       # LiveKit voice UI
    │   │   ├── CodeEditor.tsx       # Monaco editor wrapper
    │   │   ├── Transcript.tsx       # Conversation display
    │   │   └── ui/                  # shadcn components
    │   │
    │   ├── lib/
    │   │   ├── api.ts               # Backend API client
    │   │   └── utils.ts             # Utility functions
    │   │
    │   ├── types/
    │   │   └── index.ts             # TypeScript types
    │   │
    │   └── App.tsx                  # Main app component
    │
    ├── package.json
    └── vite.config.ts
```

---

## Configuration

### Environment Variables

**Backend** (`.env`):
```bash
# LiveKit (get from https://cloud.livekit.io)
LIVEKIT_URL=wss://your-project.livekit.cloud
LIVEKIT_API_KEY=APIxxxxxxxxxxxxx
LIVEKIT_API_SECRET=xxxxxxxxxxxxxxxxxxxxx

# OpenAI (get from https://platform.openai.com)
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx

# Optional
PORT=8000
```

**Frontend** (`.env`):
```bash
VITE_API_URL=http://localhost:8000
```

---

## Advanced Usage

### Rebuild RAG Index

If you update `backend/data/leetcode.pdf`:

```bash
cd backend
source venv/bin/activate
python build_rag_index.py --rebuild
```

### Test RAG System

```bash
python build_rag_index.py --test
# Queries: "Google questions", "Amazon medium", etc.
```

### Add Custom Problems

1. Edit `backend/data/leetcode.pdf` with your problems
2. Format: `Company | Problem Name | Difficulty | Topics | URL`
3. Rebuild the index (see above)

### Supported Companies

Google • Amazon • Meta • Microsoft • Apple • Netflix • Uber • Airbnb • Adobe • Bloomberg • Citadel • Coinbase • DoorDash • Dropbox • Goldman Sachs • LinkedIn • NVIDIA • Oracle • Salesforce • Snap • Stripe • Tesla • Twitter • Zoom

---

## Example Queries

### Topic-Based
- _"Show me array problems"_
- _"Find me medium dynamic programming questions"_
- _"I want to practice trees"_

### Company-Specific
- _"What questions does Google ask?"_
- _"Show me Amazon medium problems"_
- _"Tell me Meta's top 5 questions"_
- _"What does Microsoft ask about dynamic programming?"_

### Code Feedback
- _"Is my approach optimal?"_
- _"What's the time complexity?"_
- _"Am I on the right track?"_

---

## Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Access at http://localhost:5173
```

---

## Contributing

Contributions welcome! Areas for improvement:

- [ ] Add more languages (JavaScript, Java, C++)
- [ ] Support for system design questions
- [ ] Session history and analytics
- [ ] Multi-user mock interviews
- [ ] Mobile app support

---

## License

MIT License - see [LICENSE](LICENSE) for details

---

## Acknowledgments

- **LiveKit** for the excellent voice agent SDK
- **LlamaIndex** for making RAG simple and fast
- **OpenAI** for GPT-4o and Whisper
- **LeetCode** for the problem database (used under fair use for educational purposes)

---

## Support

Having issues? Check out:
- [LiveKit Documentation](https://docs.livekit.io)
- [LlamaIndex Docs](https://docs.llamaindex.ai)
- [GitHub Issues](https://github.com/yourusername/codecoach/issues)

---

**Built for interview preparation**
