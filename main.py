"""SecureBank FastAPI application entry point."""
from fastapi import FastAPI
from api import router

app = FastAPI(
    title="SecureBank API",
    description="Integration, monitoring, and serializability verification endpoints.",
    version="0.1.0",
)
app.include_router(router)

@app.get("/")
def root():
    return {
        "project": "SecureBank",
        "message": "API is running. Visit /docs for endpoints.",
        "docs": "/docs",
    }
