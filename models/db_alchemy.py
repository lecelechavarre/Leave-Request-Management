from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
DB_FILE = os.path.join(os.path.dirname(__file__), '..', 'data', 'leave_manager.db')
os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
DATABASE_URL = f'sqlite:///{DB_FILE}'
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}, echo=False)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
