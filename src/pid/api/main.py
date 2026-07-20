from fastapi import FastAPI

from pid.api.routes import router

app = FastAPI(
  title="Prompt Injection Detector",
  description="Detects direct and indirect prompt injection in text and PDF.",
  version="1.0.0",
)

app.include_router(router)

@app.get("/health")
def health():
  return {"status": "ok"}