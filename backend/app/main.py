from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import os
import sys

app = FastAPI(
    title="Dr. B.R. Ambedkar AI Persona",
    version="3.0.0"
)

# Enable CORS for API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api/v1")

# Find webapp directory dynamically
def find_webapp_path():
    # Try multiple possible locations
    possible_paths = [
        "/home/ubuntu/ambedkar-ai/webapp",  # AWS EC2
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "webapp"),  # Local Mac (backend/../webapp)
        "webapp"  # Relative path
    ]
    
    for path in possible_paths:
        if os.path.exists(path) and os.path.isdir(path):
            return path
    return None

webapp_path = find_webapp_path()
if webapp_path:
    app.mount("/", StaticFiles(directory=webapp_path, html=True), name="webapp")
    print(f"Serving webapp from {webapp_path}")
else:
    print("Webapp directory not found")

@app.get("/health")
async def health():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}
