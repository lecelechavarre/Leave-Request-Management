from models.db_alchemy import SessionLocal
from models.models_alchemy import Audit
import uuid, json
def _save(action, username, target_id, before, after):
    db = SessionLocal()
    try:
        aid = str(uuid.uuid4())[:8]
        db.add(Audit(id=aid, action=action, username=username, target_id=target_id, before=json.dumps(before) if before else None, after=json.dumps(after) if after else None))
        db.commit()
    finally:
        db.close()
def audit_create(username, target_id, before, after): _save('CREATE', username, target_id, before, after)
def audit_update(username, target_id, before, after): _save('UPDATE', username, target_id, before, after)
def audit_delete(username, target_id, before, after): _save('DELETE', username, target_id, before, after)
