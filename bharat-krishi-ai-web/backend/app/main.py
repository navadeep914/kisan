
import logging
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.routes import (
    crop_recommendation,
    plant_disease,
    soil_analysis,
    crop_yield,
    market_price,
    weather,
    crop_rotation,
    government_schemes,
    auth,
)

from app.advisory import router as farmer_advisory
from app.core.database import verify_and_init_db


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
)

logger = logging.getLogger("bharat_krishi_ai")


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="Bharat Krishi AI",
    description="Intelligent Agriculture Decision Support System",
    version="1.0.0",
)


# --------------------------------------------------
# CORS configuration
# --------------------------------------------------

# For production, replace "*" with your actual frontend
# origin(s), especially if using credentialed requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --------------------------------------------------
# Register API routers
# --------------------------------------------------

app.include_router(
    auth.router,
    prefix="/api/auth",
    tags=["Authentication"],
)

app.include_router(
    crop_recommendation.router,
    prefix="/api/crop",
    tags=["Crop Recommendation"],
)

app.include_router(
    plant_disease.router,
    prefix="/api/disease",
    tags=["Plant Disease"],
)

app.include_router(
    soil_analysis.router,
    prefix="/api/soil",
    tags=["Soil Analysis"],
)

app.include_router(
    crop_yield.router,
    prefix="/api/yield",
    tags=["Crop Yield"],
)

app.include_router(
    market_price.router,
    prefix="/api/market",
    tags=["Market Price"],
)

app.include_router(
    weather.router,
    prefix="/api/weather",
    tags=["Weather"],
)

app.include_router(
    crop_rotation.router,
    prefix="/api/rotation",
    tags=["Crop Rotation"],
)

app.include_router(
    government_schemes.router,
    prefix="/api/schemes",
    tags=["Government Schemes"],
)

app.include_router(
    farmer_advisory.router,
    prefix="/api/advisory",
    tags=["Farmer Advisory"],
)


# --------------------------------------------------
# Startup
# --------------------------------------------------

@app.on_event("startup")
async def startup_event():
    logger.info("Starting Bharat Krishi AI backend")

    try:
        logger.info("Initializing database")
        await verify_and_init_db()
        logger.info("Database initialization completed successfully")

    except Exception:
        logger.exception("Database initialization failed")
        raise

    logger.info("Bharat Krishi AI startup completed")


# --------------------------------------------------
# Health-check endpoint
# --------------------------------------------------

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": "Bharat Krishi AI",
        "version": "1.0.0",
    }


# --------------------------------------------------
# API root
# --------------------------------------------------

@app.get("/api", tags=["General"])
async def api_root():
    return {
        "message": "Bharat Krishi AI API is running",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# --------------------------------------------------
# Serve frontend production build, if available
# --------------------------------------------------

backend_directory = Path(__file__).resolve().parent
project_directory = backend_directory.parent.parent
frontend_dist = project_directory / "frontend" / "dist"

if frontend_dist.is_dir():
    logger.info("Frontend build found at %s", frontend_dist)

    # Keep this mount after API route registration.
    app.mount(
        "/",
        StaticFiles(directory=str(frontend_dist), html=True),
        name="frontend",
    )

else:
    logger.warning(
        "Frontend build not found at %s; serving API root instead",
        frontend_dist,
    )

    @app.get("/", tags=["General"])
    async def root():
        return {
            "message": "Bharat Krishi AI API is running",
            "version": "1.0.0",
            "docs": "/docs",
            "health": "/health",
        }
