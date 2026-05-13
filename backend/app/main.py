from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import os

app = FastAPI(
    title="Dr. B.R. Ambedkar AI Persona",
    description="AI that answers based on Dr. Ambedkar's writings and speeches",
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

# Include API routes (must be before static mount)
app.include_router(router, prefix="/api/v1")

# Serve static files (CSS, JS, etc.)
webapp_path = "/app/webapp"
if os.path.exists(webapp_path):
    app.mount("/static", StaticFiles(directory=webapp_path), name="static")

@app.get("/")
async def serve_index():
    """Serve the web app index.html"""
    webapp_path = "/app/webapp/index.html"
    if os.path.exists(webapp_path):
        with open(webapp_path, "r") as f:
            return HTMLResponse(content=f.read())
    return {"message": "Web app not found"}

@app.get("/health")
async def health():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}
