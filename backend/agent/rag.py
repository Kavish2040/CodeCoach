from pathlib import Path
from typing import Optional

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
    Settings,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

THIS_DIR = Path(__file__).parent
DATA_DIR = THIS_DIR.parent / "data"
PERSIST_DIR = THIS_DIR / "rag_storage"


class LeetCodeRAG:
    def __init__(self):
        self.index: Optional[VectorStoreIndex] = None
        self._initialize_settings()
        self._load_or_create_index()
    
    def _initialize_settings(self):
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
        Settings.llm = OpenAI(model="gpt-4o-mini", temperature=0.1)
        Settings.chunk_size = 2048
        Settings.chunk_overlap = 200
    
    def _load_or_create_index(self):
        try:
            if PERSIST_DIR.exists():
                storage_context = StorageContext.from_defaults(persist_dir=str(PERSIST_DIR))
                self.index = load_index_from_storage(storage_context)
            else:
                self._create_index()
        except Exception:
            self._create_index()
    
    def _create_index(self):
        if not DATA_DIR.exists():
            raise FileNotFoundError(f"Data directory not found: {DATA_DIR}")
        
        documents = SimpleDirectoryReader(
            input_dir=str(DATA_DIR),
            required_exts=[".pdf"]
        ).load_data()
        
        if not documents:
            raise ValueError(f"No PDF documents found in {DATA_DIR}")
        
        self.index = VectorStoreIndex.from_documents(documents, show_progress=False)
        
        PERSIST_DIR.mkdir(parents=True, exist_ok=True)
        self.index.storage_context.persist(persist_dir=str(PERSIST_DIR))
    
    async def query_company_questions(self, query: str, top_k: int = 5) -> str:
        if not self.index:
            return "RAG system not initialized."
        
        try:
            enhanced_query = f"COMPANY: {query} interview questions LeetCode problems difficulty topics"
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            nodes = await retriever.aretrieve(enhanced_query)
            
            if not nodes:
                return "I couldn't find relevant information about that company."
            
            context_parts = []
            for i, node in enumerate(nodes, 1):
                content = node.get_content().strip()
                if content:
                    context_parts.append(f"[Context {i}]\n{content}")
            
            return "\n\n".join(context_parts)
            
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
    
    def rebuild_index(self):
        if PERSIST_DIR.exists():
            import shutil
            shutil.rmtree(PERSIST_DIR)
        self._create_index()


_rag_instance: Optional[LeetCodeRAG] = None


def get_rag_instance() -> LeetCodeRAG:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = LeetCodeRAG()
    return _rag_instance


async def query_leetcode_rag(query: str) -> str:
    rag = get_rag_instance()
    return await rag.query_company_questions(query)

