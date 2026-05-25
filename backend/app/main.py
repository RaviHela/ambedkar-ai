from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.routes import router
from app.api.auth_routes import router as auth_router
import os

app = FastAPI(
    title="Dr. B.R. Ambedkar AI Persona",
    version="5.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(router, prefix="/api/v1")

# Serve static files
static_path = "/home/ubuntu/ambedkar-ai/webapp/static"
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve webapp
webapp_path = "/home/ubuntu/ambedkar-ai/webapp"
index_path = os.path.join(webapp_path, "index.html")
if os.path.exists(index_path):
    from fastapi.responses import FileResponse
    @app.get("/")
    async def serve_index():
        return FileResponse(index_path)
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        if full_path.startswith("api/"):
            return FileResponse(index_path)
        return FileResponse(index_path)
