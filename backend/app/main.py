from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import random
import asyncio
import os

from app.database import get_db, Base, engine
from app.models import (
    SimulationRequest, SimulationResponse,
    BiomechanicsRequest, BiomechanicsResponse,
    PlayerScoutCreate, PlayerScoutResponse
)
from app import crud
from ai_engine.simulator import run_tactical_simulation
from ai_engine.biomechanics import analyze_player_biomechanics

app = FastAPI(
    title="Cricklytics V2.0 API",
    description="Enterprise-grade AI Scouting, Tactical Match Intelligence, and Biomechanical Flaw Detection Platform",
    version="2.0.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# --- REST Endpoints ---

@app.get("/")
def read_root():
    return {
        "status": "online",
        "system": "Cricklytics V2.0 Platform API",
        "docs": "/docs",
        "version": "2.0.0"
    }

@app.post("/api/simulate", response_model=SimulationResponse)
def simulate_duel(req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Calculates ball-by-ball physical probabilities & tactical duel winner.
    """
    sim_result = run_tactical_simulation(
        batsman=req.batsman_name,
        bowler=req.bowler_name,
        format_type=req.format,
        pitch=req.pitch_condition,
        phase=req.match_phase,
        dew=req.dew_factor
    )
    crud.save_simulation_record(db, SimulationResponse(**sim_result))
    return sim_result

@app.post("/api/biomechanics/scan", response_model=BiomechanicsResponse)
def scan_biomechanics(req: BiomechanicsRequest):
    """
    Executes PyTorch Neural Network model analyzing video motion frames.
    """
    result = analyze_player_biomechanics(player_name=req.player_name, role=req.role)
    return result

@app.post("/api/scout/players", response_model=PlayerScoutResponse)
def scout_player(player: PlayerScoutCreate, db: Session = Depends(get_db)):
    """
    Saves a newly scouted player profile into database.
    """
    return crud.create_player_scout(db=db, scout=player)

@app.get("/api/scout/players", response_model=List[PlayerScoutResponse])
def get_scouted_players(db: Session = Depends(get_db)):
    """
    Returns all scouted player profiles.
    """
    return crud.get_all_scouted_players(db=db)

# --- WebSocket 0-Latency Live Score Tracking ---

@app.websocket("/ws/live-match")
async def live_match_websocket(websocket: WebSocket):
    await manager.connect(websocket)
    runs = 176
    wickets = 4
    overs = 17.2

    try:
        while True:
            await asyncio.sleep(3)
            # Step ball simulation
            runs += random.choice([0, 1, 1, 2, 4, 6])
            if random.random() < 0.1:
                wickets = min(10, wickets + 1)
            overs = round(overs + 0.1, 1)

            payload = {
                "match_id": "ind-vs-sa-t20",
                "tournament": "World T20 Sprint Cup Final",
                "team1": "India",
                "team2": "South Africa",
                "score_string": f"{runs}/{wickets} ({overs} ov)",
                "team1_score": "176/7 (20.0 ov)",
                "team2_score": f"{runs}/{wickets} ({overs} ov)",
                "status_text": "🔴 Live Ball-by-Ball Match",
                "required_rate": 9.2,
                "recent_ball": random.choice(["1", "4", "0", "W", "6", "2"]),
                "commentary": f"Over {overs}: Delivery targeted outside off stump."
            }
            await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
