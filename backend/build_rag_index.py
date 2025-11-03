#!/usr/bin/env python3
"""
Script to build or rebuild the RAG index for LeetCode company questions.

This script:
1. Loads the leetcode.pdf from the data/ directory
2. Creates embeddings using OpenAI
3. Stores the index in agent/rag_storage/

Run this script:
- After first setup
- When you update the leetcode.pdf
- If the index becomes corrupted
"""

import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Build the RAG index."""
    # Check for required environment variables
    if not os.getenv("OPENAI_API_KEY"):
        logger.error("OPENAI_API_KEY not found in environment")
        logger.error("Please set it in your .env file")
        sys.exit(1)
    
    # Check if data directory exists
    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Check if PDF exists
    pdf_file = data_dir / "leetcode.pdf"
    if not pdf_file.exists():
        logger.error(f"leetcode.pdf not found in {data_dir}")
        sys.exit(1)
    
    logger.info("=" * 80)
    logger.info("Building RAG Index for LeetCode Company Questions")
    logger.info("=" * 80)
    logger.info(f"Data directory: {data_dir}")
    logger.info(f"PDF file: {pdf_file}")
    
    try:
        # Import RAG module
        from agent.rag import get_rag_instance
        
        # Get RAG instance (this will create the index if it doesn't exist)
        logger.info("\nInitializing RAG system...")
        rag = get_rag_instance()
        
        # Force rebuild if requested
        if "--rebuild" in sys.argv:
            logger.info("\n--rebuild flag detected, forcing index rebuild...")
            rag.rebuild_index()
        
        logger.info("\n" + "=" * 80)
        logger.info("✅ RAG Index built successfully!")
        logger.info("=" * 80)
        logger.info("\nYou can now:")
        logger.info("1. Start the agent: python -m agent")
        logger.info("2. Ask company-specific questions like:")
        logger.info("   - 'What questions does Google ask?'")
        logger.info("   - 'Show me Amazon medium problems'")
        logger.info("   - 'What are the top Meta interview questions?'")
        
        # Test query
        if "--test" in sys.argv:
            logger.info("\n" + "=" * 80)
            logger.info("Running test query...")
            logger.info("=" * 80)
            
            import asyncio
            
            async def test_query():
                result = await rag.query_company_questions("What are the top Google interview questions?")
                logger.info("\nTest Query: 'What are the top Google interview questions?'")
                logger.info("\nResult:")
                logger.info("-" * 80)
                logger.info(result[:500] + "..." if len(result) > 500 else result)
                logger.info("-" * 80)
            
            asyncio.run(test_query())
        
    except Exception as e:
        logger.error(f"\n❌ Error building RAG index: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()

