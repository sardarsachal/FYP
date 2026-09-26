"""
NextTrack — Music Recommendation API
Application entry point.

This file creates the FastAPI application and wires in the API routes:
/health, /recommend, /catalogue, /feedback and the single-page web demo.
"""

from fastapi import FastAPI

from app.api.routes import router

# Basic service metadata (kept in one place so it is easy to update).
SERVICE_NAME = "nexttrack"
SERVICE_VERSION = "0.1.0"

# Create the FastAPI application instance.
app = FastAPI(
    title="NextTrack — Music Recommendation API",
    description=(
        "A stateless RESTful API that recommends the next track based on "
        "listening history, user preferences, and available track data."
    ),
    version=SERVICE_VERSION,
)

# Register all routes defined in app/api/routes.py.
app.include_router(router)
