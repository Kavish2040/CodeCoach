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
                "\n" + "="*50,        # Major section dividers
                "\n" + "━"*50,        # Unicode section lines
                "\n" + "-"*50,        # Dash section lines
                "\n" + "*"*50,        # Star section lines (common in PDFs)
                "\n" + "#"*50,        # Hash section lines
                "\nCOMPANY #",         # Company section starts
                "\nEASY QUESTIONS",    # Difficulty section starts
                "\nMEDIUM QUESTIONS",
                "\nHARD QUESTIONS",
                "\n\n\n",             # Triple newlines
                "\n\n",               # Double newlines (paragraphs)
                "\n",                 # Single newlines
                ". ",                 # Sentence endings
                "? ",                 # Question endings
                "! ",                 # Exclamation endings
                " ",                  # Word boundaries
                ""                    # Character level (last resort)
            ]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        import re
        current_company = None
        enhanced_chunks = []
        
        for chunk in chunks:
            content = chunk.page_content
            metadata = chunk.metadata.copy()
            
            # Extract company name from patterns like:
            # "COMPANY #1: Google", "Company 2: Meta", "COMPANY #15: Amazon"
            # \s* = optional spaces, \d+ = digits, [\w\s&]+ = company names with spaces/ampersands
            company_patterns = [
                r'COMPANY\s*#?\s*\d+\s*:\s*([\w\s&]+?)(?:\n|$)',  # "COMPANY #1: Google Inc"
                r'(?:^|\n)(Google|Meta|Amazon|Microsoft|Apple|Netflix|Uber|Airbnb|LinkedIn|Bloomberg|Adobe|Salesforce|Oracle|Tesla|Spotify|Dropbox|Stripe|Palantir|Coinbase|Robinhood|DoorDash|Instacart|Lyft|Pinterest|Snapchat|TikTok|ByteDance|Zoom|Slack|Atlassian|ServiceNow|Snowflake|Databricks|MongoDB|Redis|Elastic|Twilio|Square|PayPal|eBay|Shopify|Etsy|Zillow|Redfin|Expedia|Booking|Tripadvisor)(?:\s|:|\n)',  # Direct company names
            ]
            
            for pattern in company_patterns:
                company_match = re.search(pattern, content, re.IGNORECASE)
                if company_match:
                    current_company = company_match.group(1).strip().lower()
                    # Handle multi-word companies
                    current_company = re.sub(r'\s+', '_', current_company)  # "Goldman Sachs" -> "goldman_sachs"
                    break
            
            # Add company to metadata if we found one
            if current_company:
                metadata['company'] = current_company
            
            # Detect difficulty level from section headers (more flexible patterns)
            # Matches: "EASY QUESTIONS", "Easy Problems", "EASY:", "Easy (10 problems)", etc.
            difficulty_patterns = [
                (r'EASY\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'easy'),
                (r'MEDIUM\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'medium'), 
                (r'HARD\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'hard'),
                (r'BEGINNER\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'easy'),
                (r'INTERMEDIATE\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'medium'),
                (r'ADVANCED\s*(?:QUESTIONS?|PROBLEMS?|:|\()', 'hard'),
            ]
            
            for pattern, difficulty in difficulty_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    metadata['difficulty'] = difficulty
                    break
            
            # Mark overview sections for better filtering
            if "Overview:" in content or "Top Topics" in content:
                metadata['section_type'] = 'overview'
            
            # Extract common algorithm topics for better searchability
            topics = []
            topic_patterns = [
                r'\b(array|arrays)\b', r'\b(string|strings)\b', r'\b(linked.?list)\b',
                r'\b(tree|trees|binary.?tree)\b', r'\b(graph|graphs)\b', r'\b(dynamic.?programming|dp)\b',
                r'\b(hash.?table|hash.?map|dictionary)\b', r'\b(stack|stacks)\b', r'\b(queue|queues)\b',
                r'\b(heap|heaps|priority.?queue)\b', r'\b(sort|sorting)\b', r'\b(search|searching|binary.?search)\b',
                r'\b(recursion|recursive)\b', r'\b(backtrack|backtracking)\b', r'\b(greedy)\b',
                r'\b(two.?pointer|sliding.?window)\b', r'\b(bit.?manipulation)\b', r'\b(math|mathematics)\b'
            ]
            
            for pattern in topic_patterns:
                if re.search(pattern, content, re.IGNORECASE):
                    topic_match = re.search(pattern, content, re.IGNORECASE)
                    topics.append(topic_match.group(0).lower())
            
            if topics:
                metadata['topics'] = list(set(topics))  # Remove duplicates
            
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
                # Verify vectorstore is working by doing a test query
                test_results = self.vectorstore.similarity_search("test", k=1)
                return True
            except Exception as e:
                print(f"Error loading vectorstore: {e}")
                return False
        return False
    
    def setup(self, force_rebuild: bool = False) -> None:
        """Main setup method. Call this to initialize RAG."""
        if not force_rebuild and self.load_existing_vectorstore():
            return
        
        chunks = self.load_and_process_pdf()
        if chunks:
            self.create_vectorstore(chunks)
    
    def search(self, query: str, k: int = 5, company: str = None, difficulty: str = None, topic: str = None) -> list[Document]:
        """Searches the vectorstore for relevant chunks with optional metadata filtering."""
        if self.vectorstore is None:
            return []
        
        try:
            filter_dict = {}
            if company:
                # Handle multi-word companies (e.g., "Goldman Sachs" -> "goldman_sachs")
                company_clean = re.sub(r'\s+', '_', company.lower())
                filter_dict['company'] = company_clean
            if difficulty:
                filter_dict['difficulty'] = difficulty.lower()
            # Note: ChromaDB doesn't support array filtering easily, so topic filtering 
            # would need to be done post-search or with a different approach
            
            results = self.vectorstore.similarity_search(query, k=k, filter=filter_dict) if filter_dict else self.vectorstore.similarity_search(query, k=k)
            
            # Post-filter by topic if specified
            if topic and results:
                topic_lower = topic.lower()
                filtered_results = []
                for doc in results:
                    doc_topics = doc.metadata.get('topics', [])
                    if any(topic_lower in doc_topic for doc_topic in doc_topics):
                        filtered_results.append(doc)
                return filtered_results[:k]  # Maintain k limit
            
            return results
        except Exception as e:
            print(f"Error during vector search: {e}")
            return []


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
        print("⚠ Warning: LeetCode PDF not found. RAG will not be available.")
        return None
    
    try:
        rag = LeetCodeQuestionsRAG(pdf_path=pdf_path)
        rag.setup()
        
        # Verify vectorstore was loaded successfully
        if rag.vectorstore is None:
            print("⚠ Warning: Vectorstore failed to initialize")
            return None
            
        print(f"✓ RAG initialized successfully with PDF: {pdf_path}")
        return rag
    except Exception as e:
        print(f"⚠ Error initializing RAG: {e}")
        return None
