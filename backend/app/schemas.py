from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Repository ──────────────────────────────────────────────

class RepoCreate(BaseModel):
    url: str = Field(..., min_length=1)
    platform: str = Field(default="github", pattern="^(github|gitlab)$")
    branch: str = Field(default="main", max_length=255)
    access_token: Optional[str] = None
    scan_prompt: Optional[str] = None
    skill: Optional[str] = None


class RepoUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, min_length=1)
    platform: Optional[str] = Field(None, pattern="^(github|gitlab)$")
    branch: Optional[str] = Field(None, max_length=255)
    access_token: Optional[str] = None
    scan_prompt: Optional[str] = None
    skill: Optional[str] = None


class RepoOut(BaseModel):
    id: int
    name: str
    url: str
    platform: str
    branch: str
    has_token: bool
    scan_prompt: Optional[str]
    skill: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ── ScanTask ────────────────────────────────────────────────

class TaskOut(BaseModel):
    id: int
    repo_id: int
    repo_name: Optional[str] = None
    repo_url: Optional[str] = None
    status: str
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    duration_seconds: Optional[float]

    model_config = {"from_attributes": True}


# ── ScanResult ──────────────────────────────────────────────

class ResultOut(BaseModel):
    id: int
    task_id: int
    raw_output: Optional[str]
    summary: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class TaskDetailOut(TaskOut):
    result: Optional[ResultOut] = None


# ── Dashboard ───────────────────────────────────────────────

class DashboardStats(BaseModel):
    total_repos: int
    enabled_repos: int
    total_scans: int
    scans_this_month: int
    success_count: int
    failed_count: int
    running_count: int


class QueueItemOut(BaseModel):
    repo_id: int
    repo_url: str
    triggered_by: str


class QueueStatusOut(BaseModel):
    running: Optional[QueueItemOut] = None
    queued: list[QueueItemOut]
