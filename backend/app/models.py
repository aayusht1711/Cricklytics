from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# --- Pydantic Schemas ---

class SimulationRequest(BaseModel):
    batsman_name: str = Field(..., example="Virat Kohli")
    bowler_name: str = Field(..., example="Jasprit Bumrah")
    format: str = Field(default="T20", example="T20")
    pitch_condition: str = Field(default="Green Top", example="Green Top")
    match_phase: str = Field(default="Death Overs", example="Death Overs")
    dew_factor: float = Field(default=35.0, ge=0.0, le=100.0, example=35.0)

class BallByBallOutcome(BaseModel):
    ball_number: int
    delivery_type: str
    target_zone: str
    wicket_probability: float
    boundary_probability: float
    tactical_note: str

class SimulationResponse(BaseModel):
    batsman_name: str
    bowler_name: str
    format: str
    pitch_condition: str
    match_phase: str
    dew_factor: float
    wicket_probability: float
    boundary_probability: float
    dot_ball_probability: float
    expected_runs_per_over: float
    dominant_winner: str
    win_margin: str
    toss_recommendation: str
    over_sequence: List[BallByBallOutcome]



class PlayerScoutCreate(BaseModel):
    player_name: str
    role: str
    country: str
    batting_rating: float
    bowling_rating: float

class PlayerScoutResponse(PlayerScoutCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
