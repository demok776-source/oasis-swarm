import re
from fastapi import HTTPException, status

EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

def validate_email_format(email: str) -> str:
    if not re.match(EMAIL_REGEX, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="// VALIDATION ERROR: Invalid email address format."
        )
    return email

def validate_non_empty(value: str, field_name: str) -> str:
    stripped = value.strip() if value else ""
    if not stripped:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"// VALIDATION ERROR: Field '{field_name}' cannot be empty."
        )
    return stripped
