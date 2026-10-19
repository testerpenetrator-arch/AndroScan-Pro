from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.db.base import Base
from app.models.identity import Organization, User, Role
from app.models.application import Application, APKVersion
from app.models.analysis import Analysis
from app.models.tool_execution import ToolExecution
from app.models.finding import Finding, FindingReview


def test_finding_creation_and_provenance():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with Session(engine) as db:
        org=Organization(name="Org F97",slug="org-f97"); user=User(email="f97@test.local",full_name="Analyst",password_hash="x")
        db.add_all([org,user]); db.flush()
        app=Application(organization_id=org.id,name="Test App",package_name="com.example.test"); db.add(app); db.flush()
        version=APKVersion(application_id=app.id,original_filename="app.apk",size_bytes=10,sha256="a"*64,mime_type="application/vnd.android.package-archive",storage_key="x.apk",validation_status="VALIDATED"); db.add(version); db.flush()
        analysis=Analysis(organization_id=org.id,apk_version_id=version.id,state="COMPLETED"); db.add(analysis); db.flush()
        te=ToolExecution(analysis_id=analysis.id,tool_id="jadx",tool_name="JADX",tool_version="1.5.3",state="COMPLETED",exit_code=0,stdout="raw",stderr="",started_at=datetime.now(timezone.utc),finished_at=datetime.now(timezone.utc)); db.add(te); db.flush()
        finding=Finding(analysis_id=analysis.id,tool_execution_id=te.id,rule_id="MASVS-STORAGE-001",correlation_key="jadx:MASVS-STORAGE-001:foo",title="Test",description="d",category="STORAGE",severity="HIGH",priority="P2",evidence_json={"location":"AndroidManifest.xml"})
        db.add(finding); db.commit(); db.refresh(finding)
        assert finding.tool_execution_id==te.id and finding.rule_id=="MASVS-STORAGE-001" and finding.review_state=="PENDING"
        review=FindingReview(finding_id=finding.id,analyst_user_id=user.id,state="CONFIRMED",justification="Evidencia verificada")
        db.add(review); finding.review_state="CONFIRMED"; db.commit()
        assert review.finding_id==finding.id
