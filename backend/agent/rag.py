import os
from typing import Optional
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document


class LeetCodeQuestionsRAG:
    """Handles loading and querying the LeetCode company questions database."""
    
    def __init__(self, pdf_path: Optional[str] = None, persist_directory: str = "./chroma_db_leetcode"):
        self.pdf_path = pdf_path
        self.persist_directory = persist_directory
        self.vectorstore = None
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
    def load_and_process_pdf(self) -> list[Document]:
        """Loads PDF and converts to chunks."""
        if not self.pdf_path or not os.path.exists(self.pdf_path):
            return []
        
        reader = PdfReader(self.pdf_path)
        
        documents = [
            Document(
                page_content=page.extract_text(),
                metadata={"page": page_num + 1, "source": self.pdf_path}
            )
            for page_num, page in enumerate(reader.pages)
            if page.extract_text().strip()
        ]
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=500,
            length_function=len,
            separators=[
                "\n" + "="*50,
                "\n" + "━"*50,
                "\n" + "-"*50,
                "\n\n\n",
                "\n\n",
                "\n",
                ". ",
                " ",
                ""
            ]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        import re
        current_company = None
        enhanced_chunks = []
        
        for chunk in chunks:
            content = chunk.page_content
            metadata = chunk.metadata.copy()
            
            company_match = re.search(r'COMPANY\s+#\d+:\s+(\w+)', content)
            if company_match:
                current_company = company_match.group(1).lower()
            
            if current_company:
                metadata['company'] = current_company
            
            if re.search(r'EASY\s+QUESTIONS', content, re.IGNORECASE):
                metadata['difficulty'] = 'easy'
            elif re.search(r'MEDIUM\s+QUESTIONS', content, re.IGNORECASE):
                metadata['difficulty'] = 'medium'
            elif re.search(r'HARD\s+QUESTIONS', content, re.IGNORECASE):
                metadata['difficulty'] = 'hard'
            
            if "Overview:" in content or "Top Topics" in content:
                metadata['section_type'] = 'overview'
            
            enhanced_chunks.append(Document(page_content=content, metadata=metadata))
        
        return enhanced_chunks
    
    def create_vectorstore(self, chunks: list[Document]) -> None:
        """Creates embeddings and stores them in ChromaDB."""
        if not chunks:
            return
        
        self.vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=self.persist_directory
        )
    
    def load_existing_vectorstore(self) -> bool:
        """Loads an existing vectorstore if one exists."""
        if os.path.exists(self.persist_directory):
            try:
                self.vectorstore = Chroma(
                    persist_directory=self.persist_directory,
                    embedding_function=self.embeddings
                )
                return True
            except Exception:
                return False
        return False
    
    def setup(self, force_rebuild: bool = False) -> None:
        """Main setup method. Call this to initialize RAG."""
        if not force_rebuild and self.load_existing_vectorstore():
            return
        
        chunks = self.load_and_process_pdf()
        if chunks:
            self.create_vectorstore(chunks)
    
    def search(self, query: str, k: int = 5, company: str = None, difficulty: str = None) -> list[Document]:
        """Searches the vectorstore for relevant chunks with optional metadata filtering."""
        if self.vectorstore is None:
            return []
        
        filter_dict = {}
        if company:
            filter_dict['company'] = company.lower()
        if difficulty:
            filter_dict['difficulty'] = difficulty.lower()
        
        return self.vectorstore.similarity_search(query, k=k, filter=filter_dict) if filter_dict else self.vectorstore.similarity_search(query, k=k)


def initialize_rag(pdf_path: Optional[str] = None) -> Optional[LeetCodeQuestionsRAG]:
    """Helper function to initialize RAG system for LeetCode questions."""
    if pdf_path is None:
        possible_paths = [
            "./data/Leetcode.pdf",
            "../data/Leetcode.pdf",
            "./data/leetcode.pdf",
            "../data/leetcode.pdf",
        ]
        pdf_path = next((path for path in possible_paths if os.path.exists(path)), None)
    
    if pdf_path is None:
        return None
    
    try:
        rag = LeetCodeQuestionsRAG(pdf_path=pdf_path)
        rag.setup()
        return rag
    except Exception:
        return None
