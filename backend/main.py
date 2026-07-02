from fastapi import FastAPI, Depends, HTTPException, WebSocket, WebSocketDisconnect
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import database
from database import Match, TeamStats, SessionData, BattleZone, PitchDiagnostics
import routers
import players_router

app = FastAPI(title="Cricklytics Backend API")

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                pass

manager = ConnectionManager()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Next.js frontend will communicate with this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(routers.router, prefix="/api/matches")
app.include_router(players_router.router, prefix="/api/players")

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.websocket("/ws/live")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.post("/api/internal/notify_update")
async def notify_update():
    await manager.broadcast("UPDATE")
    return {"status": "broadcasted"}

from pydantic import BaseModel
import hashlib
from database import User

class AuthRequest(BaseModel):
    email: str
    password: str

@app.post("/api/auth/register")
def register(request: AuthRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    hashed_pw = hashlib.sha256(request.password.encode()).hexdigest()
    new_user = User(email=request.email, hashed_password=hashed_pw, is_premium=1)
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/api/auth/login")
def login(request: AuthRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    hashed_pw = hashlib.sha256(request.password.encode()).hexdigest()
    if user.hashed_password != hashed_pw:
        raise HTTPException(status_code=400, detail="Invalid email or password")
        
    return {"message": "Login successful", "email": user.email, "is_premium": user.is_premium}

@app.get("/")
def read_root():
    return {"message": "Welcome to Cricklytics API v2.0"}

@app.get("/api/matches/live")
def get_live_scores(db: Session = Depends(get_db)):
    matches = db.query(Match).all()
    results = []
    
    for match in matches:
        data = {
            "id": match.id,
            "format": match.format,
            "tournament": match.tournament,
            "team1": match.team1,
            "team2": match.team2,
            "status_text": match.status_text,
            "team1_score": match.team1_stats.score_string if match.team1_stats else "",
            "team2_score": match.team2_stats.score_string if match.team2_stats else "",
        }
        
        if match.format == "Test":
            data.update({
                "day": match.day,
                "target": match.target,
                "partnership": match.partnership,
                "status_message": match.status_message
            })
        elif match.format == "T20":
            data.update({
                "required_rate": match.required_rate,
                "equation": match.equation
            })
            
        results.append(data)
        
    return {"matches": results}


@app.get("/api/matches/{match_id}/test-center")
def get_test_center(match_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match or match.format != "Test":
        raise HTTPException(status_code=404, detail="Test match not found")
        
    return {
        "match_info": {
            "team1": match.team1,
            "team2": match.team2,
            "tournament": match.tournament,
            "status_text": match.status_text,
            "target": match.target,
            "partnership": match.partnership,
            "status_message": match.status_message,
            "team1_score": match.team1_stats.score_string if match.team1_stats else "",
            "team2_score": match.team2_stats.score_string if match.team2_stats else "",
        },
        "sessions": [
            {
                "name": s.name,
                "score": s.score,
                "status": s.status,
                "status_color": s.status_color,
                "is_live": bool(s.is_live)
            } for s in match.sessions
        ],
        "battle_zone": {
            "batsman_name": match.battle_zone.batsman_name if match.battle_zone else "",
            "batsman_stats": match.battle_zone.batsman_stats if match.battle_zone else "",
            "bowler_name": match.battle_zone.bowler_name if match.battle_zone else "",
            "bowler_stats": match.battle_zone.bowler_stats if match.battle_zone else "",
            "aggression_level": match.battle_zone.aggression_level if match.battle_zone else 0,
            "control_level": match.battle_zone.control_level if match.battle_zone else 0,
        },
        "pitch_diagnostics": {
            "surface_wear": match.pitch.surface_wear if match.pitch else "",
            "spin_deviation": match.pitch.spin_deviation if match.pitch else "",
            "weather": match.pitch.weather if match.pitch else "",
        }
    }
