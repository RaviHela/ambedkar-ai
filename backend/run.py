import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("Dr. B.R. Ambedkar AI Persona - API Server")
    print("=" * 50)
    print("\nStarting server...")
    print("API will be available at: http://localhost:8000")
    print("Interactive docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
