from pydantic import BaseModel, EmailStr

class TextScanRequest(BaseModel):
  text: str

class ScanResponse(BaseModel):
  verdict: str
  score: float
  stage_reached: str
  matches: list[dict]
  classifier_scores: dict | None = None

class CreateUserRequest(BaseModel):
  name: str
  email: EmailStr
  password: str