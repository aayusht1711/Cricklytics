from sqlalchemy.orm import Session
from app.database import PlayerScoutDB, SimulationHistoryDB
from app.models import PlayerScoutCreate, SimulationResponse
import datetime

def create_player_scout(db: Session, scout: PlayerScoutCreate):
    db_player = PlayerScoutDB(
        player_name=scout.player_name,
        role=scout.role,
        country=scout.country,
        batting_rating=scout.batting_rating,
        bowling_rating=scout.bowling_rating
    )
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def get_all_scouted_players(db: Session, skip: int = 0, limit: int = 100):
    return db.query(PlayerScoutDB).offset(skip).limit(limit).all()

def save_simulation_record(db: Session, sim: SimulationResponse):
    db_record = SimulationHistoryDB(
        batsman_name=sim.batsman_name,
        bowler_name=sim.bowler_name,
        format=sim.format,
        wicket_prob=sim.wicket_probability,
        boundary_prob=sim.boundary_probability,
        winner=sim.dominant_winner
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record
