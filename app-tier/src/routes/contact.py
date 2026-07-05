from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from src.db import get_db
from src.models import Contact
from src.utils.validators import validate_email_format, validate_non_empty
from src.utils.logger import get_logger

logger = get_logger("contact_route")

router = APIRouter(tags=["Contact"])

class ContactRequest(BaseModel):
    name: str = Field(..., json_schema_extra={"example": "Dima Dynamo"})
    email: str = Field(..., json_schema_extra={"example": "oasis@core.dev"})
    message: str = Field(..., json_schema_extra={"example": "Testing transmission to OASIS System Core."})

@router.post("/contact", status_code=status.HTTP_201_CREATED)
async def submit_contact(payload: ContactRequest, db: Session = Depends(get_db)):
    logger.info(f"Received contact submission from: {payload.email}")

    # Explicit custom validation checks
    name = validate_non_empty(payload.name, "name")
    email = validate_email_format(validate_non_empty(payload.email, "email"))
    message = validate_non_empty(payload.message, "message")

    try:
        new_contact = Contact(
            name=name,
            email=email,
            message=message
        )
        db.add(new_contact)
        db.commit()
        db.refresh(new_contact)
        logger.info(f"Saved contact submission (ID: {new_contact.id}) successfully.")
        return {"status": "ok", "id": new_contact.id}
    except Exception as e:
        db.rollback()
        logger.error(f"Database insertion failure: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="// DATABASE ERROR: Failed to save submission."
        )
