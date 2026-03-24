from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

from auth import router as auth_router
from protected import router as protected_router

# load environment variables
load_dotenv()

app = FastAPI(title="Instagram AI Tool")

# include routers
app.include_router(auth_router)
app.include_router(protected_router)

# CORS (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to specific domain in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# request schema
class CaptionRequest(BaseModel):
    niche: str
    topic: str
    tone: str


@app.get("/")
def home():
    return {"message": "Instagram AI Tool Running"}