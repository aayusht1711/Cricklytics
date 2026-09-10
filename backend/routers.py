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
from pydantic import BaseModel
import os
import joblib
import pandas as pd
import numpy as np

class VenuePredictRequest(BaseModel):
    venue_key: str = "wankhede-mumbai"
    timing: str = "Night Match (7:00 PM)"
    season: str = "Oct-Feb (Winter/Post-Monsoon)"

@router.get("/venues")
def get_all_venues():
    from venue_db import VENUE_DATABASE
    return {
        "venues": [
            {"key": k, "name": v["name"], "country": v["country"], "pitch": v["default_pitch"]}
            for k, v in VENUE_DATABASE.items()
        ]
    }

@router.get("/live-weather")
def get_live_weather_endpoint(venue_key: str = "wankhede-mumbai"):
    from venue_db import fetch_live_weather
    return fetch_live_weather(venue_key)

@router.post("/predict-venue-dew")
def predict_venue_dew_endpoint(req: VenuePredictRequest):
    from venue_db import predict_dew_and_pitch
    return predict_dew_and_pitch(req.venue_key, req.timing, req.season)

class DuelRequest(BaseModel):
    batsman_id: str
    bowler_id: str
    format: str = "T20"
    pitch: str = "Flat / Batting"
    timing: str = "Day/Night"
    dew_factor: float = 50.0
    phase: str = "Middle Overs"

@router.post("/analyze-duel")
def analyze_tactical_duel(req: DuelRequest):
    from players_router import MOCK_PLAYERS
    from ml_engine import get_player_ml_features, MODEL_PATH
    
    clean_bat = req.batsman_id.lower().strip().replace(" ", "-").replace(".", "")
    clean_bowl = req.bowler_id.lower().strip().replace(" ", "-").replace(".", "")
    
    batsman = next((p for p in MOCK_PLAYERS if p["id"] == clean_bat or p["name"].lower() == req.batsman_id.lower()), None)
    bowler = next((p for p in MOCK_PLAYERS if p["id"] == clean_bowl or p["name"].lower() == req.bowler_id.lower()), None)
    
    if not batsman:
        batsman = next((p for p in MOCK_PLAYERS if "virat" in p["id"]), MOCK_PLAYERS[0])
    if not bowler:
        bowler = next((p for p in MOCK_PLAYERS if "bumrah" in p["id"] or "cummin" in p["id"]), MOCK_PLAYERS[1])
        
    bat_feat = get_player_ml_features(batsman)
    bowl_feat = get_player_ml_features(bowler)
    
    # 1. Environment & Physics Calculations
    dew = max(0.0, min(100.0, float(req.dew_factor)))
    spin_reduction_pct = round(dew * 0.48, 1)
    seam_grip_penalty = round(dew * 0.38, 1)
    outfield_speed_boost = round(dew * 0.25, 1)
    
    # Pitch modifiers
    pitch_type = req.pitch
    pitch_seam_bonus = 15 if "Green" in pitch_type else ( -10 if "Flat" in pitch_type else 0 )
    pitch_spin_bonus = 20 if "Dry" in pitch_type or "Cracked" in pitch_type else ( -15 if "Flat" in pitch_type else 0 )
    
    # Adjust features based on environment
    effective_bat_power = bat_feat["power"] + (dew * 0.12)
    effective_bowl_econ = bowl_feat["economy"] + (dew * 0.08) - (pitch_seam_bonus * 0.05)
    
    # ML model prediction if available
    clf = None
    if os.path.exists(MODEL_PATH):
        try:
            clf = joblib.load(MODEL_PATH)
        except Exception:
            pass
            
    phase_map = {"Powerplay": 0, "Middle Overs": 1, "Death Overs": 2}
    p_val = phase_map.get(req.phase, 1)
    
    if clf:
        deliv_risk = np.random.uniform(15.0, 90.0, 1000)
        deliv_deviation = np.random.uniform(0.0, 4.0 - (dew * 0.02), 1000)
        deliv_speed_delta = np.random.uniform(-6.0, 6.0, 1000)
        
        features = pd.DataFrame({
            'batsman_control': [bat_feat["control"]] * 1000,
            'batsman_power': [effective_bat_power] * 1000,
            'bowler_economy': [effective_bowl_econ] * 1000,
            'bowler_strike_rate': [bowl_feat["strike_rate"]] * 1000,
            'match_phase': [p_val] * 1000,
            'delivery_risk': deliv_risk,
            'delivery_deviation': deliv_deviation,
            'delivery_speed_delta': deliv_speed_delta
        })
        preds = clf.predict(features)
        counts = pd.Series(preds).value_counts(normalize=True) * 100
        
        dot_prob = round(float(counts.get(0, 25.0)), 1)
        single_prob = round(float(counts.get(1, 45.0)), 1)
        boundary_prob = round(float(counts.get(2, 20.0)), 1)
        wicket_prob = round(float(counts.get(3, 10.0)), 1)
    else:
        dot_prob, single_prob, boundary_prob, wicket_prob = 28.0, 44.0, 20.0, 8.0
        
    expected_rpo = round((boundary_prob / 100.0 * 4.5 * 6) + (single_prob / 100.0 * 1.4 * 6), 2)
    
    # 2. Dominance & Reason Logic
    bat_score = bat_feat["control"] * 0.4 + effective_bat_power * 0.4 + (dew * 0.2)
    bowl_score = (30.0 - bowl_feat["strike_rate"]) * 1.5 + (12.0 - effective_bowl_econ) * 4.0 + pitch_seam_bonus
    
    if bat_score > bowl_score + 5:
        winner = batsman["name"]
        margin = "Favorable Matchup for Batter"
        reasoning = f"{batsman['name']} overshadows {bowler['name']} under these conditions ({req.timing}, {dew}% Dew, {pitch_type}). High dew flattens seam movement by {seam_grip_penalty}% and reduces finger spin deviation by {spin_reduction_pct}%, enabling {batsman['name']} to hit through the line into his strong zone ({batsman['technique']['strong_zone']})."
    elif bowl_score > bat_score + 5:
        winner = bowler["name"]
        margin = "Dominant Spell for Bowler"
        reasoning = f"{bowler['name']} holds the advantage over {batsman['name']}. On a {pitch_type} surface during the {req.phase}, {bowler['name']}'s {bowler['technique']['strong_zone']} creates high wicket probability ({wicket_prob}%) before the wet ball destabilizes seam landing."
    else:
        winner = "Even Battle (50-50)"
        margin = "Tightly Contested Duel"
        reasoning = f"Balanced contest. {batsman['name']}'s {bat_feat['control']}% control rate counters {bowler['name']}'s economy rate ({bowl_feat['economy']} RPO). Outcome depends on execution in the first 6 balls of the spell."

    # 3. How to Tackle Blueprint
    tackle_plan = [
        f"Delivery 1-2 (Set-up): Bowl tight stump line on back-of-a-length ({'avoid fuller length due to ' + str(dew) + '% dew' if dew > 40 else 'exploit seam movement'}). Force a defensive block.",
        f"Delivery 3-4 (Pressure): Attack {batsman['name']}'s non-dominant zone. Use a cutter or 140+ km/h pace change to disrupt timing.",
        f"Delivery 5-6 (Wicket Ball): Target outside off stump on good length to tempt the {batsman['technique']['strong_zone']}. Place Deep Point and Catching Cover."
    ]
    
    field_placements = [
        {"name": "Catching Cover", "top": "35%", "left": "70%"},
        {"name": "Deep Mid-Wicket", "top": "75%", "left": "25%"},
        {"name": "Short Third Man", "top": "25%", "left": "75%"},
        {"name": "Deep Square Leg", "top": "75%", "left": "75%"}
    ]

    # 4. 6-Ball Delivery Execution Blueprint Sequence
    over_sequence = [
        {
            "ball": 1,
            "title": "Ball 1: Sighter / Dot Ball Setup",
            "delivery_type": "Good Length Outside Off (142 km/h)",
            "target": "Top of Off-Stump",
            "wicket_risk": round(wicket_prob * 0.8, 1),
            "scoring_threat": round(boundary_prob * 0.6, 1),
            "tactical_note": f"Test {batsman['name']}'s footwork on {pitch_type} without giving width."
        },
        {
            "ball": 2,
            "title": "Ball 2: Inward Angle Pressure",
            "delivery_type": "Seam-In Back of Length (138 km/h)",
            "target": "Ribcage / Hip Line",
            "wicket_risk": round(wicket_prob * 0.9, 1),
            "scoring_threat": round(boundary_prob * 0.7, 1),
            "tactical_note": "Cramp batter for room. Prevents easy extend-arm boundary hit."
        },
        {
            "ball": 3,
            "title": "Ball 3: Pace Variation Trap",
            "delivery_type": "Off-Cutter Off-Stump (124 km/h)",
            "target": "Good Length Outside Off",
            "wicket_risk": round(wicket_prob * 1.3, 1),
            "scoring_threat": round(boundary_prob * 0.9, 1),
            "tactical_note": "Disrupt timing as batter looks to accelerate. Slower grip effective on grass top."
        },
        {
            "ball": 4,
            "title": "Ball 4: Defensive Reset",
            "delivery_type": "Wide Yorker (144 km/h)",
            "target": "Wide Off-Stump Guideline",
            "wicket_risk": round(wicket_prob * 0.7, 1),
            "scoring_threat": round(boundary_prob * 0.4, 1),
            "tactical_note": "Nullifies boundary risk. Forces single to deep cover."
        },
        {
            "ball": 5,
            "title": "Ball 5: Surprise Bouncer",
            "delivery_type": "Heavy Short Ball (145 km/h)",
            "target": "Shoulder / Helmet Height",
            "wicket_risk": round(wicket_prob * 1.4, 1),
            "scoring_threat": round(boundary_prob * 1.1, 1),
            "tactical_note": "Exploit psychological shift after Yorker. Deep fine leg in play."
        },
        {
            "ball": 6,
            "title": "Ball 6: Primary Wicket Delivery",
            "delivery_type": "Attacking Full Out-Swinger (141 km/h)",
            "target": "4th Stump Channel",
            "wicket_risk": round(wicket_prob * 1.6, 1),
            "scoring_threat": round(boundary_prob * 1.2, 1),
            "tactical_note": f"Induce drive into {batsman['technique']['strong_zone']}. Catching Cover and Slip ready."
        }
    ]

    # 5. Toss Advantage & Run-Chase Impact Calculation
    chase_win_rate = round(min(88.0, 52.0 + (dew * 0.36)), 1)
    defend_win_rate = round(100.0 - chase_win_rate, 1)
    if dew >= 40.0:
        recommended_toss = "WIN TOSS & BOWL FIRST"
        toss_rationale = f"Heavy dew factor ({dew}%) causes wet ball, reducing spin grip by {spin_reduction_pct}% in the second innings. Chasing teams have a {chase_win_rate}% win probability."
    else:
        recommended_toss = "WIN TOSS & BAT FIRST"
        toss_rationale = f"Low dew factor ({dew}%). Surface remains consistent. Batting first allows setting pressure target with {defend_win_rate}% win probability."

    toss_analytics = {
        "bowl_first_win_prob": chase_win_rate,
        "bat_first_win_prob": defend_win_rate,
        "chase_advantage_pct": round(chase_win_rate - 50.0, 1),
        "recommended_toss": recommended_toss,
        "toss_rationale": toss_rationale
    }

    return {
        "batsman": batsman["name"],
        "bowler": bowler["name"],
        "context": {
            "format": req.format,
            "pitch": req.pitch,
            "timing": req.timing,
            "dew_factor": dew,
            "phase": req.phase
        },
        "physics_analytics": {
            "spin_reduction_pct": spin_reduction_pct,
            "seam_grip_penalty_pct": seam_grip_penalty,
            "outfield_speed_boost_pct": outfield_speed_boost
        },
        "probabilities": {
            "wicket_probability": wicket_prob,
            "boundary_probability": boundary_prob,
            "dot_ball_probability": dot_prob,
            "expected_runs_per_over": expected_rpo
        },
        "h2h_winner": {
            "winner_name": winner,
            "margin": margin,
            "reasoning": reasoning
        },
        "tackle_strategy": {
            "title": f"How to Tackle {batsman['name']}",
            "blueprint": tackle_plan,
            "field_placements": field_placements
        },
        "over_sequence": over_sequence,
        "toss_analytics": toss_analytics
    }

