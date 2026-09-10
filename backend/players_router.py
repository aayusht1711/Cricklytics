from fastapi import APIRouter, HTTPException

router = APIRouter()
from csv_loader import load_all_players
MOCK_PLAYERS = load_all_players()

@router.get("/")
def get_all_players():
    # Return brief info for search/list with strictly unique IDs
    seen_ids = set()
    unique_players = []
    for p in MOCK_PLAYERS:
        if p["id"] not in seen_ids:
            seen_ids.add(p["id"])
            unique_players.append({
                "id": p["id"],
                "name": p["name"],
                "role": p["role"],
                "team": p["team"],
                "image": p["image"]
            })
    return {"players": unique_players}

@router.get("/{player_id}")
def get_player(player_id: str):
    player = next((p for p in MOCK_PLAYERS if p["id"] == player_id), None)
    if not player:
        # Try to scrape if not in mock DB
        from player_scraper import get_player_stats
        scraped_player = get_player_stats(player_id.replace("-", " "))
        if "error" not in scraped_player:
            # Dynamically add to MOCK_PLAYERS if not already present
            if not any(p["id"] == scraped_player.get("id") for p in MOCK_PLAYERS):
                MOCK_PLAYERS.append(scraped_player)
            return scraped_player
        raise HTTPException(status_code=404, detail="Player not found")
    return player

import random
import os
import joblib
import pandas as pd
import numpy as np

# Load ML Model
MODEL_PATH = "model.pkl"
clf = None
if os.path.exists(MODEL_PATH):
    try:
        clf = joblib.load(MODEL_PATH)
    except Exception as e:
        print(f"Error loading model: {e}")

@router.get("/simulate/{batsman_id}/{bowler_id}")
def simulate_matchup(batsman_id: str, bowler_id: str, phase: str = "Middle Overs"):
    clean_bat = batsman_id.lower().strip().replace(" ", "-").replace(".", "")
    clean_bowl = bowler_id.lower().strip().replace(" ", "-").replace(".", "")
    
    batsman = next((p for p in MOCK_PLAYERS if p["id"] == clean_bat or p["name"].lower() == batsman_id.lower()), None)
    bowler = next((p for p in MOCK_PLAYERS if p["id"] == clean_bowl or p["name"].lower() == bowler_id.lower()), None)
    
    # Try scraping if not found
    from player_scraper import get_player_stats
    if not batsman:
        scraped_bat = get_player_stats(batsman_id.replace("-", " "))
        if "error" not in scraped_bat and not any(p["id"] == scraped_bat.get("id") for p in MOCK_PLAYERS):
            MOCK_PLAYERS.append(scraped_bat)
            batsman = scraped_bat
            
    if not bowler:
        scraped_bowl = get_player_stats(bowler_id.replace("-", " "))
        if "error" not in scraped_bowl and not any(p["id"] == scraped_bowl.get("id") for p in MOCK_PLAYERS):
            MOCK_PLAYERS.append(scraped_bowl)
            bowler = scraped_bowl
            
    if not batsman or not bowler:
        raise HTTPException(status_code=404, detail="Batsman or Bowler not found")
        
    if clf:
        # --- REAL MACHINE LEARNING INFERENCE ---
        phase_map = {"Powerplay": 0, "Middle Overs": 1, "Death Overs": 2}
        p_val = phase_map.get(phase, 1)
        
        from ml_engine import get_player_ml_features
        bat_feat = get_player_ml_features(batsman)
        bowl_feat = get_player_ml_features(bowler)
        
        # Generate 1000 deliveries with random risk, deviation, speed delta
        np.random.seed(42)
        deliv_risk = np.random.uniform(10.0, 95.0, 1000)
        deliv_deviation = np.random.uniform(0.0, 4.0, 1000)
        deliv_speed_delta = np.random.uniform(-8.0, 8.0, 1000)
        
        features = pd.DataFrame({
            'batsman_control': [bat_feat["control"]] * 1000,
            'batsman_power': [bat_feat["power"]] * 1000,
            'bowler_economy': [bowl_feat["economy"]] * 1000,
            'bowler_strike_rate': [bowl_feat["strike_rate"]] * 1000,
            'match_phase': [p_val] * 1000,
            'delivery_risk': deliv_risk,
            'delivery_deviation': deliv_deviation,
            'delivery_speed_delta': deliv_speed_delta
        })
        
        # Run inference using the trained Random Forest
        preds = clf.predict(features)
        
        # Count outcomes (0=Dot, 1=Single, 2=Boundary, 3=Wicket)
        counts = pd.Series(preds).value_counts(normalize=True) * 100
        
        dot_prob = counts.get(0, 0.0)
        single_prob = counts.get(1, 0.0)
        adj_boundary = counts.get(2, 0.0)
        adj_wicket = counts.get(3, 0.0)
        
        expected_rpo = (adj_boundary/100 * 4.5 * 6) + (single_prob/100 * 1.5 * 6)
        sim_type = "Machine Learning (RandomForestClassifier)"
    else:
        # Fallback to Math
        bat_control = batsman["technique"]["control_percentage"]
        bowl_control = bowler["technique"]["control_percentage"]
        control_delta = bat_control - bowl_control
        
        base_boundary_prob = batsman["t20_stats"]["boundary_impact"] / 2.5
        base_wicket_prob = 100 - bat_control
        
        adj_boundary = max(5, base_boundary_prob + (control_delta * 0.2))
        adj_wicket = max(2, base_wicket_prob - (control_delta * 0.3))
        
        if phase == "Death Overs":
            adj_boundary *= 1.5
            adj_wicket *= 1.5
        elif phase == "Powerplay":
            adj_boundary *= 1.2
            adj_wicket *= 1.2
            
        dot_prob = max(10, 100 - adj_boundary - adj_wicket - 30)
        expected_rpo = (adj_boundary/100 * 4.5 * 6) + (30/100 * 1.5 * 6)
        sim_type = "Mathematical Model"

    return {
        "batsman": batsman["name"],
        "bowler": bowler["name"],
        "phase": phase,
        "simulations": 1000,
        "engine": sim_type,
        "results": {
            "wicket_probability": round(float(adj_wicket), 1),
            "boundary_probability": round(float(adj_boundary), 1),
            "dot_ball_probability": round(float(dot_prob), 1),
            "expected_runs_per_over": round(float(expected_rpo), 2)
        },
        "insight": f"Analysis powered by {sim_type}. {batsman['name']}'s {batsman['technique']['strong_zone']} vs {bowler['name']}."
    }
