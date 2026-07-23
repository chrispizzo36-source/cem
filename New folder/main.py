from fastapi import FastAPI, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import date
import os, shutil
from database import get_db
from services import validate_statutory_leave

app = FastAPI(title="Kilifi County CEMS API", version="1.0")

# Local directory to store uploaded Medical Certificates
UPLOAD_DIR = "./uploads/medical_certs"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "Kilifi County CEMS API Operational"}


# 1. Daily Officer Check-In Endpoint
@app.post("/api/v1/checkin")
def officer_checkin(pf_number: str, location: str):
    # In production: Query officer by pf_number and update current_status = 'on_duty'
    return {
        "status": "success",
        "message": f"Officer {pf_number} checked in successfully at {location}",
        "current_status": "on_duty"
    }


# 2. Statutory Leave Application Endpoint
@app.post("/api/v1/leave/apply")
async def apply_for_leave(
    pf_number: str = Form(...),
    leave_type: str = Form(...), # annual, maternity, paternity, sick
    days_requested: int = Form(...),
    start_date: date = Form(...),
    end_date: date = Form(...),
    medical_cert: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    med_cert_saved = False

    # Save uploaded file if attached
    if medical_cert:
        filename = f"{pf_number}_{date.today()}_{medical_cert.filename}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(medical_cert.file, buffer)
        med_cert_saved = True

    # Mock annual leave balance (Fetched from officers table in production)
    mock_available_balance = 15

    # Run Kenyan Labor Law Statutory Compliance Check
    try:
        validate_statutory_leave(
            leave_type=leave_type,
            days_requested=days_requested,
            available_balance=mock_available_balance,
            has_med_cert=med_cert_saved
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "status": "success",
        "message": "Leave application verified and submitted for supervisor sign-off.",
        "pf_number": pf_number,
        "leave_type": leave_type,
        "days_requested": days_requested,
        "medical_certificate_attached": med_cert_saved
    }