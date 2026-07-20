from pydantic import BaseModel

class TextScanRequest(BaseModel):
  text: str

class ScanResponse(BaseModel):
  verdict: str
  score: float
  stage_reached: str
  matches: list[dict]