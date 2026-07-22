from fastapi import FastAPI

from pid.api.routers import router
from pid.db.connection import init_db

app = FastAPI(
  title="Prompt Injection Detector",
  description="Detects direct and indirect prompt injection in text and PDF.",
  version="1.0.0",
)

app.include_router(router)

@app.on_event("startup")
def startup() -> None:
  init_db()

@app.get("/health")
def health():
  return {"status": "ok"}