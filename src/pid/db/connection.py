import os
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, JSON, String, Text, ForeignKey, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

class Base(DeclarativeBase):
    pass

class ScanResult(Base):
    __tablename__ = "scan_results"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    verdict: Mapped[str] = mapped_column(String(50), nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    stage_reached: Mapped[str] = mapped_column(String(50), nullable=False)
    input_type: Mapped[str] = mapped_column(String(20), nullable=False)
    raw_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    matches: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    classifier_scores: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    user: Mapped["User"] = relationship(back_populates="scan_results")


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    scan_results: Mapped[list[ScanResult]] = relationship(back_populates="user", cascade="all, delete-orphan")


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        if not DATABASE_URL:
            raise RuntimeError("DATABASE_URL is not configured")
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(bind=get_engine(), autoflush=False, autocommit=False, expire_on_commit=False)
    return _SessionLocal


def init_db() -> bool:
    if not DATABASE_URL:
        return False
    Base.metadata.create_all(bind=get_engine())
    return True


def create_user(*, name: str, email: str, password: str) -> Any | None:
    if not DATABASE_URL:
        return None

    session = get_session_factory()()
    try:
        user = User(name=name, email=email, password=password)
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def save_scan_result(
    *,
    user_id: uuid.UUID,
    verdict: str,
    score: float,
    stage_reached: str,
    input_type: str,
    raw_text: str | None,
    matches: list[dict] | None,
    classifier_scores: dict | None,
) -> Any | None:
    if not DATABASE_URL:
        return None

    session = get_session_factory()()
    try:
        record = ScanResult(
            user_id=user_id,
            verdict=verdict,
            score=score,
            stage_reached=stage_reached,
            input_type=input_type,
            raw_text=raw_text,
            matches=matches,
            classifier_scores=classifier_scores,
        )
        session.add(record)
        session.commit()
        session.refresh(record)
        return record
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()