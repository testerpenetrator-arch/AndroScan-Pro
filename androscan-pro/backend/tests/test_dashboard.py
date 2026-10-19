from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models.identity import Organization, User, Role, user_organization_roles
from app.models.application import Application, APKVersion
from app.models.analysis import Analysis
from app.models.tool_execution import ToolExecution
from app.models.finding import Finding
from app.api.dashboard import get_dashboard


def test_dashboard_aggregates_and_keeps_org_scope():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        org = Organization(name="Dashboard Org", slug="dashboard-org")
        other = Organization(name="Other Org", slug="other-org")
        user = User(email="dash@test.local", full_name="Dashboard User", password_hash="x")
        role = Role(name="ANALYST", description="Analyst")
        db.add_all([org, other, user, role]); db.flush()
        db.execute(user_organization_roles.insert().values(user_id=user.id, organization_id=org.id, role_id=role.id))
        app = Application(organization_id=org.id, name="Secure App", package_name="com.example.secure")
        other_app = Application(organization_id=other.id, name="Other App", package_name="com.example.other")
        db.add_all([app, other_app]); db.flush()
        v = APKVersion(application_id=app.id, original_filename="secure.apk", size_bytes=10, sha256="a"*64, mime_type="application/vnd.android.package-archive", storage_key="secure.apk", validation_status="VALIDATED")
        ov = APKVersion(application_id=other_app.id, original_filename="other.apk", size_bytes=10, sha256="b"*64, mime_type="application/vnd.android.package-archive", storage_key="other.apk", validation_status="VALIDATED")
        db.add_all([v, ov]); db.flush()
        a = Analysis(organization_id=org.id, apk_version_id=v.id, state="COMPLETED")
        oa = Analysis(organization_id=other.id, apk_version_id=ov.id, state="COMPLETED")
        db.add_all([a, oa]); db.flush()
        now = datetime.now(timezone.utc)
        te = ToolExecution(analysis_id=a.id, tool_id="jadx", tool_name="JADX", tool_version="1.5.3", state="COMPLETED", exit_code=0, stdout="", stderr="", started_at=now, finished_at=now)
        db.add(te); db.flush()
        db.add(Finding(analysis_id=a.id, tool_execution_id=te.id, correlation_key="k", title="Manifest issue", description="d", category="PLATFORM", severity="HIGH", priority="P2", evidence_json={}))
        db.add(Finding(analysis_id=oa.id, tool_execution_id=te.id, correlation_key="k2", title="Other", description="d", category="CODE", severity="CRITICAL", priority="P1", evidence_json={}))
        db.commit()
        result = get_dashboard(org.id, user, db)
        assert result.counts.applications == 1
        assert result.counts.analyses == 1
        assert result.counts.findings == 1
        assert result.counts.high_findings == 1
        assert result.counts.critical_findings == 0
        assert result.analyses[0].application_name == "Secure App"
