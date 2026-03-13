import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Repository(Base):
    __tablename__ = "repositories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(512), nullable=False)
    platform = Column(String(20), nullable=False, default="github")  # github / gitlab
    branch = Column(String(255), nullable=False, default="main")
    access_token_encrypted = Column(Text, nullable=True)
    scan_prompt = Column(Text, nullable=True)
    skill = Column(String(100), nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    tasks = relationship("ScanTask", back_populates="repository", cascade="all, delete-orphan")


class ScanTask(Base):
    __tablename__ = "scan_tasks"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repositories.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default="pending")  # pending / running / success / failed
    triggered_by = Column(String(20), nullable=False, default="manual")
    started_at = Column(DateTime, nullable=True)
    finished_at = Column(DateTime, nullable=True)
    duration_seconds = Column(Float, nullable=True)

    repository = relationship("Repository", back_populates="tasks")
    result = relationship("ScanResult", back_populates="task", uselist=False, cascade="all, delete-orphan")


class ScanResult(Base):
    __tablename__ = "scan_results"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("scan_tasks.id", ondelete="CASCADE"), nullable=False, unique=True)
    raw_output = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    task = relationship("ScanTask", back_populates="result")
