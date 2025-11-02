"""
Run the FastAPI server.
Usage: python -m api
"""

import os
import uvicorn
from dotenv import load_dotenv

load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    
    print(f"""
╔═══════════════════════════════════════╗
║   Interview Coach API Server         ║
║   Running on http://localhost:{port}   ║
╚═══════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "api.server:app",
        host="0.0.0.0",
        port=port,
        reload=True, 
        log_level="info"
    )

