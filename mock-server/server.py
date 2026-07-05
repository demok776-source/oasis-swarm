import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from mock_routes import router as mock_router

app = FastAPI(
    title="OASIS SYSTEM CORE — Local Mock Server",
    description="Development mock server hosting the landing page and mocking backend APIs.",
    version="1.0.0"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include mock endpoints under the API routes
app.include_router(mock_router)

# Locate and serve index.html statically
STATIC_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "oasis-v4"))

if os.path.exists(STATIC_DIR):
    print(f"[LOCAL] Serving landing page index.html from: {STATIC_DIR}")
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
else:
    print(f"[WARNING] Static landing page folder not found at: {STATIC_DIR}")
    @app.get("/")
    async def fallback_root():
        return {"error": f"OASIS static landing page directory not found. Please place it at: {STATIC_DIR}"}

if __name__ == "__main__":
    print("[OASIS SYSTEM CORE] Starting local development server mock...")
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
