from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
import os

app = FastAPI(
    title="Dr. B.R. Ambedkar AI Persona",
    version="4.0.0"
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

# Serve static files (images, CSS, etc.)
static_path = "/home/ubuntu/ambedkar-ai/webapp/static"
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")
    print(f"✅ Serving static files from {static_path}")

# Health endpoint at root
@app.get("/health")
async def health():
    return {"status": "healthy", "persona": "Dr. B.R. Ambedkar", "version": "4.0.0"}

# Serve webapp at root
webapp_path = "/home/ubuntu/ambedkar-ai/webapp"
if os.path.exists(webapp_path):
    @app.get("/")
    async def serve_index():
        with open(os.path.join(webapp_path, "index.html"), "r") as f:
            return HTMLResponse(content=f.read())
    print(f"✅ Serving webapp from {webapp_path}")
