from sqlalchemy.orm import Session
from .models import AuditLog

def write_audit(
    db: Session,
    *,
    actor_user_id: int | None,
    action: str,
    resource: str,
    ip: str | None,
    user_agent: str | None,
    details: dict | None = None,
):
    db.add(AuditLog(
        actor_user_id=actor_user_id,
        action=action,
        resource=resource,
        ip=ip,
        user_agent=user_agent,
        details=details or {},
    ))
    db.commit()
