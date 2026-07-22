import os
import shutil
import tempfile

from fastapi import HTTPException, UploadFile

from pid.db.connection import create_user, save_scan_result
from pid.pipeline.detector import detect_from_text, detect_from_pdf
from pid.api.jwt import generate_hash, generate_jwt, get_user_by_email, verify_password

class AuthService:
    @staticmethod
    def login(username: str, password: str) -> dict:
        user = get_user_by_email(username)
        if user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if not verify_password(password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = generate_jwt({"email": user.email, "sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}

    @staticmethod
    def register(name: str, email: str, password: str) -> dict:
        hashed_password = generate_hash(password)
        user = create_user(name=name, email=email, password=hashed_password)
        if user is None:
            raise HTTPException(status_code=500, detail="Unable to create user")

        return {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "created_at": user.created_at.isoformat(),
        }

class ScanService:
    @staticmethod
    def scan_text(payload: str, user_id: str) -> dict:
        result = detect_from_text(payload)
        return ScanService._persist_result(result, user_id, "text", payload)

    @staticmethod
    def scan_pdf(file: UploadFile, user_id: str) -> dict:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp.flush()
            tmp_path = tmp.name

        try:
            if os.path.getsize(tmp_path) == 0:
                raise HTTPException(status_code=400, detail="PDF file is empty.")

            result = detect_from_pdf(tmp_path)
            return ScanService._persist_result(result, user_id, "pdf")
        finally:
            os.remove(tmp_path)

    @staticmethod
    def _persist_result(result, user_id: str, input_type: str, raw_text: str | None = None) -> dict:
        response = {
            "verdict": result.verdict.value,
            "score": result.score,
            "stage_reached": result.stage_reached,
            "matches": [
                {
                    "pattern_id": match.pattern_id,
                    "location": match.location,
                    "matched_text": match.matched_text,
                }
                for match in result.heuristic.matches
            ],
            "classifier_scores": result.classifier_scores,
        }

        save_scan_result(
            user_id=user_id,
            verdict=response["verdict"],
            score=response["score"],
            stage_reached=response["stage_reached"],
            input_type=input_type,
            raw_text=raw_text,
            matches=response["matches"],
            classifier_scores=response["classifier_scores"],
        )
        return response
