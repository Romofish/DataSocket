# file path: /backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes_als import router as als_router
import logging

app = FastAPI(title="ALS Matrix Service")

# Simple logging baseline
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(als_router)
