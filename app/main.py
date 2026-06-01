from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth_router, product_router, checkout_router

# optionally create database tables immediately at startup (redundant but safe if not using Alembic)
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="E-Commerce Backend & Concurrency Services",
    description="Engineered using FastAPI, PostgreSQL, SQLAlchemy, and row-level pessimistic locking.",
    version="1.0.0"
)

# CORS for web integrations (replace * with secure origins in production)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# Standard API Routers
app.include_router(auth_router.router, prefix="/api")
app.include_router(product_router.router, prefix="/api")
app.include_router(checkout_router.router, prefix="/api")

@app.get("/", tags=["Root"])
def root_status():
    return {
        "service": "E-Commerce Backend API Engine",
        "engine": "FastAPI with ASGI Uvicorn",
        "database": "PostgreSQL via SQLAlchemy Transactions",
        "health": "healthy"
    }