import json
from sqlalchemy.orm import Session
from src.models import ContactMessage, SyncEventHistory

def create_contact(db: Session, name: str, email: str, message: str) -> ContactMessage:
    new_contact = ContactMessage(
        name=name,
        email=email,
        message=message
    )
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact

def get_contacts(db: Session, limit: int = 100):
    return db.query(ContactMessage).order_by(ContactMessage.id.desc()).limit(limit).all()

def create_sync_event(db: Session, module: str, event: str, payload: dict) -> SyncEventHistory:
    payload_str = json.dumps(payload)
    new_event = SyncEventHistory(
        module=module,
        event=event,
        payload=payload_str
    )
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event

def get_sync_events(db: Session, limit: int = 100):
    events = db.query(SyncEventHistory).order_by(SyncEventHistory.id.desc()).limit(limit).all()
    # Decode payload to dict dynamically
    for ev in events:
        try:
            ev.decoded_payload = json.loads(ev.payload)
        except Exception:
            ev.decoded_payload = {}
    return events

def get_sync_events_by_module(db: Session, module: str, limit: int = 100):
    events = db.query(SyncEventHistory).filter(SyncEventHistory.module == module).order_by(SyncEventHistory.id.desc()).limit(limit).all()
    for ev in events:
        try:
            ev.decoded_payload = json.loads(ev.payload)
        except Exception:
            ev.decoded_payload = {}
    return events
