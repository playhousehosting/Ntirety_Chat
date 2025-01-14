from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import os
import subprocess
import sys

app = FastAPI()

@app.get("/")
async def root():
    # Start Streamlit in a subprocess
    port = int(os.environ.get("PORT", 8501))
    streamlit_cmd = [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", str(port)]
    process = subprocess.Popen(streamlit_cmd)
    
    # Return the Streamlit interface
    return HTMLResponse(content=f"""
        <html>
            <head>
                <title>Ntirety Chatbot</title>
                <meta http-equiv="refresh" content="0;url=http://localhost:{port}">
            </head>
            <body>
                <p>Redirecting to Streamlit interface...</p>
            </body>
        </html>
    """)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
