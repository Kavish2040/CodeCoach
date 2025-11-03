# RAG Setup for Company-Specific LeetCode Questions

This document explains how the RAG (Retrieval-Augmented Generation) system works for querying company-specific LeetCode interview questions.

## Overview

The RAG system uses **LlamaIndex** to:
- Index the `leetcode.pdf` document containing company interview questions
- Retrieve relevant context when users ask about specific companies
- Provide accurate, source-based answers about interview questions

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Voice Query                         │
│        "What questions does Google ask?"                     │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  InterviewCoach Agent                        │
│         (Detects company-specific question)                  │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│         query_company_leetcode_questions() Tool              │
│              company_name="Google"                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   RAG System (rag.py)                        │
│  1. Embed query using OpenAI                                 │
│  2. Search vector index for similar content                  │
│  3. Retrieve top 3 relevant chunks                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│              Retrieved Context (from PDF)                    │
│  - Company overview                                          │
│  - Top questions with difficulty                             │
│  - Topic tags                                                │
│  - LeetCode links                                            │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   Agent Response                             │
│  "Google frequently asks these questions:                    │
│   1. Two Sum (Easy) - Array, Hash Table                      │
│   2. Validate BST (Medium) - Tree, DFS..."                   │
└─────────────────────────────────────────────────────────────┘
```

## Files

### Core RAG Module
- **`agent/rag.py`** - Main RAG implementation
  - `LeetCodeRAG` class - Manages index and queries
  - `query_leetcode_rag()` - Convenience function for queries
  - Uses OpenAI embeddings and GPT-4o-mini

### Integration
- **`agent/coach.py`** - Agent with RAG tool
  - `query_company_leetcode_questions()` - Tool for company queries
  - Integrated into InterviewCoach agent

### Data
- **`data/leetcode.pdf`** - Source document with company questions
- **`agent/rag_storage/`** - Persisted vector index (auto-generated)

### Scripts
- **`build_rag_index.py`** - Build/rebuild the index
- **`RAG_SETUP.md`** - This documentation

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
source venv/bin/activate
pip install -r requirements.txt
```

This installs:
- `llama-index` - Core framework
- `llama-index-core` - Core components
- `llama-index-embeddings-openai` - OpenAI embeddings
- `llama-index-llms-openai` - OpenAI LLM
- `pypdf` - PDF parsing

### 2. Set Environment Variables

Make sure your `.env` file has:
```bash
OPENAI_API_KEY=sk-...
```

### 3. Build the Index

First time setup:
```bash
python build_rag_index.py
```

To rebuild the index:
```bash
python build_rag_index.py --rebuild
```

To test the index:
```bash
python build_rag_index.py --test
```

### 4. Run the Agent

```bash
python -m agent
```

## Usage Examples

### Voice Queries

Users can ask:
- **"What questions does Google ask?"**
- **"Show me Amazon medium problems"**
- **"What are the top Meta interview questions?"**
- **"What easy problems does Microsoft ask?"**
- **"Tell me about Netflix's hard questions"**

### How It Works

1. **User asks a company-specific question** (voice)
2. **Agent detects company name** and calls `query_company_leetcode_questions()`
3. **RAG system retrieves** relevant chunks from the PDF
4. **Agent synthesizes** the information into a natural response
5. **Agent can then load** a specific problem using `select_leetcode_problem()`

## RAG Configuration

### Embeddings
- Model: `text-embedding-3-small`
- Dimension: 1536
- Provider: OpenAI

### LLM
- Model: `gpt-4o-mini`
- Temperature: 0.1 (for consistent retrieval)

### Chunking
- Chunk size: 512 tokens
- Overlap: 50 tokens
- Optimized for question-answer pairs

### Retrieval
- Top K: 3 chunks per query
- Similarity search using cosine similarity

## Updating the PDF

When you update `data/leetcode.pdf`:

1. **Rebuild the index:**
   ```bash
   python build_rag_index.py --rebuild
   ```

2. **Restart the agent:**
   ```bash
   python -m agent
   ```

## Troubleshooting

### Index Not Found
```bash
# Rebuild the index
python build_rag_index.py --rebuild
```

### PDF Not Loading
- Check that `data/leetcode.pdf` exists
- Verify the PDF is not corrupted
- Check file permissions

### OpenAI API Errors
- Verify `OPENAI_API_KEY` is set
- Check API quota/billing
- Ensure network connectivity

### Poor Retrieval Quality
- Try rebuilding the index
- Adjust chunk size in `rag.py` (currently 512)
- Increase `top_k` in queries (currently 3)

## Performance

### Index Building
- Time: ~30-60 seconds (depends on PDF size)
- Cost: ~$0.01-0.05 (embedding costs)
- Storage: ~5-10 MB

### Query Performance
- Latency: ~200-500ms per query
- Cost: ~$0.001 per query
- Cached: Index loaded once at startup

## Advanced Usage

### Custom Queries in Code

```python
from agent.rag import query_leetcode_rag

# Query the RAG system
result = await query_leetcode_rag("Google array questions")
print(result)
```

### Programmatic Index Rebuild

```python
from agent.rag import get_rag_instance

rag = get_rag_instance()
rag.rebuild_index()
```

### Adjusting Retrieval Parameters

Edit `agent/rag.py`:
```python
# Change number of retrieved chunks
retriever = self.index.as_retriever(similarity_top_k=5)  # Default: 3

# Change chunk size
Settings.chunk_size = 1024  # Default: 512
Settings.chunk_overlap = 100  # Default: 50
```

## Companies Supported

Based on the PDF content:
- Adobe, Airbnb, Amazon, Apple, Atlassian
- Bloomberg, ByteDance, Citadel, Coinbase
- Databricks, DoorDash, Goldman Sachs, Google
- JPMorgan, LinkedIn, Meta (Facebook), Microsoft
- NVIDIA, Netflix, Oracle, PayPal, Salesforce
- Snapchat, Snowflake, Stripe, Tesla, Twilio
- Uber, Walmart
- **LeetCode Top 100** (curated list)

## Future Enhancements

Potential improvements:
1. **Multi-document support** - Add more PDFs (system design, behavioral)
2. **Hybrid search** - Combine vector + keyword search
3. **Metadata filtering** - Filter by difficulty, topic, frequency
4. **Caching** - Cache common queries for faster responses
5. **Analytics** - Track which companies/questions are most queried

## References

- [LlamaIndex Documentation](https://docs.llamaindex.ai/)
- [LiveKit Agents RAG Guide](https://docs.livekit.io/agents/external-data-and-rag/)
- [OpenAI Embeddings](https://platform.openai.com/docs/guides/embeddings)

