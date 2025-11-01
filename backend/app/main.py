from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes_als import router as als_router

app = FastAPI(title="ALS Matrix Service")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(als_router)
