from __future__ import annotations

import os
import tempfile
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database.base import Base
from app.database.models import Report, Repository, Scan, User
from app.services.report_service import ReportService
from app.services.github.repository_service import RepositoryService


def test_repository_service_can_add_and_list_repo(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    user = User(github_id="1", username="octocat", email="octocat@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    repo = Repository(
        github_repo_id="123",
        user_id=user.id,
        name="demo",
        full_name="octocat/demo",
        default_branch="main",
        language="python",
        visibility="public",
        clone_url="https://github.com/octocat/demo",
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    service = RepositoryService()
    repos = service.list_repositories(db=db, user_id=user.id)
    assert len(repos) == 1
    assert repos[0].full_name == "octocat/demo"


def test_report_service_returns_download_metadata(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    user = User(github_id="2", username="octocat2", email="octocat2@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)

    repo = Repository(
        github_repo_id="456",
        user_id=user.id,
        name="secure-repo",
        full_name="octocat2/secure-repo",
        default_branch="main",
        language="python",
        visibility="public",
        clone_url="https://github.com/octocat2/secure-repo",
    )
    db.add(repo)
    db.commit()
    db.refresh(repo)

    scan = Scan(repository_id=str(repo.id), repository_name=repo.full_name, status="completed", trust_score=88, findings_count=2)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    report = Report(scan_id=scan.id, report_type="pdf", report_path="/tmp/report.pdf")
    db.add(report)
    db.commit()
    db.refresh(report)

    service = ReportService()
    metadata = service.get_report_download(db=db, report_id=report.id)
    assert metadata["report_id"] == report.id
    assert metadata["scan_id"] == scan.id
