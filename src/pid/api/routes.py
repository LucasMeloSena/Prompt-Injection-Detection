import tempfile
import shutil
import os

from fastapi import APIRouter, HTTPException, UploadFile, File

from pid.pipeline.detector import detect_from_text, detect_from_pdf
from pid.api.schemas import TextScanRequest, ScanResponse

router = APIRouter()

def _to_response(result) -> ScanResponse:
  return ScanResponse(
    verdict=result.verdict.value,
    score=result.score,
    stage_reached=result.stage_reached,
    matches=[
      {
        "pattern_id": m.pattern_id,
        "location": m.location,
        "matched_text": m.matched_text,
      }
      for m in result.heuristic.matches
    ],
    classifier_scores=result.classifier_scores,
  )

@router.post("/scan/text", response_model=ScanResponse)
def scan_text(payload: TextScanRequest):
  result = detect_from_text(payload.text)
  return _to_response(result)

@router.post("/scan/pdf", response_model=ScanResponse)
def scan_pdf(file: UploadFile = File(...)):
  with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
    shutil.copyfileobj(file.file, tmp)
    tmp.flush()
    tmp_path = tmp.name

  try:
    if os.path.getsize(tmp_path) == 0:
      raise HTTPException(status_code=400, detail="PDF file is empty.")

    result = detect_from_pdf(tmp_path)
    return _to_response(result)
  finally:
    os.remove(tmp_path)