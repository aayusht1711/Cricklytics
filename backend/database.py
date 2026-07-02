from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

SQLALCHEMY_DATABASE_URL = "sqlite:///./cricklytics.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# MODELS

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    format = Column(String, index=True) # "Test" or "T20"
    tournament = Column(String) # e.g. "Border-Gavaskar Trophy"
    team1 = Column(String)
    team2 = Column(String)
    status_text = Column(String) # e.g. "Day 4, Session 2" or "18.4 Overs"
    
    # Test specific
    day = Column(Integer, nullable=True)
    target = Column(Integer, nullable=True)
    partnership = Column(String, nullable=True)
    status_message = Column(String, nullable=True) # e.g. "IND needs 200"

    # T20 specific
    required_rate = Column(Float, nullable=True)
    equation = Column(String, nullable=True)

    # Relationships
    team1_stats = relationship("TeamStats", primaryjoin="and_(Match.id==TeamStats.match_id, TeamStats.team_name==Match.team1)", uselist=False, overlaps="team2_stats")
    team2_stats = relationship("TeamStats", primaryjoin="and_(Match.id==TeamStats.match_id, TeamStats.team_name==Match.team2)", uselist=False, overlaps="team1_stats")
    sessions = relationship("SessionData", back_populates="match")
    battle_zone = relationship("BattleZone", back_populates="match", uselist=False)
    pitch = relationship("PitchDiagnostics", back_populates="match", uselist=False)


class TeamStats(Base):
    __tablename__ = "team_stats"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    team_name = Column(String)
    score_string = Column(String) # e.g. "345 & 120/3" or "198/4"


class SessionData(Base):
    __tablename__ = "session_data"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    name = Column(String) # "Morning", "Afternoon (Live)", "Evening"
    score = Column(String) # "84/2"
    status = Column(String) # "Aus Dominated"
    status_color = Column(String) # "red", "blue", "gray"
    is_live = Column(Integer) # 0 or 1 (SQLite doesn't have strict boolean)
    
    match = relationship("Match", back_populates="sessions")


class BattleZone(Base):
    __tablename__ = "battle_zone"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    batsman_name = Column(String)
    batsman_stats = Column(String) # "Batting (45*)"
    bowler_name = Column(String)
    bowler_stats = Column(String) # "Bowling (1/24)"
    aggression_level = Column(Integer) # Percentage 0-100
    control_level = Column(Integer) # Percentage 0-100
    
    match = relationship("Match", back_populates="battle_zone")


class PitchDiagnostics(Base):
    __tablename__ = "pitch_diagnostics"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"))
    surface_wear = Column(String) # "75% (Cracking)"
    spin_deviation = Column(String) # "3.2°"
    weather = Column(String) # "Overcast (22°C)"
    
    match = relationship("Match", back_populates="pitch")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_premium = Column(Integer, default=1)

# Create all tables
Base.metadata.create_all(bind=engine)

