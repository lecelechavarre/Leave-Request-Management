from models.db_alchemy import engine, SessionLocal
from models.models_alchemy import Base, User
from passlib.hash import bcrypt
def init():
    Base.metadata.create_all(bind=engine)
    # create default users if none exist
    db = SessionLocal()
    try:
        if db.query(User).count() == 0:
            db.add(User(username='admin', password=bcrypt.hash('admin'), role='admin'))
            db.add(User(username='employee', password=bcrypt.hash('employee'), role='employee'))
            db.commit()
    finally:
        db.close()
if __name__ == '__main__':
    init()
