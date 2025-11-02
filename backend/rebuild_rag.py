"""
Script to rebuild the RAG database with LeetCode company questions.
Run this after updating the Leetcode.pdf file.
"""

import os
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def rebuild_rag():
    """Rebuild the RAG database from scratch."""
    
    print("🚀 Rebuilding LeetCode Questions RAG Database")
    print("=" * 80)
    
    # Import after loading env vars
    from agent.rag import initialize_rag
    
    # Path to the LeetCode PDF
    pdf_path = "./data/Leetcode.pdf"
    persist_dir = "./chroma_db_leetcode"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: {pdf_path} not found!")
        print("   Make sure the Leetcode.pdf file exists in the data/ directory")
        return False
    
    # Remove old database if it exists
    if os.path.exists(persist_dir):
        print(f"🗑️  Removing old database: {persist_dir}")
        shutil.rmtree(persist_dir)
        print("   ✓ Old database removed")
    
    print()
    print(f"📄 Loading PDF: {pdf_path}")
    print("   This may take a few minutes...")
    print()
    
    # Initialize RAG with force rebuild
    try:
        rag = initialize_rag(pdf_path=pdf_path)
        
        if rag and rag.vectorstore:
            print()
            print("=" * 80)
            print("✅ SUCCESS! LeetCode Questions Database is ready")
            print("=" * 80)
            print()
            print("You can now:")
            print("  1. Start the agent: python -m agent")
            print("  2. Ask questions like:")
            print("     - 'What are the top Meta questions?'")
            print("     - 'Show me easy questions for Google'")
            print("     - 'What are the most frequent Amazon problems?'")
            print()
            return True
        else:
            print("❌ Failed to initialize RAG database")
            return False
            
    except Exception as e:
        print(f"❌ Error during rebuild: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = rebuild_rag()
    exit(0 if success else 1)

