from fastapi import APIRouter, Depends, HTTPException
from api.deps import RoleChecker
from core.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.models import InspectionRecord

router = APIRouter()

@router.get("/{id}/report")
async def generate_evidence_report(
    id: str,
    current_user: dict = Depends(RoleChecker(["INSPECTOR", "SUPERVISOR", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(InspectionRecord).where(InspectionRecord.id == id))
    record = result.scalars().first()
    if not record:
        from api.v1.inspections import mock_db
        if id in mock_db.get("inspections", {}):
            insp = mock_db["inspections"][id]
            audit_trail = [
                log for log in mock_db.get("audit_logs", {}).values()
                if log.get("inspection_id") == id
            ]
            return {
                "title": "MetroLens Legal Metrology Evidence Report",
                "inspection_metadata": {
                    "inspection_id": id,
                    "officer_id": insp.get("officer_id"),
                    "category": insp.get("category") or insp.get("product", {}).get("category"),
                    "final_verdict": insp.get("verdict") or insp.get("overall_compliance"),
                    "rulepack_version_applied": "v1",
                    "evidence_hash": insp.get("evidence_hash"),
                },
                "measurements_and_evaluations": insp.get("evaluations") or insp.get("violations", []),
                "ai_analysis": insp.get("ai_analysis"),
                "chain_of_custody_audit_trail": audit_trail,
            }
        raise HTTPException(status_code=404, detail="Inspection not found")
    
    insp = record.data or {}
    audit_trail = insp.get("chain_of_custody_audit_trail") or insp.get("audit_trail") or []
    if not audit_trail:
        from api.v1.inspections import mock_db
        audit_trail = [
            log for log in mock_db.get("audit_logs", {}).values()
            if log.get("inspection_id") == id
        ]
    return {
        "title": "MetroLens Legal Metrology Evidence Report",
        "inspection_metadata": {
            "inspection_id": id,
            "officer_id": insp.get("officer_id"),
            "category": insp.get("product", {}).get("category"),
            "final_verdict": insp.get("overall_compliance"),
            "rulepack_version_applied": "v1",
            "evidence_hash": insp.get("evidence_hash"),
        },
        "measurements_and_evaluations": insp.get("violations", []),
        "ai_analysis": insp.get("ai_analysis"),
        "chain_of_custody_audit_trail": audit_trail,
    }

from fastapi.responses import PlainTextResponse

@router.get("/{id}/csv")
async def generate_csv_report(
    id: str,
    current_user: dict = Depends(RoleChecker(["INSPECTOR", "SUPERVISOR", "ADMIN"])),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(InspectionRecord).where(InspectionRecord.id == id))
    record = result.scalars().first()
    if not record:
        from api.v1.inspections import mock_db
        if id in mock_db.get("inspections", {}):
            insp = mock_db["inspections"][id]
        else:
            raise HTTPException(status_code=404, detail="Inspection not found")
    else:
        insp = record.data
    
    import io, csv
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Rule ID", "Rule Title", "Status", "Detail"])
    
    for v in insp.get("violations", []):
        writer.writerow([
            v.get("rule_id", ""),
            v.get("rule_title", ""),
            v.get("status", ""),
            v.get("detail", ""),
        ])
    
    return PlainTextResponse(
        output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=compliance_{id[:8]}.csv"},
    )
