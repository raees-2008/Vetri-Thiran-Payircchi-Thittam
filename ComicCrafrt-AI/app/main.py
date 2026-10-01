from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router


# Create the FastAPI application
app = FastAPI(
    title="ComicCraft AI",
    description="AI-powered comic generation API",
    version="1.0.0",
)


# Allow requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register all ComicCraft routes
app.include_router(router)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "ComicCraft AI API is running",
    }


@app.get("/health")
async def health():
    return {
        "success": True,
        "status": "healthy",
    }