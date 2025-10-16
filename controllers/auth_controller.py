from models.db_alchemy import SessionLocal
from models.models_alchemy import User
from utils import verify_password, hash_password
def login(u,p):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username==u).first()
        if user and verify_password(p, user.password):
            return {'username': user.username, 'role': user.role}
        return None
    finally:
        db.close()
def register(u,p,role='employee'):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.username==u).first():
            return False
        db.add(User(username=u, password=hash_password(p), role=role))
        db.commit()
        return True
    finally:
        db.close()
