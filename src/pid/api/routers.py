from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm

from pid.api.dependencies import get_current_user
from pid.api.schemas import CreateUserRequest, ScanResponse, TextScanRequest
from pid.api.services import AuthService, ScanService

router = APIRouter()

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
  return AuthService.login(form_data.username, form_data.password)

@router.post("/user", status_code=201)
def create_new_user(payload: CreateUserRequest):
  return AuthService.register(payload.name, str(payload.email), payload.password)

@router.post("/scan/text", response_model=ScanResponse)
def scan_text(payload: TextScanRequest, user: dict = Depends(get_current_user)):
  return ScanService.scan_text(payload.text, user["sub"])

@router.post("/scan/pdf", response_model=ScanResponse)
def scan_pdf(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
  return ScanService.scan_pdf(file, user["sub"])
