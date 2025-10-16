from models.db_alchemy import SessionLocal
from models.models_alchemy import Leave
from controllers.audit_controller import audit_create, audit_update, audit_delete
import uuid, json
def list_for(user):
    db = SessionLocal()
    try:
        if user.get('role') == 'admin':
            rows = db.query(Leave).all()
        else:
            rows = db.query(Leave).filter(Leave.username==user.get('username')).all()
        return [dict(id=r.id, username=r.username, type=r.type, start_date=r.start_date, end_date=r.end_date, status=r.status, reason=r.reason) for r in rows]
    finally:
        db.close()
def create(user, payload):
    db = SessionLocal()
    try:
        lid = str(uuid.uuid4())[:8]
        rec = Leave(id=lid, username=user['username'], type=payload.get('type'), start_date=payload.get('start_date'), end_date=payload.get('end_date'), status=payload.get('status','Pending'), reason=payload.get('reason'))
        db.add(rec); db.commit()
        audit_create(user['username'], lid, None, payload)
        return {'id': lid, 'username': rec.username, 'type': rec.type, 'start_date': rec.start_date, 'end_date': rec.end_date, 'status': rec.status, 'reason': rec.reason}
    finally:
        db.close()
def update(user, leave_id, updates):
    db = SessionLocal()
    try:
        rec = db.query(Leave).filter(Leave.id==leave_id).first()
        if not rec: return None
        if user.get('role') != 'admin' and rec.username != user.get('username'):
            return None
        before = dict(id=rec.id, username=rec.username, type=rec.type, start_date=rec.start_date, end_date=rec.end_date, status=rec.status, reason=rec.reason)
        for k,v in updates.items():
            setattr(rec, k, v)
        db.commit()
        after = dict(id=rec.id, username=rec.username, type=rec.type, start_date=rec.start_date, end_date=rec.end_date, status=rec.status, reason=rec.reason)
        audit_update(user['username'], leave_id, before, after)
        return after
    finally:
        db.close()
def delete(user, leave_id):
    db = SessionLocal()
    try:
        rec = db.query(Leave).filter(Leave.id==leave_id).first()
        if not rec: return False
        if user.get('role') != 'admin' and rec.username != user.get('username'):
            return False
        before = dict(id=rec.id, username=rec.username, type=rec.type, start_date=rec.start_date, end_date=rec.end_date, status=rec.status, reason=rec.reason)
        db.delete(rec); db.commit()
        audit_delete(user['username'], leave_id, before, None)
        return True
    finally:
        db.close()
