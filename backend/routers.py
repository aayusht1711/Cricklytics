import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import database
from database import Match

router = APIRouter()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/odi-center")
def get_odi_center(db: Session = Depends(get_db)):
    # Pick any match (preferably match 2)
    match = db.query(Match).filter(Match.id == 2).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    return {
        "match_info": {
            "team1": match.team1,
            "team2": match.team2,
            "tournament": "Global ODI Cup",
            "status_text": "Overs: 34.2",
            "team1_score": match.team1_stats.score_string if match.team1_stats else "",
            "team2_score": match.team2_stats.score_string if match.team2_stats else "",
            "required_rate": "7.20",
            "current_rate": "6.85"
        },
        "phase_analytics": [
            {"phase": "Powerplay 1 (1-10)", "runs": 62, "wickets": 1, "run_rate": 6.2},
            {"phase": "Middle Overs (11-40)", "runs": 145, "wickets": 3, "run_rate": 5.8},
            {"phase": "Death Overs (41-50)", "runs": "TBD", "wickets": "TBD", "run_rate": "TBD"}
        ],
        "strike_rotation": {
            "dot_balls": 42,
            "singles": 112,
            "boundaries": 28,
            "rotation_efficiency": "68%"
        }
    }

@router.get("/t20-center")
def get_t20_center(db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == 2).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
        
    return {
        "match_info": {
            "team1": match.team1,
            "team2": match.team2,
            "tournament": "World T20 Sprint",
            "status_text": "Overs: 16.4",
            "team1_score": match.team1_stats.score_string if match.team1_stats else "",
            "team2_score": match.team2_stats.score_string if match.team2_stats else "",
            "equation": "34 runs from 20 balls"
        },
        "boundary_impact": {
            "four_percentage": 35,
            "six_percentage": 25,
            "dot_percentage": 30,
            "rotation_percentage": 10
        },
        "matchup_predictor": {
            "batsman": "Explosive Striker",
            "bowler": "Death Specialist",
            "wicket_probability": "18%",
            "boundary_probability": "42%"
        },
        "momentum": random.randint(40, 80)
    }
