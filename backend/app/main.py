from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import os

app = FastAPI(
    title="Dr. B.R. Ambedkar AI Persona",
    description="AI that answers based on Dr. Ambedkar's writings and speeches",
    version="3.0.0"
)

# Enable CORS for all origins (allow web app to connect)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Dr. B.R. Ambedkar AI Persona API",
        "version": "3.0.0",
        "features": ["conversation memory", "voice input", "hindi support", "claude ai"],
        "endpoints": {
            "chat": "/api/v1/chat",
            "health": "/api/v1/health",
            "clear-memory": "/api/v1/clear-memory",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar"}
