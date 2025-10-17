from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from models.db_alchemy import Base
class User(Base):
    __tablename__ = 'users'
    username = Column(String, primary_key=True, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
class Leave(Base):
    __tablename__ = 'leaves'
    id = Column(String, primary_key=True, index=True)
    username = Column(String, nullable=False, index=True)
    type = Column(String)
    start_date = Column(String)
    end_date = Column(String)
    status = Column(String)
    reason = Column(Text)
    approved_by = Column(String, nullable=True)
    approved_date = Column(String, nullable=True)
    remarks = Column(Text, nullable=True)
class Audit(Base):
    __tablename__ = 'audits'
    id = Column(String, primary_key=True, index=True)
    action = Column(String)
    username = Column(String)
    target_id = Column(String)
    before = Column(Text)
    after = Column(Text)
    ts = Column(DateTime, server_default=func.now())
