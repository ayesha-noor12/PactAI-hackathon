from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.chat import router as chat_router
from app.api.routes.profile import router as profile_router
from app.api.routes.auth import router as auth_router
from app.api.routes.proposals import router as proposals_router
from app.api.routes.sessions import router as sessions_router

app = FastAPI(title="PactAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(profile_router)
app.include_router(auth_router)
app.include_router(proposals_router)
app.include_router(sessions_router)
