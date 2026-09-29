from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base
import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cricklytics_v2.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PlayerScoutDB(Base):
    __tablename__ = "player_scouts"

    id = Column(Integer, primary_key=True, index=True)
    player_name = Column(String, index=True)
    role = Column(String)
    country = Column(String)
    batting_rating = Column(Float)
    bowling_rating = Column(Float)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class SimulationHistoryDB(Base):
    __tablename__ = "simulation_history"

    id = Column(Integer, primary_key=True, index=True)
    batsman_name = Column(String)
    bowler_name = Column(String)
    format = Column(String)
    wicket_prob = Column(Float)
    boundary_prob = Column(Float)
    winner = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
