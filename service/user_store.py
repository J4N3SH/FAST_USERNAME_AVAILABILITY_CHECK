from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config import DB_URL

Base = declarative_base()
engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)

def init_db():
    Base.metadata.create_all(bind=engine)

def save_new_user(username: str):
    session = SessionLocal()
    try:
        user = User(username=username)
        session.add(user)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()