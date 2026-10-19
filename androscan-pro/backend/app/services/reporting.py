import hashlib
import html
import io
import json
from datetime import datetime, timezone
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}

def build_report_data(organization_id, analysis, version, application, findings, tool_executions):
    ordered = sorted(findings, key=lambda f: (SEVERITY_ORDER.get(f.severity, 99), f.title.lower()))
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "organization_id": organization_id,
        "application": {"id": application.id, "name": application.name, "package_name": application.package_name},
        "apk": {"version_id": version.id, "filename": version.original_filename, "sha256": version.sha256, "size_bytes": version.size_bytes, "version_name": version.version_name, "version_code": version.version_code},
        "analysis": {"id": analysis.id, "state": analysis.state, "trace_id": analysis.trace_id, "created_at": analysis.created_at.isoformat() if analysis.created_at else None, "started_at": analysis.started_at.isoformat() if analysis.started_at else None, "finished_at": analysis.finished_at.isoformat() if analysis.finished_at else None},
        "summary": {"total_findings": len(ordered), "by_severity": {s: sum(1 for f in ordered if f.severity == s) for s in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]}, "by_review_state": {s: sum(1 for f in ordered if f.review_state == s) for s in ["PENDING", "CONFIRMED", "DISMISSED"]}, "tools": len(tool_executions)},
        "tools": [{"id": t.id, "name": t.tool_name, "version": t.tool_version, "state": t.state, "exit_code": t.exit_code} for t in tool_executions],
        "findings": [{"id": f.id, "correlation_key": f.correlation_key, "rule_id": f.rule_id, "title": f.title, "description": f.description, "category": f.category, "severity": f.severity, "priority": f.priority, "review_state": f.review_state, "analyst_notes": f.analyst_notes, "evidence": f.evidence_json, "raw_result_ref": f.raw_result_ref, "tool_execution_id": f.tool_execution_id, "created_at": f.created_at.isoformat() if f.created_at else None} for f in ordered],
        "disclaimer": "Los resultados automatizados son indicios técnicos. La clasificación y decisión final de riesgo corresponde al analista humano."
    }

def render_report(data: dict, fmt: str) -> tuple[str, str, bytes]:
    fmt = fmt.upper()
    if fmt == "JSON":
        content = json.dumps(data, ensure_ascii=False, indent=2)
        return "application/json", "json", content.encode("utf-8")
    if fmt == "HTML":
        app = html.escape(data["application"]["name"])
        package = html.escape(data["application"]["package_name"])
        apk_hash = html.escape(data["apk"]["sha256"])
        rows = "".join("<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(*(html.escape(str(f[k] or "")) for k in ("title", "category", "severity", "priority", "review_state"))) for f in data["findings"])
        content = f"""<!doctype html><html lang=\"es\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\"><title>Informe AndroScan</title><style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:2rem auto;padding:0 1rem;color:#18212f}}h1{{color:#176b52}}table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ccd3dc;padding:.55rem;text-align:left}}th{{background:#edf2f7}}.note{{padding:1rem;background:#f4f7fa;border-left:4px solid #176b52}}</style></head><body><h1>Informe de análisis de seguridad — AndroScan</h1><p><b>Aplicación:</b> {app} ({package})</p><p><b>SHA-256 del APK:</b> <code>{apk_hash}</code></p><p><b>Análisis:</b> {html.escape(data['analysis']['id'])} · Estado: {html.escape(data['analysis']['state'])}</p><h2>Resumen</h2><p>Hallazgos: {data['summary']['total_findings']} · Críticos: {data['summary']['by_severity']['CRITICAL']} · Altos: {data['summary']['by_severity']['HIGH']}</p><h2>Hallazgos</h2><table><thead><tr><th>Título</th><th>Categoría</th><th>Severidad</th><th>Prioridad</th><th>Revisión</th></tr></thead><tbody>{rows or '<tr><td colspan="5">No se registraron hallazgos.</td></tr>'}</tbody></table><p class=\"note\">{html.escape(data['disclaimer'])}</p><p>Generado: {html.escape(data['generated_at'])}</p></body></html>"""
        return "text/html; charset=utf-8", "html", content.encode("utf-8")
    if fmt == "PDF":
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter, title="Informe AndroScan", author="AndroScan")
        styles = getSampleStyleSheet()
        story = [Paragraph("Informe de análisis de seguridad — AndroScan", styles["Title"]), Spacer(1, 12), Paragraph(f"Aplicación: {html.escape(data['application']['name'])} ({html.escape(data['application']['package_name'])})", styles["Normal"]), Paragraph(f"SHA-256: {html.escape(data['apk']['sha256'])}", styles["Code"]), Paragraph(f"Análisis: {html.escape(data['analysis']['id'])} · Estado: {html.escape(data['analysis']['state'])}", styles["Normal"]), Spacer(1, 12), Paragraph("Resumen", styles["Heading2"]), Paragraph(f"Hallazgos: {data['summary']['total_findings']} | Críticos: {data['summary']['by_severity']['CRITICAL']} | Altos: {data['summary']['by_severity']['HIGH']}", styles["Normal"]), Spacer(1, 12), Paragraph("Hallazgos", styles["Heading2"])]
        table_data = [["Título", "Categoría", "Severidad", "Prioridad", "Revisión"]]
        table_data.extend([[str(f[k])[:180] for k in ("title", "category", "severity", "priority", "review_state")] for f in data["findings"]])
        table = Table(table_data, repeatRows=1, colWidths=[220, 75, 65, 55, 65])
        table.setStyle(TableStyle([("BACKGROUND", (0,0),(-1,0), colors.HexColor("#e7edf2")), ("GRID", (0,0),(-1,-1),0.4,colors.grey), ("VALIGN",(0,0),(-1,-1),"TOP"), ("FONTSIZE",(0,0),(-1,-1),7), ("PADDING",(0,0),(-1,-1),5)]))
        story.append(table); story.extend([Spacer(1, 14), Paragraph(html.escape(data["disclaimer"]), styles["Italic"])])
        doc.build(story)
        return "application/pdf", "pdf", output.getvalue()
    raise ValueError("Formato no soportado")

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()
