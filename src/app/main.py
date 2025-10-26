from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .routers import auth, storage, beneficiarios, orgs, articles, donations, metrics, chat  # , users

app = FastAPI(
    title="Meu Nome Gov - API Core",
    description="API para sistema de gestão de beneficiários e ONGs",
    version="1.0.0"
)

origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware, allow_origins=origins, allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True, "message": "API is running"}

app.include_router(auth.router)
app.include_router(storage.router)
app.include_router(beneficiarios.router)
app.include_router(orgs.router)
app.include_router(articles.router)
app.include_router(donations.router)
app.include_router(metrics.router)
app.include_router(chat.router)
# app.include_router(users.router)
