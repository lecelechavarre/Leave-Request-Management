from models.db_alchemy import engine, SessionLocal
from models.models_alchemy import Base, User, Leave
from utils import hash_password
import os, datetime, random, uuid
def seed_users(db):
    users = [
        ('admin','admin123','admin'),
        ('manager1','manager123','manager'),
        ('staff1','staff123','employee'),
        ('staff2','staff123','employee'),
        ('staff3','staff123','employee')
    ]
    for u,p,r in users:
        if db.query(User).filter(User.username==u).first(): continue
        db.add(User(username=u, password=hash_password(p), role=r))
    db.commit()
def seed_leaves(db):
    if db.query(Leave).count() > 0: return
    types = ['Vacation','Sick','Others']
    statuses = ['Pending','Approved','Rejected']
    users = ['staff1','staff2','staff3','manager1']
    for i in range(10):
        lid = str(uuid.uuid4())[:8]
        uname = random.choice(users)
        sd = datetime.date.today() - datetime.timedelta(days=random.randint(1,120))
        ed = sd + datetime.timedelta(days=random.randint(1,5))
        db.add(Leave(id=lid, username=uname, type=random.choice(types), start_date=sd.isoformat(), end_date=ed.isoformat(), status=random.choice(statuses), reason='Seeded leave request'))
    db.commit()
def init():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_users(db); seed_leaves(db)
    finally:
        db.close()
if __name__ == '__main__':
    init()
