from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Repository
from app.schemas import RepoCreate, RepoOut, RepoUpdate
from app.services.scheduler import trigger_scan
from app.utils.crypto import encrypt_token

router = APIRouter(prefix="/api/repos", tags=["repositories"])


@router.get("", response_model=list[RepoOut])
def list_repos(db: Session = Depends(get_db)):
    repos = db.query(Repository).order_by(Repository.created_at.desc()).all()
    return [_to_out(r) for r in repos]


@router.get("/{repo_id}", response_model=RepoOut)
def get_repo(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    return _to_out(repo)


@router.post("", response_model=RepoOut, status_code=201)
def create_repo(body: RepoCreate, db: Session = Depends(get_db)):
    normalized_url = body.url.strip()
    existing = db.query(Repository).filter(Repository.url == normalized_url).first()
    if existing:
        raise HTTPException(status_code=400, detail="Repository URL already exists")

    repo = Repository(
        name=_derive_repo_name(normalized_url),
        url=normalized_url,
        platform=body.platform,
        branch=body.branch,
        access_token_encrypted=encrypt_token(body.access_token) if body.access_token else None,
        scan_prompt=body.scan_prompt,
        skill=body.skill,
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)
    return _to_out(repo)


@router.put("/{repo_id}", response_model=RepoOut)
def update_repo(repo_id: int, body: RepoUpdate, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")

    update_data = body.model_dump(exclude_unset=True)
    if "url" in update_data and update_data["url"]:
        normalized_url = update_data["url"].strip()
        existing = db.query(Repository).filter(Repository.url == normalized_url, Repository.id != repo_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Repository URL already exists")
        update_data["url"] = normalized_url
        update_data["name"] = _derive_repo_name(normalized_url)

    if "access_token" in update_data:
        token = update_data.pop("access_token")
        if token:
            repo.access_token_encrypted = encrypt_token(token)
        else:
            repo.access_token_encrypted = None

    for key, value in update_data.items():
        setattr(repo, key, value)

    db.commit()
    db.refresh(repo)
    return _to_out(repo)


@router.delete("/{repo_id}", status_code=204)
def delete_repo(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    db.delete(repo)
    db.commit()


@router.post("/{repo_id}/scan")
def trigger_repo_scan(repo_id: int, db: Session = Depends(get_db)):
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    task_id = trigger_scan(repo.id, triggered_by="manual")
    return {"task_id": task_id, "message": "Scan triggered"}


def _to_out(repo: Repository) -> RepoOut:
    return RepoOut(
        id=repo.id,
        name=repo.name,
        url=repo.url,
        platform=repo.platform,
        branch=repo.branch,
        has_token=repo.access_token_encrypted is not None,
        scan_prompt=repo.scan_prompt,
        skill=repo.skill,
        created_at=repo.created_at,
        updated_at=repo.updated_at,
    )


def _derive_repo_name(url: str) -> str:
    normalized = url.strip().rstrip("/")
    if normalized.endswith(".git"):
        normalized = normalized[:-4]
    name = normalized.rsplit("/", 1)[-1].strip()
    return name or "repository"
